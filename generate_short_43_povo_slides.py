#!/usr/bin/env python3
"""Generate the short deck for video 43 directly from its scenario CSV.

The CSV remains the source of truth: every unique slide ID produces one
``.slide-container`` and its ``スライドに表示する内容`` is preserved as a
traceable HTML comment beside the generated CSS component.
"""

from __future__ import annotations

import csv
import html
from collections import OrderedDict
from pathlib import Path


PROJECT = Path("/workspaces/yt-factory/packages/slide-gen")
SCENARIO = Path(
    "/workspaces/yt-factory/packages/scenario-gen/archive/videos/"
    "43_【2026年10月】楽天モバイル、繋がらないエリアが拡大？乗り換えずに備える2枚持ちという技/"
    "short/楽天モバイル2枚持ちの正解は、月額0円のpovo2.0.csv"
)
OUTPUT = PROJECT / "slides-short.html"
CTA_THUMBNAIL = (
    "public/images/thumbnails/"
    "43_【2026年10月】楽天モバイル、繋がらないエリアが拡大？"
    "乗り換えずに備える2枚持ちという技_サムネ1.png"
)


def read_slides() -> OrderedDict[str, list[str]]:
    """Group the display-content column by slide ID without changing the CSV."""
    grouped: OrderedDict[str, list[str]] = OrderedDict()
    with SCENARIO.open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            slide_id = row["スライドID"].strip()
            if not slide_id or slide_id.endswith("-0"):
                continue
            grouped.setdefault(slide_id, []).append(row["スライドに表示する内容"].strip())

    expected = [str(number) for number in range(1, 7)]
    if list(grouped) != expected:
        raise ValueError(f"Unexpected slide IDs: {list(grouped)} (expected {expected})")
    return grouped


def source_comment(slide_id: str, contents: list[str]) -> str:
    joined = " ／ ".join(contents)
    return f"<!-- スライドID: {slide_id} | CSV表示内容: {html.escape(joined)} -->"


def render_slide(slide_id: str) -> str:
    """Return the CSS component composition appropriate to each CSV slide."""
    slides: dict[str, str] = {
        "1": """
<div class="slide-container slide-thumbnail" data-slide-id="1">
  <div class="thumb-top-strip">⚡ 楽天モバイルの圏外対策 ⚡</div>
  <i class="thumb-accent-tri tl"></i><i class="thumb-accent-tri br"></i>
  <div class="thumb-content">
    <div class="thumb-tag">乗り換え不要！</div>
    <h1 class="thumb-title">繋がらない不安は<br><span>「2枚持ち」で備える</span></h1>
    <div class="thumb-sub-band">楽天モバイル × povo2.0</div>
  </div>
  <div class="thumb-sticker"><span>auローミング終了の穴を</span><br><span>カバー</span></div>
  <div class="slide-illust thumb-illust"><img src="public/images/common/複数回線持ちで通信障害対策.png" alt="複数回線で通信障害に備える"></div>
</div>""",
        "2": """
<div class="slide-container choice-slide" data-slide-id="2">
  <div class="watermark">2</div>
  <h2 class="slide-title">あなたは<span>どのタイプ？</span></h2>
  <div class="slide-body" style="margin-bottom: 120px;">
    <div class="choice-lead">「2枚目」は優先したいことから選ぶ</div>
    <div class="type-grid">
      <div class="type-card selected"><b>① 通信品質</b><small>とにかく繋がること</small></div>
      <div class="type-card"><b>② 安さ重視</b><small>月額を抑えたい</small></div>
      <div class="type-card"><b>③ 回線を選ぶ</b><small>好きな回線を持ちたい</small></div>
    </div>
  </div>
  <div class="slide-illust"><img src="public/images/irasutoya/smartphone_nidaimochi_man.png" alt="スマートフォンを2台持つ人"></div>
</div>""",
        "3": """
<div class="slide-container povo-answer-slide" data-slide-id="3">
  <div class="watermark">3</div>
  <h2 class="slide-title">通信品質重視なら<br><span>povo2.0</span></h2>
  <div class="slide-body" style="margin-bottom: 120px;">
    <div class="logo-answer"><img src="public/images/logo/Povo_logo.png" alt="povo2.0 ロゴ"><strong>迷わずコレ</strong></div>
    <div class="info-card alert"><span class="card-icon">✓</span>au回線の通信品質を<br>そのまま使える</div>
    <div class="blue-callout">楽天モバイルの“保険回線”に</div>
  </div>
  <div class="slide-illust"><img src="public/images/irasutoya/smartphone_speed_5g.png" alt="高速通信をするスマートフォン"></div>
</div>""",
        "4": """
<div class="slide-container mechanism-slide" data-slide-id="4">
  <div class="watermark">4</div>
  <h2 class="slide-title">終了するのは<br><span>楽天の借り回線</span></h2>
  <div class="slide-body" style="margin-bottom: 120px;">
    <div class="mechanism-flow">
      <div class="mechanism-card stop"><b>楽天モバイル</b><span>au回線を借りる仕組み</span><em>終了</em></div>
      <div class="flow-arrow">↓</div>
      <div class="mechanism-card solution"><b>自分で povo2.0 を1枚</b><span>au回線を直接持つ</span><em>穴を補える！</em></div>
    </div>
  </div>
  <div class="slide-illust mechanism-illust" style="z-index:2;"><img src="public/images/common/複数回線を組み合わせるイメージ図.png" alt="複数回線を組み合わせるイメージ"></div>
</div>""",
        "5": """
<div class="slide-container price-note price-slide" data-slide-id="5">
  <div class="watermark">5</div>
  <h2 class="slide-title">povo2.0の維持費は？</h2>
  <div class="slide-body" style="margin-bottom: 118px;">
    <div class="price-hero"><img src="public/images/logo/Povo_logo.png" alt="povo2.0 ロゴ"><div><span>ベースプラン</span><strong>月額 0円</strong><small>（税込）</small></div></div>
    <div class="topping-flow"><div>ふだんは<br><b>0円</b></div><span>＋</span><div>必要な時だけ<br><b>データを追加</b></div></div>
    <div class="insurance-strip">通信の“保険”として持てる</div>
  </div>
  <div class="slide-illust" style="z-index:2; bottom:88px;"><img src="public/images/irasutoya/pose_anshin_woman.png" alt="安心する女性"></div>
</div>""",
        "6": f"""
<div class="slide-container cta-slide" data-slide-id="6">
  <div class="cta-content">
    <div class="cta-logo-card"><img src="public/images/logo/Povo_logo.png" alt="povo2.0 ロゴ"></div>
    <h2 class="cta-title">本編で<br>残り2タイプも解説！</h2>
    <div class="cta-sub"><span>安さ重視派・回線を選びたい派も</span><span>あなたに合う2枚目をチェック</span></div>
    <img class="cta-banner-img" src="{CTA_THUMBNAIL}" alt="本編動画のサムネイル">
    <div class="cta-arrow">▼ 本編はこちら ▼</div>
  </div>
</div>""",
    }
    return slides[slide_id].strip()


CSS = r"""
:root { --blue:#0052cc; --blue-deep:#003380; --blue-soft:#eaf3ff; --red:#e63946; --red-deep:#b0001e; --red-soft:#fff0f0; --yellow:#ffd700; --ink:#172b4d; --muted:#5b6780; }
* { box-sizing:border-box; margin:0; padding:0; }
body { display:flex; flex-direction:column; align-items:center; gap:40px; margin:0; padding:40px; background:#f0f4f8; font-family:'Inter','Noto Sans JP',sans-serif; font-weight:700; }
.slide-container { position:relative; isolation:isolate; overflow:hidden; display:block; width:1080px; height:1080px; flex-shrink:0; padding:58px 70px; background:#fff; color:var(--ink); }
.slide-container.price-note::after {
    content: "※表示している料金はすべて月額・税込みの価格です";
    position: absolute; right: 20px; bottom: 16px; z-index: 9999;
    background: rgba(0,0,0,0.62); color: #fff;
    font-family: 'Noto Sans JP', sans-serif;
    font-size: 26px; font-weight: 700; letter-spacing: 0.02em; line-height: 1;
    padding: 10px 20px; border-radius: 10px; white-space: nowrap; pointer-events: none;
}
img { object-fit:contain; filter:drop-shadow(0 10px 20px rgba(0,0,0,.12)); }
.watermark { position:absolute; top:-74px; left:20px; z-index:-1; color:var(--blue); font:900 280px/1 'Inter',sans-serif; opacity:.07; }
.slide-title { position:relative; z-index:1; margin:0 0 30px; padding:0 0 20px; border-bottom:10px solid var(--blue); color:var(--ink); font-size:62px; font-weight:900; line-height:1.15; letter-spacing:-.045em; }
.slide-title span { color:var(--red); }
.slide-body { position:relative; z-index:1; display:flex; flex-direction:column; gap:26px; }
.slide-illust { position:absolute; right:34px; bottom:30px; z-index:2; height:250px; pointer-events:none; }
.slide-illust img { height:100%; max-width:330px; }
/* Thumbnail */
.slide-thumbnail { display:flex; flex-direction:column; align-items:center; justify-content:flex-start; padding:154px 48px 300px; border:25px solid var(--blue); background:repeating-conic-gradient(from 0deg at 52% 48%,rgba(0,82,204,.06) 0deg 2.5deg,transparent 2.5deg 16deg),radial-gradient(ellipse at 52% 48%,#fff 5%,#e8f3ff 45%,#c8dcff 100%); text-align:center; }
.thumb-top-strip { position:absolute; top:25px; left:25px; right:25px; z-index:3; padding:18px 0; background:var(--blue); color:#fff; font-size:36px; font-weight:900; letter-spacing:.06em; text-align:center; }
.thumb-accent-tri { position:absolute; width:0; height:0; }.thumb-accent-tri.tl { top:25px; left:25px; border-top:300px solid rgba(0,82,204,.09); border-right:300px solid transparent; }.thumb-accent-tri.br { right:25px; bottom:25px; border-bottom:300px solid rgba(0,82,204,.09); border-left:300px solid transparent; }
.thumb-content { position:relative; z-index:2; }.thumb-tag { display:inline-block; margin-bottom:24px; padding:18px 54px; transform:rotate(-3deg); background:var(--red); box-shadow:8px 8px 0 rgba(0,0,0,.25); color:#fff; font-size:72px; font-weight:900; }.thumb-title { max-width:920px; margin:0 auto 22px; color:#17213d; font-size:78px; font-weight:900; line-height:1.2; letter-spacing:-.055em; }.thumb-title span { color:var(--red); }.thumb-sub-band { display:inline-block; padding:16px 46px; border-radius:14px; background:var(--blue); box-shadow:4px 4px 0 rgba(0,0,0,.2); color:#fff; font-size:52px; font-weight:900; }.thumb-sticker { position:absolute; z-index:2; left:42px; bottom:78px; width:500px; padding:16px 22px; border:5px solid var(--blue); border-radius:20px; background:#fff; box-shadow:6px 7px 0 rgba(0,82,204,.18); font-size:32px; font-weight:900; line-height:1.2; text-align:center; word-break:keep-all; overflow-wrap:normal; }.thumb-sticker span { white-space:nowrap; }.thumb-illust { right:24px; bottom:16px; height:292px; }.thumb-illust img { max-width:380px; }
/* Type selection */
.choice-lead { padding:25px 30px; border-radius:20px; background:var(--ink); color:#fff; font-size:42px; font-weight:900; text-align:center; }.type-grid { display:grid; grid-template-columns:1fr 1fr; gap:20px; }.type-card { min-height:176px; padding:27px 30px; border:6px solid #c4d8f7; border-radius:22px; background:#f6faff; color:var(--muted); }.type-card b { display:block; margin-bottom:12px; color:var(--blue); font-size:48px; }.type-card small { font-size:31px; font-weight:900; }.type-card.selected { grid-column:span 2; border-color:var(--red); background:var(--red-soft); box-shadow:0 14px 30px rgba(230,57,70,.15); }.type-card.selected b { color:var(--red-deep); font-size:58px; }.type-card.selected small { color:var(--red); font-size:38px; }
/* povo answer */
.logo-answer { display:flex; align-items:center; justify-content:space-between; gap:28px; min-height:170px; padding:22px 34px; border:7px solid var(--blue); border-radius:24px; background:#fff; }.logo-answer img { width:350px; max-height:115px; }.logo-answer strong { padding:13px 20px; border-radius:14px; background:var(--red); color:#fff; font-size:36px; }.info-card { display:flex; align-items:center; gap:22px; min-height:148px; padding:22px 30px; border-left:14px solid var(--blue); border-radius:0 16px 16px 0; background:#f0f5ff; font-size:47px; font-weight:900; line-height:1.18; }.info-card.alert { border-left-color:var(--red); background:var(--red-soft); color:var(--red-deep); }.card-icon { display:grid; place-items:center; min-width:70px; height:70px; border-radius:18px; background:var(--red); color:#fff; font-size:42px; }.blue-callout { padding:20px 26px; border-radius:16px; background:var(--blue); color:#fff; font-size:43px; font-weight:900; text-align:center; }
/* Mechanism: reserve a dedicated right-bottom visual zone so the explanatory
   cards never extend beneath the illustration. */
.mechanism-slide .slide-body { width:590px; }.mechanism-flow { display:flex; flex-direction:column; gap:10px; }.mechanism-card { display:flex; flex-direction:column; gap:7px; min-height:170px; padding:20px 24px; border-radius:22px; text-align:center; }.mechanism-card b { font-size:41px; }.mechanism-card span { font-size:30px; }.mechanism-card em { align-self:center; padding:6px 18px; border-radius:999px; font-size:30px; font-style:normal; font-weight:900; }.mechanism-card.stop { border:7px solid var(--red); background:var(--red-soft); color:var(--red-deep); }.mechanism-card.stop em { background:var(--red); color:#fff; }.mechanism-flow .flow-arrow { color:var(--red); font-size:56px; font-weight:900; line-height:1; text-align:center; }.mechanism-card.solution { border:7px solid var(--blue); background:var(--blue-soft); color:var(--blue-deep); }.mechanism-card.solution em { background:var(--blue); color:#fff; }.mechanism-illust { right:34px; bottom:30px; height:230px; }.mechanism-illust img { max-width:380px; }
/* Price */
.price-hero { display:grid; grid-template-columns:320px 1fr; align-items:center; min-height:270px; padding:28px 34px; border:7px solid var(--red); border-radius:26px; background:linear-gradient(145deg,#fff7f7,#ffe3e6); }.price-hero img { width:280px; max-height:130px; }.price-hero div { text-align:center; }.price-hero span { display:block; margin-bottom:8px; color:var(--ink); font-size:35px; font-weight:900; }.price-hero strong { display:block; color:var(--red); font-size:88px; font-weight:900; line-height:1.12; letter-spacing:-.06em; }.price-hero small { color:var(--ink); font-size:34px; font-weight:900; }.topping-flow { display:grid; grid-template-columns:1fr 72px 1fr; align-items:center; gap:16px; }.topping-flow div { min-height:135px; padding:20px; border-radius:18px; background:var(--blue-soft); color:var(--blue); font-size:34px; font-weight:900; line-height:1.18; text-align:center; }.topping-flow b { font-size:44px; }.topping-flow span { color:var(--red); font-size:66px; font-weight:900; text-align:center; }.insurance-strip { padding:20px; border-radius:16px; background:var(--ink); color:#fff; font-size:40px; font-weight:900; text-align:center; }.price-note .slide-illust { height:210px; }
/* CTA */
.cta-slide { padding:20px 60px 14px; background:linear-gradient(135deg,var(--blue),var(--blue-deep)); }.cta-content { display:flex; flex-direction:column; align-items:center; height:100%; text-align:center; }.cta-logo-card { display:grid; place-items:center; height:126px; margin-bottom:5px; padding:8px 16px; border-radius:18px; background:#fff; box-shadow:4px 4px 0 rgba(0,0,0,.18); }.cta-logo-card img { height:110px; max-width:340px; filter:none; }.cta-title { margin:0 0 7px; color:var(--yellow); font-size:67px; font-weight:900; line-height:1.1; }.cta-sub { display:flex; flex-direction:column; gap:5px; width:920px; margin-bottom:9px; color:#fff; font-size:29px; font-weight:900; }.cta-sub span { padding:5px 14px; border:3px solid rgba(255,255,255,.55); border-radius:12px; background:rgba(255,255,255,.1); white-space:nowrap; }.cta-banner-img { width:850px; max-height:440px; border:7px solid #fff; border-radius:18px; box-shadow:0 18px 42px rgba(0,0,0,.4); object-fit:contain; filter:none; }.cta-arrow { margin-top:7px; color:var(--yellow); font-size:62px; font-weight:900; line-height:1.05; animation:bounce 1s infinite; }@keyframes bounce { 0%,100% { transform:translateY(0); } 50% { transform:translateY(8px); } }
"""


def main() -> None:
    grouped = read_slides()
    sections = []
    for slide_id, contents in grouped.items():
        sections.append(f"{source_comment(slide_id, contents)}\n{render_slide(slide_id)}")
    document = f"""<!doctype html>
<html lang=\"ja\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>楽天モバイル2枚持ちの正解は、月額0円のpovo2.0 - Shorts Slides</title>
  <link rel=\"preconnect\" href=\"https://fonts.googleapis.com\">
  <link rel=\"preconnect\" href=\"https://fonts.gstatic.com\" crossorigin>
  <link href=\"https://fonts.googleapis.com/css2?family=Inter:wght@700;900&family=Noto+Sans+JP:wght@700;900&display=swap\" rel=\"stylesheet\">
  <style>{CSS}</style>
</head>
<body>
{chr(10).join(sections)}
</body>
</html>
"""
    OUTPUT.write_text(document, encoding="utf-8")
    print(f"Generated {len(grouped)} slides: {OUTPUT}")


if __name__ == "__main__":
    main()
