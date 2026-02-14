import puppeteer from 'puppeteer';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const PROJECT_ROOT = path.resolve(__dirname, '..');
const PUBLIC_DIR = path.join(PROJECT_ROOT, 'public');
const OUT_DIR = path.join(PROJECT_ROOT, 'out');
const SLIDE_HTML_PATH = path.join(PUBLIC_DIR, 'スライド.html');

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

    // Find all slide containers
    const slideIds = await page.evaluate(() => {
        const slides = document.querySelectorAll('.slide-container');
        return Array.from(slides).map((slide, index) => {
            // Try to find the .slide-id element
            const idEl = slide.querySelector('.slide-id');
            if (idEl) {
                // Extract ID text, e.g., "ID: 1" -> "1"
                const text = idEl.innerText.trim();
                const match = text.match(/ID:\s*(\d+)/);
                return match ? match[1] : `unknown_${index}`;
            }
            return `unknown_${index}`;
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
