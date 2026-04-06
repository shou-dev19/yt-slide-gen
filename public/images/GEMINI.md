# 画像アセット管理（Image Assets Directory）

このディレクトリには、スライド生成に使用される画像アセットが格納されています。

## ディレクトリ構成と主な用途

### `public/images/logo/`
格安SIM各社およびキャリアのロゴ。
- `Ahamo_logo.svg`, `LINEMO_logo.svg`, `Povo_logo.svg`, `Rakuten_Mobile_logo.svg`, `Y!mobile.svg`, `hismobile_logo.svg`, `nuromobile_logo.png`, `iijmio_logo.png`, `aeonmobile_logo.png` など。

### `public/images/charts/`
各社の速度計測結果やプラン比較などのチャート。
- `ahamo.png`, `LINEMO.png`, `povo2.0.png`, `楽天モバイル.png` など。

### `public/images/common/`
格安SIMの仕組みや概念を説明するためのイラスト。
- `格安SIMを車の道路で例えたイラスト.png`
- `お昼休みの通信混雑をイメージした図.png`
- `通信制限のイメージ図.png`
- `複数回線持ちで通信障害対策.png`
- `スタバでドヤ顔のモモコ.png`（キャラクター：モモコ）
- `モモコとショウが焼肉を食べているイラスト.png`（キャラクター：モモコ、ショウ）

### `public/images/irasutoya/`
いらすとやの素材。感情表現や状況説明に使用。
- `animal_buta_shock.png`（ショック、驚き）
- `bikkuri_me_tobideru_man.png`（驚愕）
- `money_fueru.png`, `osatsu_money_yamadumi.png`（節約、お得）
- `seikyuusyo_shock.png`（高い請求書にショック）
- `smartphone_speed_5g.png`, `yajirushi_fast_.png`, `yajirushi_slow.png`（通信速度）
- `family_happy_banzai.png`, `pose_anshin_woman.png`（解決、安心、喜び）

### `public/images/slides/`
定型的なスライド画像。
- `評価項目について.png`
- `プランやキャンペーンは投稿時点のもの注意喚起.png`
- `今すぐ本編動画をチェック.png`

## 画像選択のガイドライン

1. **ロゴ**: 特定のサービスについて話している場合は、必ずそのサービスのロゴ（`logo/`）を表示してください。
2. **概念説明**: 「格安SIMとは」「通信制限」などの概念を説明する際は、`common/` 内のイラストを優先して使用してください。
3. **感情・状況**: 台本のセリフが「高い！」「びっくり！」などの感情的な場合は、`irasutoya/` から適切な画像を選んでください。
4. **比較**: 速度や料金の比較を行う場合は、`charts/` や `common/全プラン比較表.png` を使用してください。
