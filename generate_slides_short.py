#!/usr/bin/env python3
"""Generate the short-form HTML deck for video 42 from its scenario CSV."""

from __future__ import annotations

import csv
import html
from pathlib import Path


WORK_DIR = Path("/workspaces/yt-factory/packages/slide-gen")
SOURCE_CSV = Path(
    "/workspaces/yt-factory/packages/scenario-gen/archive/videos/"
    "42_【放置は損】その「無料オプション」終わると毎月いくら？月500円〜1,980円の自動課金/"
    "short/スマホ代急増、犯人は無料オプション？.csv"
)
OUTPUT_HTML = Path("/workspaces/yt-factory/packages/slide-gen/slides-short.html")
IMAGE_ROOT = Path("/workspaces/yt-factory/packages/slide-gen/public/images")


CSS = r"""
:root {
  --blue: #0052cc;
  --blue-deep: #003380;
  --blue-soft: #eaf3ff;
  --red: #e63946;
  --red-deep: #b0001e;
  --red-soft: #fff0f0;
  --yellow: #ffd43b;
  --ink: #172b4d;
  --muted: #5b6780;
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
  filter: drop-shadow(0 10px 20px rgba(0, 0, 0, .12));
}

.watermark {
  position: absolute;
  top: -74px;
  left: 20px;
  z-index: -1;
  color: var(--blue);
  font: 900 280px/1 "Inter", sans-serif;
  opacity: .07;
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
  letter-spacing: -.045em;
}

.slide-title em { color: var(--red); font-style: normal; }
.slide-body { position: relative; z-index: 1; display: flex; flex-direction: column; gap: 26px; }

.slide-illust {
  position: absolute;
  right: 34px;
  bottom: 30px;
  z-index: 2;
  height: 250px;
  pointer-events: none;
}

.slide-illust img { height: 100%; max-width: 330px; }

.semantic-line { display: block; white-space: nowrap; }

.info-card {
  display: flex;
  align-items: center;
  gap: 22px;
  min-height: 124px;
  padding: 22px 32px;
  border-left: 14px solid var(--blue);
  border-radius: 0 16px 16px 0;
  background: #f0f5ff;
  font-size: 43px;
  font-weight: 900;
  line-height: 1.2;
}

.info-card.alert { border-left-color: var(--red); background: var(--red-soft); color: var(--red-deep); }
.card-icon { display: grid; place-items: center; min-width: 72px; height: 72px; border-radius: 18px; background: var(--blue); color: #fff; font-size: 42px; }
.info-card.alert .card-icon { background: var(--red); }

/* Slide 1: thumbnail */
.slide-thumbnail {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  padding: 154px 48px 300px;
  border: 25px solid var(--blue);
  background:
    repeating-conic-gradient(from 0deg at 52% 48%, rgba(0,82,204,.06) 0deg 2.5deg, transparent 2.5deg 16deg),
    radial-gradient(ellipse at 52% 48%, #fff 5%, #e8f3ff 45%, #c8dcff 100%);
  text-align: center;
}

.thumb-top-strip { position: absolute; top: 25px; left: 25px; right: 25px; z-index: 3; padding: 18px 0; background: var(--blue); color: #fff; font-size: 36px; font-weight: 900; letter-spacing: .06em; text-align: center; }
.thumb-accent-tri { position: absolute; width: 0; height: 0; }
.thumb-accent-tri.tl { top: 25px; left: 25px; border-top: 300px solid rgba(0,82,204,.09); border-right: 300px solid transparent; }
.thumb-accent-tri.br { right: 25px; bottom: 25px; border-bottom: 300px solid rgba(0,82,204,.09); border-left: 300px solid transparent; }
.thumb-content { position: relative; z-index: 2; }
.thumb-tag { display: inline-block; margin-bottom: 24px; padding: 14px 52px; transform: rotate(-3deg); background: var(--red); box-shadow: 8px 8px 0 rgba(0,0,0,.25); color: #fff; font-size: 70px; font-weight: 900; }
.thumb-title { max-width: 920px; margin: 0 auto 22px; color: #17213d; font-size: 76px; font-weight: 900; line-height: 1.17; letter-spacing: -.055em; }
.thumb-title .impact-line { display: block; color: var(--red); font-size: 84px; }
.switch-band { display: flex; align-items: center; justify-content: center; gap: 24px; }
.switch-pill { min-width: 180px; padding: 13px 28px; border-radius: 18px; background: var(--blue); color: #fff; font-size: 50px; font-weight: 900; box-shadow: 4px 4px 0 rgba(0,0,0,.18); }
.switch-pill.paid { background: var(--red); }
.switch-arrow { color: var(--ink); font-size: 68px; font-weight: 900; }
.thumb-illust { right: 36px; bottom: 26px; height: 292px; }
.thumb-sticker { position: absolute; left: 46px; bottom: 84px; z-index: 2; width: 480px; padding: 18px 24px; border: 5px solid var(--blue); border-radius: 20px; background: #fff; box-shadow: 6px 7px 0 rgba(0,82,204,.18); color: var(--ink); font-size: 36px; font-weight: 900; }

/* Slide 2: diagnostic */
.diagnosis-panel { padding: 34px 38px; border: 6px solid #b9d1f5; border-radius: 24px; background: linear-gradient(145deg, #f7fbff, #e9f3ff); }
.diagnosis-label { margin-bottom: 18px; color: var(--blue); font-size: 32px; font-weight: 900; letter-spacing: .12em; }
.diagnosis-question { font-size: 55px; font-weight: 900; line-height: 1.2; }
.choice-row { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
.choice-card { display: grid; place-items: center; min-height: 190px; border: 7px solid var(--red); border-radius: 24px; background: var(--red-soft); color: var(--red-deep); font-size: 58px; font-weight: 900; box-shadow: 0 12px 28px rgba(230,57,70,.16); }
.choice-card.unknown { border-color: var(--blue); background: var(--blue-soft); color: var(--blue); }
.auto-note { width: 72%; padding: 24px 30px; border-radius: 18px; background: var(--ink); color: #fff; font-size: 38px; font-weight: 900; line-height: 1.25; text-align: center; }
.diagnosis-illust { height: 260px; }

/* Slide 3: application checkbox */
.phone-mock { width: 100%; padding: 34px; border: 12px solid #25324a; border-radius: 42px; background: #f8fbff; box-shadow: 0 20px 40px rgba(23,43,77,.18); }
.phone-head { margin-bottom: 22px; padding-bottom: 18px; border-bottom: 5px solid #d6dfed; color: var(--blue); font-size: 36px; font-weight: 900; }
.option-row { display: grid; grid-template-columns: 94px 1fr; gap: 24px; align-items: center; padding: 27px; border: 6px solid var(--red); border-radius: 20px; background: var(--red-soft); }
.check-box { display: grid; place-items: center; width: 82px; height: 82px; border-radius: 16px; background: var(--red); color: #fff; font-size: 62px; font-weight: 900; }
.option-copy strong { display: block; color: var(--red-deep); font-size: 46px; }
.option-copy span { color: var(--muted); font-size: 30px; }
.trial-summary { display: grid; grid-template-columns: 1fr auto 1fr; gap: 18px; align-items: center; margin-top: 24px; padding: 20px 24px; border-radius: 18px; background: #fff; color: var(--ink); font-size: 34px; font-weight: 900; text-align: center; }
.trial-summary strong { color: var(--red); font-size: 44px; }
.trial-summary-arrow { color: var(--red); font-size: 46px; }
.notice-strip { width: 62%; min-height: 136px; padding: 21px 30px; border-radius: 16px; background: var(--yellow); color: #5a4300; font-size: 40px; font-weight: 900; line-height: 1.2; text-align: center; }
.checkbox-illust { right: 24px; bottom: 22px; height: 238px; }

/* Price slides */
.fee-hero { display: grid; grid-template-columns: 310px 1fr; align-items: center; min-height: 270px; padding: 30px 36px; border: 7px solid var(--red); border-radius: 26px; background: linear-gradient(145deg, #fff7f7, #ffe3e6); }
.fee-kind { padding: 20px 16px; border-radius: 18px; background: var(--ink); color: #fff; font-size: 39px; font-weight: 900; line-height: 1.25; text-align: center; }
.fee-amount { color: var(--red); font-size: 82px; font-weight: 900; line-height: 1.05; text-align: center; letter-spacing: -.05em; }
.fee-amount small { display: block; margin-top: 14px; color: var(--ink); font-size: 32px; letter-spacing: 0; }
.charge-flow { display: grid; grid-template-columns: 1fr 90px 1fr; align-items: center; gap: 12px; }
.flow-card { display: grid; place-items: center; min-height: 172px; padding: 22px; border-radius: 20px; background: var(--blue-soft); color: var(--blue); font-size: 42px; font-weight: 900; line-height: 1.2; text-align: center; }
.flow-card.danger { background: var(--red-soft); color: var(--red); }
.flow-arrow { color: var(--red); font-size: 72px; font-weight: 900; text-align: center; }
.recurring-warning { display: grid; place-items: center; width: 72%; min-height: 150px; padding: 24px 30px; border: 7px solid var(--red); border-radius: 20px; background: var(--red); color: #fff; font-size: 42px; font-weight: 900; line-height: 1.28; text-align: center; box-shadow: 0 14px 28px rgba(230,57,70,.18); }
.fee-illust { height: 236px; }

/* Slide 5: money leak */
.leak-slide .slide-body { gap: 38px; }
.leak-panel { display: grid; grid-template-columns: 1fr 120px 1fr; align-items: center; min-height: 350px; padding: 38px; border-radius: 26px; background: linear-gradient(145deg, #f4f8ff, #e4efff); }
.leak-side { display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; }
.leak-side span { color: var(--muted); font-size: 36px; }
.leak-side strong { margin-top: 12px; color: var(--red); font-size: 78px; line-height: 1.05; }
.leak-arrow { color: var(--red); font-size: 90px; font-weight: 900; text-align: center; }
.waste-callout { display: grid; place-items: center; width: 88%; min-height: 184px; padding: 34px 36px; border: 7px solid var(--red); border-radius: 20px; background: var(--red-soft); color: var(--red-deep); font-size: 48px; font-weight: 900; line-height: 1.22; text-align: center; }
.leak-illust { height: 265px; }

/* Slide 6: timeline */
.data-fee { grid-template-columns: 310px 1fr; }
.data-fee .fee-amount { font-size: 102px; }
.billing-timeline { display: grid; grid-template-columns: 1fr 58px 1fr 58px 1fr; align-items: center; gap: 8px; }
.timeline-step { display: grid; place-items: center; min-height: 175px; padding: 18px; border-radius: 18px; background: var(--blue-soft); color: var(--blue); font-size: 35px; font-weight: 900; line-height: 1.18; text-align: center; }
.timeline-step.danger { background: var(--red); color: #fff; }
.timeline-arrow { color: var(--red); font-size: 52px; text-align: center; }
.next-month-warning { display: grid; place-items: center; width: 72%; min-height: 150px; padding: 24px 30px; border: 7px solid var(--red); border-radius: 20px; background: var(--red-soft); color: var(--red-deep); font-size: 41px; font-weight: 900; line-height: 1.28; text-align: center; }
.data-illust { height: 230px; }

/* Slide 7: bill shock */
.bill-slide .slide-body { gap: 36px; }
.bill-sheet { width: 82%; padding: 34px 38px; border: 7px solid #c9d5e8; border-radius: 22px; background: #fff; box-shadow: 0 22px 44px rgba(23,43,77,.18); }
.bill-head { display: flex; justify-content: space-between; padding-bottom: 18px; border-bottom: 5px solid #dae2ed; color: var(--muted); font-size: 32px; }
.bill-row { display: flex; justify-content: space-between; align-items: center; padding: 24px 0; font-size: 40px; }
.bill-row.plus { margin-top: 10px; padding: 27px 24px; border-radius: 16px; background: var(--red-soft); color: var(--red); font-size: 58px; font-weight: 900; }
.bill-result { display: grid; place-items: center; width: 76%; min-height: 190px; padding: 34px 30px; border-radius: 20px; background: var(--ink); color: #fff; font-size: 48px; font-weight: 900; line-height: 1.3; text-align: center; }
.bill-illust { height: 296px; }

/* Slide 8: checklist */
.check-slide .slide-body { gap: 34px; }
.checklist { display: flex; flex-direction: column; gap: 28px; width: 100%; }
.check-row { display: grid; grid-template-columns: 98px 1fr; align-items: center; min-height: 154px; padding: 26px 34px; border: 5px solid #c8d9f4; border-radius: 20px; background: #f5f9ff; }
.check-num { display: grid; place-items: center; width: 72px; height: 72px; border-radius: 50%; background: var(--blue); color: #fff; font-size: 38px; font-weight: 900; }
.check-text { font-size: 51px; font-weight: 900; }
.mypage-tip { display: grid; place-items: center; width: 70%; min-height: 118px; padding: 20px 28px; border-radius: 18px; background: var(--yellow); color: #563f00; font-size: 40px; font-weight: 900; line-height: 1.2; text-align: center; }
.check-illust { height: 265px; }

/* Slide 9: warning/action */
.warning-slide { padding: 0 70px 58px; background: #fff8f8; }
.warning-banner { margin: 0 -70px 22px; padding: 22px 0; background: var(--red); color: #fff; font-size: 62px; font-weight: 900; text-align: center; }
.warning-title { margin: 0 0 24px; color: var(--red-deep); font-size: 58px; font-weight: 900; line-height: 1.15; text-align: center; }
.warning-box { display: flex; flex-direction: column; gap: 22px; width: 100%; padding: 32px 38px; border: 10px solid var(--red); border-radius: 22px; background: var(--red-soft); }
.usage-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 22px; }
.usage-card { display: grid; place-items: center; min-height: 190px; padding: 24px; border-radius: 18px; background: #fff; color: var(--ink); font-size: 42px; font-weight: 900; text-align: center; }
.usage-card b { display: block; color: var(--red); font-size: 56px; }
.action-strip { padding: 20px 26px; border-radius: 16px; background: var(--ink); color: #fff; font-size: 39px; font-weight: 900; text-align: center; }
.warning-callout { width: 68%; margin-top: 18px; padding: 20px 24px; border-radius: 16px; background: var(--red); color: #fff; font-size: 42px; font-weight: 900; text-align: center; }
.warning-illust { right: 24px; bottom: 70px; height: 270px; }

/* Slide 10: CTA */
.cta-slide { padding: 22px 60px 14px; background: linear-gradient(135deg, var(--blue), var(--blue-deep)); }
.cta-content { display: flex; flex-direction: column; align-items: center; height: 100%; text-align: center; }
.cta-logo-card { display: flex; align-items: center; gap: 14px; height: 92px; margin-bottom: 5px; padding: 8px 24px; border-radius: 18px; background: #fff; box-shadow: 4px 4px 0 rgba(0,0,0,.18); color: var(--blue); font-size: 32px; font-weight: 900; }
.cta-logo-mark { display: grid; place-items: center; width: 58px; height: 58px; border-radius: 16px; background: var(--blue); color: #fff; font-size: 38px; }
.cta-title { margin: 0 0 7px; color: #ffd700; font-size: 72px; font-weight: 900; line-height: 1.05; }
.cta-sub { display: flex; flex-direction: column; gap: 5px; width: 920px; margin-bottom: 9px; color: #fff; font-size: 27px; font-weight: 900; }
.cta-sub span { padding: 5px 14px; border: 3px solid rgba(255,255,255,.55); border-radius: 12px; background: rgba(255,255,255,.1); white-space: nowrap; }
.cta-banner-img { width: 850px; max-height: 480px; border: 7px solid #fff; border-radius: 18px; box-shadow: 0 18px 42px rgba(0,0,0,.4); object-fit: contain; filter: none; }
.cta-arrow { margin-top: 7px; color: #ffd700; font-size: 68px; font-weight: 900; line-height: .82; animation: bounce 1s infinite; }
@keyframes bounce { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(8px); } }
"""


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def parts(row: dict[str, str]) -> list[str]:
    return [part.strip() for part in row["スライドに表示する内容"].split("／") if part.strip()]


def after_label(value: str) -> str:
    return value.split("：", 1)[1].strip() if "：" in value else value.strip()


def fee_heading_html(heading: str) -> str:
    """Keep the established term 通常料金 intact while splitting long fee labels."""
    suffix = "通常料金"
    if heading.endswith(suffix) and heading != suffix:
        prefix = heading[: -len(suffix)]
        return (
            f'<span class="semantic-line">{esc(prefix)}</span>'
            f'<span class="semantic-line">{esc(suffix)}</span>'
        )
    return f'<span class="semantic-line">{esc(heading)}</span>'


def diagnosis_prompt_html(prompt: str) -> str:
    """Keep the action phrase together when the diagnostic question wraps."""
    return esc(prompt).replace(
        "無料期間つきオプションを付けたまま？",
        "無料期間つきオプションを<br />付けたまま？",
    )


def asset(relative_path: str) -> str:
    absolute_path = IMAGE_ROOT / relative_path
    if not absolute_path.is_file():
        raise FileNotFoundError(f"Required asset is missing: {absolute_path}")
    return f"public/images/{relative_path}"


def source_comment(row: dict[str, str]) -> str:
    return f"<!-- CSV表示内容: {esc(row['スライドに表示する内容'])} -->"


def wrap_slide(row: dict[str, str], classes: str, inner: str) -> str:
    slide_id = esc(row["スライドID"])
    return (
        f"<!-- スライドID: {slide_id} -->\n"
        f"{source_comment(row)}\n"
        f'<div class="slide-container {classes}" data-slide-id="{slide_id}">\n{inner}\n</div>'
    )


def render_1(row: dict[str, str]) -> str:
    display = parts(row)
    question = after_label(display[0])
    question_lines = question.replace("、無料期間が", "<br />無料期間が").replace("終わったら", "<span class=\"impact-line\">終わったら") + "</span>"
    transition = display[1].replace("を大きく表示", "")
    return wrap_slide(
        row,
        "slide-thumbnail",
        f"""  <div class="thumb-top-strip">⚡ 放置すると自動課金かも ⚡</div>
  <i class="thumb-accent-tri tl"></i><i class="thumb-accent-tri br"></i>
  <div class="thumb-content">
    <div class="thumb-tag">放置は損！</div>
    <h1 class="thumb-title">{question_lines}</h1>
    <div class="switch-band" aria-label="{esc(transition)}"><span class="switch-pill">無料</span><span class="switch-arrow">→</span><span class="switch-pill paid">有料</span></div>
  </div>
  <div class="thumb-sticker">無料期間の「終了後」を確認</div>
  <div class="slide-illust thumb-illust"><img src="{asset('irasutoya/seikyuusyo_shock.png')}" alt="請求額に驚く人" /></div>""",
    )


def render_2(row: dict[str, str]) -> str:
    display = parts(row)
    prompt = after_label(display[0])
    prompt_html = diagnosis_prompt_html(prompt)
    choices = display[1].split("・")
    return wrap_slide(
        row,
        "diagnosis-slide",
        f"""  <div class="watermark">2</div>
  <h2 class="slide-title">まずは<em>30秒診断</em></h2>
  <div class="slide-body" style="margin-bottom: 120px;">
    <div class="diagnosis-panel"><div class="diagnosis-label">CHECK</div><div class="diagnosis-question">{prompt_html}</div></div>
    <div class="choice-row"><div class="choice-card">✓ {esc(choices[0])}</div><div class="choice-card unknown">？ {esc(choices[1])}</div></div>
    <div class="auto-note">無料期間が終わると<br />自動で通常料金に切り替わるものも</div>
  </div>
  <div class="slide-illust diagnosis-illust"><img src="{asset('irasutoya/pose_atama_kakaeru_woman.png')}" alt="契約内容がわからず困る人" /></div>""",
    )


def render_3(row: dict[str, str]) -> str:
    description = parts(row)[0]
    return wrap_slide(
        row,
        "checkbox-slide",
        f"""  <div class="watermark">3</div>
  <h2 class="slide-title">申込時の<em>チェック欄</em></h2>
  <div class="slide-body" style="margin-bottom: 120px;">
    <div class="phone-mock" aria-label="{esc(description)}">
      <div class="phone-head">お申し込み内容の確認</div>
      <div class="option-row"><span class="check-box">✓</span><div class="option-copy"><strong>無料オプション</strong><span>無料期間つき・申込時に追加</span></div></div>
      <div class="trial-summary"><span>無料期間中<br /><strong>0円</strong></span><span class="trial-summary-arrow">→</span><span>終了後は<br /><strong>通常料金</strong></span></div>
    </div>
    <div class="notice-strip">「無料だから」で付けたままかも？</div>
  </div>
  <div class="slide-illust checkbox-illust"><img src="{asset('irasutoya/smartphone_blank_tenin_woman.png')}" alt="スマホの申込画面を案内する人" /></div>""",
    )


def render_4(row: dict[str, str]) -> str:
    display = parts(row)
    heading, amount = display[0].split("：", 1)
    billing = display[1]
    heading_html = fee_heading_html(heading)
    return wrap_slide(
        row,
        "fee-slide price-note",
        f"""  <div class="watermark">4</div>
  <h2 class="slide-title">通話系は<em>毎月課金</em></h2>
  <div class="slide-body" style="margin-bottom: 120px;">
    <div class="fee-hero"><div class="fee-kind" aria-label="{esc(heading)}">{heading_html}</div><div class="fee-amount">{esc(amount)}<small>無料期間の終了後</small></div></div>
    <div class="charge-flow"><div class="flow-card">🎁 無料期間<br />終了</div><div class="flow-arrow">→</div><div class="flow-card danger">💳 {esc(billing)}</div></div>
    <div class="recurring-warning">⚠ 自分で外さない限り<br />毎月ずっとかかる</div>
  </div>
  <div class="slide-illust fee-illust"><img src="{asset('irasutoya/smartphone_talk03_man.png')}" alt="通話オプションを使う人" /></div>""",
    )


def render_5(row: dict[str, str]) -> str:
    description = parts(row)[0]
    return wrap_slide(
        row,
        "leak-slide price-note",
        f"""  <div class="watermark">5</div>
  <h2 class="slide-title">使ってないのに<em>毎月500円</em></h2>
  <div class="slide-body" style="margin-bottom: 120px;">
    <div class="leak-panel" aria-label="{esc(description)}">
      <div class="leak-side"><span>通話オプション</span><strong>未使用</strong></div><div class="leak-arrow">→</div><div class="leak-side"><span>毎月の請求</span><strong>−500円</strong></div>
    </div>
    <div class="waste-callout"><span class="semantic-line">使っていなければ</span><span class="semantic-line">その500円、もったいない！</span></div>
  </div>
  <div class="slide-illust leak-illust"><img src="{asset('irasutoya/money_fueru.png')}" alt="毎月出ていくお金" /></div>""",
    )


def render_6(row: dict[str, str]) -> str:
    display = parts(row)
    heading, amount = display[0].split("：", 1)
    transition = display[1]
    heading_html = fee_heading_html(heading)
    return wrap_slide(
        row,
        "data-slide price-note",
        f"""  <div class="watermark">6</div>
  <h2 class="slide-title">データ増量は<em>月1,980円</em>も</h2>
  <div class="slide-body" style="margin-bottom: 120px;">
    <div class="fee-hero data-fee"><div class="fee-kind" aria-label="{esc(heading)}">{heading_html}</div><div class="fee-amount">{esc(amount)}<small>通常料金</small></div></div>
    <div class="billing-timeline" aria-label="{esc(transition)}"><div class="timeline-step">無料期間<br />終了</div><div class="timeline-arrow">→</div><div class="timeline-step">翌月</div><div class="timeline-arrow">→</div><div class="timeline-step danger">請求<br />＋1,980円</div></div>
    <div class="next-month-warning">⚠ 無料期間が終わった翌月から<br />請求が増える場合も</div>
  </div>
  <div class="slide-illust data-illust"><img src="{asset('irasutoya/osatsu_money_yamadumi.png')}" alt="増えていく請求額" /></div>""",
    )


def render_7(row: dict[str, str]) -> str:
    description = parts(row)[0]
    return wrap_slide(
        row,
        "bill-slide price-note",
        f"""  <div class="watermark">7</div>
  <h2 class="slide-title">スマホ代急増の<em>犯人？</em></h2>
  <div class="slide-body" style="margin-bottom: 120px;">
    <div class="bill-sheet" aria-label="{esc(description)}"><div class="bill-head"><span>今月のご請求</span><span>明細</span></div><div class="bill-row"><span>基本料金・通信料</span><span>••••円</span></div><div class="bill-row plus"><span>データ増量</span><strong>＋1,980円</strong></div></div>
    <div class="bill-result">「急に高い！」は<br />無料期間終了が原因かも</div>
  </div>
  <div class="slide-illust bill-illust"><img src="{asset('irasutoya/seikyuusyo_shock.png')}" alt="請求画面を見て驚く人" /></div>""",
    )


def render_8(row: dict[str, str]) -> str:
    display = parts(row)
    label, first_item = display[0].split("：", 1)
    items = [first_item, *display[1:]]
    rows_html = "\n".join(
        f'      <div class="check-row"><span class="check-num">{index}</span><span class="check-text">{esc(item)}</span></div>'
        for index, item in enumerate(items, 1)
    )
    return wrap_slide(
        row,
        "check-slide",
        f"""  <div class="watermark">8</div>
  <h2 class="slide-title">{esc(label)}<em>3項目</em></h2>
  <div class="slide-body" style="margin-bottom: 120px;">
    <div class="checklist">
{rows_html}
    </div>
    <div class="mypage-tip">📱 マイページの<br />「契約中オプション」へ</div>
  </div>
  <div class="slide-illust check-illust"><img src="{asset('irasutoya/pose_yubisashi_kakunin_businesswoman.png')}" alt="確認項目を指差す人" /></div>""",
    )


def render_9(row: dict[str, str]) -> str:
    description = parts(row)[0]
    return wrap_slide(
        row,
        "warning-slide",
        f"""  <div class="warning-banner">⚠ 使っているか確認</div>
  <h2 class="warning-title">続ける前に<em>利用実績</em>を見る</h2>
  <div class="warning-box" aria-label="{esc(description)}">
    <div class="usage-grid"><div class="usage-card">📞<b>通話回数</b>本当に使った？</div><div class="usage-card">📶<b>データ使用量</b>増量が必要？</div></div>
    <div class="action-strip">スマホでマイページを開く</div>
  </div>
  <div class="warning-callout">今日のうちに確認！</div>
  <div class="slide-illust warning-illust"><img src="{asset('irasutoya/pose_necchuu_smartphone_woman.png')}" alt="スマホでマイページを確認する人" /></div>""",
    )


def render_10(row: dict[str, str]) -> str:
    display = parts(row)
    title, first_item = display[0].split("：", 1)
    items = [first_item, *display[1:]]
    items_html = "".join(f"<span>{esc(index)} {esc(item)}</span>" for index, item in zip(("①", "②", "③"), items, strict=True))
    thumbnail = asset(
        "thumbnails/42_【放置は損】その「無料オプション」終わると毎月いくら？"
        "月500円〜1,980円の自動課金_サムネ1.png"
    )
    return wrap_slide(
        row,
        "cta-slide",
        f"""  <div class="cta-content">
    <div class="cta-logo-card"><span class="cta-logo-mark">✓</span><span>スマホ料金チェック</span></div>
    <h2 class="cta-title">{esc(title)}</h2>
    <div class="cta-sub">{items_html}</div>
    <img class="cta-banner-img" src="{thumbnail}" alt="無料オプション終了後の料金を解説する本編動画" />
    <div class="cta-arrow">↓</div>
  </div>""",
    )


RENDERERS = {
    "1": render_1,
    "2": render_2,
    "3": render_3,
    "4": render_4,
    "5": render_5,
    "6": render_6,
    "7": render_7,
    "8": render_8,
    "9": render_9,
    "10": render_10,
}


def read_rows() -> list[dict[str, str]]:
    with SOURCE_CSV.open("r", encoding="utf-8-sig", newline="") as csv_file:
        rows = list(csv.DictReader(csv_file))
    if not rows:
        raise ValueError(f"No rows found in {SOURCE_CSV}")
    slide_ids = [row["スライドID"].strip() for row in rows]
    if len(slide_ids) != len(set(slide_ids)):
        raise ValueError(f"Slide IDs must be unique for a short deck: {slide_ids}")
    if any(slide_id.endswith("-0") for slide_id in slide_ids):
        raise ValueError(f"N-0 price spreads are not supported in short decks: {slide_ids}")
    if set(slide_ids) != set(RENDERERS):
        raise ValueError(f"Renderer/CSV ID mismatch: CSV={slide_ids}, renderers={list(RENDERERS)}")
    return rows


def build_html(rows: list[dict[str, str]]) -> str:
    slides = "\n\n".join(RENDERERS[row["スライドID"]](row) for row in rows)
    return f"""<!doctype html>
<html lang="ja">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>無料オプション終了後の自動課金 - Shorts Slides</title>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@700;900&amp;family=Noto+Sans+JP:wght@700;900&amp;display=swap" rel="stylesheet" />
    <style>
{CSS}
    </style>
  </head>
  <body>
{slides}
  </body>
</html>
"""


def main() -> None:
    if WORK_DIR != OUTPUT_HTML.parent:
        raise ValueError(f"Output must stay in the slide-gen work directory: {OUTPUT_HTML}")
    rows = read_rows()
    document = build_html(rows)
    OUTPUT_HTML.write_text(document, encoding="utf-8")
    print(f"Generated {len(rows)} slides: {OUTPUT_HTML}")


if __name__ == "__main__":
    main()
