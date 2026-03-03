import puppeteer from 'puppeteer';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const PROJECT_ROOT = path.resolve(__dirname, '..');
const OUT_DIR = path.join(PROJECT_ROOT, 'out');

// Get mode from command line args
const mode = process.argv[2] === 'short' ? 'short' : 'long';
const isShort = mode === 'short';

const SLIDE_HTML_PATH = isShort ? path.join(PROJECT_ROOT, 'slides-short.html') : path.join(PROJECT_ROOT, 'slides.html');
const SLIDE_SELECTOR = isShort ? '.slide' : '.slide-container';
// always set a large viewport so the layout avoids tight squeeze/scrollbars
const VIEWPORT_WIDTH = 1920;
const VIEWPORT_HEIGHT = 1080;
const FILE_PREFIX = isShort ? 'short_slide_' : 'slide_';

async function main() {
    // Ensure output directory exists
    if (!fs.existsSync(OUT_DIR)) {
        fs.mkdirSync(OUT_DIR, { recursive: true });
    }

    const browser = await puppeteer.launch({
        headless: 'new',
        args: ['--no-sandbox', '--disable-setuid-sandbox'],
    });
    const page = await browser.newPage();

    // Set viewport
    await page.setViewport({ width: VIEWPORT_WIDTH, height: VIEWPORT_HEIGHT });

    const fileUrl = `file://${SLIDE_HTML_PATH}`;
    console.log(`Loading: ${fileUrl} (Mode: ${mode})`);
    await page.goto(fileUrl, { waitUntil: 'networkidle0' });

    // Find all slide containers and extract their IDs
    const slideIds = await page.evaluate((selector) => {
        const slides = document.querySelectorAll(selector);
        return Array.from(slides).map((slide, index) => {
            // Find the previous comment node to extract the slide ID
            let prev = slide.previousSibling;
            while (prev) {
                if (prev.nodeType === 8) { // Node.COMMENT_NODE is 8
                    const match = prev.nodeValue.match(/スライドID:\s*([\w.-]+)/);
                    if (match) return match[1];
                }
                prev = prev.previousSibling;
            }
            // Fallback to sequential index if comment is not found
            return `${index + 1}`;
        });
    }, SLIDE_SELECTOR);

    console.log(`Found ${slideIds.length} slides.`);

    for (let i = 0; i < slideIds.length; i++) {
        const id = slideIds[i];
        console.log(`Processing Slide ID: ${id}`);

        // Select the slide element
        const slideElement = (await page.$$(SLIDE_SELECTOR))[i];

        if (slideElement) {
            const outFile = path.join(OUT_DIR, `${FILE_PREFIX}${id}.png`);
            await slideElement.screenshot({ path: outFile });
            console.log(`Saved: ${outFile}`);
        }
    }

    await browser.close();
}

main().catch(console.error);
