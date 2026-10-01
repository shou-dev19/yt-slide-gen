#!/usr/bin/env python3
"""Render video 50's master CSV into the shared book spread components."""

import csv
import html
import re
from collections import OrderedDict
from pathlib import Path

ROOT = Path('/workspaces/yt-factory/packages/slide-gen')
MASTER = Path('/workspaces/yt-factory/packages/scenario-gen/archive/videos/50_【2026年12月】ahamoが値上げ＆大盛り終了！？対象者と今やるべき3つの対策/long/【2026年12月】ahamoが値上げ＆大盛り終了！？対象者と今やるべき3つの対策.csv')
OUTPUT = ROOT / 'slides.html'
BRAND = '--brand:#C8102E;--brand-deep:#9a0c23;--brand-soft:#fde3e7'
LOGO = 'public/images/logo/Ahamo_logo.png'
CHART = 'public/images/charts/ahamo.png'
RANKS = ('データ料金', '通信品質', '初期費用', '通話料', '店舗サポート', 'オプション')


def esc(s):
    return html.escape(s, quote=True)


def asset(path):
    if not (ROOT / path).is_file():
        raise FileNotFoundError(ROOT / path)
    return esc(path)


def parts(text):
    return [part.strip() for part in text.split('／')]


def spread(slide_id, left, right, *, price=False):
    cls = 'slide-container price-note' if price else 'slide-container'
    return (f'<!-- Slide ID: {slide_id} -->\n<div class="{cls}" style="{BRAND}">'
            f'<div class="book"><div class="spine"></div>'
            f'<div class="page left">{left}</div><div class="page right">{right}</div>'
            '</div></div>')


def page(title, body, *, center=False):
    body_class = 'page-body center' if center else 'page-body'
    return f'<div class="page-head">{esc(title)}</div><div class="{body_class}">{body}</div>'


def lead(text, *, tight=False):
    return f'<div class="lead{" tight" if tight else ""}">{esc(text)}</div>'


def emph(text):
    return f'<div class="emph">{esc(text)}</div>'


def rows(items, *, start=1):
    return '<ul class="rows">' + ''.join(
        f'<li><span class="badge">{i}</span><span class="tx">{esc(s)}</span></li>'
        for i, s in enumerate(items, start)) + '</ul>'


def std(slide_id, kicker, title, footer, *, price=False, title_lines=None):
    cls = 'slide-container std' + (' price-note' if price else '')
    if title_lines:
        assert ''.join(title_lines) == title
        cls += ' std-three-line'
        title_html = '<br>'.join(esc(line) for line in title_lines)
    else:
        title_html = esc(title)
    return (f'<!-- Slide ID: {slide_id} -->\n<div class="{cls}" style="{BRAND}">'
            '<div class="std-burst"></div><div class="std-copy">'
            f'<img class="std-logo" src="{asset(LOGO)}" alt="ahamo">'
            f'<div class="std-kicker">{esc(kicker)}</div>'
            f'<div class="std-title">{title_html}</div>'
            f'<div class="std-footer">{esc(footer)}</div>'
            '</div></div>')


def chapter(slide_id, content):
    match = re.match(r'第(\d)章\s*(.+)', content)
    assert match, (slide_id, content)
    num, title = match.groups()
    # Chapter titles need deliberate phrase boundaries; automatic wrapping split
    # compounds and left 1–3 characters alone on the last line.
    title_lines = {
        '6-0': ('いつ・いくら', '変わるの？'),
        '8-0': ('ahamoの', '独自評価'),
        '11-0': ('それでもahamoを', '選ぶべき4つの条件'),
        '14-0': ('データ量・通信品質で', '外れる人は？'),
        '16-0': ('海外・通話・初期費用で', '外れる人は？'),
    }.get(slide_id)
    if title_lines:
        assert ''.join(title_lines) == title
        title_html = '<br>'.join(f'<span class="chapter-line">{esc(line)}</span>' for line in title_lines)
    else:
        title_html = esc(title)
    left = f'<div class="divider"><div class="kicker">CHAPTER</div><div class="num">{num}</div><div class="seal">FILE No.{num}</div></div>'
    right = (f'<div class="page-body center"><div class="big-title chapter-title chapter-{num}">'
             f'{title_html}</div><div class="lead">第{num}章のポイントを確認</div></div>')
    return spread(slide_id, left, right)


def agenda(slide_id, content):
    p = parts(content)
    chapters = [x.split(' ', 1)[-1] for x in p if re.match(r'第\d章 ', x)]
    # Keep all chapter subjects while making each line readable at the shared 56px size.
    compact = ('料金改定', 'ahamoの独自評価', '選ぶべき4条件', 'データ量・通信品質', '海外・通話・初期費用', 'まとめ')
    assert len(chapters) == len(compact) == 6
    benefits = [x.strip() for x in re.split(r'[①②③]', p[-1].split('】', 1)[1]) if x.strip()]
    assert len(benefits) == 3
    left = page('格安SIM図鑑 もくじ', '<ul class="agenda">' + ''.join(
        f'<li><span class="num">{i:02d}</span><span>{esc(x)}</span></li>'
        for i, x in enumerate(compact, 1)) + '</ul>')
    right = page('この動画でわかること', '<ul class="benefits">' + ''.join(
        f'<li><span class="check">✓</span><span>{esc(x)}</span></li>' for x in benefits) + '</ul>')
    return spread(slide_id, left, right)


def eval_details(content):
    p = parts(content)
    assert p[0] == '評価見開き' and p[1] == 'ahamo'
    overall = p[2].split(':', 1)[1]
    findings = []
    for name in RANKS:
        entry = next(x for x in p if x.startswith(name + ':'))
        match = re.match(r'[^:]+:([A-Z]+)（＋(.+)', entry)
        assert match, entry
        rank, pro = match.groups()
        # The separator inside each criterion is also a full-width slash.
        idx = p.index(entry)
        con = p[idx + 1].removeprefix('－').removesuffix('）')
        findings.append((name, rank, pro, con))
    return overall, findings


def evaluation_intro(slide_id, content):
    eval_details(content)
    left = (f'<div class="head-left"><img class="logo" src="{asset(LOGO)}" alt="ahamo">'
            '<span class="file-no">料金と評価</span></div>'
            f'<div class="page-body center"><div class="visual"><img src="{asset(CHART)}" alt="ahamoの6観点レーダーチャート"></div></div>')
    p = parts(content)
    data = next(x for x in p if x.startswith('データ料金:'))
    price = re.search(r'月額[\d,]+円', data)
    assert price
    right = page('ahamoの料金プラン',
                 '<div class="lead">12月1日から使った量で決まる3段階</div>'
                 '<table class="sheet"><tr><th>利用量</th><th>月額</th></tr>'
                 '<tr><td>40GBまで</td><td>3,135円</td></tr>'
                 '<tr><td>60GBまで</td><td>4,125円</td></tr>'
                 '<tr><td>120GBまで</td><td>5,115円</td></tr></table>')
    return spread(slide_id, left, right, price=True)


def evaluation(slide_id, content):
    overall, findings = eval_details(content)
    # All source wording stays in data-full; the video-sized card uses a concise
    # reading of the same facts so all six criteria fit above the subtitle band.
    summaries = {
        'データ料金': ('40GBまで月額3,135円・上限後も最大1Mbps', '小容量は割高・繰り越し不可'),
        '通信品質': ('ドコモ回線をそのまま使える', '大手4社比較でドコモは最下位'),
        '初期費用': ('契約事務手数料0円', '契約解除料1,100円の場合あり'),
        '通話料': ('国内5分通話が無料', '超過分は30秒22円'),
        '店舗サポート': ('ドコモショップで有料サポート', '基本はオンライン専用'),
        'オプション': ('海外でも手続き不要・12月から40GB', '大盛りは11月30日終了'),
    }
    def card(item):
        name, rank, pro, con = item
        short_pro, short_con = summaries[name]
        return (f'<div class="card"><span class="rank {esc(rank)}">{esc(rank)}</span>'
                f'<div class="card-name">{esc(name)}</div>'
                f'<div class="line pro" data-full="{esc(pro)}"><span class="tag">＋</span>{esc(short_pro)}</div>'
                f'<div class="line con" data-full="{esc(con)}"><span class="tag">－</span>{esc(short_con)}</div></div>')
    left = (f'<div class="head-left"><img class="logo" src="{asset(LOGO)}" alt="ahamo">'
            f'<div class="total"><div class="label">総合評価</div><div class="grade">{esc(overall)}</div></div></div>'
            '<div class="cards">' + ''.join(map(card, findings[:3])) + '</div>')
    right = ('<div class="cards">' + ''.join(map(card, findings[3:])) + '</div>'
             '<div class="note" style="font-size:28px;text-align:center;">※本評価は当チャンネルの独断と偏見による独自評価であり、キャンペーン割引等は考慮していません</div>')
    return spread(slide_id, left, right, price=True)


def past_video(slide_id, content):
    key = '39_' if slide_id == '7-3' else '【2026年最新】ドコモの通信品質が4キャリア中最下位'
    files = sorted((ROOT / 'public/images/thumbnails').glob(key + '*.png'))
    assert files, key
    image = asset('public/images/thumbnails/' + files[-1].name)
    left = page('関連動画もチェック', f'<div class="visual"><img src="{image}" alt="過去動画サムネイル"></div>')
    right = page('もっと詳しく', '<div class="bigicon">▶</div>' + lead(parts(content)[0].removeprefix('テロップ：')), center=True)
    return spread(slide_id, left, right)


def body_slide(slide_id, content):
    p = parts(content)
    if slide_id == '7':
        left = page('ahamoの新料金', '<table class="sheet"><tr><th>データ量</th><th>月額</th></tr>' + ''.join(
            f'<tr><td>{esc(x.split("：")[0])}</td><td>{esc(x.split("：")[1].replace("月額", ""))}</td></tr>'
            for x in p[2:5]) + '</table>')
        right = page('現行料金との違い', lead(p[5]) + lead(p[6], tight=True), center=True)
    elif slide_id == '7-1':
        left = page('値上げの対象', emph('ahamo契約者 全員') + lead(p[2]))
        right = page('上限設定に注意', lead(p[3], tight=True) + emph(p[4]), center=True)
    elif slide_id == '7-2':
        left = page('上限設定は無料', emph(p[2]) + lead('予想外の料金アップを防ぎやすい'), center=True)
        assert len(p) == 5 and p[3].endswith('（LINEMOベストプラン：3GB 月額990円（税込）→10GBまで月額2,090円（税込）')
        assert p[4] == 'Rakuten最強プラン：3GB 月額1,078円（税込）→20GBまで月額2,178円（税込））'
        _, linemo = p[3].split('（', 1)
        right = page('3GBを少し超えると…',
                     '<div class="lead tight price-lead">'
                     '<div>ショウの経験：楽天モバイルやLINEMOで3GB超え→料金アップ（</div>'
                     f'<div class="price-case">{esc(linemo)}／</div>'
                     f'<div class="price-case">{esc(p[4])}</div>'
                     '</div>', center=True)
    elif slide_id == '9-1':
        left = page('「Sなのに最下位？」', lead(p[0].removeprefix('テロップ：')) + lead(p[1], tight=True), center=True)
        right = page('比べる相手が違う', lead('当チャンネルはオンライン専用プランと格安SIMも比較', tight=True) + emph(p[3].split('：', 1)[1]), center=True)
    elif slide_id == '12':
        left = page('ahamoを選ぶ4条件', rows([re.sub(r'^[①②③④]', '', x) for x in p[2:4]]))
        right = page('4つ全部ならおすすめ', rows([re.sub(r'^[①②③④]', '', x) for x in p[4:6]], start=3))
    elif slide_id == '15':
        assert '最大3Mbpsのパケット放題が無料' in p[3] and 'データ繰り越しあり' in p[3]
        assert p[6] == 'povo2.0 データ追加30GB（30日間）2,780円'
        left = page('データ量で選ぶ',
                    '<ul class="rows data-choice">'
                    '<li><span class="badge">1</span><span class="tx">3GB・20GB未満：LINEMO・povo2.0・楽天モバイル</span></li>'
                    '<li><span class="badge">2</span><span class="tx">低速ならmineo：15GB 1,958円／30GB 2,178円'
                    '<span class="sub">最大3Mbpsのパケット放題無料・繰り越しあり</span></span></li>'
                    '<li><span class="badge">3</span><span class="tx">高速50GB：日本通信SIM 2,178円</span></li>'
                    '</ul>')
        right = page('通信品質で選ぶ', lead(p[5], tight=True).replace(
                         'LINEMOベストプランV', '<span style="white-space:nowrap">LINEMOベストプランV</span>')
                     + lead(p[6], tight=True), center=True)
    elif slide_id == '17':
        assert all(x in content for x in ('LINEMO', '楽天モバイル', 'HISモバイル', '日本通信SIM', 'povo2.0', 'mineo'))
        left = page('海外・初期費用で選ぶ', rows([
            'LINEMO：海外7日間無料（要申込）',
            '楽天モバイル：月2GB／HISモバイル：年1回4GB',
            '初期費用0円：povo2.0・楽天モバイル・mineo提携リンクeSIM']))
        right = page('通話で選ぶ', '<table class="sheet"><tr><th>サービス</th><th>通話</th></tr>'
                     '<tr><td>LINEMO</td><td>5分込み</td></tr>'
                     '<tr><td>楽天モバイル</td><td>Linkで無料</td></tr>'
                     '<tr><td>HISモバイル</td><td>6分かけ放題</td></tr>'
                     '<tr><td>日本通信SIM</td><td>5分or70分</td></tr></table>'
                     '<div class="note" style="font-size:28px;">※mineoの物理SIMは発行料440円</div>')
    elif slide_id == '17-1':
        left = page('今やるべき3つの対策', rows([re.sub(r'^[①②③]', '', x) for x in p[2:4]]))
        right = page('条件に合う1枚へ', emph(re.sub(r'^[①②③]', '', p[4])), center=True)
    elif slide_id == '19':
        left = page('今回のまとめ', rows([re.sub(r'^[①②③]', '', x) for x in p[1:3]]))
        right = page('ahamoを選ぶ人', emph(re.sub(r'^[①②③]', '', p[3])), center=True)
    elif slide_id == '20':
        assert 'https://www.linemo.jp/' in content and p[-1] == '※料金・条件は動画投稿時点の情報です'
        left = page('投稿時点のご注意',
                    '<div class="bigicon"><i class="fa-solid fa-circle-info" aria-hidden="true"></i></div>'
                    '<div class="big-title">ご注意</div>'
                    f'<div class="lead tight posting-note">{esc(p[-1])}</div>', center=True)
        right = page('公式サイトで確認',
                     '<div class="warn">申し込みの際は必ず各社の公式サイトをご確認ください</div>'
                     '<ul class="rows official-links">'
                     '<li><span class="ic"><i class="fa-solid fa-circle-check" aria-hidden="true"></i></span><span class="tx">ahamoの料金改定はahamo公式サイトの内容が正</span></li>'
                     '<li><span class="ic"><i class="fa-solid fa-circle-check" aria-hidden="true"></i></span><span class="tx">LINEMOの詳細はソフトバンク公式<br><span class="official-url">https://www.linemo.jp/</span></span></li>'
                     '</ul>')
    elif slide_id == '21':
        assert p[1] == 'あなたの使い方・エリアの電波・わかりにくかった点、ぜひ教えてください'
        left = page('コメント募集',
                    '<div class="bigicon"><i class="fa-solid fa-comments" aria-hidden="true"></i></div>'
                    '<div class="big-title comments-title">コメント<br>ありがとう<br>ございます！</div>', center=True)
        right = page('ぜひ教えてください', rows(['あなたの使い方', 'エリアの電波状況', 'わかりにくかった点']))
    elif slide_id == '22':
        assert p[0].startswith('テロップ：値上げのタイミングこそ、')
        left = page('今が見直すチャンス',
                    '<div class="big-title closing-title">値上げの<br>タイミングこそ</div>'
                    + emph('自分に合う1枚を見直すチャンス')
                    + lead(p[1]))
        right = page('これからも発信します',
                     '<div class="bigicon closing-icon"><i class="fa-solid fa-pen" aria-hidden="true"></i></div>'
                     + lead(p[2])
                     + lead('ブログとnoteの記事は概要欄から', tight=True))
    elif slide_id in ('13', '23'):
        left = page('チャンネル登録',
                    '<div class="bigicon">🔔</div><div class="big-title subscribe-title">'
                    'チャンネル登録<br><span class="subscribe-request">よろしくお願いします！</span></div>', center=True)
        right_head = '速報を見逃さない！' if slide_id == '13' else 'ご視聴ありがとうございます！'
        right = page(right_head, '<div class="bigicon">👍</div>' + lead(p[0].removeprefix('テロップ：')), center=True)
    else:
        raise ValueError((slide_id, content))
    return spread(slide_id, left, right, price=bool(re.search(r'[\d,]+円', content)))


def main():
    with MASTER.open(encoding='utf-8-sig', newline='') as file:
        slides = OrderedDict()
        for row in csv.DictReader(file):
            slide_id = row['スライドID']
            content = row['スライドに表示する内容']
            if slide_id and content and content != '同上':
                if slide_id in slides and slides[slide_id] != content:
                    raise ValueError(f'Conflicting display content for {slide_id}')
                slides[slide_id] = content
    output = []
    for slide_id, content in slides.items():
        if slide_id == '1':
            markup = std(slide_id, '速報｜2026年12月1日から', content.removeprefix('テロップ：'), 'ahamoの料金が変わる')
        elif slide_id == '2':
            p = parts(content)
            old = re.search(r'(\d+GB).*?月額([\d,]+円)', p[2])
            new = re.search(r'(\d+GB).*?月額([\d,]+円)', p[1])
            change = re.search(r'([+-]\d+円)', p[2])
            assert old and new and change
            price_change = f'{old[1]} {old[2]} → {new[1]} {new[2]}（{change[1]}）'
            markup = std(slide_id, '使った量で決まる3段階', p[0].removeprefix('テロップ：'),
                         price_change, price=True,
                         title_lines=('ahamoは12月1日から', '使った量で決まる', '3段階の料金に'))
        elif slide_id == '3':
            p = parts(content)
            markup = std(slide_id, '大盛りオプション', p[0].removeprefix('テロップ：'), p[1])
        elif slide_id == '4':
            markup = std(slide_id, '格安SIM図鑑｜特集', 'ahamo値上げ＆大盛り終了', '対象者と今やるべき3つの対策')
        elif slide_id == '5':
            markup = agenda(slide_id, content)
        elif slide_id in ('6-0', '8-0', '11-0', '14-0', '16-0', '18-0'):
            markup = chapter(slide_id, content)
        elif slide_id == '9-0':
            markup = evaluation_intro(slide_id, content)
        elif slide_id == '9':
            markup = evaluation(slide_id, content)
        elif slide_id in ('7-3', '9-2'):
            markup = past_video(slide_id, content)
        else:
            markup = body_slide(slide_id, content)
        output.append(markup)
    css = '''
    .slide-container.std {width:1280px;height:720px;border:10px solid #C8102E;background:#fff;display:flex;align-items:center;justify-content:center;padding:40px;}
    .std-burst {position:absolute;inset:0;background:repeating-conic-gradient(from 0deg at 50% 45%,rgba(200,16,46,.07) 0deg 5deg,transparent 5deg 10deg);}
    .std-copy {position:relative;z-index:1;width:100%;display:flex;flex-direction:column;align-items:center;text-align:center;gap:20px;}
    .std-logo {width:320px;height:95px;object-fit:contain;background:#fff;border-radius:18px;padding:8px 24px;box-shadow:0 8px 25px #0002;}
    .std-kicker {font-size:48px;font-weight:900;color:#9a0c23;}
    .std-title {font-size:86px;font-weight:900;line-height:1.18;color:#212121;word-break:auto-phrase;text-wrap:balance;}
    .std-footer {font-size:44px;font-weight:900;background:#C8102E;color:#fff;padding:12px 28px;border-radius:12px;}
    .std-three-line .std-copy {gap:12px;}
    .std-three-line .std-logo {height:85px;}
    .chapter-line {white-space:nowrap;}
    .chapter-3 {font-size:88px;}
    .chapter-4,.chapter-5 {font-size:72px;}
    .subscribe-title {font-size:92px;}
    .subscribe-request {font-size:68px;white-space:nowrap;}
    .price-lead {display:flex;flex-direction:column;gap:15px;}
    .price-case {background:#fff;border-radius:12px;padding:16px 18px;font-size:44px;font-weight:900;line-height:1.35;}
    .data-choice .tx .sub {font-size:38px;line-height:1.3;}
    .data-choice li {padding:12px 18px;}
    .official-links .tx {font-size:40px;}
    .official-links li {padding:18px 22px;}
    .official-url {font-size:38px;white-space:nowrap;}
    .posting-note {padding:20px 28px;}
    .comments-title {font-size:92px;}
    .closing-title {font-size:84px;}
    .closing-icon {font-size:180px;}
    '''
    document = ('<!DOCTYPE html><html lang="ja"><head><meta charset="utf-8">'
                '<link href="https://fonts.googleapis.com/css2?family=M+PLUS+Rounded+1c:wght@400;500;700;800;900&display=swap" rel="stylesheet">'
                '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">'
                '<link rel="stylesheet" href="templates/spread-base.css">'
                f'<style>{css}</style></head><body>\n' + '\n'.join(output) + '\n</body></html>\n')
    OUTPUT.write_text(document, encoding='utf-8')
    print(f'Generated {len(output)} slides: {OUTPUT}')


if __name__ == '__main__':
    main()
