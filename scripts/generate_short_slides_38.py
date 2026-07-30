#!/usr/bin/env python3
"""Generate the square short deck for video 38 from its scenario CSV.

The CSV's 「スライドに表示する内容」 column is the content source. Repeated
「同上」 rows are resolved to the preceding instruction and one single-page
slide is emitted per unique slide ID. Pricing-pair IDs ending in ``-0`` are
intentionally ignored because those long-form spreads are not part of shorts.
"""

from __future__ import annotations

import csv
import html
import re
from dataclasses import dataclass
from pathlib import Path


PROJECT_DIR = Path("/workspaces/yt-factory/packages/slide-gen")
SCENARIO_CSV = Path(
    "/workspaces/yt-factory/packages/scenario-gen/archive/videos/"
    "38_【2026年最新】格安SIMの無制限プラン比較！最安は月250円/"
    "short/【月250円〜】無制限プランの正解は3択.csv"
)
OUTPUT_HTML = PROJECT_DIR / "slides-short.html"
IMAGE_DIR = PROJECT_DIR / "public/images"
LONG_THUMBNAIL = (
    IMAGE_DIR
    / "thumbnails"
    / "【2026年最新】格安SIMの無制限プラン比較！最安は月250円_サムネ1.png"
)


@dataclass(frozen=True)
class Slide:
    slide_id: str
    display: str

    @property
    def parts(self) -> list[str]:
        cleaned = re.sub(r"^テロップ：", "", self.display).strip()
        return [part.strip() for part in cleaned.split("／") if part.strip()]


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def file_url(path: Path) -> str:
    absolute_path = path.resolve()
    if not absolute_path.is_file():
        raise FileNotFoundError(f"Required file is missing: {path}")
    return absolute_path.relative_to(PROJECT_DIR.resolve()).as_posix()


def asset(relative_path: str) -> str:
    return file_url(IMAGE_DIR / relative_path)


def load_slides() -> list[Slide]:
    displays: dict[str, str] = {}
    order: list[str] = []
    previous_display = ""

    with SCENARIO_CSV.open("r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        required = {"スライドに表示する内容", "スライドID"}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError(f"CSV columns are missing: {sorted(required)}")

        for line_number, row in enumerate(reader, start=2):
            slide_id = row["スライドID"].strip()
            raw_display = row["スライドに表示する内容"].strip()
            if not slide_id:
                raise ValueError(f"Empty slide ID at CSV line {line_number}")
            if re.fullmatch(r"\d+-0", slide_id):
                continue

            display = previous_display if raw_display == "同上" else raw_display
            if not display:
                raise ValueError(f"Unresolved 同上 at CSV line {line_number}")
            previous_display = display

            if slide_id in displays and displays[slide_id] != display:
                raise ValueError(
                    f"Slide ID {slide_id} has conflicting display instructions: "
                    f"{displays[slide_id]!r} / {display!r}"
                )
            if slide_id not in displays:
                displays[slide_id] = display
                order.append(slide_id)

    expected = [str(number) for number in range(1, len(order) + 1)]
    if order != expected:
        raise ValueError(
            "Short slide IDs must be contiguous. "
            f"Found {order}; expected {expected}"
        )
    return [Slide(slide_id, displays[slide_id]) for slide_id in order]


def slide_comment(slide: Slide, label: str) -> str:
    return (
        f"<!-- Slide ID: {esc(slide.slide_id)} -->\n"
        f"<!-- {esc(label)} | CSV表示内容: {esc(slide.display)} -->"
    )


def standard_header(slide: Slide, title: str) -> str:
    return f"""
  <div class="watermark">{esc(slide.slide_id)}</div>
  <h2 class="slide-title">{title}</h2>"""


def render_thumbnail(slide: Slide) -> str:
    topic = slide.parts[0]
    title = topic.replace("格安SIMの", "", 1)
    title = title.replace("あなたに合うのはどれ？", "").strip()
    return f"""
{slide_comment(slide, "診断サムネイル")}
<div class="slide-container slide-thumbnail">
  <div class="thumb-top-strip">⚡ 2026年最新・無制限プラン診断 ⚡</div>
  <i class="thumb-accent-tri tl"></i>
  <i class="thumb-accent-tri br"></i>
  <div class="thumb-content">
    <div class="thumb-tag">正解は3択</div>
    <h1>{esc(title)}<br><em>あなたに合うのはどれ？</em></h1>
    <div class="thumb-sub-band">動画派？ <b>SNS派？</b></div>
  </div>
  <div class="thumb-logo-row">
    <span class="thumb-logo-card wide"><img src="{asset("logo/Mobile_logo_1line_magenta.png")}" alt="楽天モバイル"></span>
    <span class="thumb-logo-card"><img src="{asset("logo/Mineo_logo.png")}" alt="mineo"></span>
    <span class="thumb-logo-card"><img src="{asset("logo/Povo_logo.png")}" alt="povo"></span>
  </div>
  <div class="slide-illust thumb-illust" style="z-index: 2;">
    <img src="{asset("irasutoya/smartphone04_laugh.png")}" alt="スマートフォンを楽しむ人">
  </div>
</div>"""


def render_three_types(slide: Slide) -> str:
    if len(slide.parts) != 2:
        raise ValueError(f"Slide 2 requires a heading and item group: {slide.parts}")
    items = re.findall(r"([①②③])\s*([^①②③]+)", slide.parts[1])
    if len(items) != 3:
        raise ValueError(f"Slide 2 requires three numbered items: {slide.parts[1]}")

    icons = ("⚡", "🐢", "＋")
    rows = "\n".join(
        f"""      <li class="type-row type-{number}">
        <span class="badge">{number}</span>
        <span class="type-icon">{icons[number - 1]}</span>
        <span class="tx">{esc(label.strip())}</span>
      </li>"""
        for number, (_, label) in enumerate(items, start=1)
    )
    return f"""
{slide_comment(slide, "無制限の3タイプ")}
<div class="slide-container three-types-slide">
{standard_header(slide, "「無制限」は<em>3タイプ</em>")}
  <div class="report-header-card">
    <span class="report-icon">∞</span>
    <span>同じ「無制限」でも<br><b>仕組みが違う</b></span>
  </div>
  <div class="slide-body">
    <ul class="type-rows">
{rows}
    </ul>
  </div>
  <div class="slide-illust compact-illust" style="z-index: 2;">
    <img src="{asset("irasutoya/wifi_speed_slow_l.png")}" alt="通信速度の違い">
  </div>
</div>"""


def render_diagnosis(slide: Slide) -> str:
    if len(slide.parts) != 3:
        raise ValueError(f"Slide 3 requires a heading and two choices: {slide.parts}")
    option_a = re.sub(r"^A\s*", "", slide.parts[1])
    option_b = re.sub(r"^B\s*", "", slide.parts[2])
    return f"""
{slide_comment(slide, "動画派・SNS派診断")}
<div class="slide-container diagnosis-slide">
{standard_header(slide, esc(slide.parts[0]))}
  <div class="diagnosis-lead">使い方に近いほうを選んで！</div>
  <div class="choice-grid">
    <section class="choice-card choice-a">
      <span class="choice-letter">A</span>
      <h3 class="choice-title-a">{esc(option_a)}</h3>
      <p>毎日たっぷり再生</p>
      <img src="{asset("irasutoya/pose_necchuu_smartphone_woman.png")}" alt="動画を楽しむ人">
    </section>
    <section class="choice-card choice-b">
      <span class="choice-letter">B</span>
      <h3 class="choice-title-b">{esc(option_b).replace("中心派", "<br>中心派")}</h3>
      <p>連絡・投稿がメイン</p>
      <img src="{asset("irasutoya/sns_happy_woman.png")}" alt="SNSを楽しむ人">
    </section>
  </div>
</div>"""


def render_rakuten(slide: Slide) -> str:
    if len(slide.parts) != 3:
        raise ValueError(f"Slide 4 requires three slash-separated parts: {slide.parts}")
    price_match = re.search(r"月[\d,]+円", slide.parts[1])
    if not price_match:
        raise ValueError(f"Slide 4 price not found: {slide.parts[1]}")
    price = price_match.group(0)
    unlimited_label = re.sub(r"で?月[\d,]+円", "", slide.parts[1]).strip()
    return f"""
{slide_comment(slide, "動画派の正解")}
<div class="slide-container rakuten-slide price-note">
{standard_header(slide, "Aの正解は <em>楽天モバイル</em>")}
  <div class="rakuten-logo-card">
    <img src="{asset("logo/Mobile_logo_2line_magenta.png")}" alt="楽天モバイル">
    <strong>Rakuten最強プラン</strong>
  </div>
  <div class="emph price-emph">
    <span>どれだけ使っても</span>
    <b>{esc(price)}</b>
    <small>で頭打ち</small>
  </div>
  <div class="feature-stack">
    <div class="info-card alert"><span>∞</span><b>{esc(unlimited_label)}</b></div>
    <div class="info-card"><span>⚡</span><b>{esc(slide.parts[2])}</b></div>
  </div>
  <div class="slide-illust rakuten-illust" style="z-index: 2;">
    <img src="{asset("irasutoya/family_happy_banzai.png")}" alt="使い放題を喜ぶ家族">
  </div>
</div>"""


def render_wifi(slide: Slide) -> str:
    message = slide.parts[0]
    if "から" not in message:
        raise ValueError(f"Slide 5 must contain a cause and benefit: {message}")
    lead, benefit = message.split("から", 1)
    return f"""
{slide_comment(slide, "上限なしの活用法")}
<div class="slide-container wifi-slide">
{standard_header(slide, "上限を気にせず<em>使える</em>")}
  <div class="emph wifi-emph">
    <span>{esc(lead)}</span>
    <b>残量チェック不要</b>
  </div>
  <div class="lead wifi-lead">
    {esc(benefit).replace("自宅のWi-Fiがわり", "<strong>自宅のWi-Fiがわり</strong>")}
  </div>
  <div class="benefit-stack">
    <div class="benefit-chip"><span>✓</span>動画をたっぷり楽しめる</div>
    <div class="benefit-chip"><span>✓</span>テザリングでPCにも共有</div>
  </div>
  <div class="device-flow"><span>📱</span><b>→</b><span>📶</span><b>→</b><span>💻</span></div>
  <div class="slide-illust wifi-illust" style="z-index: 2;">
    <img src="{asset("irasutoya/internet_modem_router.png")}" alt="Wi-Fiルーター">
  </div>
</div>"""


def render_cta(slide: Slide) -> str:
    message = slide.parts[0]
    mineo_match = re.search(r"（([^）]*mineo)）", message)
    mineo_text = mineo_match.group(1) if mineo_match else "月250円〜のmineo"
    return f"""
{slide_comment(slide, "本編へのCTA")}
<div class="slide-container cta-slide price-note">
  <div class="cta-content">
    <div class="cta-logo-card">
      <img class="cta-logo" src="{asset("logo/Mineo_logo.png")}" alt="mineo ロゴ">
    </div>
    <h2 class="cta-title">Bの正解は<br>本編で！</h2>
    <div class="cta-sub">
      <strong>{esc(mineo_text)}</strong>
      <span>＋ povoの2枚持ちも徹底解説</span>
    </div>
    <img class="cta-banner-img" src="{file_url(LONG_THUMBNAIL)}" alt="格安SIM無制限プラン比較の長尺動画サムネイル">
    <div class="cta-arrow">↓</div>
  </div>
</div>"""


RENDERERS = {
    "1": render_thumbnail,
    "2": render_three_types,
    "3": render_diagnosis,
    "4": render_rakuten,
    "5": render_wifi,
    "6": render_cta,
}


CSS = r"""
:root {
  --blue: #0052cc;
  --blue-dark: #003380;
  --red: #e63946;
  --ink: #172b4d;
  --ink-soft: #5b6780;
}

* { box-sizing: border-box; }

body {
  margin: 0;
  padding: 40px;
  gap: 40px;
  align-items: center;
  background: #f0f4f8;
  font-family: 'Inter', 'Noto Sans JP', sans-serif;
  font-weight: 700;
}

.slide-container {
  width: 1080px;
  height: 1080px;
  flex-shrink: 0;
  position: relative;
  overflow: hidden;
  padding: 58px 70px;
  background: #ffffff;
  color: var(--ink);
  isolation: isolate;
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
  filter: drop-shadow(0 10px 20px rgba(0,0,0,0.1));
}

.watermark {
  position: absolute;
  top: -74px;
  left: 20px;
  z-index: -1;
  font-family: 'Inter', sans-serif;
  font-size: 280px;
  font-weight: 900;
  line-height: 1;
  color: var(--blue);
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
  line-height: 1.15;
  font-weight: 900;
  letter-spacing: -0.04em;
}

.slide-title em {
  color: var(--red);
  font-style: normal;
}

.slide-body {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  gap: 28px;
}

.slide-illust {
  position: absolute;
  right: 40px;
  bottom: 32px;
  z-index: 2;
  height: 260px;
  pointer-events: none;
}

.slide-illust img {
  height: 100%;
  max-width: 310px;
}

/* Thumbnail */
.slide-thumbnail {
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  padding: 160px 58px 300px;
  border: 25px solid var(--blue);
  text-align: center;
  background:
    repeating-conic-gradient(from 0deg at 52% 48%, rgba(0,82,204,0.06) 0deg 2.5deg, transparent 2.5deg 16deg),
    radial-gradient(ellipse at 52% 48%, #ffffff 5%, #e8f3ff 45%, #c8dcff 100%);
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

.thumb-accent-tri {
  position: absolute;
  width: 0;
  height: 0;
}

.thumb-accent-tri.tl {
  top: 25px;
  left: 25px;
  border-top: 300px solid rgba(0,82,204,0.09);
  border-right: 300px solid transparent;
}

.thumb-accent-tri.br {
  right: 25px;
  bottom: 25px;
  border-bottom: 300px solid rgba(0,82,204,0.09);
  border-left: 300px solid transparent;
}

.thumb-content {
  position: relative;
  z-index: 2;
}

.thumb-tag {
  display: inline-block;
  margin-bottom: 28px;
  padding: 18px 54px;
  transform: rotate(-3deg);
  background: var(--red);
  box-shadow: 8px 8px 0 rgba(0,0,0,0.25);
  color: #fff;
  font-size: 72px;
  font-weight: 900;
}

.thumb-content h1 {
  max-width: 900px;
  margin: 0 auto 22px;
  color: #17213d;
  font-size: 80px;
  font-weight: 900;
  line-height: 1.18;
  letter-spacing: -0.055em;
}

.thumb-content h1 em {
  color: var(--red);
  font-style: normal;
}

.thumb-sub-band {
  display: inline-block;
  padding: 18px 60px;
  border-radius: 12px;
  background: var(--blue);
  box-shadow: 4px 4px 0 rgba(0,0,0,0.2);
  color: #fff;
  font-size: 52px;
  font-weight: 900;
}

.thumb-sub-band b { color: #ffd700; }

.thumb-illust {
  right: 38px;
  bottom: 14px;
  height: 286px;
}

/* いらすとや左側の余白に、扱う3ブランドのロゴを2段（1段目=楽天モバイル、2段目=mineo・povo）で置く */
.thumb-logo-row {
  position: absolute;
  left: 52px;
  bottom: 52px;
  z-index: 2;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
  width: 500px;
}

.thumb-logo-card {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 112px;
  padding: 14px 18px;
  overflow: hidden;
  border: 4px solid var(--blue);
  border-radius: 16px;
  background: #fff;
  box-shadow: 5px 5px 0 rgba(0,82,204,0.18);
}

/* 1段目の楽天モバイルは横幅いっぱいに使う */
.thumb-logo-card.wide {
  grid-column: 1 / -1;
}

/* 素材ごとに縦横比が大きく違うため、% ではなく px で上限を切る */
.thumb-logo-card img {
  width: auto;
  height: auto;
  max-width: 200px;
  max-height: 80px;
  filter: none;
}

.thumb-logo-card.wide img {
  max-width: 400px;
}

/* Slide 2 */
.report-header-card {
  display: flex;
  align-items: center;
  gap: 24px;
  min-height: 138px;
  margin-bottom: 24px;
  padding: 22px 34px;
  border-radius: 20px;
  background: linear-gradient(135deg, var(--blue), #003fa0);
  color: #fff;
  font-size: 38px;
  font-weight: 700;
  line-height: 1.18;
}

.report-header-card b {
  color: #ffd700;
  font-size: 46px;
}

.report-icon {
  color: #ffd700;
  font-size: 88px;
  font-weight: 900;
}

.type-rows {
  display: flex;
  flex-direction: column;
  margin: 0;
  padding: 0;
  gap: 18px;
  list-style: none;
}

.type-row {
  display: flex;
  align-items: center;
  min-height: 132px;
  gap: 20px;
  padding: 18px 28px;
  border-left: 14px solid var(--blue);
  border-radius: 0 18px 18px 0;
  background: #f0f5ff;
  box-shadow: 0 8px 16px rgba(0,0,0,0.06);
}

.type-row .badge {
  display: grid;
  place-items: center;
  width: 76px;
  height: 76px;
  flex-shrink: 0;
  border-radius: 18px;
  background: var(--blue);
  color: #fff;
  font-size: 44px;
}

.type-row .type-icon {
  width: 72px;
  flex-shrink: 0;
  text-align: center;
  font-size: 52px;
}

.type-row .tx {
  font-size: 48px;
  font-weight: 900;
}

.type-rows .type-3 {
  width: 650px;
}

.type-rows .type-3 .tx {
  font-size: 44px;
}

.compact-illust {
  right: 40px;
  bottom: 42px;
  height: 200px;
}

/* Slide 3 */
.diagnosis-lead {
  margin: -6px 0 22px;
  color: var(--blue-dark);
  font-size: 38px;
  font-weight: 900;
  text-align: center;
}

.choice-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 28px;
}

.choice-card {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 660px;
  overflow: hidden;
  padding: 30px 22px 18px;
  border: 8px solid;
  border-radius: 28px;
  text-align: center;
  box-shadow: 0 14px 28px rgba(0,0,0,0.13);
}

.choice-a {
  border-color: var(--red);
  background: linear-gradient(155deg, #fff8f8, #ffe0e3);
}

.choice-b {
  border-color: var(--blue);
  background: linear-gradient(155deg, #f5f9ff, #dceaff);
}

.choice-letter {
  display: grid;
  place-items: center;
  width: 94px;
  height: 94px;
  flex-shrink: 0;
  margin: 0 auto 18px;
  border-radius: 50%;
  box-shadow: 0 8px 0 rgba(0,0,0,0.13);
  background: var(--blue);
  color: #fff;
  font-family: 'Inter', sans-serif;
  font-size: 62px;
  font-weight: 900;
}

.choice-a .choice-letter { background: var(--red); }

.choice-card h3 {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 104px;
  margin: 0;
  font-size: 42px;
  font-weight: 900;
  line-height: 1.22;
  letter-spacing: -0.035em;
}

.choice-title-a {
  white-space: nowrap;
}

.choice-title-b {
  font-size: 41px;
}

.choice-card p {
  display: inline-block;
  flex-shrink: 0;
  margin: 10px 0 8px;
  padding: 10px 16px;
  border-radius: 999px;
  background: rgba(255,255,255,0.82);
  font-size: 27px;
  font-weight: 900;
  white-space: nowrap;
}

.choice-card img {
  width: 100%;
  height: 270px;
  margin-top: auto;
  flex-shrink: 0;
}

/* Slide 4 */
.rakuten-slide {
  --brand: #bf0000;
}

.rakuten-slide .slide-title { border-bottom-color: #bf0000; }

.rakuten-logo-card {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 28px;
  height: 120px;
  margin-bottom: 20px;
  padding: 16px 28px;
  border: 5px solid #bf0000;
  border-radius: 22px;
  background: #fff;
  box-shadow: 0 8px 0 rgba(0,0,0,0.09);
}

.rakuten-logo-card img {
  width: 250px;
  max-height: 88px;
  filter: none;
}

.rakuten-logo-card strong {
  color: #bf0000;
  font-size: 37px;
  font-weight: 900;
}

.price-emph {
  display: block;
  width: 100%;
  margin-bottom: 20px;
  padding: 20px 26px;
  border: 6px solid #bf0000;
  border-radius: 22px;
  background: #fff0f2;
  line-height: 1.12;
  text-align: center;
}

.price-emph span {
  display: block;
  font-size: 34px;
}

.price-emph b {
  color: #bf0000;
  font-size: 96px;
  font-weight: 900;
  white-space: nowrap;
}

.price-emph small {
  font-size: 31px;
  font-weight: 900;
}

.feature-stack {
  display: flex;
  flex-direction: column;
  gap: 16px;
  width: 620px;
}

.info-card {
  display: flex;
  align-items: center;
  gap: 20px;
  min-height: 105px;
  padding: 18px 24px;
  border-left: 14px solid var(--blue);
  border-radius: 0 16px 16px 0;
  background: #edf4ff;
  font-size: 36px;
  font-weight: 900;
}

.info-card.alert {
  border-left-color: var(--red);
  background: #fff0f0;
  color: var(--red);
}

.info-card span {
  width: 62px;
  flex-shrink: 0;
  color: inherit;
  font-size: 52px;
  text-align: center;
}

.info-card b { font-size: inherit; }

.rakuten-illust {
  right: 38px;
  bottom: 72px;
  height: 220px;
}

.rakuten-illust img { max-width: 300px; }

/* Slide 5 */
.wifi-slide {
  --brand: var(--blue);
  --brand-deep: var(--blue-dark);
  --brand-soft: #eaf3ff;
}

.wifi-slide .slide-title { border-bottom-color: var(--brand); }

.wifi-emph {
  display: block;
  width: 680px;
  margin-bottom: 20px;
  padding: 22px 26px;
  border: 6px solid var(--brand);
  border-radius: 22px;
  background: var(--brand-soft);
  line-height: 1.2;
  text-align: center;
}

.wifi-emph span {
  display: block;
  font-size: 34px;
}

.wifi-emph b {
  display: block;
  color: var(--brand-deep);
  font-size: 67px;
  font-weight: 900;
}

.wifi-lead {
  width: 680px;
  margin-bottom: 18px;
  padding: 24px 28px;
  border-left: 14px solid var(--brand);
  border-radius: 0 16px 16px 0;
  background: var(--brand-soft);
  font-size: 38px;
  font-weight: 900;
  line-height: 1.3;
}

.wifi-lead strong {
  color: var(--red);
  font-size: 1.08em;
}

.benefit-stack {
  display: flex;
  flex-direction: column;
  gap: 13px;
  width: 650px;
}

.benefit-chip {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 22px;
  border-left: 11px solid var(--brand);
  border-radius: 0 15px 15px 0;
  background: #fff;
  font-size: 31px;
  font-weight: 900;
}

.benefit-chip span {
  color: var(--brand);
  font-size: 39px;
}

.device-flow {
  position: absolute;
  right: 50px;
  bottom: 270px;
  z-index: 3;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border: 4px solid var(--brand);
  border-radius: 999px;
  background: #fff;
  font-size: 33px;
}

.device-flow b {
  color: var(--brand);
  font-size: 28px;
}

.wifi-illust {
  right: 34px;
  bottom: 54px;
  height: 236px;
}

/* Slide 6 */
.cta-slide {
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: 24px 58px 78px;
  background:
    radial-gradient(circle at 50% -10%, rgba(255,255,255,0.2), transparent 42%),
    linear-gradient(135deg, var(--blue), var(--blue-dark));
  color: #fff;
}

.cta-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  text-align: center;
}

.cta-logo-card {
  display: grid;
  place-items: center;
  width: 300px;
  height: 116px;
  margin-bottom: 8px;
  padding: 8px 20px;
  border-radius: 18px;
  background: #fff;
  box-shadow: 4px 4px 0 rgba(0,0,0,0.18);
}

.cta-logo {
  width: 260px;
  height: 90px;
  filter: none;
}

.cta-title {
  margin: 0 0 6px;
  color: #ffd700;
  font-size: 78px;
  font-weight: 900;
  line-height: 1.08;
  letter-spacing: -0.05em;
}

.cta-sub {
  display: flex;
  flex-direction: column;
  gap: 2px;
  margin-bottom: 12px;
  color: #fff;
  font-size: 35px;
  font-weight: 900;
  line-height: 1.22;
}

.cta-sub strong {
  color: #ffd700;
  font-size: 43px;
}

.cta-banner-img {
  width: 760px;
  max-height: 428px;
  border: 7px solid #fff;
  border-radius: 18px;
  box-shadow: 0 18px 42px rgba(0,0,0,0.4);
  filter: none;
}

.cta-arrow {
  margin-top: 0;
  color: #ffd700;
  font-size: 74px;
  font-weight: 900;
  line-height: 0.88;
  animation: bounce 1s infinite;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(10px); }
}
"""


def render_document(slides: list[Slide]) -> str:
    unsupported = [slide.slide_id for slide in slides if slide.slide_id not in RENDERERS]
    if unsupported:
        raise ValueError(f"No renderer for slide IDs: {unsupported}")

    rendered = "\n\n".join(RENDERERS[slide.slide_id](slide) for slide in slides)
    return f"""<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>【月250円〜】無制限プランの正解は3択</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@700;900&amp;family=Noto+Sans+JP:wght@700;900&amp;display=swap" rel="stylesheet">
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
    slides = load_slides()
    OUTPUT_HTML.write_text(render_document(slides), encoding="utf-8")
    print(f"Generated {len(slides)} slides: {OUTPUT_HTML}")
    print("Slide IDs:", ", ".join(slide.slide_id for slide in slides))


if __name__ == "__main__":
    main()
