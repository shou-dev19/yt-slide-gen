#!/usr/bin/env python3
"""Generate the ahamo short deck from the CSV's display-content column."""
from __future__ import annotations

import csv
import re
from html import escape
from pathlib import Path

ROOT = Path('/workspaces/yt-factory/packages/slide-gen')
CSV_PATH = Path('/workspaces/yt-factory/packages/scenario-gen/archive/videos/50_【2026年12月】ahamoが値上げ＆大盛り終了！？対象者と今やるべき3つの対策/short/【12月値上げ】ahamoが月3,135円に.csv')
OUTPUT = ROOT / 'slides-short.html'
ASSET_ROOT = ROOT / 'public/images'
LOGO = ASSET_ROOT / 'logo/Ahamo_logo.png'
BANNER = ASSET_ROOT / 'thumbnails/50_【2026年12月】ahamoが値上げ＆大盛り終了！？対象者と今やるべき3つの対策_サムネ1.png'
ILLUST = {
    '1': 'irasutoya/bikkuri_me_tobideru_man.png',
    '2': 'irasutoya/shinpai_man.png',
    '3': 'irasutoya/seikyuusyo_shock.png',
    '4': 'irasutoya/pose_naruhodo_woman.png',
    '5': 'irasutoya/pose_necchuu_smartphone_man.png',
    '6': 'irasutoya/smartphone_photo_satsuei_man.png',
    '7': 'irasutoya/smartphone_talk03_man.png',
    '8': 'irasutoya/pose_anshin_woman.png',
    '9': 'irasutoya/pose_anshin_woman.png',
}

STYLE = r'''
:root { --blue:#0052cc; --blue-dark:#003380; --red:#e63946; --ink:#172033; --brand:#0052cc; --brand-deep:#003380; --brand-soft:#eaf3ff; }
* { box-sizing:border-box; margin:0; padding:0; }
body { display:flex; flex-direction:column; align-items:center; background:#f0f4f8; color:var(--ink); font-family:'Inter','Noto Sans JP',sans-serif; gap:40px; padding:40px; }
.slide-container { position:relative; overflow:hidden; display:flex; width:1080px; height:1080px; flex:none; flex-direction:column; justify-content:flex-start; align-items:stretch; background:#fff; }
img { object-fit:contain; filter:drop-shadow(0 10px 20px rgba(0,0,0,.1)); }
.slide-container.price-note::after {
    content: "※表示している料金はすべて月額・税込みの価格です";
    position: absolute; right: 20px; bottom: 16px; z-index: 9999;
    background: rgba(0,0,0,0.62); color: #fff;
    font-family: 'Noto Sans JP', sans-serif;
    font-size: 26px; font-weight: 700; letter-spacing: 0.02em; line-height: 1;
    padding: 10px 20px; border-radius: 10px; white-space: nowrap; pointer-events: none;
}
.slide-thumbnail { align-items:center; text-align:center; border:25px solid var(--blue); padding:160px 42px 300px; background:repeating-conic-gradient(from 0deg at 52% 48%,rgba(0,82,204,.06) 0deg 2.5deg,transparent 2.5deg 16deg),radial-gradient(ellipse at 52% 48%,#fff 5%,#e8f3ff 45%,#c8dcff 100%); }
.thumb-top-strip { position:absolute; top:25px; left:25px; right:25px; background:var(--blue); color:#fff; font-size:36px; font-weight:900; padding:18px 0; letter-spacing:.06em; z-index:3; }
.thumb-tag { font-size:76px; font-weight:900; color:#fff; background:var(--red); padding:18px 54px; transform:rotate(-3deg); box-shadow:8px 8px 0 rgba(0,0,0,.25); margin-bottom:28px; z-index:2; }
.thumb-title { font-size:80px; line-height:1.25; font-weight:900; margin-bottom:22px; max-width:900px; z-index:2; }
.thumb-sub-band { font-size:56px; font-weight:900; color:#fff; background:var(--blue); padding:18px 55px; border-radius:12px; box-shadow:4px 4px 0 rgba(0,0,0,.2); z-index:2; }
.thumb-logo { position:absolute; left:95px; bottom:80px; width:350px; height:150px; padding:12px 25px; background:#fff; border-radius:18px; filter:none; z-index:2; }
.thumb-illust { position:absolute; right:45px; bottom:40px; height:290px; z-index:2; }
.slide-pad { padding:75px 70px; }
.watermark { position:absolute; top:-42px; left:10px; font-size:280px; line-height:1; color:var(--blue); opacity:.07; font-weight:900; }
.slide-title { position:relative; font-size:62px; line-height:1.2; font-weight:900; border-bottom:10px solid var(--blue); padding-bottom:15px; margin-bottom:30px; }
.slide-body { position:relative; display:flex; flex-direction:column; gap:26px; margin-bottom:150px; z-index:1; }
.slide-body .lead { background:#eaf3ff; border-left:14px solid var(--blue); color:var(--ink); font-size:52px; font-weight:900; padding:25px 30px; line-height:1.28; }
.slide-body .emph { background:#eaf3ff; border:5px solid var(--blue); color:var(--ink); font-size:54px; font-weight:900; padding:30px; line-height:1.3; }
.slide-body .emph .big { color:var(--red); font-size:90px; }
.slide-body .rows { flex:none; gap:18px; }
.slide-body .rows li { background:#f0f5ff; border:0; border-left:14px solid var(--blue); padding:20px 25px; }
.slide-body .rows .tx { color:var(--ink); font-size:44px; font-weight:900; line-height:1.25; }
.info-card { display:flex; align-items:center; gap:22px; padding:23px 30px; border-radius:0 16px 16px 0; background:#f0f5ff; border-left:14px solid var(--blue); font-size:47px; font-weight:900; line-height:1.24; }
.info-card.alert { background:#fff0f0; border-left-color:var(--red); color:var(--red); }
.info-card.compact { font-size:39px; }
.info-card strong { color:var(--red); }
.slide-illust { position:absolute; right:40px; bottom:36px; height:235px; z-index:2; }
.price-note .slide-illust { bottom:70px; }
.slide-body.fill { flex:1; min-height:0; margin-bottom:215px; justify-content:space-evenly; }
.slide-body.fill .info-card { min-height:125px; }
.hero-panel { display:flex; flex-direction:column; justify-content:center; align-items:center; flex:1; min-height:0; padding:12px 25px; border:8px solid var(--blue); border-radius:25px; background:linear-gradient(145deg,#eaf3ff,#fff); text-align:center; }
.hero-panel .hero-number { color:var(--red); font-size:135px; line-height:1.25; font-weight:900; }
.hero-panel .hero-label { color:var(--blue-dark); font-size:57px; line-height:1.2; font-weight:900; }
.hero-panel .hero-small { font-size:38px; font-weight:900; }
.condition-dots { display:flex; justify-content:space-around; gap:12px; }
.condition-dots span { display:flex; align-items:center; justify-content:center; width:155px; height:155px; border-radius:50%; background:var(--blue); color:#fff; font-size:75px; font-weight:900; }
.split-fact { display:flex; align-items:center; justify-content:center; flex:1; gap:15px; border:8px solid var(--blue); border-radius:24px; background:#eaf3ff; font-weight:900; }
.split-fact b { color:var(--red); font-size:120px; line-height:1; }
.split-fact span { font-size:53px; line-height:1.2; }
.large-card { display:flex; flex-direction:column; justify-content:center; min-height:160px; padding:25px 35px; border-left:16px solid var(--blue); border-radius:0 18px 18px 0; background:#f0f5ff; font-size:49px; line-height:1.2; font-weight:900; }
.large-card.alert { border-color:var(--red); background:#fff0f0; color:var(--red); }
.large-card small { font-size:35px; }
.fact-stack { display:flex; flex:1; flex-direction:column; gap:22px; min-height:0; }
.fact-stack > * { flex:1; }
.fact-stack .hero-panel { flex:1.25; }
.compact-facts .hero-panel { flex:2; padding:7px 20px; }
.compact-facts .hero-number { font-size:90px; }
.compact-facts .hero-label { font-size:45px; }
.compact-facts .hero-small { font-size:28px; }
.compact-facts .large-card { min-height:108px; padding:12px 25px; font-size:42px; }
.three-facts .hero-panel { padding:8px 20px; }
.three-facts .hero-number { font-size:100px; }
.three-facts .hero-label { font-size:45px; }
.fee-detail { display:flex; align-items:center; justify-content:center; gap:25px; padding:15px; border:6px solid var(--blue); border-radius:18px; background:#f0f5ff; font-size:65px; font-weight:900; }
.fee-detail b { color:var(--red); font-size:84px; }
.slide-pad.sparse .slide-body { flex:1; min-height:0; margin-bottom:220px; }
.slide-pad.sparse .slide-illust { height:255px; }
.slide-pad.sparse .slide-title { margin-bottom:22px; }
.kicker { display:inline-block; align-self:flex-start; color:#fff; background:var(--red); border-radius:100px; padding:10px 25px; font-size:39px; font-weight:900; }
.fee-grid { display:grid; grid-template-columns:1fr 1fr; gap:18px; }
.fee-cell { border:6px solid var(--blue); background:#eaf3ff; border-radius:18px; padding:20px; text-align:center; }
.fee-cell.new { border-color:var(--red); background:#fff0f0; }
.fee-cell small { display:block; font-size:37px; font-weight:900; }
.fee-cell strong { display:block; font-size:65px; line-height:1.2; font-weight:900; color:var(--blue); }
.fee-cell.new strong { color:var(--red); }
.fee-cell span { display:block; font-size:29px; }
.summary-slide .slide-body { flex:1; min-height:0; margin-bottom:0; }
.summary-grid { display:grid; flex:1; min-height:0; grid-template-columns:1fr 1fr; grid-template-rows:1fr 1fr; gap:18px; }
.summary-grid .info-card { min-height:0; display:flex; flex-direction:column; justify-content:space-between; align-items:stretch; gap:16px; padding:25px; }
.summary-head { display:flex; align-items:center; gap:16px; flex:1; }
.summary-main { font-size:39px; line-height:1.24; font-weight:900; }
.summary-detail { width:100%; border-top:3px solid #bfd3f2; padding-top:14px; color:var(--blue-dark); font-size:35px; line-height:1.23; font-weight:900; }
.summary-grid .num { display:flex; align-items:center; justify-content:center; flex:none; width:70px; height:70px; border-radius:50%; background:var(--blue); color:#fff; font-size:38px; }
.warning-slide { background:#fff8f8; padding:0 65px 75px; }
.warning-banner { margin:0 -65px 52px; padding:24px 0; text-align:center; font-size:62px; font-weight:900; color:#fff; background:var(--red); }
.warning-title { font-size:75px; font-weight:900; color:var(--red); margin-bottom:28px; }
.warning-box { border:10px solid var(--red); background:#fff0f0; border-radius:20px; padding:36px 42px; display:flex; flex-direction:column; gap:26px; }
.warning-box .w-title { font-size:58px; font-weight:900; }
.warning-box .w-item { font-size:50px; font-weight:900; }
.cta-slide { background:linear-gradient(135deg,#0052cc,#003380); color:#fff; align-items:center; text-align:center; padding:45px 55px; }
.cta-content { display:flex; flex-direction:column; align-items:center; width:100%; }
.cta-logo { width:280px; height:110px; padding:8px 16px; border-radius:18px; background:#fff; filter:none; box-shadow:4px 4px 0 rgba(0,0,0,.18); margin-bottom:12px; }
.cta-title { font-size:80px; line-height:1.13; color:#ffd700; font-weight:900; margin-bottom:10px; }
.cta-sub { font-size:46px; line-height:1.2; font-weight:900; margin-bottom:18px; }
.cta-banner-img { width:880px; max-height:455px; object-fit:contain; border:10px solid #fff; border-radius:12px; }
.cta-arrow { font-size:80px; color:#ffd700; line-height:1; margin-top:9px; animation:bounce 1.4s infinite; }
@keyframes bounce { 50% { transform:translateY(12px); } }
'''


def e(value: str) -> str:
    return escape(value, quote=True)


def image(path: Path, css: str, alt: str) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return f'<img class="{css}" src="{e(path.relative_to(ROOT).as_posix())}" alt="{e(alt)}">'


def illust(slide_id: str) -> str:
    path = ASSET_ROOT / ILLUST[slide_id]
    return image(path, 'slide-illust', '内容を補うイラスト')


def card(text: str, *, alert: bool = False, compact: bool = False) -> str:
    classes = 'info-card' + (' alert' if alert else '') + (' compact' if compact else '')
    return f'<div class="{classes}">{e(text)}</div>'


def standard(slide_id: str, title: str, body: str, price: bool = False, sparse: bool = False, summary: bool = False) -> str:
    price_class = ' price-note' if price else ''
    sparse_class = ' sparse' if sparse else ''
    summary_class = ' summary-slide' if summary else ''
    illustration = '' if summary else f'  {illust(slide_id)}\n'
    return f'''<!-- Slide ID: {e(slide_id)} -->
<div class="slide-container slide-pad{price_class}{sparse_class}{summary_class}">
  <div class="watermark">{e(slide_id)}</div>
  <h2 class="slide-title">{e(title).replace(chr(10), '<br>')}</h2>
  <div class="slide-body">{body}</div>
{illustration}</div>'''


def render(slide_id: str, content: str) -> str:
    chunks = [part.strip() for part in content.split('／')]
    if slide_id == '1':
        title = chunks[0].removeprefix('タイトル：')
        first, second = title.split('！', 1)
        return f'''<!-- Slide ID: 1 -->
<div class="slide-container slide-thumbnail price-note">
  <div class="thumb-top-strip">⚡ 2026年12月 ahamo料金改定 ⚡</div>
  <div class="thumb-tag">{e(first)}！</div>
  <h1 class="thumb-title">{e(second).replace('？', '？<br>', 1)}</h1>
  <div class="thumb-sub-band">40GBまで月3,135円に</div>
  {image(LOGO, 'thumb-logo', 'ahamo')}
  {image(ASSET_ROOT / ILLUST['1'], 'thumb-illust', '驚く人')}
</div>'''
    if slide_id == '2':
        body = '''<div class="hero-panel"><div class="hero-small">値上げ後もおすすめ</div><div class="hero-number">4つ</div><div class="hero-label">の条件</div></div>
        <div class="large-card alert">全部そろう人だけ</div>'''
        return standard(slide_id, 'ahamo値上げ後も\nおすすめな人は？', body, sparse=True)
    if slide_id == '3':
        current, previous = chunks[1:3]
        current_value = int(re.search(r'([\d,]+)円', current).group(1).replace(',', ''))
        previous_value = int(re.search(r'([\d,]+)円', previous).group(1).replace(',', ''))
        current_label = current.split(' 月額')[0]
        previous_label = previous.split(' 月額')[0]
        body = f'''<div class="fee-grid">
          <div class="fee-cell new"><small>{e(current_label)}</small><strong>{current_value:,}円</strong><span>月額・税込</span></div>
          <div class="fee-cell"><small>{e(previous_label)}</small><strong>{previous_value:,}円</strong><span>月額・税込</span></div>
        </div><div class="fee-detail"><span>30GB</span><span>→</span><b>40GB</b></div>
        <div class="large-card alert">今より月{current_value - previous_value:,}円アップ</div>'''
        return standard(slide_id, chunks[0], body, price=True, sparse=True)
    if slide_id == '4':
        body = '''<div class="condition-dots"><span>①</span><span>②</span><span>③</span><span>④</span></div>
        <div class="hero-panel"><div class="hero-number">4つ全部</div><div class="hero-label">そろう人だけ</div></div>'''
        return standard(slide_id, 'ahamoがぴったりな人の\n4つの条件', body, sparse=True)
    if slide_id == '5':
        body = '''<div class="fact-stack compact-facts">
          <div class="hero-panel"><div class="hero-number">40GB</div><div class="hero-label">まで 月額3,135円</div><div class="hero-small">枠を無駄にしにくい</div></div>
          <div class="large-card">40GBに上限設定</div>
          <div class="large-card alert">超えても料金は上がらず<br>最大1Mbpsで使える</div>
        </div>'''
        return standard(slide_id, '条件①｜毎月30〜40GBを\n高速で使う', body, price=True, sparse=True)
    if slide_id == '6':
        body = '''<div class="fact-stack three-facts">
          <div class="hero-panel"><div class="hero-number">海外</div><div class="hero-label">によく行く</div></div>
          <div class="large-card">追加の手続きなし</div>
          <div class="large-card alert">海外でもデータ通信が使える</div>
        </div>'''
        return standard(slide_id, '条件②｜海外によく行く', body, sparse=True)
    if slide_id == '7':
        body = '''<div class="fact-stack">
          <div class="hero-panel"><div class="hero-number">5分</div><div class="hero-label">かけ放題</div></div>
          <div class="large-card alert">最初から込み</div>
        </div>'''
        return standard(slide_id, '条件③｜5分以内の通話を\nよくかける', body, sparse=True)
    if slide_id == '8':
        body = '''<div class="fact-stack">
          <div class="hero-panel"><div class="hero-small">契約時の事務手数料</div><div class="hero-number">0円</div></div>
          <div class="large-card">初期費用をかけたくない人へ</div>
        </div>'''
        return standard(slide_id, '条件④｜初期費用を\nかけたくない', body, sparse=True)
    if slide_id == '9':
        # Four conditions are separated by numbered glyphs in one CSV field.
        items = [item.strip() for item in re.split(r'(?=[①②③④])', chunks[1]) if item.strip()]
        if len(items) != 4:
            raise ValueError(f'Expected four summary conditions: {items}')
        # These details come from the display-content fields for slides 5–8.
        details = (
            '40GBに上限設定で<br>超えても最大1Mbps',
            '追加の手続きなしで<br>海外でもデータ通信',
            '5分かけ放題が<br>最初から込み',
            '契約事務手数料<br>0円',
        )
        summary = '<div class="summary-grid">' + ''.join(
            f'<div class="info-card"><div class="summary-head"><span class="num">{index}</span>'
            + '<span class="summary-main">' + e(item[1:].strip()).replace('初期費用を', '初期費用を<br>') + '</span></div>'
            + '<div class="summary-detail">' + detail + '</div>'
            + '</div>'
            for index, (item, detail) in enumerate(zip(items, details), 1)
        ) + '</div>'
        return standard(slide_id, '4つ全部そろえば、\nahamoを続けて正解', summary, summary=True)
    if slide_id == '10':
        return f'''<!-- Slide ID: 10 -->
<div class="slide-container cta-slide">
  <div class="cta-content">
    {image(LOGO, 'cta-logo', 'ahamo')}
    <div class="cta-title">{e(chunks[0])}</div>
    <div class="cta-sub">{e(chunks[1])}</div>
    {image(BANNER, 'cta-banner-img', '関連する長尺動画のサムネイル')}
    <div class="cta-arrow">⇧ 本編へ</div>
  </div>
</div>'''
    raise ValueError(f'Unexpected slide ID: {slide_id}')


def main() -> None:
    with CSV_PATH.open(encoding='utf-8-sig', newline='') as f:
        rows = list(csv.DictReader(f))
    slides: dict[str, str] = {}
    prior = ''
    for row in rows:
        slide_id = row['スライドID'].strip()
        content = row['スライドに表示する内容'].strip()
        if content == '同上':
            content = prior
        else:
            prior = content
        if slide_id in slides and slides[slide_id] != content:
            raise ValueError(f'Inconsistent content for slide {slide_id}')
        slides[slide_id] = content
    if list(slides) != [str(i) for i in range(1, 11)]:
        raise ValueError(f'Unexpected slide IDs: {list(slides)}')
    markup = '\n'.join(render(slide_id, content) for slide_id, content in slides.items())
    document = f'''<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>ahamo値上げ｜続ける？乗り換える？</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@700;900&family=Noto+Sans+JP:wght@700;900&display=swap" rel="stylesheet">
<style>{STYLE}</style>
</head>
<body>
{markup}
</body>
</html>
'''
    OUTPUT.write_text(document, encoding='utf-8')
    print(f'Generated {len(slides)} slides: {OUTPUT}')


if __name__ == '__main__':
    main()
