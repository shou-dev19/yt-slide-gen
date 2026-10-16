#!/usr/bin/env python3
"""Generate the 1:1 short deck from the script CSV's display-content column."""

from __future__ import annotations

import csv
import html
import re
from collections import OrderedDict
from pathlib import Path


ROOT = Path("/workspaces/yt-factory/packages/slide-gen")
SCRIPT = Path("/workspaces/yt-factory/packages/scenario-gen/archive/videos/29_格安SIM診断チャート/short/格安SIM15種を最短3問で診断.csv")
OUTPUT = ROOT / "slides-short.html"
CTA_FALLBACK = "public/images/slides/今すぐ本編動画をチェック.png"
LONG_THUMBNAIL = "public/images/thumbnails/29_格安SIM診断チャート_サムネ1.png"


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def first_per_slide(rows: list[dict[str, str]]) -> OrderedDict[str, str]:
    contents: OrderedDict[str, str] = OrderedDict()
    for row in rows:
        slide_id = row["スライドID"].strip()
        content = row["スライドに表示する内容"].strip()
        if slide_id not in contents and content != "同上":
            contents[slide_id] = content
        elif slide_id not in contents:
            contents[slide_id] = content
    return contents


def card(text: str, kind: str = "info-card") -> str:
    return f'<div class="{kind}">{esc(text)}</div>'


def split_options(text: str) -> list[str]:
    """Split script alternatives on either supported Japanese separator."""
    return [part.strip() for part in re.split(r"[／｜]", text) if part.strip()]


def render_slide(slide_id: str, content: str, index: int, total: int, thumbnail: str) -> str:
    content = content.strip()
    if index == 1:
        title = content.partition("：")[2].split("／", 1)[0] if "：" in content else "格安SIM15種診断"
        return f'''<!-- Slide ID: {esc(slide_id)} -->
<div class="slide-container slide-thumbnail">
  <div class="thumb-top-strip">⚡ 格安SIM選び 15種診断 ⚡</div>
  <div class="thumb-tag">最短3問！</div>
  <h1 class="thumb-title">{esc(title)}</h1>
  <div class="thumb-sub-band">あなたに合う1枚が見つかる</div>
  <div class="thumb-flow" aria-label="診断チャート">
    <span>START</span><b>→</b><span>Q1</span><b>→</b><span>Q2</span><b>→</b><span>Q3</span><b>→</b><span>あなたの1枚</span>
  </div>
</div>'''

    if index == total:
        title, _, subtitle = content.partition("／")
        title = title.removeprefix("本編：")
        title_html = esc(title).replace("！最短", "！<br>最短")
        return f'''<!-- Slide ID: {esc(slide_id)} -->
<div class="slide-container cta-slide">
  <div class="cta-content">
    <div class="cta-kicker">続きの診断は本編で</div>
    <h2 class="cta-title">{title_html}</h2>
    <p class="cta-sub">診断チャートを一緒に進めよう</p>
    <img class="cta-banner-img" src="{esc(thumbnail)}" alt="本編動画のサムネイル">
    <div class="cta-arrow">本編をチェック <span>⬇</span></div>
  </div>
</div>'''

    title = content.partition("／")[0]
    title = re.sub(r"^(?:タイトル|テロップ)：", "", title)
    body: str
    if index == 2 and content.startswith("テロップ：") and "START→Q1" in content:
        title = "最短3問で15種から診断"
        body = f'''<div class="path-panel"><div class="path-count">15<span>種</span></div>
          <div class="path-step">START <b>→</b> Q1</div><p>質問に答えて診断</p></div>'''
    elif index == 3 and "早い人は" in content:
        title = "質問数はルートで変わる"
        body = '''<div class="two-counts"><div class="count-card"><strong>3</strong><span>問で決まる</span><b>早いルート</b></div>
          <div class="count-card red"><strong>6</strong><span>問でもOK</span><b>長いルート</b></div></div>'''
    elif content.startswith("Q1"):
        question, _, branches = content.partition("／")
        yesno = split_options(branches)
        title = "診断 Q1"
        question_html = esc(question.removeprefix("Q1 ")).replace("店舗での対面サポートは必要？", "店舗での<br>対面サポートは必要？")
        left = esc(yesno[0] if yesno else "はい→店舗派")
        right = esc(yesno[1] if len(yesno) > 1 else "いいえ→オンライン派").replace("→オンライン派", "→<br>オンライン派")
        body = f'''<div class="question-card"><span class="q-badge">Q1</span><h3>{question_html}</h3></div>
          <div class="choice-grid">{card(left, "choice blue")}<b>OR</b><div class="choice red">{right}</div></div>'''
    elif content.startswith("Q5 "):
        question, _, choices = content.partition("／")
        options = split_options(choices)
        title = "診断 Q5"
        question_html = esc(question.removeprefix("Q5 ")).replace("、どっちを優先？", "、<br>どっちを優先？")
        body = f'''<div class="question-card"><span class="q-badge">Q5</span><h3>{question_html}</h3></div>
          <div class="choice-grid">{card(options[0] if options else "通信品質", "choice blue")}<b>OR</b>{card(options[1] if len(options)>1 else "コスパ", "choice red")}</div>'''
    elif "通信品質派｜コスパ派" in content:
        title = "Q5で分かれ道"
        labels = split_options(content.partition("／")[2])
        left_label, right_label = (labels + ["通信品質派", "コスパ派"])[:2]
        body = f'''<div class="route-diagram">
          <div class="route-start">オンライン派</div>
          <div class="route-down" aria-hidden="true">↓</div>
          <div class="route-question">Q5</div>
          <svg class="route-branches" viewBox="0 0 800 150" role="img" aria-label="Q5から通信品質派とコスパ派に分岐">
            <path d="M400 0 V55 H190 V145 M400 55 H610 V145" fill="none" stroke="#78849a" stroke-width="12" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M190 125 L165 100 M190 125 L215 100 M610 125 L585 100 M610 125 L635 100" fill="none" stroke="#78849a" stroke-width="12" stroke-linecap="round"/>
          </svg>
          <div class="route-outcomes">
            <div class="route-outcome blue">{esc(left_label)}</div>
            <div class="route-outcome red">{esc(right_label)}</div>
          </div>
          <p class="route-note">同じオンライン派でも、進む先が変わる</p>
        </div>'''
    elif "店舗派は5社" in content:
        title = "店舗派も複数に分岐"
        body = '''<div class="split-panel"><div class="split-side"><span class="split-number">5</span><strong>店舗派</strong><p>候補の会社に分岐</p></div>
          <div class="split-divider" aria-hidden="true"></div><div class="split-side online"><span class="split-number">?</span><strong>オンライン派</strong><p>さらに質問が続く</p></div></div>'''
    else:
        parts = [p.strip() for p in content.split("／") if p.strip()]
        body = "".join(card(p) for p in parts)

    return f'''<!-- Slide ID: {esc(slide_id)} -->
<div class="slide-container">
  <div class="watermark">{esc(slide_id)}</div>
  <div class="slide-content">
    <h2 class="slide-title">{esc(title)}</h2>
    <div class="slide-body">{body}</div>
  </div>
</div>'''


def main() -> None:
    with SCRIPT.open(encoding="utf-8-sig", newline="") as source:
        rows = list(csv.DictReader(source))
    slides = first_per_slide(rows)
    if not slides:
        raise SystemExit("No slides found in the CSV")
    thumbnail = LONG_THUMBNAIL if (ROOT / LONG_THUMBNAIL).is_file() else CTA_FALLBACK

    slide_html = "\n".join(
        render_slide(slide_id, content, index, len(slides), thumbnail)
        for index, (slide_id, content) in enumerate(slides.items(), start=1)
    )
    document = f'''<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>格安SIM15種診断｜最短3問</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@700;900&family=Noto+Sans+JP:wght@700;900&display=swap" rel="stylesheet">
<style>
:root{{--blue:#0052cc;--blue-dark:#003380;--red:#e63946;--ink:#172033;--pale:#eaf3ff}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{display:flex;flex-direction:column;align-items:center;gap:40px;padding:40px;background:#f0f4f8;color:var(--ink);font-family:Inter,'Noto Sans JP',sans-serif}}
.slide-container{{position:relative;overflow:hidden;display:flex;width:1080px;height:1080px;flex:none;background:#fff}}
.slide-thumbnail{{align-items:center;justify-content:center;flex-direction:column;text-align:center;border:25px solid var(--blue);padding:160px 42px 210px;background:repeating-conic-gradient(from 0deg at 52% 48%,rgba(0,82,204,.06) 0deg 2.5deg,transparent 2.5deg 16deg),radial-gradient(ellipse at 52% 48%,#fff 5%,#e8f3ff 45%,#c8dcff 100%)}}
.thumb-top-strip{{position:absolute;top:25px;left:25px;right:25px;background:var(--blue);color:#fff;font-size:36px;font-weight:900;padding:18px 0;letter-spacing:.06em;z-index:3}}
.thumb-tag{{font-size:80px;font-weight:900;color:#fff;background:var(--red);padding:18px 54px;transform:rotate(-3deg);box-shadow:8px 8px 0 #0004;margin-bottom:28px}}
.thumb-title{{font-size:80px;line-height:1.25;font-weight:900;margin-bottom:22px;max-width:900px}}
.thumb-sub-band{{font-size:54px;font-weight:900;color:#fff;background:var(--blue);padding:18px 48px;border-radius:12px;box-shadow:4px 4px 0 #0003}}
.thumb-flow{{display:flex;align-items:center;gap:12px;white-space:nowrap;margin-top:35px;font-size:33px;font-weight:900;color:var(--blue-dark)}}
.thumb-flow span{{padding:10px 16px;border:4px solid var(--blue);border-radius:16px;background:#fff}}.thumb-flow b{{color:var(--red);font-size:38px}}
.slide-content{{position:relative;z-index:1;display:flex;flex:1;min-height:0;flex-direction:column;padding:75px 70px}}
.watermark{{position:absolute;top:-38px;left:10px;color:var(--blue);opacity:.07;font-size:280px;line-height:1;font-weight:900}}
.slide-title{{position:relative;font-size:62px;line-height:1.2;font-weight:900;border-bottom:10px solid var(--blue);padding-bottom:15px;margin-bottom:30px}}
.slide-body{{position:relative;z-index:1;display:flex;flex:1;min-height:0;flex-direction:column;justify-content:space-evenly;gap:22px}}
.info-card{{padding:26px 32px;border-left:14px solid var(--blue);border-radius:0 18px 18px 0;background:#f0f5ff;font-size:48px;line-height:1.25;font-weight:900}}
.path-panel{{display:flex;flex:1;flex-direction:column;align-items:center;justify-content:center;gap:22px;border:8px solid var(--blue);border-radius:28px;background:linear-gradient(145deg,#eaf3ff,#fff);text-align:center;padding:32px}}
.path-count{{color:var(--red);font-size:180px;font-weight:900;line-height:1}}.path-count span{{font-size:82px}}.path-step{{font-size:64px;font-weight:900;color:var(--blue-dark)}}.path-step b{{color:var(--red);padding:0 18px}}.path-panel p{{font-size:40px;font-weight:900}}
.two-counts{{display:grid;grid-template-columns:1fr 1fr;gap:25px;flex:1;align-items:stretch}}
.count-card{{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:14px;border:8px solid var(--blue);border-radius:25px;background:var(--pale);text-align:center;padding:20px}}
.count-card.red{{border-color:var(--red);background:#fff0f0}}.count-card strong{{font-size:210px;line-height:1;color:var(--blue)}}.count-card.red strong{{color:var(--red)}}.count-card span{{font-size:44px;font-weight:900}}.count-card b{{font-size:36px}}
.question-card{{display:flex;align-items:center;gap:24px;padding:28px;border-radius:22px;background:#eaf3ff;border:5px solid var(--blue)}}.q-badge{{flex:none;width:120px;height:120px;display:grid;place-items:center;border-radius:50%;background:var(--blue);color:#fff;font-size:50px;font-weight:900}}.question-card h3{{font-size:52px;line-height:1.25;font-weight:900}}
.choice-grid{{display:grid;grid-template-columns:1fr auto 1fr;align-items:center;gap:18px;flex:1}}.choice{{display:grid;place-items:center;height:300px;padding:22px;text-align:center;border:8px solid;border-radius:25px;font-size:44px;font-weight:900;line-height:1.3}}.choice.blue{{color:var(--blue);border-color:var(--blue);background:#eaf3ff}}.choice.red{{color:var(--red);border-color:var(--red);background:#fff0f0}}.choice-grid> b{{font-size:38px;color:#78849a}}
.route-diagram{{display:flex;flex:1;min-height:0;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:4px 16px}}.route-start,.route-question{{display:grid;place-items:center;min-width:340px;padding:18px 38px;border:7px solid var(--blue);border-radius:24px;background:#eaf3ff;color:var(--blue-dark);font-size:46px;font-weight:900}}.route-down{{height:54px;color:var(--red);font-size:54px;line-height:1;font-weight:900}}.route-question{{min-width:200px;border-color:var(--red);background:#fff0f0;color:var(--red);font-size:52px}}.route-branches{{width:100%;height:150px;flex:none;overflow:visible}}.route-outcomes{{display:grid;width:100%;grid-template-columns:1fr 1fr;gap:60px;margin-top:-8px}}.route-outcome{{display:grid;min-height:160px;place-items:center;border:8px solid var(--blue);border-radius:25px;background:#eaf3ff;color:var(--blue);font-size:48px;font-weight:900}}.route-outcome.red{{border-color:var(--red);background:#fff0f0;color:var(--red)}}.route-note{{margin-top:28px;color:var(--blue-dark);font-size:36px;font-weight:900}}.split-panel{{display:grid;grid-template-columns:1fr auto 1fr;align-items:center;gap:18px;flex:1;border:8px solid var(--blue);border-radius:28px;background:linear-gradient(145deg,#f7faff,#fff);padding:24px}}.split-side{{display:flex;flex-direction:column;align-items:center;gap:15px;text-align:center}}.split-number{{font-size:190px;line-height:1;color:var(--blue);font-weight:900}}.split-side.online .split-number{{color:var(--red)}}.split-side strong{{font-size:47px;font-weight:900}}.split-side p{{font-size:33px;font-weight:900;color:#526078}}.split-divider{{width:5px;height:300px;border-radius:999px;background:#9aa6b7}}
.cta-slide{{align-items:center;justify-content:center;background:linear-gradient(135deg,#0052cc,#003380);padding:48px;color:#fff;text-align:center}}.cta-content{{display:flex;align-items:center;justify-content:space-evenly;flex-direction:column;width:100%;height:100%;gap:14px}}.cta-kicker{{font-size:44px;font-weight:900;color:#fff}}.cta-title{{font-size:52px;white-space:nowrap;line-height:1.25;color:#ffd700;font-weight:900}}.cta-sub{{font-size:40px;line-height:1.3;font-weight:900}}.cta-banner-img{{width:820px;max-height:460px;object-fit:contain;background:#fff;border:8px solid #fff;border-radius:20px;filter:drop-shadow(0 10px 20px #0004)}}.cta-arrow{{font-size:48px;font-weight:900;color:#ffd700}}.cta-arrow span{{display:block;font-size:75px;line-height:.9;animation:bounce 1.1s infinite}}@keyframes bounce{{50%{{transform:translateY(12px)}}}}
</style></head><body>
{slide_html}
</body></html>'''
    OUTPUT.write_text(document, encoding="utf-8")
    print(f"Generated {len(slides)} slides: {OUTPUT}")
    print(f"Slide IDs: {', '.join(slides)}")
    print(f"CTA thumbnail: {thumbnail}")


if __name__ == "__main__":
    main()
