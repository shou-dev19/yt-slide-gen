import puppeteer from 'puppeteer';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';
import { resolveBrowserExecutable } from './resolve_browser.js';
import { copyCapturedSlides } from './copy_captured_slides.js';
import { measureSlideWhitespace, findOverThreshold } from './measure_whitespace.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const PROJECT_ROOT = path.resolve(__dirname, '..');
const OUT_DIR = path.join(PROJECT_ROOT, 'out');

// Get mode from command line args
const mode = process.argv[2] === 'short' ? 'short' : 'long';
const isShort = mode === 'short';
const SLIDE_DEST_DIR = path.resolve(
    PROJECT_ROOT,
    '..',
    'video-studio',
    'video',
    'public',
    'temp',
    mode,
    'slides',
);

const SLIDE_HTML_PATH = isShort ? path.join(PROJECT_ROOT, 'slides-short.html') : path.join(PROJECT_ROOT, 'slides.html');
const SLIDE_SELECTOR = '.slide-container';
// always set a large viewport so the layout avoids tight squeeze/scrollbars
const VIEWPORT_WIDTH = 1920;
const VIEWPORT_HEIGHT = 1080;
const FILE_PREFIX = isShort ? 'short_slide_' : 'slide_';

async function main() {
    // Ensure output directory exists
    if (!fs.existsSync(OUT_DIR)) {
        fs.mkdirSync(OUT_DIR, { recursive: true });
    }

    // Remove stale PNGs from a previous video's run so bridge.sh never picks up
    // leftover slide IDs that no longer exist in the current slides.html.
    const staleFiles = fs.readdirSync(OUT_DIR).filter((f) => f.startsWith(FILE_PREFIX) && f.endsWith('.png'));
    for (const f of staleFiles) {
        fs.unlinkSync(path.join(OUT_DIR, f));
    }
    if (staleFiles.length > 0) {
        console.log(`Removed ${staleFiles.length} stale PNG(s) from ${OUT_DIR}`);
    }

    const executablePath = resolveBrowserExecutable();

    const browser = await puppeteer.launch({
        headless: 'new',
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--font-render-hinting=none',
        ],
        ...(executablePath ? { executablePath } : {}),
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

    const whitespaceResults = [];

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

            // 余白率の計測（SKILL.md §10「ページの1/3以上が空白なら不合格」の機械判定）
            const pages = await measureSlideWhitespace(page, SLIDE_SELECTOR, i);
            whitespaceResults.push({ id, file: `${FILE_PREFIX}${paddedId}.png`, pages });
        }
    }

    await browser.close();

    // --- 余白レポートの出力 ---
    const reportPath = path.join(OUT_DIR, `${FILE_PREFIX}whitespace-report.json`);
    const overThreshold = findOverThreshold(whitespaceResults);
    fs.writeFileSync(
        reportPath,
        JSON.stringify({ mode, threshold: Number((1 / 3).toFixed(3)), slides: whitespaceResults, overThreshold }, null, 2),
    );
    console.log(`\n余白レポート: ${reportPath}`);
    if (overThreshold.length === 0) {
        console.log('✅ 下端の空きが 1/3 以上のページはありません。');
    } else {
        console.warn(`⚠️  下端の空きが 1/3 以上のページ: ${overThreshold.length} 件`);
        for (const o of overThreshold) {
            console.warn(
                `  - ${o.id} (${o.label}): 下端の空き ${(o.bottomGapRatio * 100).toFixed(0)}% / 総余白 ${(o.whitespaceRatio * 100).toFixed(0)}%`,
            );
        }
        console.warn('  SKILL.md §10 の優先順位（①台本から不足内容を追記 → ②文字・アイコン拡大 → ③隣ページと再配分 → ④いらすとや）で埋めること。');
    }

    const { copiedCount, removedCount } = copyCapturedSlides({
        sourceDir: OUT_DIR,
        destinationDir: SLIDE_DEST_DIR,
        mode,
    });
    console.log(`Removed ${removedCount} old PNG(s) from ${SLIDE_DEST_DIR}`);
    console.log(`Copied ${copiedCount} ${mode} slide PNG(s) to ${SLIDE_DEST_DIR}`);
}

main().catch((error) => {
    console.error(error);
    process.exitCode = 1;
});
