#!/usr/bin/env python3
"""Generate the satellite-communication short deck from its script CSV."""
from __future__ import annotations

import csv
import html
import re
from pathlib import Path

ROOT = Path('/workspaces/yt-factory/packages/slide-gen')
CSV_PATH = Path('/workspaces/yt-factory/packages/scenario-gen/archive/videos/51_【2026年最新】登山で圏外でも連絡できる格安SIMは？衛星通信が使える4つの選び方/short/衛星通信、追加料金なしの格安SIMは？.csv')
OUTPUT = ROOT / 'slides-short.html'
LONG_THUMB = 'public/images/thumbnails/51_【2026年最新】登山で圏外でも連絡できる格安SIMは？衛星通信が使える4つの選び方_サムネ1.png'


def load_slides():
    with CSV_PATH.open(encoding='utf-8-sig', newline='') as f:
        rows = list(csv.DictReader(f))
    slides = {}
    previous = ''
    for row in rows:
        slide_id = row['スライドID'].strip()
        text = row['スライドに表示する内容'].strip()
        if text == '同上':
            text = previous
        else:
            previous = text
        slides.setdefault(slide_id, text)
    return slides


def esc(value):
    return html.escape(value, quote=True)


def content_lines(raw):
    # Remove production notes such as "...の図" before rendering script text.
    parts = [part.strip() for part in re.split(r'[/／]', raw) if part.strip() and part.strip() != '同上']
    return [part for part in parts if not re.search(r'(?:の図|のイラスト)$', part) and not part.startswith('タイトル：') and not part.startswith('残り：')]


def line_html(text, idx=0, alert=False, hero=False):
    cls = 'info-card alert' if alert else 'info-card'
    icons = ['📡', '📱', '✅', '⚠️']
    hero_cls = ' hero' if hero or (len(text) > 26 and idx == 0) else ''
    return f'<div class="{cls}{hero_cls}"><span class="emoji">{icons[idx % len(icons)]}</span><span>{esc(text)}</span></div>'


def standard_slide(slide_id, raw):
    lines = content_lines(raw)
    title = {
        '2': '空が見えれば衛星と通信',
        '3': '衛星通信を始めた3社',
        '4': 'できること・できないこと',
        '5': 'あなたはどっち派？',
        '6': '手間なし派は ahamo',
        '7': '安さとLINE派は LINEMO',
        '8': '衛星通信中もLINEが使える',
        '9': 'LINEMOは申し込みが必要',
        '10': 'povo2.0・UQ mobileは？',
    }.get(slide_id, '衛星通信の選び方')
    if slide_id == '2':
        body = '''<div class="satellite-diagram" aria-label="衛星とスマホが直接つながる図">
          <div class="diagram-node satellite-node"><span>🛰️</span><b>衛星</b></div>
          <div class="signal-line"><span>直接通信</span></div>
          <div class="diagram-node phone-node"><span>📱</span><b>スマホ</b></div>
        </div>
        <div class="slide-facts"><div class="info-card"><span class="emoji">👀</span><span>空が見える場所なら</span></div><div class="info-card"><span class="emoji">💬</span><span>メッセージが送れる</span></div></div>'''
    elif slide_id == '3':
        carriers = [('docomo_logo.png', 'ドコモ'), ('au_logo.png', 'au'), ('Softbank_logo.png', 'ソフトバンク')]
        body = '<div class="carrier-grid">' + ''.join(f'<div class="carrier-card"><img src="public/images/logo/{name}" alt="{label}"></div>' for name, label in carriers) + '</div><div class="info-card carrier-caption"><span class="emoji">📡</span><span>3社が衛星との直接通信を提供</span></div>'
    elif slide_id == '4':
        card_lines = []
        for i, line in enumerate(lines):
            label, sep, value = line.partition('：')
            if sep:
                card_lines.append(f'<div class="capability {"good" if i == 0 else "bad"}"><span class="cap-label">{esc(label)}</span><span class="cap-value">{esc(value)}</span></div>')
            else:
                card_lines.append(line_html(line, i, i == 1))
        body = ''.join(card_lines)
    elif slide_id == '5':
        options = [line for line in lines if '診断：' not in line]
        display_options = ['手間なしで<br>データ多め派', '安さと<br>LINE派']
        body = '<div class="choice-grid">' + ''.join(f'<div class="choice-card"><span>{"A" if i == 0 else "B"}</span>{display_options[i]}</div>' for i, _ in enumerate(options)) + '</div>'
        body += '<div class="pick-banner">モモコは安さとLINE派！</div>'
    elif slide_id == '6':
        body = '''<div class="brand-logo-card"><img src="public/images/logo/Ahamo_logo.png" alt="ahamo"></div>
          <div class="slide-facts"><div class="info-card"><span class="emoji">🙌</span><span>手間なしでデータ多め派</span></div><div class="info-card"><span class="emoji">📡</span><span>衛星通信は当面、追加料金なし・<br>申し込み不要</span></div></div>'''
    elif slide_id == '7':
        body = '''<div class="brand-logo-card"><img src="public/images/logo/LINEMO_logo.png" alt="LINEMO"></div>
          <div class="slide-facts"><div class="info-card"><span class="emoji">💴</span><span>3GBまで月額990円</span></div><div class="info-card"><span class="emoji">📡</span><span>追加料金なしで衛星通信</span></div></div>'''
    elif slide_id == '8':
        body = '''<div class="line-feature"><div class="line-mark">LINE</div><div class="line-feature-title">衛星通信中に送れる</div></div>
          <div class="slide-facts"><div class="info-card"><span class="emoji">💬</span><span>LINEのテキスト</span></div><div class="info-card"><span class="emoji">📍</span><span>位置情報</span></div></div>'''
    elif slide_id == '9':
        body = '''<div class="warning-box"><div class="w-title">2026年冬（予定）までは</div>
          <div class="w-item">衛星通信の申し込みが必要</div></div>
          <img class="warning-illust" src="public/images/irasutoya/pop_chuui.png" alt="注意" style="z-index: 2;">'''
    elif slide_id == '10':
        body = '''<div class="carrier-grid two-carriers"><div class="carrier-card"><img src="public/images/logo/Povo_logo.png" alt="povo2.0"></div><div class="carrier-card"><img src="public/images/logo/UQ_logo_2.png" alt="UQ mobile"></div></div>
          <div class="slide-facts"><div class="info-card"><span class="emoji">🛰️</span><span>衛星通信の使い方は？</span></div><div class="info-card"><span class="emoji">▶️</span><span>回線の足し方は本編で解説</span></div></div>'''
    else:
        body = ''.join(line_html(line, i, slide_id == '9', slide_id in ('8', '10')) for i, line in enumerate(lines))
    price_class = ' price-note' if slide_id == '7' else ''
    warning_class = ' warning-slide' if slide_id == '9' else ''
    is_warning = slide_id == '9'
    banner = '<div class="warning-banner">⚠ 申し込みを忘れずに</div>' if is_warning else ''
    return f'''<!-- Slide ID: {slide_id} -->
<div class="slide-container slide-pad{price_class}{warning_class}">
  <div class="watermark">{esc(slide_id)}</div>
  {banner}
  <h2 class="slide-title">{('LINEMOは<br>申し込みが必要' if slide_id == '9' else esc(title))}</h2>
  <div class="slide-body">{body}</div>
</div>'''


def thumbnail(raw):
    m = re.search(r'タイトル：([^／]+)', raw)
    title = m.group(1).strip() if m else '登山で圏外でも連絡できる？'
    return f'''<!-- Slide ID: 1 -->
<div class="slide-container slide-thumbnail">
  <div class="thumb-top-strip">⚡ 圏外でも連絡できる格安SIM ⚡</div>
  <div class="thumb-tag">衛星通信</div>
  <h1 class="thumb-title">登山で圏外でも<br>連絡できる格安SIMは？</h1>
  <div class="thumb-sub-band">追加料金なしで使える？</div>
  <img class="thumb-illust" src="public/images/irasutoya/pose_necchuu_smartphone_man.png" alt="スマートフォンを使う人">
</div>'''


def cta_slide(slide_id, raw):
    body = content_lines(raw)
    sub = body[-1] if body else '回線の足し方を本編で解説'
    sub = re.sub(r'^残り：', '', sub)
    return f'''<!-- Slide ID: {slide_id} -->
<div class="slide-container cta-slide">
  <div class="cta-content">
    <div class="cta-kicker">続きは本編で解説</div>
    <div class="cta-logos"><div class="cta-logo-card"><img src="public/images/logo/Povo_logo.png" alt="povo2.0"></div><div class="cta-logo-card"><img src="public/images/logo/UQ_logo_2.png" alt="UQ mobile"></div></div>
    <h2 class="cta-title">povo2.0・UQ mobile<br>衛星通信の使い方</h2>
    <div class="cta-sub">{esc(sub)}</div>
    <img class="cta-banner-img" src="{LONG_THUMB}" alt="長尺動画のサムネイル">
    <div class="cta-arrow">▼</div>
  </div>
</div>'''


def main():
    slides = load_slides()
    ids = list(slides)
    if not ids or ids != [str(i) for i in range(1, len(ids) + 1)]:
        raise SystemExit(f'Unexpected slide IDs: {ids}')
    rendered = []
    for slide_id, raw in slides.items():
        if slide_id == '1':
            rendered.append(thumbnail(raw))
        elif slide_id == ids[-1]:
            rendered.append(cta_slide(slide_id, raw))
        else:
            rendered.append(standard_slide(slide_id, raw))
    OUTPUT.write_text(HTML_HEAD + '\n'.join(rendered) + HTML_TAIL, encoding='utf-8')
    print(f'Generated {OUTPUT} with {len(rendered)} slides (IDs: {", ".join(ids)}).')


HTML_HEAD = '''<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>衛星通信、追加料金なしの格安SIMは？</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@700;900&family=Noto+Sans+JP:wght@700;900&display=swap" rel="stylesheet">
<style>
:root{--blue:#0052cc;--blue-dark:#003380;--red:#e63946;--ink:#172033}
*{box-sizing:border-box;margin:0;padding:0}
body{display:flex;flex-direction:column;align-items:center;gap:40px;padding:40px;background:#f0f4f8;color:var(--ink);font-family:Inter,'Noto Sans JP',sans-serif}
.slide-container{position:relative;overflow:hidden;display:flex;width:1080px;height:1080px;flex:none;flex-direction:column;background:#fff}
img{object-fit:contain;filter:drop-shadow(0 10px 20px rgba(0,0,0,.1))}
.slide-container.price-note::after{content:"※表示している料金はすべて月額・税込みの価格です";position:absolute;right:20px;bottom:16px;z-index:9999;background:rgba(0,0,0,.62);color:#fff;font-family:'Noto Sans JP',sans-serif;font-size:26px;font-weight:700;letter-spacing:.02em;line-height:1;padding:10px 20px;border-radius:10px;white-space:nowrap;pointer-events:none}
.slide-thumbnail{align-items:center;text-align:center;border:25px solid var(--blue);padding:160px 42px 300px;background:repeating-conic-gradient(from 0deg at 52% 48%,rgba(0,82,204,.06) 0deg 2.5deg,transparent 2.5deg 16deg),radial-gradient(ellipse at 52% 48%,#fff 5%,#e8f3ff 45%,#c8dcff 100%)}
.thumb-top-strip{position:absolute;top:25px;left:25px;right:25px;background:var(--blue);color:#fff;font-size:36px;font-weight:900;padding:18px 0;text-align:center;letter-spacing:.06em;z-index:3}
.thumb-tag{font-size:80px;font-weight:900;color:#fff;background:var(--red);padding:18px 54px;transform:rotate(-3deg);box-shadow:8px 8px 0 rgba(0,0,0,.25);margin-bottom:28px;z-index:2}
.thumb-title{font-size:80px;line-height:1.25;font-weight:900;margin-bottom:22px;max-width:900px;z-index:2}
.thumb-sub-band{font-size:58px;font-weight:900;color:#fff;background:var(--blue);padding:18px 55px;border-radius:12px;box-shadow:4px 4px 0 rgba(0,0,0,.2);z-index:2}
.thumb-illust{position:absolute;right:45px;bottom:40px;height:290px;z-index:2}
.slide-pad{padding:75px 70px}
.watermark{position:absolute;top:-42px;left:10px;font-size:280px;line-height:1;color:var(--blue);opacity:.07;font-weight:900}
.slide-title{position:relative;font-size:62px;line-height:1.2;font-weight:900;border-bottom:10px solid var(--blue);padding-bottom:15px;margin-bottom:30px;z-index:1}
.slide-body{position:relative;display:flex;flex:1;min-height:0;flex-direction:column;justify-content:space-evenly;gap:24px;z-index:1;padding-bottom:10px}
.info-card{display:flex;flex:1;align-items:center;gap:22px;min-height:130px;padding:22px 30px;border-radius:0 16px 16px 0;background:#f0f5ff;border-left:14px solid var(--blue);font-size:47px;font-weight:900;line-height:1.25}
.info-card.hero{font-size:58px;line-height:1.32}.info-card.alert{background:#fff0f0;border-left-color:var(--red);color:var(--red)}
.emoji{flex:none;font-size:54px}.slide-illust{position:absolute;right:35px;bottom:25px;height:210px;z-index:2}
.capability{display:flex;flex:1;min-height:250px;flex-direction:column;justify-content:center;gap:15px;padding:25px 35px;border:8px solid #16834a;border-radius:22px;background:#edfff5;text-align:center}
.capability.bad{border-color:var(--red);background:#fff0f0}.cap-label{font-size:46px;font-weight:900;color:#16834a}.bad .cap-label,.bad .cap-value{color:var(--red)}.cap-value{font-size:50px;font-weight:900;line-height:1.25}
.choice-grid{display:grid;flex:1;grid-template-columns:1fr 1fr;gap:24px}.choice-card{display:flex;flex-direction:column;justify-content:center;align-items:center;gap:24px;padding:35px;border:8px solid var(--blue);border-radius:26px;background:#eaf3ff;text-align:center;font-size:48px;font-weight:900;line-height:1.3}.choice-card span{display:flex;width:110px;height:110px;align-items:center;justify-content:center;border-radius:50%;background:var(--blue);color:white;font-size:65px}.pick-banner{padding:20px;background:var(--red);color:white;text-align:center;font-size:50px;font-weight:900;border-radius:14px}
.warning-slide{background:#fff8f8}.warning-banner{margin:-75px -70px 42px;padding:22px 0;text-align:center;font-size:56px;font-weight:900;color:#fff;background:var(--red)}.warning-slide .slide-title{color:var(--red);border-color:var(--red)}
.cta-slide{justify-content:center;align-items:center;text-align:center;padding:38px 50px;background:linear-gradient(135deg,#0052cc,#003380);color:#fff}.cta-content{display:flex;width:100%;height:100%;flex-direction:column;align-items:center;justify-content:space-between}.cta-kicker{font-size:44px;font-weight:900;color:#fff}.cta-title{font-size:67px;line-height:1.18;color:#ffd700;font-weight:900}.cta-sub{font-size:39px;line-height:1.2;font-weight:900}.cta-banner-img{width:900px;max-height:400px;object-fit:contain;border-radius:12px}.cta-arrow{font-size:76px;color:#ffd700;line-height:1;animation:bounce 1.4s infinite}@keyframes bounce{50%{transform:translateY(12px)}}
.slide-facts{display:flex;flex:1;min-height:0;flex-direction:column;gap:18px}.slide-facts .info-card{min-height:0}
.satellite-diagram{display:flex;flex:1;min-height:300px;align-items:center;justify-content:center;gap:28px;padding:24px 36px;border:6px solid #d9e8ff;border-radius:28px;background:linear-gradient(135deg,#eef6ff,#fff)}
.diagram-node{display:flex;width:210px;height:210px;flex-direction:column;align-items:center;justify-content:center;gap:10px;border:6px solid var(--blue);border-radius:50%;background:#fff;color:var(--blue)}.diagram-node span{font-size:82px}.diagram-node b{font-size:40px}
.signal-line{position:relative;display:flex;flex:1;max-width:260px;height:8px;align-items:center;justify-content:center;background:var(--blue)}.signal-line:before,.signal-line:after{position:absolute;top:-11px;width:22px;height:22px;border-top:8px solid var(--blue);content:""}.signal-line:before{left:0;border-left:8px solid var(--blue);transform:rotate(-45deg)}.signal-line:after{right:0;border-right:8px solid var(--blue);transform:rotate(45deg)}.signal-line span{position:absolute;top:18px;white-space:nowrap;color:var(--blue-dark);font-size:30px;font-weight:900}
.carrier-grid{display:grid;flex:1;min-height:240px;grid-template-columns:repeat(3,1fr);gap:20px}.carrier-grid.two-carriers{grid-template-columns:1fr 1fr;flex:0 0 230px}.carrier-card,.brand-logo-card{display:flex;align-items:center;justify-content:center;padding:20px;border:5px solid #dce7f5;border-radius:24px;background:#fff;box-shadow:0 8px 0 rgba(0,82,204,.08)}.carrier-card img{width:100%;height:150px;filter:none}.carrier-caption{flex:0 0 190px}.brand-logo-card{flex:0 0 190px}.brand-logo-card img{width:100%;height:130px;filter:none}
.choice-card{font-size:54px}.choice-card span{width:125px;height:125px;font-size:72px}.pick-banner{font-size:52px}
.line-feature{display:flex;flex:0 0 210px;align-items:center;justify-content:center;gap:36px;border-radius:26px;background:#06c755;color:#fff}.line-mark{padding:18px 26px;border:5px solid #fff;border-radius:26px;font-size:56px;font-weight:900}.line-feature-title{font-size:48px;font-weight:900}
.warning-slide .slide-title{margin-bottom:18px}.warning-slide .slide-body{padding-bottom:0}.warning-box{display:flex;flex:1;min-height:0;flex-direction:column;justify-content:center;gap:32px;padding:38px 42px 260px;border:10px solid var(--red);border-radius:24px;background:#fff0f0;color:var(--red);text-align:center}.w-title{font-size:58px;font-weight:900;line-height:1.2}.w-item{font-size:50px;font-weight:900;line-height:1.3}.warning-illust{position:absolute;right:48px;bottom:28px;height:280px}
.cta-content{justify-content:space-around}.cta-logos{display:flex;align-items:center;justify-content:center;gap:26px;margin-bottom:4px}.cta-logo-card{display:flex;height:130px;min-width:240px;align-items:center;justify-content:center;padding:8px 16px;border-radius:18px;background:#fff;box-shadow:4px 4px 0 rgba(0,0,0,.18)}.cta-logo-card img{height:110px;max-width:280px;filter:none}.cta-title{font-size:84px;line-height:1.13}.cta-sub{font-size:50px;line-height:1.2}.cta-banner-img{width:800px;max-height:330px}.cta-arrow{font-size:90px}
</style></head><body>'''
HTML_TAIL = '</body></html>\n'

if __name__ == '__main__':
    main()
