import puppeteer from 'puppeteer';
import pptxgen from 'pptxgenjs';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const PROJECT_ROOT = path.resolve(__dirname, '..');
const OUT_DIR = path.join(PROJECT_ROOT, 'out');

const mode = process.argv[2] === 'short' ? 'short' : 'long';
const isShort = mode === 'short';

const SLIDE_HTML_PATH = isShort
    ? path.join(PROJECT_ROOT, 'slides-short.html')
    : path.join(PROJECT_ROOT, 'slides.html');
const SLIDE_SELECTOR = isShort ? '.slide' : '.slide-container';
const VIEWPORT_WIDTH = 1920;
const VIEWPORT_HEIGHT = 1080;

async function main() {
    if (!fs.existsSync(OUT_DIR)) {
        fs.mkdirSync(OUT_DIR, { recursive: true });
    }

    const systemChromiumCandidates = [
        '/usr/bin/chromium',
        '/usr/bin/chromium-browser',
        '/usr/bin/google-chrome',
        '/usr/bin/google-chrome-stable',
    ];
    const systemChromium =
        process.env.PUPPETEER_EXECUTABLE_PATH ||
        systemChromiumCandidates.find((p) => fs.existsSync(p));

    const browser = await puppeteer.launch({
        headless: 'new',
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--font-render-hinting=none'],
        ...(systemChromium ? { executablePath: systemChromium } : {}),
    });
    const page = await browser.newPage();
    await page.setViewport({ width: VIEWPORT_WIDTH, height: VIEWPORT_HEIGHT });

    const fileUrl = `file://${SLIDE_HTML_PATH}`;
    console.log(`Loading: ${fileUrl} (Mode: ${mode})`);
    await page.goto(fileUrl, { waitUntil: 'networkidle0' });

    await page.evaluate(async () => {
        await document.fonts.ready;
        const imgs = Array.from(document.images);
        await Promise.all(
            imgs.map((img) => {
                if (img.complete) return Promise.resolve();
                return new Promise((resolve, reject) => {
                    img.onload = resolve;
                    img.onerror = reject;
                });
            })
        );
        await Promise.all(imgs.map((img) => img.decode().catch(() => {})));
    });

    const slideIds = await page.evaluate((selector) => {
        const slides = document.querySelectorAll(selector);
        return Array.from(slides).map((slide, index) => {
            let prev = slide.previousSibling;
            while (prev) {
                if (prev.nodeType === 8) {
                    const match = prev.nodeValue.match(/(?:スライドID|Slide ID):\s*([\w.-]+)/);
                    if (match) return match[1];
                }
                prev = prev.previousSibling;
            }
            return `${index + 1}`;
        });
    }, SLIDE_SELECTOR);

    console.log(`Found ${slideIds.length} slides.`);

    const pptx = new pptxgen();
    pptx.layout = 'LAYOUT_WIDE'; // 13.33" x 7.5" (16:9)

    const slideElements = await page.$$(SLIDE_SELECTOR);

    for (let i = 0; i < slideIds.length; i++) {
        const id = slideIds[i];
        console.log(`Processing Slide ID: ${id} (${i + 1}/${slideIds.length})`);

        const slideElement = slideElements[i];
        if (!slideElement) continue;

        const imageData = await slideElement.screenshot({ encoding: 'base64' });

        const pptxSlide = pptx.addSlide();
        pptxSlide.addImage({
            data: `image/png;base64,${imageData}`,
            x: 0,
            y: 0,
            w: '100%',
            h: '100%',
        });
    }

    await browser.close();

    const outFileName = isShort ? 'slides-short.pptx' : 'slides.pptx';
    const outPath = path.join(OUT_DIR, outFileName);
    await pptx.writeFile({ fileName: outPath });
    console.log(`PPTX saved: ${outPath}`);
}

main().catch(console.error);
