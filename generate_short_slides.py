#!/usr/bin/env python3
"""Generate the LINEMO satellite-communication short deck from its scenario CSV."""

from __future__ import annotations

import argparse
import csv
import html
from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path


WORKDIR = Path("/workspaces/yt-factory/packages/slide-gen")
DEFAULT_SCENARIO = Path(
    "/workspaces/yt-factory/packages/scenario-gen/archive/videos/"
    "41_【2026年9月】LINEMOが月額そのままで衛星通信＆海外無制限！？知らないと損する2つのこと/"
    "short/【9月1日から】LINEMOが衛星通信に対応.csv"
)
DEFAULT_OUTPUT = WORKDIR / "slides-short.html"

LINEMO_LOGO = "public/images/logo/LINEMO_logo.png"
THUMBNAIL = (
    "public/images/thumbnails/"
    "41_【2026年9月】LINEMOが月額そのままで衛星通信＆海外無制限！？今やるべき2つのこと_サムネ1.png"
)
ASSETS = {
    "surprised": "public/images/irasutoya/bikkuri_me_tobideru_man.png",
    "phone": "public/images/irasutoya/smartphone_talk03_man.png",
    "happy_phone": "public/images/irasutoya/smartphone04_laugh.png",
    "warning": "public/images/irasutoya/business_man2_3_surprise.png",
    "application_check": "public/images/irasutoya/pose_yubisashi_kakunin_businesswoman.png",
}


@dataclass(frozen=True)
class Slide:
    slide_id: str
    raw_content: str
    parts: tuple[str, ...]


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def semantic_lines(value: str, line_end_markers: tuple[str, ...]) -> str:
    """Escape text and lock its wrapping to intentional phrase boundaries."""
    lines: list[str] = []
    remainder = value
    for marker in line_end_markers:
        before, separator, after = remainder.partition(marker)
        if not separator:
            raise ValueError(f"semantic line marker {marker!r} is missing from {value!r}")
        lines.append(before + separator)
        remainder = after
    lines.append(remainder)
    if any(not line for line in lines):
        raise ValueError(f"semantic line split produced an empty line: {value!r}")
    return "".join(f'<span class="semantic-line">{esc(line)}</span>' for line in lines)


def parse_slides(csv_path: Path) -> list[Slide]:
    """Resolve 同上 and collapse dialogue rows to one display record per slide ID."""
    grouped: OrderedDict[str, str] = OrderedDict()
    previous_content = ""
    with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"スライドに表示する内容", "スライドID"}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError(f"CSV is missing required columns: {sorted(required)}")
        for line_number, row in enumerate(reader, start=2):
            slide_id = (row.get("スライドID") or "").strip()
            content = (row.get("スライドに表示する内容") or "").strip()
            if not slide_id:
                raise ValueError(f"line {line_number}: empty slide ID")
            if slide_id.endswith("-0"):
                raise ValueError(f"line {line_number}: N-0 spread ID is not allowed: {slide_id}")
            if content == "同上":
                if not previous_content:
                    raise ValueError(f"line {line_number}: 同上 has no preceding content")
                content = previous_content
            else:
                previous_content = content
            if slide_id in grouped and grouped[slide_id] != content:
                raise ValueError(
                    f"slide {slide_id} has conflicting display content: "
                    f"{grouped[slide_id]!r} != {content!r}"
                )
            grouped.setdefault(slide_id, content)

    slides = [
        Slide(slide_id=sid, raw_content=content, parts=tuple(content.split("／")))
        for sid, content in grouped.items()
    ]
    expected = [str(number) for number in range(1, len(slides) + 1)]
    actual = [slide.slide_id for slide in slides]
    if actual != expected:
        raise ValueError(f"slide IDs must be consecutive: expected {expected}, got {actual}")
    if len(slides) != 6:
        raise ValueError(f"this deck expects 6 unique slide IDs, got {len(slides)}")
    return slides


def assert_assets_exist() -> None:
    relative_assets = [LINEMO_LOGO, THUMBNAIL, *ASSETS.values()]
    missing = [path for path in relative_assets if not (WORKDIR / path).is_file()]
    if missing:
        raise FileNotFoundError(f"missing assets: {missing}")


CSS = r"""
:root {
  --blue: #0052cc;
  --blue-deep: #003380;
  --blue-soft: #eaf3ff;
  --linemo: #00b900;
  --linemo-deep: #008f2d;
  --linemo-soft: #ebfff0;
  --red: #e63946;
  --amber: #f5a000;
  --ink: #172b4d;
  --ink-soft: #5b6780;
}

* { box-sizing: border-box; margin: 0; padding: 0; }

body {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 40px;
  margin: 0;
  padding: 40px;
  background: #f0f4f8;
  font-family: "Inter", "Noto Sans JP", sans-serif;
  font-weight: 700;
}

.slide-container {
  position: relative;
  isolation: isolate;
  overflow: hidden;
  display: block;
  width: 1080px;
  height: 1080px;
  flex-shrink: 0;
  padding: 58px 70px;
  background: #fff;
  color: var(--ink);
}

.slide-container.price-note::after {
    content: "※表示している料金はすべて月額・税込みの価格です";
    position: absolute; right: 20px; bottom: 16px; z-index: 9999;
    background: rgba(0,0,0,0.62); color: #fff;
    font-family: 'Noto Sans JP', sans-serif;
    font-size: 26px; font-weight: 700; letter-spacing: 0.02em; line-height: 1;
    padding: 10px 20px; border-radius: 10px; white-space: nowrap; pointer-events: none;
}

img {
  object-fit: contain;
  filter: drop-shadow(0 10px 20px rgba(0, 0, 0, 0.12));
}

.watermark {
  position: absolute;
  top: -74px;
  left: 20px;
  z-index: -1;
  color: var(--blue);
  font: 900 280px/1 "Inter", sans-serif;
  opacity: 0.07;
}

.slide-title {
  position: relative;
  z-index: 1;
  margin: 0 0 30px;
  padding: 0 0 20px;
  border-bottom: 10px solid var(--blue);
  color: var(--ink);
  font-size: 62px;
  font-weight: 900;
  line-height: 1.15;
  letter-spacing: -0.045em;
}

.slide-title em,
.warning-title em { color: var(--red); font-style: normal; }
.slide-title .green { color: var(--linemo-deep); }

.slide-body {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  gap: 26px;
}

.slide-illust {
  position: absolute;
  right: 34px;
  bottom: 30px;
  height: 250px;
  pointer-events: none;
}

.slide-illust img { height: 100%; max-width: 320px; }

.info-card {
  display: flex;
  align-items: center;
  gap: 22px;
  padding: 22px 32px;
  border-left: 14px solid var(--blue);
  border-radius: 0 16px 16px 0;
  background: #f0f5ff;
  font-size: 43px;
  font-weight: 800;
  line-height: 1.24;
}

.info-card.alert {
  border-left-color: var(--red);
  background: #fff0f0;
  color: var(--red);
  font-size: 48px;
  font-weight: 900;
}

.card-icon {
  display: grid;
  place-items: center;
  min-width: 72px;
  height: 72px;
  border-radius: 18px;
  background: var(--blue);
  color: #fff;
  font-size: 42px;
  line-height: 1;
}

.info-card.alert .card-icon { background: var(--red); }

.semantic-line {
  display: block;
  white-space: nowrap;
}

/* Slide 1: thumbnail */
.slide-thumbnail {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  padding: 154px 48px 300px;
  border: 25px solid var(--blue);
  background:
    repeating-conic-gradient(from 0deg at 52% 48%, rgba(0,82,204,0.06) 0deg 2.5deg, transparent 2.5deg 16deg),
    radial-gradient(ellipse at 52% 48%, #ffffff 5%, #e8f3ff 45%, #c8dcff 100%);
  text-align: center;
}

.thumb-top-strip {
  position: absolute;
  top: 25px;
  left: 25px;
  right: 25px;
  z-index: 3;
  padding: 18px 0;
  background: var(--blue);
  color: #fff;
  font-size: 36px;
  font-weight: 900;
  letter-spacing: 0.06em;
  text-align: center;
}

.thumb-accent-tri { position: absolute; width: 0; height: 0; }
.thumb-accent-tri.tl { top: 25px; left: 25px; border-top: 300px solid rgba(0,82,204,.09); border-right: 300px solid transparent; }
.thumb-accent-tri.br { right: 25px; bottom: 25px; border-bottom: 300px solid rgba(0,82,204,.09); border-left: 300px solid transparent; }

.thumb-content { position: relative; z-index: 2; }

.thumb-tag {
  display: inline-block;
  margin-bottom: 20px;
  padding: 13px 48px;
  transform: rotate(-3deg);
  background: var(--red);
  box-shadow: 8px 8px 0 rgba(0,0,0,.25);
  color: #fff;
  font-size: 68px;
  font-weight: 900;
}

.thumb-title {
  max-width: 920px;
  margin: 0 auto 18px;
  color: #17213d;
  font-size: 68px;
  font-weight: 900;
  line-height: 1.16;
  letter-spacing: -0.055em;
}

.thumb-title .brand-line { display: block; color: var(--linemo-deep); }
.thumb-title .impact-line { display: block; color: var(--red); font-size: 84px; }

.thumb-sub-band {
  display: inline-block;
  padding: 15px 52px;
  border-radius: 12px;
  background: var(--blue);
  box-shadow: 4px 4px 0 rgba(0,0,0,.2);
  color: #fff;
  font-size: 47px;
  font-weight: 900;
}

.thumb-logo-wrap {
  position: absolute;
  left: 48px;
  bottom: 78px;
  z-index: 2;
  display: grid;
  place-items: center;
  width: 470px;
  height: 145px;
  padding: 20px 25px;
  border: 5px solid var(--linemo);
  border-radius: 20px;
  background: #fff;
  box-shadow: 6px 7px 0 rgba(0,185,0,.16);
}

.thumb-logo-wrap img { width: 380px; max-height: 92px; filter: none; }
.thumb-illust { right: 38px; bottom: 24px; height: 284px; }

/* Slide 2: announcement */
.news-body { gap: 25px; }

.report-header-card {
  display: flex;
  align-items: center;
  gap: 24px;
  min-height: 138px;
  padding: 24px 32px;
  border-radius: 20px;
  background: linear-gradient(135deg, var(--blue), var(--blue-deep));
  color: #fff;
}

.report-header-card img {
  width: 270px;
  max-height: 82px;
  padding: 10px 16px;
  border-radius: 12px;
  background: #fff;
  filter: none;
}

.report-copy { font-size: 35px; font-weight: 900; line-height: 1.28; }
.report-copy small { display: block; color: #cfe2ff; font-size: 27px; }

.plan-ribbon {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 18px;
  min-height: 134px;
  padding: 22px 28px;
  border: 5px solid var(--linemo);
  border-radius: 20px;
  background: var(--linemo-soft);
  color: var(--ink);
  font-size: 38px;
  font-weight: 900;
  text-align: center;
}

.plan-ribbon .plus { color: var(--linemo-deep); font-size: 62px; }

.news-highlights {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 22px;
  min-height: 310px;
}

.news-highlight {
  display: flex;
  min-height: 310px;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 28px 22px;
  border-radius: 20px;
  background: var(--blue-soft);
  text-align: center;
}

.news-highlight span { color: var(--ink-soft); font-size: 34px; }
.news-highlight strong {
  margin: 10px 0 14px;
  color: var(--red);
  font-size: 76px;
  line-height: 1.08;
}
.news-highlight small {
  color: var(--ink);
  font-size: 27px;
  font-weight: 900;
  line-height: 1.2;
}
.news-illust { right: 18px; bottom: 20px; height: 210px; }

/* Slide 3: Starlink mechanism */
.orbit-panel {
  position: relative;
  display: grid;
  grid-template-columns: 1fr 160px 1fr;
  align-items: center;
  min-height: 300px;
  padding: 25px 30px;
  border: 5px solid #cddcf4;
  border-radius: 24px;
  background: linear-gradient(150deg, #f8fbff, #e8f3ff);
}

.orbit-node { display: flex; flex-direction: column; align-items: center; gap: 12px; text-align: center; }
.orbit-symbol { font-size: 100px; line-height: 1; filter: drop-shadow(0 8px 12px rgba(0,0,0,.12)); }
.orbit-node strong { font-size: 37px; line-height: 1.16; }
.orbit-link { position: relative; height: 8px; border-radius: 999px; background: var(--linemo); }
.orbit-link::before, .orbit-link::after { content: ""; position: absolute; top: -13px; width: 32px; height: 32px; border: 7px solid var(--linemo); border-bottom: 0; border-left-color: transparent; border-right-color: transparent; border-radius: 50%; }
.orbit-link::before { left: 35px; }
.orbit-link::after { right: 35px; }
.orbit-link span { position: absolute; top: 25px; left: 50%; transform: translateX(-50%); color: var(--linemo-deep); font-size: 27px; white-space: nowrap; }

.feature-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }

.feature-card {
  min-height: 156px;
  padding: 22px 24px;
  border-left: 12px solid var(--blue);
  border-radius: 0 18px 18px 0;
  background: #f0f5ff;
}

.feature-card.wide { grid-column: 1 / -1; min-height: 150px; border-left-color: var(--linemo); background: var(--linemo-soft); }
.feature-card b { display: block; margin-bottom: 7px; color: var(--blue); font-size: 36px; }
.feature-card.wide b { color: var(--linemo-deep); }
.feature-card p { font-size: 31px; line-height: 1.25; }
.starlink-illust { right: 20px; bottom: 20px; height: 210px; }

/* Slide 4: limitations */
.limit-body { width: 78%; gap: 22px; }

.limit-card {
  display: flex;
  align-items: center;
  gap: 24px;
  min-height: 145px;
  padding: 22px 28px;
  border: 5px solid #f0b1b7;
  border-radius: 20px;
  background: #fff4f4;
}

.limit-mark {
  display: grid;
  place-items: center;
  min-width: 82px;
  height: 82px;
  border-radius: 50%;
  background: var(--red);
  color: #fff;
  font-size: 50px;
  font-weight: 900;
}

.limit-card strong { color: var(--red); font-size: 42px; line-height: 1.2; }
.limit-card p { margin-top: 5px; color: var(--ink-soft); font-size: 27px; line-height: 1.25; }

.insurance-note {
  width: 78%;
  padding: 22px 28px;
  border-radius: 18px;
  background: var(--ink);
  color: #fff;
  font-size: 35px;
  font-weight: 900;
  line-height: 1.22;
  text-align: center;
}

.limit-illust { right: 18px; bottom: 30px; height: 286px; }

/* Slide 5: application warning */
.warning-slide { padding: 0 70px 58px; background: #fff8f8; }

.warning-banner {
  margin: 0 -70px 20px;
  padding: 20px 0;
  background: var(--red);
  color: #fff;
  font-size: 58px;
  font-weight: 900;
  text-align: center;
}

.warning-title {
  margin: 0 0 18px;
  color: #b0001e;
  font-size: 54px;
  font-weight: 900;
  line-height: 1.15;
  text-align: center;
}

.warning-box {
  display: flex;
  flex-direction: column;
  gap: 18px;
  width: 100%;
  padding: 28px 34px;
  border: 10px solid var(--red);
  border-radius: 22px;
  background: #fff0f0;
}

.period-badge {
  align-self: center;
  padding: 12px 28px;
  border-radius: 999px;
  background: var(--ink);
  color: #fff;
  font-size: 32px;
  font-weight: 900;
}

.application-flow { display: grid; grid-template-columns: 1fr 65px 1fr; align-items: center; gap: 12px; }

.flow-card {
  display: flex;
  min-height: 174px;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 18px;
  border-radius: 18px;
  background: #fff;
  text-align: center;
}

.flow-card span { color: var(--ink-soft); font-size: 28px; }
.flow-card strong { color: var(--red); font-size: 47px; line-height: 1.14; }
.flow-card.green strong { color: var(--linemo-deep); }
.flow-arrow { color: var(--red); font-size: 58px; font-weight: 900; }

.winter-note {
  padding: 17px 22px;
  border-radius: 14px;
  background: #fff;
  color: var(--ink);
  font-size: 31px;
  font-weight: 900;
  line-height: 1.2;
  text-align: center;
}

.warning-callout {
  width: 72%;
  margin-top: 19px;
  padding: 20px 28px;
  border-radius: 14px;
  background: var(--ink);
  color: #fff;
  font-size: 38px;
  font-weight: 900;
  text-align: center;
}

.warning-illust { right: 22px; bottom: 88px; height: 250px; }

/* Slide 6: CTA */
.cta-slide { padding: 24px 60px 16px; background: linear-gradient(135deg, var(--blue), var(--blue-deep)); }

.cta-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 100%;
  text-align: center;
}

.cta-logo-card {
  display: grid;
  place-items: center;
  height: 96px;
  margin-bottom: 6px;
  padding: 8px 20px;
  border-radius: 18px;
  background: #fff;
  box-shadow: 4px 4px 0 rgba(0,0,0,.18);
}

.cta-logo { width: 310px; height: 74px; filter: none; }
.cta-title { margin: 0 0 5px; color: #ffd700; font-size: 68px; font-weight: 900; line-height: 1.08; }

.cta-sub {
  display: flex;
  flex-direction: column;
  gap: 5px;
  width: 920px;
  margin-bottom: 9px;
  color: #fff;
  font-size: 28px;
  font-weight: 900;
}

.cta-sub span { padding: 5px 14px; border: 3px solid rgba(255,255,255,.55); border-radius: 12px; background: rgba(255,255,255,.1); white-space: nowrap; }

.cta-banner-img {
  width: 900px;
  max-height: 505px;
  border: 7px solid #fff;
  border-radius: 18px;
  box-shadow: 0 18px 42px rgba(0,0,0,.4);
  object-fit: contain;
  filter: none;
}

.cta-arrow { margin-top: 8px; color: #ffd700; font-size: 70px; font-weight: 900; line-height: .82; animation: bounce 1s infinite; }

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(8px); }
}
"""


def slide_comment(slide: Slide) -> str:
    return (
        f'    <!-- Slide ID: {esc(slide.slide_id)} -->\n'
        f'    <!-- CSV表示内容: {esc(slide.raw_content)} -->'
    )


def render_slide_1(slide: Slide) -> str:
    _, date = slide.parts
    return f"""{slide_comment(slide)}
    <div class="slide-container slide-thumbnail" data-slide-id="{esc(slide.slide_id)}">
      <div class="thumb-top-strip">⚡ {esc(date)} サービス開始 ⚡</div>
      <i class="thumb-accent-tri tl"></i><i class="thumb-accent-tri br"></i>
      <div class="thumb-content">
        <div class="thumb-tag">月額そのまま</div>
        <h1 class="thumb-title"><span class="brand-line">LINEMOが</span><span class="impact-line">衛星通信に対応！</span></h1>
        <div class="thumb-sub-band">圏外でもLINEが送れる</div>
      </div>
      <div class="thumb-logo-wrap"><img src="{LINEMO_LOGO}" alt="LINEMO" /></div>
      <div class="slide-illust thumb-illust" style="z-index: 2;"><img src="{ASSETS['surprised']}" alt="新サービスに驚く人" /></div>
    </div>"""


def render_slide_2(slide: Slide) -> str:
    _, announced, expansion, benefits = slide.parts
    unchanged, existing = benefits.split("・", 1)
    start = expansion.split("から", 1)[0]
    unchanged_subject, unchanged_value = unchanged.split("は", 1)
    return f"""{slide_comment(slide)}
    <div class="slide-container news-slide" data-slide-id="{esc(slide.slide_id)}">
      <div class="watermark">{esc(slide.slide_id)}</div>
      <h2 class="slide-title">9月から<em>サービス拡充</em></h2>
      <div class="slide-body news-body" style="margin-bottom: 120px;">
        <div class="report-header-card">
          <img src="{LINEMO_LOGO}" alt="LINEMO" />
          <div class="report-copy"><small>NEWS</small>{esc(announced)}</div>
        </div>
        <div class="plan-ribbon"><span>LINEMOベストプラン</span><span class="plus">＋</span><span>ベストプランV</span></div>
        <div class="news-highlights">
          <div class="news-highlight"><span>サービス開始</span><strong>{esc(start)}</strong><small>2プラン同時に拡充</small></div>
          <div class="news-highlight"><span>{esc(unchanged_subject)}は</span><strong>{esc(unchanged_value)}</strong><small>✓ {esc(existing)}</small></div>
        </div>
      </div>
      <div class="slide-illust news-illust" style="z-index: 2;"><img src="{ASSETS['phone']}" alt="スマホで発表を見る人" /></div>
    </div>"""


def render_slide_3(slide: Slide) -> str:
    _, mechanism, antenna, available = slide.parts
    mechanism_lines = semantic_lines(mechanism, ("と",))
    available_lines = semantic_lines(available, ("圏外でも", "LINEで"))
    return f"""{slide_comment(slide)}
    <div class="slide-container starlink-slide" data-slide-id="{esc(slide.slide_id)}">
      <div class="watermark">{esc(slide.slide_id)}</div>
      <h2 class="slide-title"><span class="green">Starlink Direct</span>とは？</h2>
      <div class="slide-body" style="margin-bottom: 120px;">
        <div class="orbit-panel">
          <div class="orbit-node"><div class="orbit-symbol">🛰️</div><strong>通信衛星</strong></div>
          <div class="orbit-link"><span>直接つながる</span></div>
          <div class="orbit-node"><div class="orbit-symbol">📱</div><strong>いつもの<br />スマホ</strong></div>
        </div>
        <div class="feature-grid">
          <div class="feature-card"><b>📡 専用機器なし</b><p>{esc(antenna)}</p></div>
          <div class="feature-card"><b>🌤️ 空が見えれば</b><p>{mechanism_lines}</p></div>
          <div class="feature-card wide"><b>圏外でもメッセージ</b><p>{available_lines}</p></div>
        </div>
      </div>
      <div class="slide-illust starlink-illust" style="z-index: 2;"><img src="{ASSETS['happy_phone']}" alt="衛星通信でメッセージを送る人" /></div>
    </div>"""


def render_slide_4(slide: Slide) -> str:
    _, no_calls, limited_apps, clear_sky = slide.parts
    no_calls_lines = semantic_lines(no_calls, ("は",))
    return f"""{slide_comment(slide)}
    <div class="slide-container limits-slide" data-slide-id="{esc(slide.slide_id)}">
      <div class="watermark">{esc(slide.slide_id)}</div>
      <h2 class="slide-title">衛星通信の<em>注意点</em></h2>
      <div class="slide-body limit-body">
        <div class="limit-card"><span class="limit-mark">×</span><div><strong>{no_calls_lines}</strong><p>電話の代わりではありません</p></div></div>
        <div class="limit-card"><span class="limit-mark">!</span><div><strong>データ通信は対象アプリのみ</strong><p>{esc(limited_apps)}</p></div></div>
        <div class="limit-card"><span class="limit-mark">☁</span><div><strong>{esc(clear_sky)}</strong><p>屋内や障害物の近くではつながりにくい</p></div></div>
      </div>
      <div class="insurance-note">あくまで「メッセージの保険」</div>
      <div class="slide-illust limit-illust" style="z-index: 2;"><img src="{ASSETS['warning']}" alt="利用条件に驚く人" /></div>
    </div>"""


def render_slide_5(slide: Slide) -> str:
    _, period, fee, after_winter = slide.parts
    period_lines = semantic_lines(period, ("は",))
    return f"""{slide_comment(slide)}
    <div class="slide-container warning-slide price-note" data-slide-id="{esc(slide.slide_id)}">
      <div class="warning-banner">⚠ 要注意</div>
      <h2 class="warning-title">開始直後は<em>申し込み必須</em></h2>
      <div class="warning-box">
        <div class="period-badge">{period_lines}</div>
        <div class="application-flow">
          <div class="flow-card"><span>オプション</span><strong>自分で<br />申し込む</strong></div>
          <div class="flow-arrow">→</div>
          <div class="flow-card green"><span>月額1,650円</span><strong>全額割引<br />実質0円</strong></div>
        </div>
        <div class="winter-note">❄️ {esc(after_winter)}</div>
      </div>
      <div class="warning-callout">9月に入ったら まず申し込み！</div>
      <div class="slide-illust warning-illust" style="z-index: 2;"><img src="{ASSETS['application_check']}" alt="申し込みを確認する人" /></div>
    </div>"""


def render_slide_6(slide: Slide) -> str:
    _, point1, point2, point3 = slide.parts
    return f"""{slide_comment(slide)}
    <div class="slide-container cta-slide" data-slide-id="{esc(slide.slide_id)}">
      <div class="cta-content">
        <div class="cta-logo-card"><img class="cta-logo" src="{LINEMO_LOGO}" alt="LINEMO" /></div>
        <h2 class="cta-title">本編で解説</h2>
        <div class="cta-sub"><span>{esc(point1)}</span><span>{esc(point2)}</span><span>{esc(point3)}</span></div>
        <img class="cta-banner-img" src="{THUMBNAIL}" alt="LINEMOの衛星通信と海外データ通信を解説する本編動画" />
        <div class="cta-arrow">↓</div>
      </div>
    </div>"""


RENDERERS = {
    "1": render_slide_1,
    "2": render_slide_2,
    "3": render_slide_3,
    "4": render_slide_4,
    "5": render_slide_5,
    "6": render_slide_6,
}


def render_document(slides: list[Slide]) -> str:
    rendered = "\n".join(RENDERERS[slide.slide_id](slide) for slide in slides)
    return f"""<!doctype html>
<html lang="ja">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>LINEMOが衛星通信に対応 - Shorts Slides</title>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@700;900&amp;family=Noto+Sans+JP:wght@700;900&amp;display=swap" rel="stylesheet" />
    <style>
{CSS}
    </style>
  </head>
  <body>
{rendered}
  </body>
</html>
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", type=Path, default=DEFAULT_SCENARIO)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    scenario = args.scenario
    output = args.output
    if not scenario.is_absolute() or not output.is_absolute():
        parser.error("--scenario and --output must be absolute paths")
    if output.parent != WORKDIR:
        parser.error(f"output must be directly inside {WORKDIR}")

    assert_assets_exist()
    slides = parse_slides(scenario)
    output.write_text(render_document(slides), encoding="utf-8")
    print(f"generated {len(slides)} slides: {output}")


if __name__ == "__main__":
    main()
