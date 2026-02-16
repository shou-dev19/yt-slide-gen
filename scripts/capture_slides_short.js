import puppeteer from 'puppeteer';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const PROJECT_ROOT = path.resolve(__dirname, '..');
const PUBLIC_DIR = path.join(PROJECT_ROOT, 'public');
const OUT_DIR = path.join(PROJECT_ROOT, 'out');
const SLIDE_HTML_PATH = path.join(PUBLIC_DIR, 'スライド_ショート.html');

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
    // Even though content is 720x720 inside, the container is 1280x720
    await page.setViewport({ width: 1280, height: 720 });

    const fileUrl = `file://${SLIDE_HTML_PATH}`;
    console.log(`Loading: ${fileUrl}`);
    await page.goto(fileUrl, { waitUntil: 'networkidle0' });

    // Wait for fonts to load
    await page.evaluate(() => document.fonts.ready);

    // Find all slide containers
    const slides = await page.$$('.slide-container');
    console.log(`Found ${slides.length} slides.`);

    // Remove border from slide-container for cleaner screenshots
    await page.evaluate(() => {
        const style = document.createElement('style');
        style.textContent = '.slide-container { border: none !important; }';
        document.head.appendChild(style);
    });

    for (let i = 0; i < slides.length; i++) {
        // Use 1-based index for file naming
        const id = i + 1;
        console.log(`Processing Short Slide: ${id}`);

        const slideElement = slides[i];

        if (slideElement) {
            const outFile = path.join(OUT_DIR, `short_slide_${id}.png`);
            await slideElement.screenshot({ path: outFile });
            console.log(`Saved: ${outFile}`);
        }
    }

    await browser.close();
}

main().catch(console.error);
