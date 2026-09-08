#!/usr/bin/env python3
"""Generate the HIS Mobile #45 short deck from its scenario CSV.

The CSV is the source of truth for slide IDs, visible copy, and spoken hooks.
Re-run this generator after changing the scenario; do not hand-edit
slides-short.html.
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
    "45_【9月17日開始】HISモバイル新プラン自由自在3.0！30GB1,999円は買いか/"
    "short/HISモバイルの新プラン、30GBで最安クラスに.csv"
)
OUTPUT_HTML = WORKDIR / "slides-short.html"

LOGO = "public/images/logo/hismobile_logo.png"
POVO_LOGO = "public/images/logo/Povo_logo.png"
AHAMO_LOGO = "public/images/logo/Ahamo_logo.png"
LINEMO_LOGO = "public/images/logo/LINEMO_logo.png"
SHOCK = "public/images/irasutoya/bikkuri_me_tobideru_man.png"
MONEY = "public/images/irasutoya/money_fueru.png"
CALL = "public/images/irasutoya/smartphone_talk03_man.png"
THINK = "public/images/irasutoya/pose_atama_kakaeru_woman.png"
CTA_THUMBNAIL = (
    "public/images/thumbnails/"
    "45_【9月17日開始】HISモバイル新プラン自由自在3.0！30GB1,999円は買いか_サムネ1.png"
)


def read_source() -> tuple[OrderedDict[str, str], dict[str, list[str]]]:
    """Return display instructions and all spoken lines grouped by slide ID."""
    slides: OrderedDict[str, str] = OrderedDict()
    spoken_lines: dict[str, list[str]] = {}
    with SCENARIO_CSV.open(encoding="utf-8", newline="") as source:
        for row in csv.DictReader(source):
            slide_id = row["スライドID"].strip()
            display = row["スライドに表示する内容"].strip()
            dialogue = row["セリフ"].strip()
            if slide_id and dialogue:
                spoken_lines.setdefault(slide_id, []).append(dialogue)
            if slide_id and display and display != "同上" and slide_id not in slides:
                slides[slide_id] = display
    return slides, spoken_lines


def parts(copy: str) -> list[str]:
    value = re.sub(r"^テロップ：", "", copy)
    return [item.strip() for item in value.split("／") if item.strip()]


def pick(items: list[str], pattern: str, fallback: str) -> str:
    return next((item for item in items if re.search(pattern, item)), fallback)


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def source_comment(slide_id: str, copy: str) -> str:
    return f"    <!-- Slide ID: {esc(slide_id)} | CSV表示内容: {esc(copy)} -->"


def slide_1(slide_id: str, copy: str, spoken_lines: list[str]) -> str:
    items = parts(copy)
    schedule = pick(items, r"発表|受付開始", "8月28日発表・9月17日受付開始予定")
    price_hook = next(
        (
            match
            for line in spoken_lines
            if (match := re.search(r"(30GB).*?([\d,]+円)", line))
        ),
        None,
    )
    hook = (
        f"{price_hook.group(1)}がまさかの{price_hook.group(2)}!?"
        if price_hook
        else "30GBがまさかの1,999円!?"
    )
    price_note_class = " price-note" if re.search(r"[\d,]+円", hook) else ""
    return f'''{source_comment(slide_id, copy)}
    <div class="slide-container slide-thumbnail{price_note_class}" data-slide-id="{esc(slide_id)}">
      <div class="thumb-top-strip">⚡ {esc(schedule)} ⚡</div>
      <i class="thumb-accent-tri tl"></i><i class="thumb-accent-tri br"></i>
      <div class="thumb-content">
        <div class="thumb-tag">新プラン登場！</div>
        <h1 class="thumb-title">HISモバイル<br /><span>自由自在 3.0</span></h1>
        <div class="thumb-sub-band">{esc(hook)}</div>
      </div>
      <div class="thumb-logo-card"><img src="{LOGO}" alt="HISモバイル ロゴ" /></div>
      <div class="slide-illust thumb-illust" style="z-index: 2;"><img src="{SHOCK}" alt="新プランに驚く人" /></div>
    </div>'''


def slide_2(slide_id: str, copy: str) -> str:
    item = parts(copy)[0]
    match = re.search(r"(30GB)\s*([\d,]+円)→([\d,]+円)（(\u25b2[\d,]+円の値下げ)）", item)
    if not match:
        raise ValueError(f"Slide {slide_id}: unexpected price copy: {item}")
    capacity, old_price, new_price, saving = match.groups()
    return f'''{source_comment(slide_id, copy)}
    <div class="slide-container price-note" data-slide-id="{esc(slide_id)}">
      <div class="watermark">{esc(slide_id)}</div>
      <h2 class="slide-title">{esc(capacity)}が<span>2,000円切り</span>へ</h2>
      <div class="slide-body" style="margin-bottom: 130px;">
        <div class="price-change">
          <div class="old-price"><small>従来</small><del>{esc(old_price)}</del></div>
          <div class="price-arrow">➡</div>
          <div class="new-price"><small>新料金</small><strong>{esc(new_price)}</strong></div>
        </div>
        <div class="saving-badge">{esc(saving)}</div>
        <div class="blue-callout">HISモバイルの新プランで実現</div>
      </div>
      <div class="slide-illust" style="z-index: 2;"><img src="{MONEY}" alt="値下げでお金が浮くイメージ" /></div>
    </div>'''


def parse_comparison(copy: str) -> tuple[str, list[tuple[str, str]]]:
    items = parts(copy)
    heading = items[0]
    rows: list[tuple[str, str]] = []
    for item in items[1:]:
        match = re.fullmatch(r"(.+?)\s+([\d,]+円)", item)
        if not match:
            raise ValueError(f"Unexpected comparison row: {item}")
        rows.append(match.groups())
    return heading, rows


def comparison_row(carrier: str, price: str) -> str:
    logo_map = {
        "povo2.0": POVO_LOGO,
        "ahamo・LINEMO": None,
        "HISモバイル": LOGO,
    }
    if carrier == "ahamo・LINEMO":
        logos = (
            f'<span class="dual-logos"><img src="{AHAMO_LOGO}" alt="ahamo ロゴ" />'
            f'<img src="{LINEMO_LOGO}" alt="LINEMO ロゴ" /></span>'
        )
    else:
        logo = logo_map[carrier]
        logos = f'<img class="carrier-logo" src="{logo}" alt="{esc(carrier)} ロゴ" />'
    highlight = " best" if carrier == "HISモバイル" else ""
    badge = '<span class="best-badge">最安クラス</span>' if highlight else ""
    return (
        f'<div class="comparison-row{highlight}">{logos}'
        f'<span class="carrier-name">{esc(carrier)}</span>'
        f'<strong>{esc(price)}</strong>{badge}</div>'
    )


def slide_3(slide_id: str, copy: str) -> str:
    heading, rows = parse_comparison(copy)
    return f'''{source_comment(slide_id, copy)}
    <div class="slide-container price-note" data-slide-id="{esc(slide_id)}">
      <div class="watermark">{esc(slide_id)}</div>
      <h2 class="slide-title">{esc(heading)}</h2>
      <div class="slide-body comparison-body">
        {''.join(comparison_row(carrier, price) for carrier, price in rows)}
        <div class="winner-strip">HISモバイルが<span>頭一つ抜けて安い！</span></div>
      </div>
    </div>'''


def slide_4(slide_id: str, copy: str) -> str:
    items = parts(copy)
    free_call = pick(items, r"6分かけ放題", "20GB・30GBに6分かけ放題無料")
    unit_price = pick(items, r"通話料", "通話料9円/30秒")
    return f'''{source_comment(slide_id, copy)}
    <div class="slide-container price-note" data-slide-id="{esc(slide_id)}">
      <div class="watermark">{esc(slide_id)}</div>
      <h2 class="slide-title">通話も<span>追加料金なし</span></h2>
      <div class="slide-body" style="margin-bottom: 135px;">
        <div class="call-hero">
          <span class="phone-icon">📞</span>
          <div><small>20GB・30GBなら</small><strong>{esc(free_call.replace('20GB・30GBに', ''))}</strong></div>
        </div>
        <div class="info-card alert"><span class="card-icon">円</span>{esc(unit_price)}</div>
        <div class="blue-callout">通話料も最安レベル</div>
      </div>
      <div class="slide-illust" style="z-index: 2;"><img src="{CALL}" alt="スマートフォンで通話する人" /></div>
    </div>'''


def slide_5(slide_id: str, copy: str) -> str:
    question = parts(copy)[0]
    question_match = re.fullmatch(r"(.+?を)(使う人は[？?])", question)
    question_html = (
        f"{esc(question_match.group(1))}<br />{esc(question_match.group(2))}"
        if question_match
        else esc(question)
    )
    return f'''{source_comment(slide_id, copy)}
    <div class="slide-container warning-slide" data-slide-id="{esc(slide_id)}">
      <div class="watermark">{esc(slide_id)}</div>
      <div class="warning-banner">⚠ ここは要チェック</div>
      <h2 class="warning-title">30GBが合うのは<br /><span>20〜30GB使う人</span></h2>
      <div class="warning-box">
        <div class="w-title">{question_html}</div>
        <div class="w-item">📱 20GB以下で足りる人</div>
        <div class="w-item">🚀 50GB以上使う人</div>
      </div>
      <div class="slide-illust warning-illust" style="z-index: 2;"><img src="{THINK}" alt="プラン選びに悩む人" /></div>
    </div>'''


def slide_6(slide_id: str, copy: str) -> str:
    cta = "詳しくは本編をチェック！"
    return f'''{source_comment(slide_id, copy)}
    <div class="slide-container cta-slide" data-slide-id="{esc(slide_id)}">
      <div class="cta-content">
        <div class="cta-logo-card"><img src="{LOGO}" alt="HISモバイル ロゴ" /></div>
        <h2 class="cta-title">あなたに合うSIMは？</h2>
        <div class="cta-sub">{esc(cta)}</div>
        <img class="cta-banner-img" src="{CTA_THUMBNAIL}" alt="HISモバイル新プランを解説する本編動画のサムネイル" />
        <div class="cta-arrow">▼ 本編はこちら ▼</div>
      </div>
    </div>'''


STYLE = r'''    <style>
      :root { --blue:#0052cc; --blue-deep:#003380; --blue-soft:#eaf3ff; --red:#e63946; --red-deep:#b0001e; --red-soft:#fff0f0; --yellow:#ffd700; --ink:#172b4d; --muted:#5b6780; }
      * { box-sizing:border-box; margin:0; padding:0; }
      body { display:flex; flex-direction:column; align-items:center; gap:40px; margin:0; padding:40px; background:#f0f4f8; color:var(--ink); font-family:"Inter","Noto Sans JP",sans-serif; font-weight:700; }
      .slide-container { position:relative; isolation:isolate; overflow:hidden; width:1080px; height:1080px; flex-shrink:0; padding:58px 70px; background:#fff; }
      .slide-container.price-note::after { content:"※表示している料金はすべて月額・税込みの価格です"; position:absolute; right:20px; bottom:16px; z-index:9999; background:rgba(0,0,0,.62); color:#fff; font-family:'Noto Sans JP',sans-serif; font-size:26px; font-weight:700; letter-spacing:.02em; line-height:1; padding:10px 20px; border-radius:10px; white-space:nowrap; pointer-events:none; }
      img { object-fit:contain; filter:drop-shadow(0 10px 20px rgba(0,0,0,.1)); }
      .watermark { position:absolute; top:-74px; left:20px; z-index:-1; color:var(--blue); font:900 280px/1 "Inter",sans-serif; opacity:.07; }
      .slide-title { position:relative; z-index:1; margin:0 0 30px; padding:0 0 20px; border-bottom:10px solid var(--blue); font-size:62px; font-weight:900; line-height:1.15; letter-spacing:-.045em; }
      .slide-title span { color:var(--red); }
      .slide-body { position:relative; z-index:1; display:flex; flex-direction:column; gap:28px; }
      .slide-illust { position:absolute; right:34px; bottom:30px; height:250px; pointer-events:none; }
      .price-note:not(.slide-thumbnail) .slide-illust { bottom:82px; }
      .slide-illust img { height:100%; max-width:330px; }
      .slide-thumbnail { display:flex; flex-direction:column; align-items:center; justify-content:flex-start; padding:150px 48px 300px; border:25px solid var(--blue); background:repeating-conic-gradient(from 0deg at 52% 48%,rgba(0,82,204,.06) 0deg 2.5deg,transparent 2.5deg 16deg),radial-gradient(ellipse at 52% 48%,#fff 5%,#e8f3ff 45%,#c8dcff 100%); text-align:center; }
      .thumb-top-strip { position:absolute; top:25px; left:25px; right:25px; z-index:3; padding:18px 0; background:var(--blue); color:#fff; font-size:36px; font-weight:900; letter-spacing:.04em; }
      .thumb-accent-tri { position:absolute; width:0; height:0; }
      .thumb-accent-tri.tl { top:25px; left:25px; border-top:300px solid rgba(0,82,204,.09); border-right:300px solid transparent; }
      .thumb-accent-tri.br { right:25px; bottom:25px; border-bottom:300px solid rgba(0,82,204,.09); border-left:300px solid transparent; }
      .thumb-content { position:relative; z-index:2; }
      .thumb-tag { display:inline-block; margin:20px 0 28px; padding:18px 54px; transform:rotate(-3deg); background:var(--red); box-shadow:8px 8px 0 rgba(0,0,0,.25); color:#fff; font-size:76px; font-weight:900; }
      .thumb-title { max-width:900px; margin:0 auto 22px; color:#17213d; font-size:80px; font-weight:900; line-height:1.2; letter-spacing:-.055em; }
      .thumb-title span { color:var(--red); }
      .thumb-sub-band { display:inline-block; padding:18px 42px; border-radius:12px; background:var(--blue); box-shadow:4px 4px 0 rgba(0,0,0,.2); color:#fff; font-size:42px; font-weight:900; }
      .thumb-logo-card { position:absolute; z-index:2; left:45px; bottom:82px; display:grid; place-items:center; width:390px; height:135px; padding:18px; border:5px solid var(--blue); border-radius:20px; background:#fff; box-shadow:6px 7px 0 rgba(0,82,204,.18); }
      .thumb-logo-card img { max-width:340px; max-height:88px; }
      .thumb-illust { right:24px; bottom:16px; height:278px; }
      .thumb-illust img { max-width:350px; }
      .price-change { display:grid; grid-template-columns:1fr 88px 1.15fr; align-items:center; min-height:300px; padding:30px; border:8px solid var(--red); border-radius:28px; background:linear-gradient(145deg,#fff8f8,#ffe5e8); text-align:center; }
      .price-change small { display:block; margin-bottom:15px; color:var(--muted); font-size:33px; font-weight:900; }
      .old-price del { color:#67728a; font-size:55px; font-weight:900; }
      .price-arrow { color:var(--blue); font-size:70px; }
      .new-price strong { display:block; color:var(--red); font-size:84px; font-weight:900; letter-spacing:-.065em; }
      .saving-badge { align-self:center; padding:15px 36px; border-radius:999px; background:var(--yellow); box-shadow:4px 5px 0 rgba(0,0,0,.16); color:var(--red-deep); font-size:51px; font-weight:900; }
      .blue-callout { padding:20px 24px; border-radius:16px; background:var(--blue); color:#fff; font-size:39px; font-weight:900; text-align:center; }
      .comparison-body { gap:17px; }
      .comparison-row { position:relative; display:grid; grid-template-columns:175px 1fr 250px; align-items:center; min-height:130px; padding:16px 24px; border:5px solid #c5d7f4; border-radius:20px; background:#f5f9ff; }
      .comparison-row.best { min-height:155px; border:8px solid var(--red); background:linear-gradient(145deg,#fff6f6,#ffe1e5); box-shadow:0 14px 28px rgba(230,57,70,.18); }
      .carrier-logo { width:155px; max-height:68px; filter:none; }
      .dual-logos { display:flex; flex-direction:column; align-items:center; gap:7px; }
      .dual-logos img { width:125px; max-height:42px; filter:none; }
      .carrier-name { font-size:34px; font-weight:900; }
      .comparison-row strong { justify-self:end; color:var(--blue-deep); font-size:46px; font-weight:900; }
      .comparison-row.best strong { color:var(--red); font-size:55px; white-space:nowrap; }
      .best-badge { position:absolute; top:-19px; right:18px; padding:7px 19px; border-radius:999px; background:var(--red); color:#fff; font-size:24px; font-weight:900; }
      .winner-strip { padding:15px 24px; border-radius:16px; background:var(--ink); color:#fff; font-size:37px; font-weight:900; text-align:center; }
      .winner-strip span { margin-left:12px; color:var(--yellow); }
      .call-hero { display:flex; align-items:center; gap:28px; min-height:275px; padding:30px 38px; border:8px solid var(--blue); border-radius:28px; background:linear-gradient(145deg,#f3f8ff,#deecff); }
      .phone-icon { display:grid; place-items:center; width:150px; height:150px; border-radius:50%; background:var(--blue); font-size:82px; }
      .call-hero small { display:block; margin-bottom:12px; color:var(--muted); font-size:34px; font-weight:900; }
      .call-hero strong { display:block; color:var(--red); font-size:55px; font-weight:900; line-height:1.18; }
      .info-card { display:flex; align-items:center; gap:22px; padding:22px 32px; border-left:14px solid var(--blue); border-radius:0 16px 16px 0; background:#f0f5ff; font-size:46px; font-weight:700; }
      .info-card.alert { border-left-color:var(--red); background:var(--red-soft); color:var(--red); font-size:50px; font-weight:900; }
      .card-icon { display:grid; place-items:center; min-width:72px; height:72px; border-radius:18px; background:var(--red); color:#fff; font-size:34px; font-weight:900; }
      .warning-slide { padding:0 70px 58px; background:#fff8f8; }
      .warning-banner { margin:0 -70px 30px; padding:22px 0; background:var(--red); color:#fff; font-size:62px; font-weight:900; text-align:center; }
      .warning-title { margin-bottom:28px; font-size:58px; font-weight:900; line-height:1.18; text-align:center; }
      .warning-title span { color:var(--red); }
      .warning-box { display:flex; flex-direction:column; gap:26px; padding:36px 42px 165px; border:10px solid var(--red); border-radius:24px; background:#fff0f0; }
      .w-title { color:var(--red-deep); font-size:53px; font-weight:900; line-height:1.18; text-align:center; }
      .w-item { padding:17px 22px; border-radius:16px; background:#fff; font-size:45px; font-weight:900; }
      .warning-illust { right:45px; bottom:24px; height:265px; }
      .cta-slide { padding:20px 60px 12px; background:linear-gradient(135deg,var(--blue),var(--blue-deep)); }
      .cta-content { display:flex; flex-direction:column; align-items:center; height:100%; text-align:center; }
      .cta-logo-card { display:grid; place-items:center; height:126px; margin-bottom:8px; padding:8px 16px; border-radius:18px; background:#fff; box-shadow:4px 4px 0 rgba(0,0,0,.18); }
      .cta-logo-card img { height:110px; max-width:420px; filter:none; }
      .cta-title { margin:0 0 8px; color:var(--yellow); font-size:73px; font-weight:900; line-height:1.06; }
      .cta-sub { width:920px; margin-bottom:12px; padding:8px 14px; border:3px solid rgba(255,255,255,.55); border-radius:12px; background:rgba(255,255,255,.1); color:#fff; font-size:35px; font-weight:900; }
      .cta-banner-img { width:830px; max-height:460px; border:7px solid #fff; border-radius:18px; box-shadow:0 18px 42px rgba(0,0,0,.4); object-fit:contain; filter:none; }
      .cta-arrow { margin-top:8px; color:var(--yellow); font-size:63px; font-weight:900; line-height:1.05; animation:bounce 1s infinite; }
      @keyframes bounce { 0%,100% { transform:translateY(0); } 50% { transform:translateY(8px); } }
    </style>'''


def render(
    slides: OrderedDict[str, str], spoken_lines: dict[str, list[str]]
) -> str:
    expected_ids = ["1", "2", "3", "4", "5", "6"]
    if list(slides) != expected_ids:
        raise ValueError(f"Expected short slide IDs {expected_ids}; found {list(slides)}")

    required_assets = [
        LOGO,
        POVO_LOGO,
        AHAMO_LOGO,
        LINEMO_LOGO,
        SHOCK,
        MONEY,
        CALL,
        THINK,
        CTA_THUMBNAIL,
    ]
    missing = [path for path in required_assets if not (WORKDIR / path).is_file()]
    if missing:
        raise FileNotFoundError(f"Missing assets: {missing}")

    pages = "\n".join(
        [
            slide_1("1", slides["1"], spoken_lines.get("1", [])),
            slide_2("2", slides["2"]),
            slide_3("3", slides["3"]),
            slide_4("4", slides["4"]),
            slide_5("5", slides["5"]),
            slide_6("6", slides["6"]),
        ]
    )
    return f'''<!doctype html>
<html lang="ja">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>HISモバイル 自由自在3.0 - Shorts Slides</title>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@700;900&amp;family=Noto+Sans+JP:wght@700;900&amp;display=swap" rel="stylesheet" />
{STYLE}
  </head>
  <body>
{pages}
  </body>
</html>
'''


def main() -> None:
    slides, spoken_lines = read_source()
    OUTPUT_HTML.write_text(render(slides, spoken_lines), encoding="utf-8")
    print(f"Generated {len(slides)} slides: {OUTPUT_HTML}")


if __name__ == "__main__":
    main()
