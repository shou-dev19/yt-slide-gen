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
- 同じくキャプチャ時に**いらすとや主役化とテキスト見切れ・はみ出しを計測**し `out/{slide_|short_slide_}layout-report.json` に出力する（`scripts/measure_layout.js`）。判定は次の3つで、いずれも警告のみ（終了コードは0）:
  - **いらすとや主役化**: ページ内容に占めるいらすとや画像の面積比が **テキスト面積を上回る**、または **0.4 以上**なら不合格（生成 SKILL.md §7・§9）。「見出し要素の矩形との比」は、いらすとや PNG の透明余白で面積が水増しされ良品が落ちるため判定に使わない（参考値としてのみ出力）。
  - **見切れ**: `overflow` が visible 以外の要素で、**自分の直接のテキスト**が `scrollWidth/Height` 超過で切られているもの。子孫まで対象にすると、角の菱形アクセントのように意図的に枠外へ抜く装飾を持つコンテナが毎回引っかかる。
  - **はみ出し**: 見開き（`.page`）は**内容領域**が枠（下部 padding ＝字幕帯への侵入を検出したい）、std・ショートは**要素の外形**が枠（`.watermark` や `.slide-illust` を padding 領域へ意図的に絶対配置する書式のため）。
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
