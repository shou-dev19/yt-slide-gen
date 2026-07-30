import puppeteer from 'puppeteer';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';
import { resolveBrowserExecutable } from './resolve_browser.js';
import { copyCapturedSlides } from './copy_captured_slides.js';
import { measureSlideWhitespace, findOverThreshold } from './measure_whitespace.js';
import {
    measureSlideLayout,
    measureShortSpread,
    measureImagePaths,
    findIllustrationDominant,
    collectOverflow,
    collectBrokenIcons,
    collectShortSpreadViolations,
    collectImagePathViolations,
} from './measure_layout.js';

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
    const layoutResults = [];

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

            // いらすとや主役化（§7・§9）／テキスト見切れ・はみ出し（§10）／未定義アイコン（§9）の機械判定
            const layout = await measureSlideLayout(page, SLIDE_SELECTOR, i);
            // ショートで禁止されている見開き構造・図鑑装丁（generate-short-slides §0）の機械判定
            const shortSpread = isShort ? await measureShortSpread(page, SLIDE_SELECTOR, i) : null;
            // 画像パス規約（generate-short-slides §4）の機械判定。long / short 共通。
            const imagePaths = await measureImagePaths(page, SLIDE_SELECTOR, i);
            layoutResults.push({
                id,
                file: `${FILE_PREFIX}${paddedId}.png`,
                ...layout,
                ...(isShort ? { shortSpread } : {}),
                imagePaths,
            });
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

    // --- レイアウトレポート（いらすとや主役化 / 見切れ・はみ出し）の出力 ---
    const layoutReportPath = path.join(OUT_DIR, `${FILE_PREFIX}layout-report.json`);
    const dominant = findIllustrationDominant(layoutResults);
    const { clipped, outOfBounds } = collectOverflow(layoutResults);
    const brokenIcons = collectBrokenIcons(layoutResults);
    const shortSpreadViolations = isShort ? collectShortSpreadViolations(layoutResults) : [];
    const imagePathViolations = collectImagePathViolations(layoutResults);
    fs.writeFileSync(
        layoutReportPath,
        JSON.stringify(
            {
                mode,
                slides: layoutResults,
                illustrationDominant: dominant,
                clipped,
                outOfBounds,
                brokenIcons,
                ...(isShort ? { shortSpreadViolations } : {}),
                imagePathViolations,
            },
            null,
            2,
        ),
    );
    console.log(`\nレイアウトレポート: ${layoutReportPath}`);

    if (dominant.length === 0) {
        console.log('✅ いらすとやが主役になっているページはありません。');
    } else {
        console.warn(`⚠️  いらすとやが主役になっているページ: ${dominant.length} 件`);
        for (const d of dominant) {
            console.warn(
                `  - ${d.id} (${d.label}): ${d.reasons.join(' / ')}` +
                ` — イラスト ${(d.illustrationAreaRatio * 100).toFixed(0)}% / テキスト ${(d.textAreaRatio * 100).toFixed(0)}%` +
                ` [${d.images.join(', ')}]`,
            );
        }
        console.warn('  SKILL.md §7・§9（主役はテキスト。いらすとやは脇役）に沿って、台本の情報をテキスト・表・部品として足すこと。');
    }

    if (clipped.length === 0 && outOfBounds.length === 0) {
        console.log('✅ テキストの見切れ・はみ出しはありません。');
    } else {
        if (clipped.length > 0) {
            console.warn(`⚠️  テキストが見切れている箇所: ${clipped.length} 件`);
            for (const c of clipped) {
                const dir = [c.clippedXPx > 0 ? `横 ${c.clippedXPx}px` : null, c.clippedYPx > 0 ? `縦 ${c.clippedYPx}px` : null]
                    .filter(Boolean)
                    .join(' / ');
                console.warn(`  - ${c.id} (${c.label}) ${c.path}: ${dir} 切れ 「${c.text}」`);
            }
        }
        if (outOfBounds.length > 0) {
            console.warn(`⚠️  内容領域からはみ出している箇所: ${outOfBounds.length} 件`);
            for (const o of outOfBounds) {
                const dirs = Object.entries(o.overflowPx).map(([k, v]) => `${k} ${v}px`).join(' / ');
                console.warn(`  - ${o.id} (${o.label}) ${o.path}: ${dirs} 「${o.text}」`);
            }
        }
        console.warn('  SKILL.md §10（オーバーフロー厳禁・下端の字幕帯に本文を置かない）に沿って、フォント縮小・行数削減・隣ページへの分割で直すこと。');
    }

    if (brokenIcons.length === 0) {
        console.log('✅ 表示されていない FontAwesome アイコンはありません。');
    } else {
        console.warn(`⚠️  表示されていない FontAwesome アイコン: ${brokenIcons.length} 件`);
        for (const b of brokenIcons) {
            const names = b.iconClasses.length > 0 ? b.iconClasses.join(', ') : b.classes;
            console.warn(`  - ${b.id} (${b.label}) ${b.path}: ${names}`);
        }
        console.warn('  Free 版に存在しない名前（Pro 限定アイコンや綴り間違い）です。実在する近縁アイコンを探して差し替えること:');
        console.warn("    curl -s https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css | grep -o '\\.fa-<語幹>[a-z0-9-]*:before'");
    }

    if (imagePathViolations.length === 0) {
        console.log('✅ 規約違反の画像パスはありません。');
    } else {
        console.warn(`⚠️  規約違反の画像パス: ${imagePathViolations.length} 件`);
        for (const violation of imagePathViolations) {
            console.warn(`  - ${violation.id}: ${violation.reasons.join(' / ')} — src="${violation.src}"`);
        }
        console.warn(
            '  generate-short-slides の SKILL.md §4（画像パスは public/ 始まりの相対パス。絶対パス・file://・他パッケージ参照は禁止）を参照して直すこと。',
        );
    }

    const { copiedCount, removedCount } = copyCapturedSlides({
        sourceDir: OUT_DIR,
        destinationDir: SLIDE_DEST_DIR,
        mode,
    });
    console.log(`Removed ${removedCount} old PNG(s) from ${SLIDE_DEST_DIR}`);
    console.log(`Copied ${copiedCount} ${mode} slide PNG(s) to ${SLIDE_DEST_DIR}`);

    if (isShort) {
        if (shortSpreadViolations.length === 0) {
            console.log('✅ 見開き構造・図鑑装丁を使用しているショートはありません。');
        } else {
            console.warn(`⚠️  見開き構造・図鑑装丁を使用しているショート: ${shortSpreadViolations.length} 件`);
            for (const violation of shortSpreadViolations) {
                const evidence = [];
                if (violation.reasons.includes('見開き構造')) {
                    evidence.push(`.page ${violation.evidence.pageCount} 個`);
                    if (violation.evidence.hasLeftAndRight) evidence.push('.page.left / .page.right');
                }
                if (violation.reasons.includes('図鑑装丁クラス')) {
                    evidence.push(violation.evidence.classes.map((className) => `.${className}`).join(', '));
                }
                console.warn(`  - ${violation.id}: ${violation.reasons.join(' / ')} — ${evidence.join(' / ')}`);
            }
            console.warn(
                '  generate-short-slides の SKILL.md §0（見開き構成・図鑑装丁の使用禁止。直近の video/short-* ブランチの slides-short.html を踏襲する）を参照して直すこと。',
            );
        }
    }
}

main().catch((error) => {
    console.error(error);
    process.exitCode = 1;
});
