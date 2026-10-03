#!/usr/bin/env python3
"""Generate the six mineo short slides from the script's slide IDs and copy."""

from __future__ import annotations

import csv
from html import escape
from pathlib import Path


ROOT = Path('/workspaces/yt-factory/packages/slide-gen')
CSV_PATH = Path('/workspaces/yt-factory/packages/scenario-gen/archive/videos/48_【2026年決定版】mineoのプラン選びは3択でいい。歴8年が教える実質使い放題の選び方/short/mineoならデータ使い放題が無料って本当?.csv')
OUTPUT = ROOT / 'slides-short.html'
IMAGES = ROOT / 'public/images'

ASSETS = {
    'logo': 'logo/Mineo_logo.png',
    'switch': 'temp/mineo/mineoスイッチ_切り出し.png',
    'thumbnail': 'thumbnails/48_【決定版】mineoのプラン選びは3択でいい。歴8年が教える実質使い放題の選び方_サムネ1.png',
    'cover': 'irasutoya/pose_yubisashi_kakunin_businesswoman.png',
    'diagnosis': 'irasutoya/businessman2_kangaechu.png',
    'benefit': 'irasutoya/sns_happy_woman.png',
    'price': 'irasutoya/pose_necchuu_smartphone_woman.png',
    'switch_illust': 'irasutoya/pose_anshin_woman.png',
}


def image(name: str, class_name: str, alt: str) -> str:
    asset = ASSETS[name]
    if not (IMAGES / asset).is_file():
        raise FileNotFoundError(IMAGES / asset)
    return f'<img class="{class_name}" src="public/images/{escape(asset, quote=True)}" alt="{escape(alt, quote=True)}">'


def parse_slides() -> list[tuple[str, str, str]]:
    slides: dict[str, str] = {}
    with CSV_PATH.open(encoding='utf-8-sig', newline='') as handle:
        for row in csv.DictReader(handle):
            slide_id = row['スライドID'].strip()
            content = row['スライドに表示する内容'].strip()
            if not slide_id:
                raise ValueError('空のスライドIDがあります')
            if content == '同上':
                if slide_id not in slides:
                    raise ValueError(f'{slide_id}: 「同上」の参照先がありません')
                continue
            if slide_id in slides and slides[slide_id] != content:
                raise ValueError(f'{slide_id}: 1つのIDに異なる表示内容があります')
            slides[slide_id] = content
    parsed = []
    for slide_id, content in slides.items():
        content = content.removeprefix('テロップ：')
        title, separator, detail = content.partition('／')
        if not separator:
            if '3Mbps' in content:
                title, detail = content.split('3Mbps', 1)
                detail = '3Mbps' + detail
            elif 'の選び方は本編で' in content:
                title, detail = content.split('の選び方は本編で', 1)
                title += 'の選び方'
                detail = '本編で' + detail
            else:
                raise ValueError(f'{slide_id}: 見出しと本文を「／」で区切ってください')
        parsed.append((slide_id, title.strip(), detail.strip()))
    return parsed


def standard_slide(slide_id: str, title: str, body: str, illustration: str, kind: str, price_note: bool = False) -> str:
    classes = 'slide-container slide-pad' + (' price-note' if price_note else '')
    return f'''<!-- Slide ID: {escape(slide_id)} -->
<div class="{classes} {kind}" data-slide-id="{escape(slide_id, quote=True)}">
  <div class="watermark">{escape(slide_id)}</div>
  <h2 class="slide-title">{escape(title)}</h2>
  <div class="slide-body">{body}</div>
  <div class="slide-illust" style="z-index: 2;">{image(illustration, 'illust-img', 'スライド内容のイラスト')}</div>
</div>'''


def render_slide(slide_id: str, title: str, detail: str, position: int, count: int) -> str:
    if position == 1:
        first, arrow, second = detail.partition('→')
        if not arrow:
            raise ValueError(f'{slide_id}: 表紙の選択肢に「→」が必要です')
        return f'''<!-- Slide ID: {escape(slide_id)} -->
<div class="slide-container slide-thumbnail" data-slide-id="{escape(slide_id, quote=True)}">
  <div class="thumb-top-strip">⚡ mineo プラン選び ⚡</div>
  <div class="thumb-accent-tri tl"></div><div class="thumb-accent-tri br"></div>
  <div class="thumb-tag">迷う人へ</div>
  <h1 class="thumb-title">{escape(title)}</h1>
  <div class="thumb-sub-band"><span>{escape(first)}</span><b>→</b><strong>{escape(second)}</strong></div>
  <div class="thumb-logo-wrap">{image('logo', 'thumb-logo', 'mineo ロゴ')}</div>
  <div class="thumb-illust">{image('cover', 'cover-illust-img', '案内する人物')}</div>
</div>'''

    if position == count:
        # The short directs viewers to the corresponding long video thumbnail.
        return f'''<!-- Slide ID: {escape(slide_id)} -->
<div class="slide-container cta-slide" data-slide-id="{escape(slide_id, quote=True)}">
  <div class="cta-content">
    {image('logo', 'cta-logo', 'mineo ロゴ')}
    <h2 class="cta-title">{escape(title)}</h2>
    <div class="cta-sub">続きは本編で詳しく解説</div>
    {image('thumbnail', 'cta-banner-img', 'mineo の本編動画サムネイル')}
    <div class="cta-arrow">▼</div>
  </div>
</div>'''

    if '診断' in title:
        question = detail.removesuffix('?').removesuffix('？')
        body = f'<div class="question-card"><div class="question-icon">？</div><div class="question-text">{escape(question)}<span class="red">？</span></div></div><div class="diagnosis-hint">使い方でコースを絞る</div>'
        return standard_slide(slide_id, title, body, 'diagnosis', 'diagnosis')

    if '3GB' in title:
        condition, separator, benefit = detail.partition('なら')
        if not separator or '1Mbps' not in benefit:
            raise ValueError(f'{slide_id}: 3GB スライドの条件か速度を読み取れません')
        body = f'''<div class="condition-card">{escape(condition)}なら</div>
<div class="benefit-card"><div class="benefit-main"><strong>1Mbps</strong><span>が無料</span></div><div class="benefit-unlimited">使い放題</div></div>
<div class="benefit-usage"><strong>日常利用に十分！</strong><div class="usage-tags"><span>💬 LINE</span><span>🎵 音楽</span></div></div>'''
        return standard_slide(slide_id, title, body, 'benefit', 'benefit')

    if '385円' in detail:
        speed, _, price = detail.partition('（')
        price = price.rstrip('）')
        body = f'<div class="speed-card"><strong>{escape(speed)}</strong><span>SNSの動画も楽しめる</span></div><div class="price-card"><span>アップグレード</span><strong>{escape(price)}</strong></div>'
        return standard_slide(slide_id, title, body, 'price', 'price', price_note=True)

    body = f'<div class="switch-lead">{escape(detail)}</div><div class="switch-frame">{image("switch", "switch-image", "mineoスイッチの画面")}</div>'
    return standard_slide(slide_id, title, body, 'switch_illust', 'switch')


STYLE = r'''
:root { --blue:#0052cc; --blue-dark:#003380; --red:#e63946; --ink:#172033; --pale:#f0f5ff; }
* { box-sizing:border-box; margin:0; padding:0; }
body { background:#f0f4f8; color:var(--ink); font-family:'Inter','Noto Sans JP',sans-serif; display:flex; flex-direction:column; align-items:center; gap:40px; padding:40px; }
.slide-container { position:relative; display:flex; flex-direction:column; width:1080px; height:1080px; overflow:hidden; background:#fff; }
img { object-fit:contain; filter:drop-shadow(0 10px 20px rgba(0,0,0,.1)); }
.red { color:var(--red); }
.slide-container.price-note::after {
    content: "※表示している料金はすべて月額・税込みの価格です";
    position: absolute; right: 20px; bottom: 16px; z-index: 9999;
    background: rgba(0,0,0,0.62); color: #fff;
    font-family: 'Noto Sans JP', sans-serif;
    font-size: 26px; font-weight: 700; letter-spacing: 0.02em; line-height: 1;
    padding: 10px 20px; border-radius: 10px; white-space: nowrap; pointer-events: none;
}
.slide-thumbnail { align-items:center; text-align:center; border:25px solid var(--blue); padding:160px 45px 300px;
    background:repeating-conic-gradient(from 0deg at 52% 48%,rgba(0,82,204,.06) 0deg 2.5deg,transparent 2.5deg 16deg),radial-gradient(ellipse at 52% 48%,#fff 5%,#e8f3ff 45%,#c8dcff 100%); }
.thumb-top-strip { position:absolute; top:25px; left:25px; right:25px; z-index:3; background:var(--blue); color:#fff; font-size:36px; font-weight:900; padding:18px 0; text-align:center; letter-spacing:.06em; }
.thumb-accent-tri { position:absolute; width:0; height:0; z-index:1; }
.thumb-accent-tri.tl { top:25px; left:25px; border-top:300px solid rgba(0,82,204,.09); border-right:300px solid transparent; }
.thumb-accent-tri.br { bottom:25px; right:25px; border-bottom:300px solid rgba(0,82,204,.09); border-left:300px solid transparent; }
.thumb-tag { z-index:2; background:var(--red); color:#fff; font-size:72px; font-weight:900; padding:13px 44px; transform:rotate(-3deg); box-shadow:8px 8px 0 rgba(0,0,0,.25); margin-bottom:22px; }
.thumb-title { z-index:2; font-size:76px; line-height:1.2; font-weight:900; max-width:900px; margin-bottom:24px; text-wrap:balance; }
.thumb-sub-band { z-index:2; display:flex; align-items:center; justify-content:center; flex-wrap:wrap; gap:12px; width:930px; background:var(--blue); color:#fff; font-size:45px; line-height:1.2; font-weight:900; padding:20px 22px; border-radius:12px; box-shadow:4px 4px 0 rgba(0,0,0,.2); }
.thumb-sub-band b { color:#ffd700; font-size:60px; }
.thumb-sub-band strong { color:#ffd700; }
.thumb-logo-wrap { position:absolute; z-index:2; left:74px; bottom:75px; height:175px; display:flex; align-items:center; }
.thumb-logo { width:335px; height:150px; background:#fff; border-radius:18px; padding:15px 22px; filter:none; box-shadow:6px 6px 0 rgba(0,0,0,.18); }
.thumb-illust { position:absolute; z-index:2; right:45px; bottom:30px; }
.cover-illust-img { height:290px; max-width:330px; }
.slide-pad { padding:72px 70px; }
.watermark { position:absolute; top:-45px; left:10px; z-index:0; color:var(--blue); font-size:280px; font-weight:900; line-height:1; opacity:.07; }
.slide-title { position:relative; z-index:1; font-size:62px; line-height:1.2; font-weight:900; border-bottom:10px solid var(--blue); padding-bottom:14px; margin-bottom:30px; }
.slide-body { position:relative; z-index:1; display:flex; flex-direction:column; gap:28px; margin-bottom:120px; }
.slide-illust { position:absolute; right:40px; bottom:40px; z-index:2; }
.illust-img { height:260px; max-width:290px; }
.question-card { min-height:500px; border:8px solid var(--blue); background:var(--pale); border-radius:28px; box-shadow:8px 8px 0 #cfe1ff; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:20px; padding:35px; }
.question-icon { width:116px; height:116px; border-radius:50%; display:flex; align-items:center; justify-content:center; background:var(--blue); color:#fff; font-size:85px; font-weight:900; }
.question-text { max-width:820px; font-size:70px; line-height:1.25; font-weight:900; text-align:center; text-wrap:balance; }
.diagnosis-hint { align-self:flex-start; font-size:43px; font-weight:900; color:var(--blue); }
.condition-card { align-self:flex-start; background:var(--blue); color:#fff; padding:18px 34px; border-radius:18px; font-size:50px; font-weight:900; }
.benefit-card { display:flex; flex-direction:column; align-items:center; justify-content:center; min-height:310px; background:var(--pale); border:9px solid var(--blue); border-radius:26px; box-shadow:8px 8px 0 #cfe1ff; padding:25px 26px; }
.benefit-main { display:flex; align-items:baseline; gap:15px; color:var(--red); font-weight:900; }
.benefit-main strong { font-size:120px; line-height:1.1; }
.benefit-main span { font-size:70px; }
.benefit-unlimited { color:var(--blue); font-size:64px; line-height:1.1; font-weight:900; }
.benefit-usage { align-self:flex-start; display:flex; flex-direction:column; justify-content:center; gap:16px; min-height:195px; width:655px; padding:24px 30px; border-left:14px solid var(--blue); border-radius:0 20px 20px 0; background:var(--pale); }
.benefit-usage strong { color:var(--blue); font-size:53px; line-height:1.15; font-weight:900; }
.usage-tags { display:flex; gap:16px; }
.usage-tags span { border-radius:30px; padding:8px 18px; background:#fff; color:var(--ink); font-size:34px; font-weight:900; white-space:nowrap; }
.speed-card { display:flex; flex-direction:column; align-items:center; background:var(--pale); border-left:14px solid var(--blue); border-radius:0 20px 20px 0; padding:25px 30px; }
.speed-card strong { font-size:145px; color:var(--blue); line-height:1.1; }
.speed-card span { font-size:43px; font-weight:900; }
.price-card { display:flex; align-items:center; justify-content:space-between; gap:18px; background:#fff0f0; border-left:14px solid var(--red); border-radius:0 20px 20px 0; padding:28px 32px; font-weight:900; }
.price-card span { font-size:43px; }
.price-card strong { color:var(--red); font-size:67px; white-space:nowrap; }
.switch-lead { background:var(--pale); border-left:14px solid var(--blue); border-radius:0 20px 20px 0; padding:24px 32px; font-size:55px; font-weight:900; }
.switch-frame { align-self:center; width:690px; height:410px; display:flex; align-items:center; justify-content:center; border:8px solid var(--blue); border-radius:22px; background:#fff; box-shadow:8px 8px 0 #cfe1ff; }
.switch-image { width:620px; height:360px; }
.cta-slide { background:linear-gradient(135deg,#0052cc,#003380); color:#fff; align-items:center; justify-content:center; }
.cta-content { display:flex; flex-direction:column; align-items:center; text-align:center; width:100%; padding:38px 50px 28px; gap:12px; }
.cta-logo { width:280px; height:110px; margin-bottom:12px; background:#fff; border-radius:18px; padding:8px 16px; filter:none; box-shadow:4px 4px 0 rgba(0,0,0,.18); }
.cta-title { color:#ffd700; font-size:84px; line-height:1.15; font-weight:900; max-width:970px; text-wrap:balance; }
.cta-sub { color:#fff; font-size:50px; font-weight:900; }
.cta-banner-img { width:900px; max-height:420px; object-fit:contain; border:8px solid #fff; border-radius:14px; background:#fff; }
.cta-arrow { color:#ffd700; font-size:90px; font-weight:900; line-height:1; animation:bounce 1.3s ease-in-out infinite; }
@keyframes bounce { 0%,100% { transform:translateY(0); } 50% { transform:translateY(12px); } }
'''


def main() -> None:
    slides = parse_slides()
    html = f'''<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>mineo プラン選びショート</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@700;900&family=Noto+Sans+JP:wght@700;900&display=swap" rel="stylesheet">
<style>{STYLE}</style></head><body>
{chr(10).join(render_slide(slide_id, title, detail, index, len(slides)) for index, (slide_id, title, detail) in enumerate(slides, 1))}
</body></html>
'''
    OUTPUT.write_text(html, encoding='utf-8')
    print(f'{len(slides)} slides -> {OUTPUT}')
    print('slide IDs:', ', '.join(slide_id for slide_id, _, _ in slides))


if __name__ == '__main__':
    main()
