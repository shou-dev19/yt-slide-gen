#!/usr/bin/env python3
"""Generate the #46 Japanese Communication SIM / AEON Mobile short deck.

The source CSV determines the slide count and the facts to communicate.  Each
renderer turns those facts into a single, purposeful visual hierarchy; it does
not mechanically repeat the CSV's teleprompter text as an additional label.
"""

from __future__ import annotations

import argparse
import csv
import html
from collections import OrderedDict
from pathlib import Path
from textwrap import dedent


PROJECT = Path("/workspaces/yt-factory/packages/slide-gen")
DEFAULT_SCRIPT = Path(
    "/workspaces/yt-factory/packages/scenario-gen/archive/videos/"
    "46_格安SIM総合満足度No.1は日本通信SIM！サポート満足度No.1はイオンモバイル/"
    "short/日本通信SIMとイオンモバイル、あなたはどっち？.csv"
)
DEFAULT_OUTPUT = PROJECT / "slides-short.html"


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def image_src(relative: str) -> str:
    """Validate an asset with an absolute path, emit only a repo-relative src."""
    asset = PROJECT / relative
    if not asset.is_file():
        raise FileNotFoundError(f"Required slide asset is missing: {asset}")
    return relative


def read_slides(script_path: Path) -> OrderedDict[str, dict[str, list[str]]]:
    slides: OrderedDict[str, dict[str, list[str]]] = OrderedDict()
    with script_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"スライドに表示する内容", "スライドID"}
        if not required.issubset(reader.fieldnames or set()):
            raise ValueError("CSV must have スライドに表示する内容 and スライドID columns")
        for row in reader:
            slide_id = (row["スライドID"] or "").strip()
            display = (row["スライドに表示する内容"] or "").strip()
            if not slide_id:
                continue
            slide = slides.setdefault(slide_id, {"display": []})
            if display and display != "同上" and display not in slide["display"]:
                slide["display"].append(display.removeprefix("テロップ："))
    return slides


def logo(relative: str, alt: str, css_class: str = "brand-logo") -> str:
    return f'<img src="{image_src(relative)}" class="{css_class}" alt="{esc(alt)}">'


def illustration(relative: str, alt: str, height: int = 230) -> str:
    return (
        '<div class="slide-illust" style="z-index: 2;">'
        f'<img src="{image_src(relative)}" alt="{esc(alt)}" style="height: {height}px;">'
        "</div>"
    )


def render_thumbnail(slide: dict[str, list[str]]) -> str:
    return f'''<!-- Slide ID: 1 -->
<div class="slide-container slide-thumbnail">
  <div class="thumb-top-strip">⚡ 格安SIMアワード 2026上半期 ⚡</div>
  <div class="thumb-accent-tri tl"></div><div class="thumb-accent-tri br"></div>
  <div class="thumb-tag">満足度 No.1 発表！</div>
  <h1 class="thumb-title"><span class="blue-text">コスパ派</span>？<br><span class="red-text">サポート派</span>？</h1>
  <div class="thumb-sub-band">あなたはどっち？</div>
  <div class="thumb-illust"><img src="{image_src('public/images/irasutoya/animal_buta_shock.png')}" alt="驚く人" style="height: 270px;"></div>
</div>'''


def render_winners(slide: dict[str, list[str]]) -> str:
    return f'''<!-- Slide ID: 2 -->
<div class="slide-container slide-pad">
  <div class="watermark">2</div>
  <h2 class="slide-title">No.1は<span class="red-text">別々の会社</span></h2>
  <div class="slide-body winners-body">
    <div class="winner-grid">
      <div class="winner-card cost"><span class="winner-label">総合満足度 No.1</span>{logo('public/images/logo/nihon_tsushin.jpg', '日本通信SIM')}<strong>コスパ重視なら</strong><b>日本通信SIM</b></div>
      <div class="versus">VS</div>
      <div class="winner-card support"><span class="winner-label">サポート満足度 No.1</span>{logo('public/images/logo/aeonmobile_logo.png', 'イオンモバイル')}<strong>相談重視なら</strong><b>イオンモバイル</b></div>
    </div>
  </div>
</div>'''


def render_cost(slide: dict[str, list[str]]) -> str:
    return f'''<!-- Slide ID: 3 -->
<div class="slide-container slide-pad price-note">
  <div class="watermark">3</div>
  <h2 class="slide-title"><span class="blue-text">コスパ重視派</span>の答え</h2>
  <div class="slide-body" style="margin-bottom: 150px;">
    <div class="report-header-card">{logo('public/images/logo/nihon_tsushin.jpg', '日本通信SIM', 'report-logo')}<span>総合満足度<br><b>No.1</b></span></div>
    <div class="price-hero"><span>20GB</span><i>月額</i><strong>1,390円</strong></div>
    <div class="info-card"><span>💡</span>たっぷり使っても<br>この安さ！</div>
  </div>
  {illustration('public/images/irasutoya/money_fueru.png', 'お金が増えるイメージ', 210)}
</div>'''


def render_small_plan(slide: dict[str, list[str]]) -> str:
    return f'''<!-- Slide ID: 4 -->
<div class="slide-container slide-pad price-note">
  <div class="watermark">4</div>
  <h2 class="slide-title">小容量なら<span class="red-text">月額290円</span></h2>
  <div class="slide-body small-plan-body" style="margin-bottom: 150px;">
    <div class="plan-name">日本通信SIM<br><b>合理的シンプル290</b></div>
    <div class="price-hero compact"><span>1GB</span><i>月額</i><strong>290円</strong></div>
    <div class="info-card alert"><span>📱</span>サブ回線にも<br>ぴったり！</div>
  </div>
  {illustration('public/images/irasutoya/smartphone_nidaimochi_man.png', 'スマホを2台持つ人', 215)}
</div>'''


def render_calling(slide: dict[str, list[str]]) -> str:
    return f'''<!-- Slide ID: 5 -->
<div class="slide-container slide-pad">
  <div class="watermark">5</div>
  <h2 class="slide-title">通話オプションも<span class="red-text">無料付帯</span></h2>
  <div class="slide-body calling-body" style="margin-bottom: 150px;">
    <div class="condition-badge">対象：20GB以上のプラン</div>
    <div class="fee-grid calling-fee-grid">
      <div class="fee-card"><span>☎</span><b>5分かけ放題</b><strong>無料</strong></div>
      <div class="fee-or">または</div>
      <div class="fee-card"><span>🕒</span><b>月70分パック</b><strong>無料</strong></div>
    </div>
  </div>
  {illustration('public/images/irasutoya/smartphone_talk03_man.png', 'スマホで通話する人', 220)}
</div>'''


def render_warning(slide: dict[str, list[str]]) -> str:
    return f'''<!-- Slide ID: 6 -->
<div class="slide-container warning-slide">
  <div class="watermark warning-mark">!</div>
  <div class="warning-banner">契約前にここだけ注意！</div>
  <h2 class="warning-title">日本通信SIMの<br><span class="red-text">気をつけたい点</span></h2>
  <div class="warning-box">
    <div class="w-item"><span>📡</span><b>ドコモ回線専用</b></div>
    <div class="w-item"><span>🏬</span><b>実店舗のサポートなし</b></div>
  </div>
  {illustration('public/images/irasutoya/shinpai_man.png', '心配する人', 220)}
</div>'''


def render_cta(slide: dict[str, list[str]]) -> str:
    return f'''<!-- Slide ID: 7 -->
<div class="slide-container cta-slide">
  <div class="cta-content">
    <div class="cta-logos">{logo('public/images/logo/nihon_tsushin.jpg', '日本通信SIM', 'cta-logo')}{logo('public/images/logo/aeonmobile_logo.png', 'イオンモバイル', 'cta-logo')}</div>
    <div class="cta-title">サポート満足度 No.1<br>イオンモバイルの理由は？</div>
    <div class="cta-sub">選ばれた理由は本編でチェック！</div>
    <img src="{image_src('public/images/thumbnails/46_格安SIM総合満足度No.1は日本通信SIM！サポート満足度No.1はイオンモバイル_サムネ1.png')}" class="cta-banner-img" alt="本編動画のサムネイル">
    <div class="cta-arrow">▼</div>
  </div>
</div>'''


def stylesheet() -> str:
    return dedent('''
    :root { --blue:#0052cc; --blue-dark:#003380; --red:#e63946; --ink:#172033; --white:#fff; --pale:#f0f5ff; }
    * { box-sizing:border-box; margin:0; padding:0; }
    body { background:#f0f4f8; color:var(--ink); font-family:'Inter','Noto Sans JP',sans-serif; display:flex; flex-direction:column; align-items:center; gap:40px; padding:40px; }
    .slide-container { width:1080px; height:1080px; background:var(--white); position:relative; overflow:hidden; display:flex; flex-direction:column; }
    img { object-fit:contain; filter:drop-shadow(0 10px 20px rgba(0,0,0,.12)); }
    .blue-text { color:var(--blue); } .red-text { color:var(--red); }
    .slide-container.price-note::after { content:"※表示している料金はすべて月額・税込みの価格です"; position:absolute; right:20px; bottom:16px; z-index:9999; background:rgba(0,0,0,.62); color:#fff; font-family:'Noto Sans JP',sans-serif; font-size:26px; font-weight:700; letter-spacing:.02em; line-height:1; padding:10px 20px; border-radius:10px; white-space:nowrap; pointer-events:none; }

    .slide-thumbnail { align-items:center; text-align:center; border:25px solid var(--blue); padding:160px 45px 300px; background:repeating-conic-gradient(from 0deg at 52% 48%,rgba(0,82,204,.06) 0deg 2.5deg,transparent 2.5deg 16deg),radial-gradient(ellipse at 52% 48%,#fff 5%,#e8f3ff 45%,#c8dcff 100%); }
    .thumb-top-strip { position:absolute; top:25px; left:25px; right:25px; z-index:3; background:var(--blue); color:#fff; font-size:36px; font-weight:900; letter-spacing:.06em; padding:18px 0; }
    .thumb-accent-tri { position:absolute; width:0; height:0; z-index:1; } .thumb-accent-tri.tl { top:25px; left:25px; border-top:300px solid rgba(0,82,204,.09); border-right:300px solid transparent; } .thumb-accent-tri.br { bottom:25px; right:25px; border-bottom:300px solid rgba(0,82,204,.09); border-left:300px solid transparent; }
    .thumb-tag { z-index:2; color:#fff; background:var(--red); font-size:76px; font-weight:900; padding:18px 54px; transform:rotate(-3deg); box-shadow:8px 8px 0 rgba(0,0,0,.25); margin-bottom:28px; }
    .thumb-title { z-index:2; font-size:80px; font-weight:900; line-height:1.22; margin-bottom:22px; max-width:900px; } .thumb-sub-band { z-index:2; color:#fff; background:var(--blue); font-size:60px; font-weight:900; padding:18px 70px; border-radius:12px; box-shadow:4px 4px 0 rgba(0,0,0,.2); }
    .thumb-illust { position:absolute; z-index:2; right:42px; bottom:26px; } .thumb-illust img { filter:drop-shadow(0 10px 20px rgba(0,0,0,.18)); }

    .slide-pad { padding:72px 70px; } .watermark { position:absolute; top:-45px; left:10px; z-index:0; color:var(--blue); font-size:280px; font-weight:900; line-height:1; opacity:.07; }
    .slide-title { z-index:1; border-bottom:10px solid var(--blue); font-size:62px; font-weight:900; line-height:1.2; padding-bottom:14px; margin-bottom:24px; } .slide-body { z-index:1; display:flex; flex-direction:column; gap:22px; }
    .slide-illust { position:absolute; right:40px; bottom:40px; } .slide-illust img { filter:drop-shadow(0 10px 20px rgba(0,0,0,.14)); }
    .report-header-card { display:flex; align-items:center; gap:26px; min-height:150px; color:#fff; background:linear-gradient(135deg,var(--blue),#003fa0); border-radius:20px; font-size:42px; font-weight:900; padding:20px 30px; } .report-header-card b { color:#ffd700; font-size:58px; } .report-logo { width:230px; height:105px; background:#fff; border-radius:14px; padding:10px 16px; filter:none; }
    .info-card { display:flex; align-items:center; gap:20px; color:var(--ink); background:var(--pale); border-left:14px solid var(--blue); border-radius:0 16px 16px 0; font-size:46px; font-weight:700; line-height:1.25; padding:20px 28px; } .info-card > span { font-size:50px; } .info-card.alert { color:var(--red); background:#fff0f0; border-left-color:var(--red); font-size:50px; font-weight:900; }
    .price-hero { display:flex; align-items:baseline; justify-content:center; gap:16px; color:var(--blue); background:#fff; border:8px solid var(--blue); border-radius:22px; padding:14px 22px; box-shadow:8px 8px 0 #cfe1ff; } .price-hero span { font-size:70px; font-weight:900; } .price-hero i { color:var(--ink); font-size:36px; font-style:normal; font-weight:900; } .price-hero strong { color:var(--red); font-size:88px; font-weight:900; letter-spacing:-.05em; } .price-hero.compact strong { font-size:96px; }
    .plan-name { color:#fff; background:var(--blue); border-radius:18px; font-size:32px; font-weight:900; line-height:1.25; padding:16px 26px; text-align:center; } .plan-name b { color:#ffd700; font-size:42px; }

    /* Slide 2: paired winners use the lower canvas as part of the comparison, not as dead space. */
    .winners-body { gap:20px; } .winner-grid { display:grid; grid-template-columns:1fr 90px 1fr; align-items:center; gap:10px; margin-top:10px; } .winner-card { display:flex; min-height:760px; flex-direction:column; align-items:center; justify-content:center; gap:28px; border-radius:24px; padding:32px 18px; text-align:center; box-shadow:0 12px 26px rgba(0,0,0,.12); } .winner-card.cost { background:#e9f3ff; border:8px solid var(--blue); } .winner-card.support { background:#fff0f0; border:8px solid var(--red); } .winner-label { color:#fff; background:var(--blue); border-radius:999px; font-size:32px; font-weight:900; padding:12px 16px; } .support .winner-label { background:var(--red); } .brand-logo { width:300px; height:150px; background:#fff; border-radius:16px; padding:12px 18px; filter:none; } .winner-card strong { font-size:38px; } .winner-card b { color:var(--blue); font-size:50px; line-height:1.15; } .support b { color:var(--red); } .versus { color:var(--red); font-size:62px; font-style:italic; font-weight:900; text-align:center; }

    .condition-badge { align-self:center; background:#172033; color:#fff; border-radius:999px; font-size:34px; font-weight:900; padding:13px 34px; } .fee-grid { display:grid; grid-template-columns:1fr 110px 1fr; align-items:center; gap:12px; } .fee-card { display:flex; flex-direction:column; align-items:center; gap:8px; min-height:290px; background:#eef6ff; border:7px solid var(--blue); border-radius:22px; padding:25px 12px; text-align:center; } .fee-card span { font-size:68px; } .fee-card b { font-size:38px; } .fee-card strong { color:var(--red); font-size:68px; } .fee-or { color:var(--blue); font-size:30px; font-weight:900; text-align:center; }
    .calling-body { gap:26px; } .calling-body .condition-badge { font-size:40px; padding:16px 42px; } .calling-fee-grid { gap:16px; } .calling-fee-grid .fee-card { min-height:500px; justify-content:center; gap:20px; padding:42px 14px; } .calling-fee-grid .fee-card span { font-size:96px; } .calling-fee-grid .fee-card b { font-size:46px; line-height:1.2; } .calling-fee-grid .fee-card strong { font-size:88px; } .calling-fee-grid .fee-or { font-size:34px; }

    /* Slide 4: the plan, price, and use-case card form one large price stack. */
    .small-plan-body { max-width:690px; gap:32px; } .small-plan-body .plan-name { font-size:38px; line-height:1.25; padding:28px 32px; } .small-plan-body .plan-name b { font-size:56px; } .small-plan-body .price-hero.compact { gap:18px; padding:30px 28px; } .small-plan-body .price-hero.compact span { font-size:82px; } .small-plan-body .price-hero.compact i { font-size:44px; } .small-plan-body .price-hero.compact strong { font-size:110px; } .small-plan-body .info-card.alert { gap:24px; font-size:60px; line-height:1.25; padding:34px 32px; } .small-plan-body .info-card.alert > span { font-size:62px; }

    /* Slide 6: keep warning elements at the prescribed baseline or larger and use the full safe left column. */
    .warning-slide { background:#fff8f8; padding:70px; } .warning-mark { color:var(--red); left:25px; } .warning-banner { z-index:1; color:#fff; background:var(--red); font-size:62px; font-weight:900; margin:0 -70px 24px; padding:22px 0; text-align:center; } .warning-title { z-index:1; font-size:64px; font-weight:900; line-height:1.2; margin-bottom:28px; } .warning-box { z-index:1; display:flex; flex-direction:column; justify-content:space-evenly; min-height:400px; gap:26px; background:#fff0f0; border:10px solid var(--red); padding:36px 42px; margin-right:210px; } .w-item { display:flex; align-items:center; gap:16px; color:#87212b; font-size:50px; font-weight:900; } .w-item span { font-size:58px; }

    .cta-slide { align-items:center; justify-content:center; background:linear-gradient(135deg,var(--blue),var(--blue-dark)); padding:44px 60px; text-align:center; } .cta-content { display:flex; flex-direction:column; align-items:center; } .cta-logos { display:flex; align-items:center; justify-content:center; gap:22px; height:120px; margin-bottom:8px; } .cta-logo { width:250px; height:100px; background:#fff; border-radius:18px; padding:8px 16px; filter:none; box-shadow:4px 4px 0 rgba(0,0,0,.18); } .cta-title { color:#ffd700; font-size:61px; font-weight:900; line-height:1.2; margin-bottom:10px; } .cta-sub { color:#fff; font-size:39px; font-weight:900; margin-bottom:12px; } .cta-banner-img { width:790px; max-height:430px; object-fit:contain; border-radius:18px; filter:none; box-shadow:0 14px 40px rgba(0,0,0,.35); } .cta-arrow { color:#ffd700; font-size:68px; font-weight:900; line-height:.8; animation:bounce 1s infinite; } @keyframes bounce { 0%,100% { transform:translateY(0); } 50% { transform:translateY(-16px); } }
    ''').strip()


def generate(slides: OrderedDict[str, dict[str, list[str]]]) -> str:
    expected = [str(number) for number in range(1, 8)]
    if list(slides) != expected:
        raise ValueError(f"Expected slide IDs {expected}, got {list(slides)}")
    renderers = {
        "1": render_thumbnail, "2": render_winners, "3": render_cost,
        "4": render_small_plan, "5": render_calling, "6": render_warning,
        "7": render_cta,
    }
    deck = "\n\n".join(renderers[slide_id](slide) for slide_id, slide in slides.items())
    return f'''<!doctype html>
<html lang="ja"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>日本通信SIMとイオンモバイル、あなたはどっち？（Short）</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@700;900&family=Noto+Sans+JP:wght@700;900&display=swap" rel="stylesheet">
<style>\n{stylesheet()}\n</style>
</head><body>
{deck}
</body></html>
'''


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--script", type=Path, default=DEFAULT_SCRIPT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    slides = read_slides(args.script)
    args.output.write_text(generate(slides), encoding="utf-8")
    print(f"Generated {len(slides)} slides: {args.output}")


if __name__ == "__main__":
    main()
