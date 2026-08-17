#!/usr/bin/env node
// Capture and validate slides.html without copying PNGs outside slide-gen.

import fs from 'fs';
import path from 'path';
import puppeteer from 'puppeteer';
import { resolveBrowserExecutable } from '/workspaces/yt-factory/packages/slide-gen/scripts/resolve_browser.js';
import { measureSlideWhitespace, findOverThreshold } from '/workspaces/yt-factory/packages/slide-gen/scripts/measure_whitespace.js';
import {
    measureSlideLayout,
    measureImagePaths,
    findIllustrationDominant,
    findIllustrationOccluded,
    collectOverflow,
    collectBrokenIcons,
    collectImagePathViolations,
} from '/workspaces/yt-factory/packages/slide-gen/scripts/measure_layout.js';

const PROJECT_ROOT = '/workspaces/yt-factory/packages/slide-gen';
const OUT_DIR = path.join(PROJECT_ROOT, 'out');
const SLIDE_HTML_PATH = path.join(PROJECT_ROOT, 'slides.html');
const SLIDE_SELECTOR = '.slide-container';

async function main() {
    fs.mkdirSync(OUT_DIR, { recursive: true });
    for (const file of fs.readdirSync(OUT_DIR)) {
        if (/^slide_[0-9].*\.png$/.test(file)) fs.unlinkSync(path.join(OUT_DIR, file));
    }

    const executablePath = resolveBrowserExecutable();
    const browser = await puppeteer.launch({
        headless: 'new',
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--font-render-hinting=none',
            '--allow-file-access-from-files',
        ],
        ...(executablePath ? { executablePath } : {}),
    });
    const page = await browser.newPage();
    await page.setViewport({ width: 1920, height: 1080 });
    await page.goto(`file://${SLIDE_HTML_PATH}`, { waitUntil: 'networkidle0' });
    await Promise.race([
        page.evaluate(async () => { await document.fonts.ready; }),
        new Promise((resolve) => setTimeout(resolve, 3000)),
    ]);
    await page.evaluate(async () => {
        const images = Array.from(document.images);
        await Promise.all(images.map((img) => img.complete ? Promise.resolve() : new Promise((resolve, reject) => {
            img.onload = resolve;
            img.onerror = reject;
        })));
        await Promise.all(images.map((img) => img.decode().catch(() => {})));
    });

    const slideIds = await page.evaluate((selector) => Array.from(document.querySelectorAll(selector)).map((slide, index) => {
        let previous = slide.previousSibling;
        while (previous) {
            if (previous.nodeType === 8) {
                const match = previous.nodeValue.match(/Slide ID:\s*([\w.-]+)/);
                if (match) return match[1];
            }
            previous = previous.previousSibling;
        }
        return String(index + 1);
    }), SLIDE_SELECTOR);

    const whitespaceResults = [];
    const layoutResults = [];
    const slideElements = await page.$$(SLIDE_SELECTOR);
    for (let index = 0; index < slideIds.length; index += 1) {
        const id = slideIds[index];
        const paddedId = id.replace(/^(\d+)/, (number) => number.padStart(2, '0'));
        const file = `slide_${paddedId}.png`;
        await slideElements[index].screenshot({ path: path.join(OUT_DIR, file) });
        const pages = await measureSlideWhitespace(page, SLIDE_SELECTOR, index);
        whitespaceResults.push({ id, file, pages });
        const layout = await measureSlideLayout(page, SLIDE_SELECTOR, index);
        const imagePaths = await measureImagePaths(page, SLIDE_SELECTOR, index);
        layoutResults.push({ id, file, ...layout, imagePaths });
        console.log(`captured ${id} -> ${path.join(OUT_DIR, file)}`);
    }
    await browser.close();

    const overThreshold = findOverThreshold(whitespaceResults);
    const dominant = findIllustrationDominant(layoutResults);
    const occluded = findIllustrationOccluded(layoutResults);
    const { clipped, outOfBounds } = collectOverflow(layoutResults);
    const brokenIcons = collectBrokenIcons(layoutResults);
    const imagePathViolations = collectImagePathViolations(layoutResults);

    fs.writeFileSync(
        path.join(OUT_DIR, 'slide_whitespace-report.json'),
        JSON.stringify({ mode: 'long-local', threshold: Number((1 / 3).toFixed(3)), slides: whitespaceResults, overThreshold }, null, 2),
    );
    fs.writeFileSync(
        path.join(OUT_DIR, 'slide_layout-report.json'),
        JSON.stringify({
            mode: 'long-local',
            slides: layoutResults,
            illustrationDominant: dominant,
            illustrationOccluded: occluded,
            clipped,
            outOfBounds,
            brokenIcons,
            imagePathViolations,
        }, null, 2),
    );

    console.log(JSON.stringify({
        slideCount: slideIds.length,
        overThreshold: overThreshold.length,
        illustrationDominant: dominant.length,
        illustrationOccluded: occluded.length,
        clipped: clipped.length,
        outOfBounds: outOfBounds.length,
        brokenIcons: brokenIcons.length,
        imagePathViolations: imagePathViolations.length,
    }, null, 2));
}

main().catch((error) => {
    console.error(error);
    process.exitCode = 1;
});
