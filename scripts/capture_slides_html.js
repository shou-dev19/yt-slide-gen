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

    // Determine the Chromium executable to use.
    // On ARM64 Linux containers, Puppeteer's bundled Chromium is x64 and fails
    // via Rosetta. Prefer a system-installed Chromium when available.
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
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--font-render-hinting=none',
        ],
        ...(systemChromium ? { executablePath: systemChromium } : {}),
    });
    const page = await browser.newPage();

    // Set viewport
    await page.setViewport({ width: VIEWPORT_WIDTH, height: VIEWPORT_HEIGHT });

    const fileUrl = `file://${SLIDE_HTML_PATH}`;
    console.log(`Loading: ${fileUrl} (Mode: ${mode})`);
    await page.goto(fileUrl, { waitUntil: 'networkidle0' });

    // Wait for fonts to load. Google Fonts may fail to load from file:// (CORS),
    // so we race against a 3s timeout to avoid hanging on a failed font fetch.
    await Promise.race([
        page.evaluate(async () => { await document.fonts.ready; }),
        new Promise(resolve => setTimeout(resolve, 3000)),
    ]);

    // Ensure all images are decoded and rendered before proceeding
    await page.evaluate(async () => {
        const imgs = Array.from(document.images);
        await Promise.all(imgs.map(img => {
            if (img.complete) return Promise.resolve();
            return new Promise((resolve, reject) => {
                img.onload = resolve;
                img.onerror = reject;
            });
        }));
        // Use decode() to wait for painted pixels if supported
        await Promise.all(imgs.map(img => img.decode().catch(() => { })));
    });

    // Find all slide containers and extract their IDs
    const slideIds = await page.evaluate((selector) => {
        const slides = document.querySelectorAll(selector);
        return Array.from(slides).map((slide, index) => {
            // Find the previous comment node to extract the slide ID
            let prev = slide.previousSibling;
            while (prev) {
                if (prev.nodeType === 8) { // Node.COMMENT_NODE is 8
                    const match = prev.nodeValue.match(/(?:スライドID|Slide ID):\s*([\w.-]+)/);
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
            const paddedId = id.replace(/^(\d+)/, (n) => n.padStart(2, '0'));
            const outFile = path.join(OUT_DIR, `${FILE_PREFIX}${paddedId}.png`);
            await slideElement.screenshot({ path: outFile });
            console.log(`Saved: ${outFile}`);
        }
    }

    await browser.close();
}

main().catch(console.error);
