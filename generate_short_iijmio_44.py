#!/usr/bin/env python3
"""Generate the IIJmio #44 short deck from the master scenario CSV.

The CSV remains the source of truth: slide IDs and every on-screen phrase are
read from its `スライドに表示する内容` column.  Run this file again after a
scenario edit; do not hand-edit the generated HTML.
"""

from __future__ import annotations

import csv
import html
import re
from collections import OrderedDict
from pathlib import Path


WORKDIR = Path("/workspaces/yt-factory/packages/slide-gen")
SCENARIO_CSV = Path(
    "/workspaces/yt-factory/packages/scenario-gen/archive/videos/"
    "44_【11月4日まで】IIJmioのデータeSIMが最大3ヵ月0円！au回線で2枚目の副回線を持つ方法/"
    "short/【11月4日まで】IIJmio、au回線データeSIMが3ヶ月0円.csv"
)
OUTPUT_HTML = WORKDIR / "slides-short.html"

LOGO = "public/images/logo/iijmio_logo.png"
MULTI_LINE = "public/images/common/複数回線持ちで通信障害対策.png"
TWO_PHONES = "public/images/irasutoya/smartphone_nidaimochi_man.png"
FAST_PHONE = "public/images/irasutoya/smartphone_speed_5g.png"
MONEY = "public/images/irasutoya/money_fueru.png"
CTA_THUMBNAIL = (
    "public/images/thumbnails/44_【〜11／4】IIJmioのデータeSIMが最大3ヵ月0円！"
    "au回線で2枚目の副回線を持つ方法_サムネ1.png"
)


def read_slides() -> OrderedDict[str, str]:
    """Return first-seen display copy per slide ID, preserving CSV order."""
    slides: OrderedDict[str, str] = OrderedDict()
    with SCENARIO_CSV.open(encoding="utf-8", newline="") as source:
        for row in csv.DictReader(source):
            slide_id = row["スライドID"].strip()
            display = row["スライドに表示する内容"].strip()
            if slide_id and display and slide_id not in slides:
                slides[slide_id] = display
    return slides


def clean_display_copy(value: str) -> list[str]:
    """Split the authored telop into display phrases without using dialogue."""
    value = re.sub(r"^テロップ：", "", value)
    return [part.strip() for part in value.split("／") if part.strip()]


def get_phrase(parts: list[str], pattern: str, fallback: str) -> str:
    return next((part for part in parts if re.search(pattern, part)), fallback)


def card(icon: str, text: str, alert: bool = False) -> str:
    class_name = "info-card alert" if alert else "info-card"
    return f'<div class="{class_name}"><span class="card-icon">{icon}</span>{html.escape(text)}</div>'


def slide_1(slide_id: str, copy: str) -> str:
    parts = clean_display_copy(copy)
    service = get_phrase(parts, r"IIJmio", "IIJmioのデータ専用eSIM")
    second_line = get_phrase(parts, r"au回線", "au回線で2枚目の副回線に")
    offer = get_phrase(parts, r"0円", "月額最大3ヶ月間0円")
    return f'''    <!-- Slide ID: {slide_id} | CSV表示内容: {html.escape(copy)} -->
    <div class="slide-container slide-thumbnail price-note" data-slide-id="{slide_id}">
      <div class="thumb-top-strip">⚡ 11月4日までの期間限定 ⚡</div>
      <i class="thumb-accent-tri tl"></i><i class="thumb-accent-tri br"></i>
      <div class="thumb-content">
        <div class="thumb-tag">最大3ヶ月 0円！</div>
        <h1 class="thumb-title">{html.escape(service)}<br /><span>{html.escape(offer)}</span></h1>
        <div class="thumb-sub-band">{html.escape(second_line)}</div>
      </div>
      <div class="thumb-logo-card"><img src="{LOGO}" alt="IIJmio ロゴ" /></div>
      <div class="slide-illust thumb-illust" style="z-index: 2;"><img src="{MULTI_LINE}" alt="複数回線で通信障害に備える" /></div>
    </div>'''


def slide_2(slide_id: str, copy: str) -> str:
    parts = clean_display_copy(copy)
    question = get_phrase(parts, r"あなたは", "あなたはどっち？")
    use_often = get_phrase(parts, r"毎月", "① 毎月ちょっとずつ使う派")
    insurance = get_phrase(parts, r"保険", "② たまにしか使わない保険派")
    return f'''    <!-- Slide ID: {slide_id} | CSV表示内容: {html.escape(copy)} -->
    <div class="slide-container choice-slide" data-slide-id="{slide_id}">
      <div class="watermark">{slide_id}</div>
      <h2 class="slide-title">{html.escape(question)}</h2>
      <div class="slide-body" style="margin-bottom: 120px;">
        <div class="choice-lead">2枚目の副回線、選び方はここ！</div>
        <div class="type-card use-often"><b>{html.escape(use_often)}</b><small>キャンペーンを活かせる</small></div>
        <div class="vs-badge">or</div>
        <div class="type-card insurance"><b>{html.escape(insurance)}</b><small>必要な時だけ使いたい</small></div>
      </div>
      <div class="slide-illust" style="z-index: 2;"><img src="{TWO_PHONES}" alt="スマートフォンを2台持つ人" /></div>
    </div>'''


def slide_3(slide_id: str, copy: str) -> str:
    parts = clean_display_copy(copy)
    campaign = get_phrase(parts, r"2ギガ", "9月1日〜11月4日の新規申込で2ギガが最大3ヶ月間0円")
    date_match = re.search(r"(9月1日〜11月4日)", campaign)
    plan_match = re.search(r"(2ギガが最大3ヶ月間0円)", campaign)
    date = date_match.group(1) if date_match else "9月1日〜11月4日"
    plan = plan_match.group(1) if plan_match else "2ギガが最大3ヶ月間0円"
    au = get_phrase(parts, r"au回線", "au回線が新規追加")
    return f'''    <!-- Slide ID: {slide_id} | CSV表示内容: {html.escape(copy)} -->
    <div class="slide-container campaign-slide price-note" data-slide-id="{slide_id}">
      <div class="watermark">{slide_id}</div>
      <h2 class="slide-title">毎月使う派は<br /><span>今がチャンス！</span></h2>
      <div class="slide-body" style="margin-bottom: 120px;">
        <div class="logo-answer"><img src="{LOGO}" alt="IIJmio ロゴ" /><strong>データ専用eSIM</strong></div>
        <div class="date-badge">{html.escape(date)} の新規申込</div>
        {card("0", plan, True)}
        {card("au", au)}
        <div class="blue-callout">eSIMなら最短で申込当日から使える</div>
      </div>
      <div class="slide-illust" style="z-index: 2;"><img src="{FAST_PHONE}" alt="高速通信をするスマートフォン" /></div>
    </div>'''


def slide_4(slide_id: str, copy: str) -> str:
    parts = clean_display_copy(copy)
    price = "1,650円" if re.search(r"1,650円", copy) else "初期費用 1,650円"
    usual = "通常3,300円 → 半額" if re.search(r"通常3,300円", copy) else "通常3,300円 → 半額"
    return f'''    <!-- Slide ID: {slide_id} | CSV表示内容: {html.escape(copy)} -->
    <div class="slide-container setup-slide price-note" data-slide-id="{slide_id}">
      <div class="watermark">{slide_id}</div>
      <h2 class="slide-title">始めるなら今！<br /><span>初期費用も半額</span></h2>
      <div class="slide-body" style="margin-bottom: 130px;">
        <div class="price-hero"><img src="{LOGO}" alt="IIJmio ロゴ" /><div><span>今だけの初期費用</span><strong>{html.escape(price)}</strong><small>{html.escape(usual)}</small></div></div>
        <div class="saving-strip">✨ 0円キャンペーンと合わせて始めやすい</div>
      </div>
      <div class="slide-illust" style="z-index: 2;"><img src="{MONEY}" alt="お金が増えるイメージ" /></div>
    </div>'''


def slide_5(slide_id: str, copy: str) -> str:
    return f'''    <!-- Slide ID: {slide_id} | CSV表示内容: {html.escape(copy)} -->
    <div class="slide-container cta-slide" data-slide-id="{slide_id}">
      <div class="cta-content">
        <div class="cta-logo-card"><img src="{LOGO}" alt="IIJmio ロゴ" /></div>
        <h2 class="cta-title">保険派に向いてる<br />回線は？</h2>
        <div class="cta-sub"><span>答えは本編でくわしく解説！</span><span>あなたに合う2枚目を見つけよう</span></div>
        <img class="cta-banner-img" src="{CTA_THUMBNAIL}" alt="本編動画のサムネイル" />
        <div class="cta-arrow">▼ 本編はこちら ▼</div>
      </div>
    </div>'''


STYLE = r'''    <style>
      :root { --blue:#0052cc; --blue-deep:#003380; --blue-soft:#eaf3ff; --red:#e63946; --red-deep:#b0001e; --red-soft:#fff0f0; --yellow:#ffd700; --ink:#172b4d; --muted:#5b6780; }
      * { box-sizing:border-box; margin:0; padding:0; }
      body { display:flex; flex-direction:column; align-items:center; gap:40px; margin:0; padding:40px; background:#f0f4f8; color:var(--ink); font-family:"Inter","Noto Sans JP",sans-serif; font-weight:700; }
      .slide-container { position:relative; isolation:isolate; overflow:hidden; width:1080px; height:1080px; flex-shrink:0; padding:58px 70px; background:#fff; }
      .slide-container.price-note::after { content:"※表示している料金はすべて月額・税込みの価格です"; position:absolute; right:20px; bottom:16px; z-index:9999; background:rgba(0,0,0,.62); color:#fff; font-family:"Noto Sans JP",sans-serif; font-size:26px; font-weight:700; letter-spacing:.02em; line-height:1; padding:10px 20px; border-radius:10px; white-space:nowrap; pointer-events:none; }
      img { object-fit:contain; filter:drop-shadow(0 10px 20px rgba(0,0,0,.12)); }
      .watermark { position:absolute; top:-74px; left:20px; z-index:-1; color:var(--blue); font:900 280px/1 "Inter",sans-serif; opacity:.07; }
      .slide-title { position:relative; z-index:1; margin:0 0 30px; padding:0 0 20px; border-bottom:10px solid var(--blue); font-size:62px; font-weight:900; line-height:1.15; letter-spacing:-.045em; }
      .slide-title span { color:var(--red); }
      .slide-body { position:relative; z-index:1; display:flex; flex-direction:column; gap:24px; }
      .slide-illust { position:absolute; right:34px; bottom:30px; height:250px; pointer-events:none; }
      .slide-illust img { height:100%; max-width:330px; }
      .slide-thumbnail { display:flex; flex-direction:column; align-items:center; justify-content:flex-start; padding:154px 48px 300px; border:25px solid var(--blue); background:repeating-conic-gradient(from 0deg at 52% 48%,rgba(0,82,204,.06) 0deg 2.5deg,transparent 2.5deg 16deg),radial-gradient(ellipse at 52% 48%,#fff 5%,#e8f3ff 45%,#c8dcff 100%); text-align:center; }
      .thumb-top-strip { position:absolute; top:25px; left:25px; right:25px; z-index:3; padding:18px 0; background:var(--blue); color:#fff; font-size:36px; font-weight:900; letter-spacing:.06em; }
      .thumb-accent-tri { position:absolute; width:0; height:0; } .thumb-accent-tri.tl { top:25px; left:25px; border-top:300px solid rgba(0,82,204,.09); border-right:300px solid transparent; } .thumb-accent-tri.br { right:25px; bottom:25px; border-bottom:300px solid rgba(0,82,204,.09); border-left:300px solid transparent; }
      .thumb-content { position:relative; z-index:2; } .thumb-tag { display:inline-block; margin-bottom:22px; padding:18px 50px; transform:rotate(-3deg); background:var(--red); box-shadow:8px 8px 0 rgba(0,0,0,.25); color:#fff; font-size:70px; font-weight:900; }
      .thumb-title { max-width:900px; margin:0 auto 24px; color:#17213d; font-size:72px; font-weight:900; line-height:1.18; letter-spacing:-.055em; } .thumb-title span { color:var(--red); }
      .thumb-sub-band { display:inline-block; padding:17px 35px; border-radius:14px; background:var(--blue); box-shadow:4px 4px 0 rgba(0,0,0,.2); color:#fff; font-size:46px; font-weight:900; }
      .thumb-logo-card { position:absolute; z-index:2; left:45px; bottom:82px; display:grid; place-items:center; width:345px; height:126px; padding:14px; border:5px solid var(--blue); border-radius:20px; background:#fff; box-shadow:6px 7px 0 rgba(0,82,204,.18); } .thumb-logo-card img { max-width:285px; max-height:86px; }
      .thumb-illust { right:24px; bottom:16px; height:278px; } .thumb-illust img { max-width:350px; }
      .choice-lead,.blue-callout,.saving-strip { padding:21px 26px; border-radius:16px; background:var(--ink); color:#fff; font-size:40px; font-weight:900; text-align:center; }
      .type-card { min-height:150px; padding:23px 30px; border:7px solid #c4d8f7; border-radius:22px; background:#f6faff; } .type-card b { display:block; margin-bottom:10px; font-size:48px; } .type-card small { color:var(--muted); font-size:31px; font-weight:900; }
      .type-card.use-often { border-color:var(--blue); background:var(--blue-soft); color:var(--blue-deep); } .type-card.insurance { border-color:var(--red); background:var(--red-soft); color:var(--red-deep); } .vs-badge { align-self:center; width:72px; height:52px; border-radius:28px; background:var(--yellow); font-size:29px; font-weight:900; line-height:52px; text-align:center; }
      .logo-answer { display:flex; align-items:center; justify-content:space-between; gap:20px; min-height:146px; padding:20px 30px; border:7px solid var(--blue); border-radius:24px; background:#fff; } .logo-answer img { width:300px; max-height:105px; } .logo-answer strong { padding:12px 18px; border-radius:14px; background:var(--blue); color:#fff; font-size:31px; }
      .date-badge { align-self:center; padding:10px 28px; border-radius:999px; background:var(--yellow); color:var(--ink); font-size:38px; font-weight:900; }
      .info-card { display:flex; align-items:center; gap:20px; min-height:116px; padding:18px 27px; border-left:14px solid var(--blue); border-radius:0 16px 16px 0; background:#f0f5ff; font-size:42px; font-weight:900; line-height:1.16; } .info-card.alert { border-left-color:var(--red); background:var(--red-soft); color:var(--red-deep); font-size:49px; } .card-icon { display:grid; place-items:center; min-width:66px; height:66px; border-radius:18px; background:var(--red); color:#fff; font-size:30px; font-weight:900; }
      .blue-callout { background:var(--blue); font-size:37px; }
      .price-hero { display:grid; grid-template-columns:300px 1fr; align-items:center; min-height:282px; padding:27px 30px; border:7px solid var(--red); border-radius:26px; background:linear-gradient(145deg,#fff7f7,#ffe3e6); } .price-hero img { width:260px; max-height:122px; } .price-hero div { text-align:center; } .price-hero span { display:block; margin-bottom:8px; font-size:34px; font-weight:900; } .price-hero strong { display:block; color:var(--red); font-size:75px; font-weight:900; line-height:1.1; letter-spacing:-.06em; } .price-hero small { font-size:30px; font-weight:900; }
      .saving-strip { background:var(--blue); font-size:42px; }
      .cta-slide { padding:20px 60px 14px; background:linear-gradient(135deg,var(--blue),var(--blue-deep)); } .cta-content { display:flex; flex-direction:column; align-items:center; height:100%; text-align:center; } .cta-logo-card { display:grid; place-items:center; height:126px; margin-bottom:5px; padding:8px 16px; border-radius:18px; background:#fff; box-shadow:4px 4px 0 rgba(0,0,0,.18); } .cta-logo-card img { height:110px; max-width:340px; filter:none; } .cta-title { margin:0 0 7px; color:var(--yellow); font-size:63px; font-weight:900; line-height:1.08; } .cta-sub { display:flex; flex-direction:column; gap:5px; width:920px; margin-bottom:9px; color:#fff; font-size:29px; font-weight:900; } .cta-sub span { padding:5px 14px; border:3px solid rgba(255,255,255,.55); border-radius:12px; background:rgba(255,255,255,.1); white-space:nowrap; } .cta-banner-img { width:850px; max-height:430px; border:7px solid #fff; border-radius:18px; box-shadow:0 18px 42px rgba(0,0,0,.4); object-fit:contain; filter:none; } .cta-arrow { margin-top:7px; color:var(--yellow); font-size:62px; font-weight:900; line-height:1.05; animation:bounce 1s infinite; } @keyframes bounce { 0%,100% { transform:translateY(0); } 50% { transform:translateY(8px); } }
    </style>'''


def render(slides: OrderedDict[str, str]) -> str:
    expected_ids = ["1", "2", "3", "4", "5"]
    if list(slides) != expected_ids:
        raise ValueError(f"Expected short slide IDs {expected_ids}; found {list(slides)}")
    builders = [slide_1, slide_2, slide_3, slide_4, slide_5]
    pages = "\n".join(builder(slide_id, slides[slide_id]) for slide_id, builder in zip(slides, builders))
    return f'''<!doctype html>
<html lang="ja">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>IIJmio データeSIM 最大3ヶ月0円 - Shorts Slides</title>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@700;900&family=Noto+Sans+JP:wght@700;900&display=swap" rel="stylesheet" />
{STYLE}
  </head>
  <body>
{pages}
  </body>
</html>
'''


def main() -> None:
    slides = read_slides()
    OUTPUT_HTML.write_text(render(slides), encoding="utf-8")
    print(f"Generated {len(slides)} slides: {OUTPUT_HTML}")


if __name__ == "__main__":
    main()
