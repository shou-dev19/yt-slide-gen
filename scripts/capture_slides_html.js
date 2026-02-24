import puppeteer from 'puppeteer';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const PROJECT_ROOT = path.resolve(__dirname, '..');
const OUT_DIR = path.join(PROJECT_ROOT, 'out');
const SLIDE_HTML_PATH = path.join(PROJECT_ROOT, 'slides.html');

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

    // Set viewport to 1280x720 (Slide size)
    await page.setViewport({ width: 1280, height: 720 });

    const fileUrl = `file://${SLIDE_HTML_PATH}`;
    console.log(`Loading: ${fileUrl}`);
    await page.goto(fileUrl, { waitUntil: 'networkidle0' });

    // Find all slide containers and extract their IDs
    const slideIds = await page.evaluate(() => {
        const slides = document.querySelectorAll('.slide-container');
        return Array.from(slides).map((slide, index) => {
            // Find the previous comment node to extract the slide ID
            let prev = slide.previousSibling;
            while (prev) {
                if (prev.nodeType === 8) { // Node.COMMENT_NODE is 8
                    const match = prev.nodeValue.match(/スライドID:\s*(\d+)/);
                    if (match) return match[1];
                }
                prev = prev.previousSibling;
            }
            // Fallback to sequential index if comment is not found
            return `${index + 1}`;
        });
    });

    console.log(`Found ${slideIds.length} slides.`);

    for (let i = 0; i < slideIds.length; i++) {
        const id = slideIds[i];
        console.log(`Processing Slide ID: ${id}`);

        // Select the slide element
        const slideElement = (await page.$$('.slide-container'))[i];

        if (slideElement) {
            const outFile = path.join(OUT_DIR, `slide_${id}.png`);
            await slideElement.screenshot({ path: outFile });
            console.log(`Saved: ${outFile}`);
        }
    }

    await browser.close();
}

main().catch(console.error);
