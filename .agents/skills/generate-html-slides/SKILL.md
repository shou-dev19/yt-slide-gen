---
name: generate-html-slides
description: "Generate the long-form '格安SIM図鑑' presentation slides as full-screen 1920x1080 two-page book spreads (見開き), with carrier evaluation spreads, chapter dividers, and asset mapping."
---

Script file path: $ARGUMENTS (default: `台本.txt`)

---

# Generate HTML Slides Skill（図鑑見開き版）

このスキルは「格安SIM図鑑」チャンネルの**長尺動画**スライドを HTML で生成する。

## 大原則：本編スライドは全て「図鑑見開き」

本編のスライドは**例外なく** 1920×1080 の**左右2ページの本（見開き）＋机背景**で作る。
動画側（video-studio `BookSpread`）は各スライドを全画面表示するため、紙の見開きが画面いっぱいに広がり、評価パートでは ZukanSpread がその上にカメラ演出を重ねる。

唯一の例外は**冒頭のつかみスライド**（速報／タイトル／初回チャンネル誘導など、目次より前の導入カット）で、ここだけ従来の `std`（1280×720・デカ文字）を許容する。**目次以降の全スライド（解説・比較表・評価・章扉/章カード・おすすめ診断・まとめ・過去動画CTA・定型の注意喚起/ブログ/チャンネル登録）は見開き**にすること。

> 旧仕様（1スライド=1280×720 のデカ文字カード）はもう使わない。評価パートだけ見開き、という中途半端な状態にしないこと。

## 1. 装丁と共有CSS

`templates/spread-base.css` に見開きの装丁と本文レイアウト部品が**全て**入っている。生成HTMLでは必ずこれをリンクし、定義済みクラスを使う（重複定義しない）。

```html
<link href="https://fonts.googleapis.com/css2?family=M+PLUS+Rounded+1c:wght@400;500;700;800;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
<link rel="stylesheet" href="templates/spread-base.css">
```

各見開きスライドの骨格（`--brand` 系はブランド色の上書き）:

```html
<!-- Slide ID: N -->
<div class="slide-container" style="--brand:#1565C0;--brand-deep:#0d47a1;--brand-soft:#e3f0fb">
  <div class="book">
    <div class="spine"></div>
    <div class="page left">
      <div class="page-head">左ページの見出し</div>
      <div class="page-body center"> … </div>
      <span class="page-no">― 11 ―</span>
    </div>
    <div class="page right">
      <span class="index-tab">格安SIM図鑑</span>
      <div class="page-head">右ページの見出し</div>
      <div class="page-body center"> … </div>
      <span class="page-no">― 12 ―</span>
    </div>
  </div>
</div>
```

- `.index-tab` は**右ページのみ**に置く（図鑑インデックスタブ）。右ページの `.page-head` はタブを避けるよう自動で右側に余白が入る（`spread-base.css` 側で対応済み）。
- `.page-no` はノンブル。解説・評価などの本文ページに付け、左右で連番（章扉/章カード/CTA/定型などの「扉・特殊ページ」は省略してよい）。
- **本（見開き）はほぼ全画面で表示され、スライドのコンテンツは各ページの上部 約80% に描画される。ページ下部 約20% は空白の紙面として残り、その上に video-studio の字幕が重なる**（`spread-base.css` の `.page` の `padding-bottom` で担保。per-slide で本やページの寸法を変えない）。本文がこの字幕帯に被らないよう、コンテンツは上部80%だけに収める。
- 各ページの内容領域は約 **810×772px**。`.page-body` は既定で余白を `space-evenly` に散らして縦を使い切る。単一ブロック（lead/emph 一個など）は `.center` で縦中央寄せにする。

### ブランド色（per-slide で上書き）

`--brand` / `--brand-deep` / `--brand-soft` をキャリア・章ごとに設定する。

| 対象 | brand | brand-deep | brand-soft |
|---|---|---|---|
| ドコモ系 / 赤系（ahamo・楽天・一般章） | `#C8102E` | `#9a0c23` | `#fde3e7` |
| IIJmio・青系 | `#1565C0` | `#0d47a1` | `#e3f0fb` |
| 緑系（mineo 等） | `#22a73f` | `#1c8b34` | `#e8f5e6` |

1枚の見開き内でページごとに別ブランド色にしたい場合は、その**ブロック要素に `style="--brand:…;--brand-deep:…;--brand-soft:…"` を再指定**すれば局所的に切り替わる（例：左ページ=赤、右ページ=青の比較）。

## 2. 共通レイアウト部品（spread-base.css 由来）

ページ本文はこれらの部品を組み合わせて作る。per-slide の微調整は `style` 属性で。

| クラス | 用途 |
|---|---|
| `.page-head`（`<small>` で副題） | ページ見出し（ブランド色の下線） |
| `.page-body` / `.page-body.center` | 本文コンテナ（縦に使い切る／縦中央寄せ） |
| `.lead`（`.em` で強調） | 紙のテロップ風リード文 |
| `.rows > li`（`.ic` / `.badge` / `.tx`、`.tx .sub` / `.tx .em`） | アイコン or 番号付きリスト行 |
| `.emph`（`.big` / `.em`） | 数値・結論の強調ボックス |
| `.warn`（`.ic` / `.em`） | 注意ボックス |
| `.note` | 小さなグレーの注記 |
| `.sheet`（`th`/`td`、`.em` / `.sub`） | 紙の表（料金・比較） |
| `.big-title`（`.em`） | ページ中央の大見出し（章タイトル・CTA等） |
| `.divider`（`.kicker` / `.num` / `.seal`） | 章扉のエンブレム |
| `.visual > img` | サムネ等のビジュアルを1ページに大きく |
| `.bigicon` | 中央の大アイコン（FontAwesome） |
| `.logos > img` | ロゴ並べ |
| `.agenda` / `.benefits` | 目次／「この動画でわかること」 |
| `.head-left`/`.total`/`.head-right`/`.cards`/`.card`/`.card .rank`/`.card-name`/`.card .line`（`.line.pro`/`.line.con` の `.tag`） | 評価 Layout B（1社1見開き） |
| `.rank.SS`/`.S`/`.A`/`.B`/`.C` | 評価ランクバッジ（色は段階固定） |

### コンテンツ種別 → レイアウト指針

- **目次**：左 `.agenda`（動画の流れ）／右 `.benefits`（この動画でわかること）。
- **解説（リスト系）**：`.page-head` + `.rows`。項目が多ければ左右ページに分割（見出しに `<small>①②</small>` 等で続きを示す）。
- **数値・結論**：`.emph`。補足は隣ページに `.lead` / `.note`。
- **料金・比較表**：`.sheet`。列・行が多ければ左右ページに分割。
- **注意点**：`.warn` ＋ `.note`、または左ページに `.bigicon`（⚠）。
- **イラスト/図解**：片ページを `.visual` にして大きく、もう片方で要点を `.lead`。
- **おすすめ診断・まとめ**：`.rows`（番号バッジ）や `.emph` を左右に。

## 3. 評価見開き（1社1見開き）— 必須ルール

各キャリアの評価は**1社につき1見開き**で表現する（Layout B）。台本の「スライドに表示する内容」書式：

```
評価見開き／社名／総合:rank／観点:rank(＋pro／－con) を6観点
```

- データは原則 `shared/sim_evaluations.json` と `primary-information.md` から取る（未登録キャリアは台本側のランク・所感を使う）。
- **6観点固定順**：データ料金・通信品質・初期費用・通話料・店舗サポート・オプション。
- **左ページ**：`.head-left`（ロゴ＋`.file-no`＋`.total`総合評価）／`.cards` に観点3枚（`.card` = `.rank` + `.card-name` + `.line.pro` + `.line.con`）。
- **右ページ**：`.index-tab` ＋ `.head-right` にレーダーチャート（`public/images/charts/<社名>.png`）／`.cards` に残り観点3枚。
- ランクの色は `.rank.SS/S/A/B/C` に従う（独自配色にしない）。pro は `＋`、con は `－`。
- レーダーチャートは `.head-right img`（`height:100%`）で表示。評価バッジを別途並べない。

## 4. 章扉（N-0）と章カード（N）— 見開きで作る・役割を分ける

章の入口は**2枚**あり、どちらも見開きにするが**見た目を明確に変える**。

- **章扉 `N-0`（にぎやか・扉ページ）**：左ページに `.divider`（`CHAPTER`/大きな番号/`FILE No.0X` シール）、右ページに `.big-title`（章テーマ）＋丸いリード。`.page-no` は付けない。
  - **キャラクター画像はスライドに焼き込まない**。本編では video-studio 側がショウ／モモコを画面隅にライブ合成するため、見開きにも描くと二重になる。扉は番号エンブレムと大見出しで魅せる。
- **章カード `N`（シンプル・タイポ）**：左ページに `CHAPTER` ラベル＋巨大番号、右ページに `.big-title` で章名のみ。バッジ・吹き出し・アイコンは足さない。

> **コンテンツ移送ルール**：同じプレーン番号 `N` に「章名」と「解説本文」の両方が紐づく場合、`N` は章カードのみにし、解説は新スライド `N-1` に移して台本側のナレーション行も `N`→`N-1` に振り直す（音声/スライド同期を保つ）。

## 5. 過去動画 CTA 見開き

- 片ページを `.visual` にして `public/images/thumbnails/` の**実サムネイル**を大きく置く（汎用アイコンで代用しない。社名/トピックで部分一致選択）。
- もう片方に `.bigicon`（▶）＋ `.big-title`（「○○の解説動画もチェック！」）＋ `.note`。

## 6. 定型スライド（注意喚起／ブログ／チャンネル登録）も見開きで

旧 `public/images/slides/*.png` の貼り付けは使わない。次の内容を見開きで作る：

- **投稿時点の注意喚起**：左 `.bigicon`（ℹ）＋`.big-title`「ご注意」／右 `.warn`「料金・プラン・キャンペーンは投稿時点の情報」＋`.note`「最新は各社公式で確認」。
- **ブログ／note案内**：左 `.bigicon`（ペン）＋`.big-title`／右 `.lead`＋`.note`。
- **チャンネル登録・高評価**：左 `.bigicon`（ベル）＋`.big-title`／右 `.logos`（👍🔔）＋`.lead`。

## 7. 冒頭つかみスライド（std を許容する唯一の例外）

目次より前の導入カット（速報・タイトル・初回チャンネル誘導）だけ `std`（1280×720）でよい。最小限の `std` CSS を `<style>` にインラインし、`<div class="slide-container std" …>` で作る。

```css
.slide-container.std { width:1280px;height:720px;border:10px solid var(--primary-color);background:white;box-sizing:border-box;position:relative;overflow:hidden;display:flex;flex-direction:column;justify-content:center;align-items:center;padding:40px;flex-shrink:0; }
body { --primary-color:#C8102E; --accent-red:#E53935; --text-dark:#212121; }
.terop-box { background:rgba(255,255,255,.9); border-left:16px solid var(--primary-color); padding:16px 32px; font-size:58px; font-weight:900; color:var(--text-dark); text-align:center; line-height:1.4; box-shadow:0 10px 20px rgba(0,0,0,.1); }
```

## 8. 文字組み・改行（必須）

- 大きな文字サイズでは長い日本語が不自然な位置で折り返す。意味の切れ目（助詞「が/を/も」の後、句読点、論理的まとまりの境界）に `<br>` を明示。各行の見た目の長さを揃える。数字と単位は切り離さない。
- 「ホッピング」のような鉤括弧の固有語は `white-space: nowrap` で割らない。
- **キャリア/サービス名は省略しない**：✅`ソフトバンク`/`楽天モバイル`/`ドコモ`。❌`SB`/`楽天`(単体)。
- 1ページは約792px幅。`.rows .tx`(38px)なら1行18文字程度で `<br>`、`.sheet`(32px)のセルも長ければ改行。

## 9. 画像アセット

- **プレースホルダ禁止**。`public/images/` から文脈に最適な既存画像を選ぶ（`GEMINI.md` に一覧）。
- 選択優先度：`temp/<carrier>/`（キャンペーンバナー等の直接的画像） > `charts/`（レーダーチャート） > `thumbnails/`（過去動画CTA） > `logo/` > `irasutoya/`（状況イラスト） > `common/`（概念図）。
- **外部出典の明記（必須）**：第三者サイトから取得した画像には取得元を正確に併記（例 `出典：Amazon.co.jp（IIJmio商品ページ）`。Amazon が権利者ではない点に注意）。キャプションは `.note` 相当の小さめ・グレーで画像直下に。

## 10. 自己チェック（重要）

- **オーバーフロー厳禁**：各ページ（約810×772px）に全要素が収まること。はみ出すならフォント10〜20%縮小／行数削減／隣ページへ分割。本の下端より下（画面下部約20%）は字幕帯なので、ここに本文を置かない。
- **余白を残さない**：文字・アイコン・画像は大きめに。`.page-body`（既定 `space-evenly`）とフォント/行間で縦を使い切る。1ページ1〜3要素のような薄い内容でも、大きな文字・大アイコン・大ビジュアルでスカスカに見せない（目安：本文の文字は 40px 以上、見出し 56〜60px、章タイトル・CTA は 90px 以上）。詰めすぎてもいけない。
- 評価見開きの `.cards` は左右3枚ずつが基本。card 内のテキストが長い時は `.line` を短く要約。

## 11. 出力フォーマット

- 全スライドを1つのHTMLファイルに `div` で縦に並べる（`body` レイアウトは `spread-base.css` が担う）。
- 各スライドの直前に `<!-- Slide ID: XX -->` を置き、台本の行IDと対応付ける（`N-0`/`N-1`/`N-2` などのサフィックスも可）。
- 出力後、`npm run capture-slides-html` でキャプチャされ、見開きは 1920×1080、冒頭 std は 1280×720 の PNG になる。
