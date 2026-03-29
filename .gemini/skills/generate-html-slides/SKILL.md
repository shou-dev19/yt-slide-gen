---
name: generate-html-slides
description: Generate a presentation slides HTML file based on a script, applying a 'Huge Text' design, specific colors, and image/placeholder mapping.
---

# Generate HTML Slides Skill

This skill provides instructions on how to generate "Yukkuri Kaisetsu" style presentation slides in HTML.

## Design Rules ("デカ文字" / Huge Text Style)

視聴維持率を高めるため、スマホで見た際にも文字がはっきり読める**「超・巨大文字サイズ」**を基準とします。

1.  **基本設定**
    * **解像度:** `1280px × 720px`
    * **フォント:** 'M PLUS Rounded 1c' (Weight: 800/900) を使用し、親しみやすさと視認性を確保。
    * **配色:** ユーザーから指定されたテーマカラーをベースに、白背景＋枠線で統一感を出す。

2.  **CSSスタイル要件（厳守）**

    * **コンテナ:** `.slide-container` { width: 1280px; height: 720px; border: 10px solid var(--primary-color); background: white; box-sizing: border-box; position: relative; overflow: hidden; display: flex; flex-direction: column; justify-content: center; align-items: center; padding: 40px; flex-shrink: 0; }
    * **見出し (H1):** フォントサイズ **130px** 基準。太字。文字の縁取り（text-shadow）を適用。例: `text-shadow: 4px 4px 0px white, -4px -4px 0px white, 4px -4px 0px white, -4px 4px 0px white, 0px 4px 0px var(--primary-color), 0px -4px 0px var(--primary-color), 4px 0px 0px var(--primary-color), -4px 0px 0px var(--primary-color);`
    * **中見出し (H2):** フォントサイズ **90px** 基準。下線装飾（border-bottom: 8px solid var(--accent-yellow);）あり。
    * **本文 (p, li):** フォントサイズ **64px** 基準。行間 1.4。
    * **強調色:** 重要な数字やキーワードは `color: var(--accent-red);` で強調し、通常の文字色は `color: var(--text-dark);` を基本とする。
    * **アイコン:** FontAwesome (`<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">`) を使用し、サイズは **100px〜200px** で大きく配置。
    * **リスト:** FontAwesome等のアイコンをリスト項目（li）の先頭に付ける場合は、デフォルトの黒丸（・）が表示されないよう、必ず `ul` 要素に `list-style-type: none; padding: 0;` を指定すること。

3.  **レイアウト構成**

    * **センター配置:** 基本は画面中央にテキストとアイコンを大きく配置。
    * **2カラム (Split):** 左右に要素を分ける場合、余白を詰めすぎず、要素を大きく保つ。
      `.split { display: flex; width: 100%; justify-content: space-around; align-items: center; }`
      `.split-col { flex: 1; display: flex; flex-direction: column; align-items: center; padding: 20px; }`
    * **表 (Table):** フォントサイズ **50px** 基準。セル内余白は十分に取りつつ、行数が多い場合は上下のパディング（例: `padding: 10px 15px;`）やフォントサイズを微調整し、親コンテナ（高さ720px）から絶対に縦に見切れないよう細心の注意を払うこと。
    * **見切れ防止（全体）:** H2や画像、表、箇条書きを組み合わせる際は、マージン（margin）や画像の `max-height` を緻密に計算し、縦の範囲内に要素がぴったり収まるようにすること。

4. **画像の選定と配置のルール**

    * イラストやロゴなどを表示する場合は、 `public/images/` 配下の既存の画像（`common`, `irasutoya`, `logo` 等）を `img` タグで配置する。
    * 既存の画像で横幅や縦幅が大きなものは `max-height: 500px; max-width: 100%; object-fit: contain;` 等のスタイルでスライド内に収めること。
    * 全画面表示が必要な画像（共通の注意書きスライドやチャートなど）は以下のようなクラスを当てて背景全体を覆うようにする。この時、親要素からの `max-height` 制限などを上書きして見切れを防ぐため、必ず `max-width: 100%; max-height: 100%; object-fit: contain;` にすること。（画像によって `cover` と `contain` は使い分けるが、基本として端が切れない `contain` を優先する）
      `.fullscreen-img { width: 100%; height: 100%; max-width: 100%; max-height: 100%; object-fit: contain; position: absolute; top: 0; left: 0; z-index: 10; }`
    * **注釈・引用表記:** 画像の下部に「※docomoのページから引用」「※キャンペーンのリンクは概要欄をチェック！」などの注釈テキストを追加する場合は、本文より控えめなサイズ（`font-size: 20px〜35px`程度）、色（`#666` 等）にすること。注釈テキスト分の高さを確保できるよう、画像の `max-height` を縮小して縦はみ出しを防ぐこと。

5. **プレースホルダーの設定**

    * プロジェクト内で適切な素材やイラストが見つからない場合、後程画像生成ができるように `<Placeholder>` タグに必要な画像生成プロンプトを記載して配置する。
    * 例: `<Placeholder>スマホ代に悩む女性のイラスト</Placeholder>`
    * CSS例: `Placeholder { display: flex; justify-content: center; align-items: center; background: #f0f0f0; border: 4px dashed #999; border-radius: 20px; padding: 40px; font-size: 50px; font-weight: bold; color: #666; text-align: center; width: 80%; margin: 20px auto; } Placeholder::before { content: "🖼️ "; margin-right: 10px; }`

6. **出力形式要件**

    * 出力は単一の HTML ファイルとし、すべてのスライド（div要素）を含めること。
    * `body` は `display: flex; flex-direction: column; gap: 40px;` のようにし、すべての `.slide-container` を縦並びに表示できるようにする。
    * 各スライドの HTML 直前に `<!-- スライドID: 〇〇 -->` を記載し、台本のどのスライドに対応するかを明確にすること。

## 特殊な共通スライドの配置例

複数の動画で使い回すスライド等、特定の画像が指定されている場合は、文字やプレースホルダーは作成せず、以下のように画像のみを配置する。

```html
<!-- スライドID: XX -->
<div class="slide-container">
  <img src="public/images/slides/評価項目について.png" class="fullscreen-img">
</div>
```
