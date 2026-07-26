# CLAUDE.md

台本からスライド画像（PNG）を生成するサブモジュール。実体は「スライド HTML を編集 → Puppeteer でキャプチャ」の2段階。

## Commands

```bash
npm run capture-slides-html         # slides.html       → out/slide_NN.png (long)
npm run capture-short-slides-html   # slides-short.html → out/short_slide_NN.png (short)
npm run export-pptx [/ export-short-pptx]  # スライドHTML → PPTX
```

## 非自明な値・挙動

- キャプチャ対象は各 HTML 内の `.slide-container` 要素（1要素=1枚、1920×1080）。
- キャプチャ実行時に `out/` の同プレフィックス PNG を**全削除してから**生成する（前回動画の残骸を bridge.sh が拾わないため）。
- キャプチャと同時に**余白率を計測**し `out/{slide_|short_slide_}whitespace-report.json` に出力する（`scripts/measure_whitespace.js`）。判定は各ページの **`bottomGapRatio`（内容の最下端から内容領域の下端までの空き）が 1/3 以上で不合格**。総余白率で判定すると章扉・CTA のような中央寄せレイアウトが軒並み引っかかるため、判定には使わず参考値として出すだけにしている。閾値超過があれば警告を出す（終了コードは0）。
- ブラウザは `scripts/resolve_browser.js` が解決する（ARM64 コンテナではシステムの Chromium を使用）。Puppeteer の bundled Chromium 前提のコードを書かないこと。

## File Roles

| File | Role |
|---|---|
| `slides.html` / `slides-short.html` | キャプチャ対象のスライド本体。`generate-youtube-video` パイプラインの Step 3 が台本から生成・上書きする |
| `slides-spread-templates.html` / `slides-zukan-sample*.html` | 見開き・図鑑スライドのデザインテンプレート／サンプル（キャプチャ対象外） |
| `台本.txt` | 親リポジトリの `bridge.sh a` がコピーしてくる入力 |
| `public/images/{logo,charts,characters,thumbnails}` | **sync-assets の配布先（編集禁止）**。マスターは親の `shared/assets/`、`bash scripts/sync-assets.sh` で配備 |
| `src/` | Vite + React アプリ（旧方式のスライド。現行パイプラインは HTML 直編集方式） |

## Skills

スキルの実体は `.agents/skills/<name>/` のみ。`.claude/skills/<name>` はディレクトリ単位のシンボリックリンク。**編集は `.agents/skills/` 側のみ。**
