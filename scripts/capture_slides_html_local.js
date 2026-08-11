import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import puppeteer from 'puppeteer';

import {
    collectBrokenIcons,
    collectImagePathViolations,
    collectOverflow,
    findIllustrationDominant,
    findIllustrationOccluded,
    measureImagePaths,
    measureSlideLayout,
} from './measure_layout.js';
import { findOverThreshold, measureSlideWhitespace } from './measure_whitespace.js';
import { resolveBrowserExecutable } from './resolve_browser.js';


const SCRIPT_DIR = path.dirname(fileURLToPath(import.meta.url));
const PROJECT_ROOT = path.resolve(SCRIPT_DIR, '..');
const HTML_PATH = path.resolve(PROJECT_ROOT, 'slides.html');
const OUT_DIR = path.resolve(PROJECT_ROOT, 'out');
const SLIDE_SELECTOR = '.slide-container';


async function main() {
    fs.mkdirSync(OUT_DIR, { recursive: true });
    for (const filename of fs.readdirSync(OUT_DIR)) {
        if (/^slide_[\d-]+\.png$/.test(filename)) {
            fs.unlinkSync(path.resolve(OUT_DIR, filename));
        }
    }

    const executablePath = resolveBrowserExecutable();
    const browser = await puppeteer.launch({
        headless: 'new',
        // --allow-file-access-from-files はいらすとやの可視率計測（canvas で透明画素を除く）に必要。
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--font-render-hinting=none', '--allow-file-access-from-files'],
        ...(executablePath ? { executablePath } : {}),
    });
    const page = await browser.newPage();
    await page.setViewport({ width: 1920, height: 1080 });
    await page.goto(`file://${HTML_PATH}`, { waitUntil: 'networkidle0' });
    await Promise.race([
        page.evaluate(async () => { await document.fonts.ready; }),
        new Promise((resolve) => setTimeout(resolve, 3000)),
    ]);
    await page.evaluate(async () => {
        const images = Array.from(document.images);
        await Promise.all(images.map((img) => img.decode().catch(() => {})));
    });

    const slideIds = await page.evaluate((selector) => {
        return Array.from(document.querySelectorAll(selector)).map((slide, index) => {
            let previous = slide.previousSibling;
            while (previous) {
                if (previous.nodeType === 8) {
                    const match = previous.nodeValue.match(/Slide ID:\s*([\w.-]+)/);
                    if (match) return match[1];
                }
                previous = previous.previousSibling;
            }
            return String(index + 1);
        });
    }, SLIDE_SELECTOR);

    const whitespaceResults = [];
    const layoutResults = [];
    const slideElements = await page.$$(SLIDE_SELECTOR);
    for (let index = 0; index < slideIds.length; index += 1) {
        const id = slideIds[index];
        const paddedId = id.replace(/^(\d+)/, (number) => number.padStart(2, '0'));
        const filename = `slide_${paddedId}.png`;
        await slideElements[index].screenshot({ path: path.resolve(OUT_DIR, filename) });
        const pages = await measureSlideWhitespace(page, SLIDE_SELECTOR, index);
        whitespaceResults.push({ id, file: filename, pages });
        const layout = await measureSlideLayout(page, SLIDE_SELECTOR, index);
        const imagePaths = await measureImagePaths(page, SLIDE_SELECTOR, index);
        layoutResults.push({ id, file: filename, ...layout, imagePaths });
        console.log(`Captured Slide ID ${id}: ${path.resolve(OUT_DIR, filename)}`);
    }
    await browser.close();

    const overThreshold = findOverThreshold(whitespaceResults);
    const whitespaceReport = path.resolve(OUT_DIR, 'slide_whitespace-report.json');
    fs.writeFileSync(
        whitespaceReport,
        JSON.stringify({ mode: 'long', threshold: Number((1 / 3).toFixed(3)), slides: whitespaceResults, overThreshold }, null, 2),
    );

    const illustrationDominant = findIllustrationDominant(layoutResults);
    const illustrationOccluded = findIllustrationOccluded(layoutResults);
    const { clipped, outOfBounds } = collectOverflow(layoutResults);
    const brokenIcons = collectBrokenIcons(layoutResults);
    const imagePathViolations = collectImagePathViolations(layoutResults);
    const layoutReport = path.resolve(OUT_DIR, 'slide_layout-report.json');
    fs.writeFileSync(
        layoutReport,
        JSON.stringify({
            mode: 'long',
            slides: layoutResults,
            illustrationDominant,
            illustrationOccluded,
            clipped,
            outOfBounds,
            brokenIcons,
            imagePathViolations,
        }, null, 2),
    );

    console.log(`Slides: ${slideIds.length}`);
    console.log(`Whitespace warnings: ${overThreshold.length}`);
    console.log(`Illustration warnings: ${illustrationDominant.length}`);
    console.log(`Occluded illustration warnings: ${illustrationOccluded.length}`);
    console.log(`Clipped text warnings: ${clipped.length}`);
    console.log(`Out-of-bounds warnings: ${outOfBounds.length}`);
    console.log(`Broken icon warnings: ${brokenIcons.length}`);
    console.log(`Image path warnings: ${imagePathViolations.length}`);
    console.log(`Whitespace report: ${whitespaceReport}`);
    console.log(`Layout report: ${layoutReport}`);
}


main().catch((error) => {
    console.error(error);
    process.exitCode = 1;
});
