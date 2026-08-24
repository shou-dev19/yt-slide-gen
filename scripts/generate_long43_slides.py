#!/usr/bin/env python3
"""Build the long-43 slide deck from the master scenario CSV.

The deck is deliberately data-driven: every HTML slide is selected from its
``スライドに表示する内容`` field and emitted through the shared spread CSS
components.  Edit this generator, then rerun it; do not hand edit slides.html.
"""
from __future__ import annotations

import csv
import html
from pathlib import Path

ROOT = Path('/workspaces/yt-factory/packages/slide-gen')
CSV_PATH = Path('/workspaces/yt-factory/packages/scenario-gen/archive/videos/43_【2026年10月】楽天モバイル、繋がらないエリアが拡大？乗り換えずに備える2枚持ちという技/long/【2026年10月】楽天モバイル、繋がらないエリアが拡大？乗り換えずに備える2枚持ちという技.csv')
OUT = ROOT / 'slides.html'

RED = '--brand:#C8102E;--brand-deep:#9a0c23;--brand-soft:#fde3e7'
BLUE = '--brand:#1565C0;--brand-deep:#0d47a1;--brand-soft:#e3f0fb'
GREEN = '--brand:#22a73f;--brand-deep:#1c8b34;--brand-soft:#e8f5e6'


def e(value: str) -> str:
    return html.escape(value, quote=True)


def read_display() -> dict[str, str]:
    result: dict[str, str] = {}
    with CSV_PATH.open(encoding='utf-8-sig', newline='') as fh:
        for row in csv.DictReader(fh):
            slide_id = row['スライドID'].strip()
            display = row['スライドに表示する内容'].strip()
            if slide_id and display and slide_id not in result:
                result[slide_id] = display
    return result


def split_display(display: str) -> list[str]:
    display = display.removeprefix('テロップ：').removeprefix('タイトル：')
    return [part.strip() for part in display.split('／') if part.strip()]


def spread(slide_id: str, left: str, right: str, style: str = RED, *, price: bool = False) -> str:
    klass = 'slide-container price-note' if price else 'slide-container'
    return f'''<!-- Slide ID: {e(slide_id)} -->
<div class="{klass}" style="{style}">
  <div class="book"><div class="spine"></div>{left}{right}</div>
</div>'''


def page(side: str, head: str, body: str, no: int | None, *, tab: bool = False) -> str:
    tab_html = '<span class="index-tab">格安SIM図鑑</span>' if tab else ''
    head_html = f'<div class="page-head">{head}</div>' if head else ''
    no_html = f'<span class="page-no">― {no} ―</span>' if no else ''
    return f'<div class="page {side}">{tab_html}{head_html}<div class="page-body">{body}</div>{no_html}</div>'


def rows(items: list[str], *, numbered: bool = False, start: int = 1) -> str:
    rendered = []
    for index, item in enumerate(items, start):
        token = f'<span class="badge">{index}</span>' if numbered else '<span class="ic"><i class="fa-solid fa-circle-check"></i></span>'
        rendered.append(f'<li>{token}<div class="tx">{e(item)}</div></li>')
    return '<ul class="rows">' + ''.join(rendered) + '</ul>'


def generic_spread(slide_id: str, display: str, page_no: int, style: str = RED) -> str:
    parts = split_display(display)
    title, items = parts[0], parts[1:]
    title = display_heading(slide_id, title)
    # Two-point slides are common in this script.  A one-row list on each
    # page looks unfinished in a book spread, so use the same CSV facts as a
    # large conclusion plus a supporting statement instead.
    if len(items) <= 2:
        main = items[0] if items else '楽天モバイルを残したまま、必要な場面だけ2枚目へ切り替える'
        support = items[1] if len(items) == 2 else '普段は楽天モバイル、必要な時だけ予備回線を使う'
        left_body = f'<div class="bigicon"><i class="fa-solid fa-circle-check"></i></div><div class="emph">{e(main)}</div>'
        right_body = f'<div class="bigicon"><i class="fa-solid fa-lightbulb"></i></div><div class="lead" style="text-align:center">{e(support)}</div><div class="note" style="text-align:center">楽天モバイルを活かして、安心を足す選び方</div>'
        left = page('left', title, left_body, page_no)
        right = page('right', 'ここが大事', right_body, page_no + 1, tab=True)
        return spread(slide_id, left, right, style, price=('円' in display and ('月額' in display or '料金' in display)))
    midpoint = max(1, (len(items) + 1) // 2)
    left_items, right_items = items[:midpoint], items[midpoint:]
    if not right_items:
        right_items = ['楽天モバイルを残したまま、必要な場面だけ2枚目へ切り替える']
    left = page('left', title, rows(left_items), page_no)
    right = page('right', right_heading(slide_id), rows(right_items), page_no + 1, tab=True)
    return spread(slide_id, left, right, style, price=('円' in display and ('月額' in display or '料金' in display)))


def display_heading(slide_id: str, title: str) -> str:
    """Compose the remaining long headings at meaningful Japanese boundaries."""
    return {
        '6': '10月から何が変わる？<br><small>1分でおさらい</small>',
    }.get(slide_id, e(title))


def right_heading(slide_id: str) -> str:
    """Give each right page a subject-specific heading, never a stock label."""
    headings = {
        '6': '終了で変わる<br>つながり方',
        '11': '維持条件と<br>利用停止の注意',
        '11-1': '混雑時に役立つ<br>予備回線',
        '11-2': '0円維持の仕組みと<br>注意点',
        '12': '1GBを安く持つ<br>料金と条件',
        '12-1': 'ドコモ回線で<br>穴を埋める',
        '13': '選べる3回線と<br>マイそく料金',
        '13-1': '緊急用での<br>速度制限',
        '13-2': '3Mbpsを選ぶ<br>実用的な理由',
        '15': '対応端末と<br>初期費用を確認',
        '15-2': '申し込み前の<br>費用をチェック',
        '16': '2枚持ちを<br>シンプルに考える',
    }
    return headings.get(slide_id, 'ポイントを整理')


def chapter(slide_id: str, display: str, number: int, style: str = RED) -> str:
    topic = display.removeprefix(f'第{number}章 ').strip()
    if display == 'まとめ':
        topic = '今日の内容をおさらい'
    # Chapter themes are deliberately composed at phrase boundaries so their
    # large type never leaves a one-character orphan on the second line.
    topic = {
        '10月から何が変わる？': '10月から何が<br>変わる？',
        '用途別・おすすめの2枚目3選': '用途別・<br>おすすめの2枚目3選',
        '始める前の注意点': '始める前の<br>注意点',
    }.get(topic, e(topic))
    left = f'''<div class="page left"><div class="divider"><div class="kicker">CHAPTER</div><div class="num">{number}</div><div class="seal">FILE No.{number:02d}</div></div></div>'''
    right = f'''<div class="page right"><span class="index-tab">格安SIM図鑑</span><div class="page-body center"><div class="big-title">{topic}</div><div class="lead" style="text-align:center">楽天モバイルを活かす<br>2枚持ちのポイントを解説</div></div></div>'''
    return spread(slide_id, left, right, style)


def std(slide_id: str, kicker: str, title: str, chips: list[str]) -> str:
    chip_html = ''.join(f'<span>{e(x)}</span>' for x in chips)
    return f'''<!-- Slide ID: {slide_id} -->
<div class="slide-container std" style="{RED}">
  <div class="std-rays"></div><div class="std-corner">2026年10月</div>
  <div class="std-copy"><div class="std-kicker">{e(kicker)}</div><h1>{title}</h1><div class="std-chips">{chip_html}</div></div>
</div>'''


def cta(slide_id: str, display: str, image: str, title: str, page_no: int) -> str:
    left = page('left', '詳しく解説した過去動画', f'<div class="visual"><img src="{image}" alt="過去動画のサムネイル"></div>', page_no)
    title_html = '<br>'.join(e(line) for line in title.splitlines())
    right = page('right', '', f'<div class="bigicon"><i class="fa-solid fa-play"></i></div><div class="big-title cta-title">{title_html}</div><div class="lead" style="text-align:center">気になる方は<br>こちらもチェック！</div>', page_no + 1, tab=True)
    return spread(slide_id, left, right, RED)


def agenda(slide_id: str, display: str, page_no: int) -> str:
    parts = split_display(display)
    chapters = [x for x in parts if x.startswith('第')]
    benefits_text = next(x for x in parts if x.startswith('【この動画'))
    benefit_parts = benefits_text.replace('【この動画でわかること】', '').split('  ')
    left = page('left', '格安SIM図鑑 もくじ', '<ul class="agenda">' + ''.join(f'<li><span class="num">{i}</span>{e(x)}</li>' for i, x in enumerate(chapters, 1)) + '</ul>', page_no)
    right = page('right', 'この動画でわかること', '<ul class="benefits">' + ''.join(f'<li><span class="check">✓</span>{e(x)}</li>' for x in benefit_parts) + '</ul><div class="emph agenda-answer">楽天モバイルはそのまま。<br><span class="em">安い2枚目</span>を足せばいい！</div>', page_no + 1, tab=True)
    return spread(slide_id, left, right, RED)


def dual_sim(slide_id: str, display: str, page_no: int) -> str:
    parts = split_display(display)
    left = page('left', '2枚持ち<br>（デュアルSIM）とは？', '<div class="bigicon"><i class="fa-solid fa-mobile-screen-button"></i></div><div class="emph">スマホ1台に<br><span class="big">SIMを2枚</span></div>', page_no)
    right = page('right', '使い方はシンプル', rows(parts[1:]), page_no + 1, tab=True)
    return spread(slide_id, left, right, RED)


def comparison(slide_id: str, display: str, page_no: int) -> str:
    parts = split_display(display)
    left = page('left', e(parts[0]), '<div class="emph">出番は<br><span class="big">つながらない時だけ</span></div><div class="lead">だから2枚目は<br><span class="em">毎月の安さ</span>を重視</div>', page_no)
    right = page('right', '選び方は用途別', rows(parts[1:]), page_no + 1, tab=True)
    return spread(slide_id, left, right, RED)


def summary(slide_id: str, display: str, page_no: int) -> str:
    parts = split_display(display)
    left = page('left', '今日のまとめ', rows(parts[1:3], numbered=True), page_no)
    right = page('right', '自分に合う2枚目を<br>選ぼう', rows(parts[3:], numbered=True, start=3), page_no + 1, tab=True)
    return spread(slide_id, left, right, RED)


def logo_lockup(src: str, alt: str, caption: str) -> str:
    return f'''<div class="brand-lockup"><img src="{src}" alt="{e(alt)}"><span>{e(caption)}</span></div>'''


def carrier_recommendation(slide_id: str, page_no: int) -> str:
    """Use a logo plus a plan-focused component for each recommended carrier."""
    if slide_id == '11':
        left = page('left', 'おすすめ①<br>通信品質重視ならpovo2.0', logo_lockup('public/images/logo/Povo_logo.png', 'povo2.0', 'au回線をそのまま使える') + '<div class="emph">ベースプラン<br><span class="big">月額0円</span></div><div class="note" style="text-align:center">必要な時だけデータをトッピング</div>', page_no)
        right = page('right', '維持条件と<br>利用停止の注意', '<div class="emph">契約解除料<br><span class="big">0円</span></div>' + rows(['最低利用期間なし', '180日間購入なしで利用停止'], numbered=True) + '<div class="note" style="text-align:center">※2026年8月時点の料金です</div>', page_no + 1, tab=True)
        return spread(slide_id, left, right, BLUE, price=True)
    if slide_id == '12':
        left = page('left', 'おすすめ②<br>安さ重視なら日本通信SIM', logo_lockup('public/images/logo/nihon_tsushin.jpg', '日本通信SIM', 'ドコモ回線の低価格SIM') + '''<table class="sheet compact-sheet"><tr><th>プラン</th><th>データ量</th><th>月額</th></tr><tr><td>合理的<br>シンプル290</td><td>1GB</td><td><span class="em">290円</span></td></tr></table><div class="lead" style="text-align:center">緊急用の2枚目を<br><span class="em">とにかく安く</span>持ちたい人へ</div>''', page_no)
        right = page('right', '1GBを安く持つ<br>料金と条件', '<div class="emph">緊急時だけなら<br><span class="big">1GBでOK</span></div>' + rows(['回線はドコモ', 'データ繰越なし・契約解除料0円'], numbered=True) + '<div class="note" style="text-align:center">※2026年8月時点の料金です</div>', page_no + 1, tab=True)
        return spread(slide_id, left, right, RED, price=True)
    left = page('left', 'おすすめ③<br>回線を選べるmineo', logo_lockup('public/images/logo/Mineo_logo.png', 'mineo', 'ドコモ・au・ソフトバンクから選べる') + '''<table class="sheet compact-sheet"><tr><th>プラン</th><th>最大速度</th><th>月額</th></tr><tr><td>マイそく<br>ライト</td><td>300kbps</td><td><span class="em">660円</span></td></tr></table><div class="lead" style="text-align:center">特に<span class="em">ソフトバンク回線</span>を<br>選びたい人に</div>''', page_no)
    right = page('right', '選べる3回線と<br>マイそく料金', '<div class="emph">データ容量<br><span class="big">無制限</span></div>' + rows(['自分に合う回線を選べる', '契約解除料0円'], numbered=True) + '<div class="note" style="text-align:center">※2026年8月時点の料金です</div>', page_no + 1, tab=True)
    return spread(slide_id, left, right, GREEN, price=True)


def experience_povo(slide_id: str, page_no: int) -> str:
    left = page('left', 'ショウの実体験', rows(['混雑したイベント会場では、都心でも楽天モバイルがつながらず困った', 'そのときpovoに助けてもらった']), page_no)
    right_body = '''<div class="visual support-illustration"><img src="public/images/irasutoya/smartphone_nidaimochi_man.png" alt="2台持ちのスマホ利用イメージ"></div><div class="lead" style="text-align:center">友人や同僚に相談されたら<br><span class="em">まず勧められる1枚</span></div>'''
    right = page('right', '混雑時に役立つ<br>予備回線', right_body, page_no + 1, tab=True)
    return spread(slide_id, left, right, BLUE)


def docomo_reason(slide_id: str, page_no: int) -> str:
    left = page('left', 'それでもドコモ回線が<br>効く理由', rows(['楽天モバイルが弱いのは、屋内・郊外・混雑エリア', 'エリアの広いドコモ回線が、郊外の穴を埋める']), page_no)
    right_body = '''<div class="network-pair"><img src="public/images/logo/Mobile_logo_1line_magenta.png" alt="楽天モバイル"><i class="fa-solid fa-arrow-right"></i><img src="public/images/logo/docomo_logo.png" alt="ドコモ"></div><div class="emph">緊急時だけなら<br><span class="big">1GBで足りる</span></div><div class="lead" style="text-align:center">ふだんは楽天モバイル<br>必要な時だけ切り替え</div>'''
    right = page('right', 'ドコモ回線で<br>穴を埋める', right_body, page_no + 1, tab=True)
    return spread(slide_id, left, right, RED)


def mineo_speed(slide_id: str, page_no: int) -> str:
    left_body = '''<div class="brand-lockup"><img src="public/images/logo/Mineo_logo.png" alt="mineo"><span>最大速度で選ぶ「マイそく」</span></div><table class="sheet compact-sheet"><tr><th>コース</th><th>最大速度</th><th>月額</th></tr><tr><td>ライト</td><td>300kbps</td><td><span class="em">660円</span></td></tr><tr><td>スーパーライト</td><td>32kbps</td><td>250円</td></tr></table>'''
    left = page('left', 'mineo「マイそく」は<br>最大速度で選ぶプラン', left_body, page_no)
    right = page('right', '緊急用での<br>速度制限', '<div class="warn"><span class="ic"><i class="fa-solid fa-triangle-exclamation"></i></span>スーパーライトの32kbpsは<br><span class="em">緊急用には現実的でない</span></div><div class="emph">平日12時〜13時は<br><span class="big">最大32kbps</span></div>', page_no + 1, tab=True)
    return spread(slide_id, left, right, GREEN, price=True)


def mineo_usage(slide_id: str, page_no: int) -> str:
    left = page('left', 'ショウ自身のmineoの使い方', '''<table class="sheet compact-sheet"><tr><th>内訳</th><th>月額</th></tr><tr><td>マイピタ 3GB</td><td><span class="em">1,298円</span></td></tr><tr><td>パケット放題（最大3Mbps）</td><td>385円</td></tr><tr><td>パスケット</td><td>110円</td></tr></table><div class="lead" style="text-align:center">3GBを超えた高速通信は<br>ほとんど使わない運用</div>''', page_no)
    right = page('right', '3Mbpsを選ぶ<br>実用的な理由', '<div class="emph">高速通信は月3GB未満<br><span class="big">3Mbpsを追加</span></div><div class="lead" style="text-align:center">あえて有料オプションを付けて<br><span class="em">メイン回線として利用中</span></div>', page_no + 1, tab=True)
    return spread(slide_id, left, right, GREEN, price=True)


def preflight(slide_id: str, page_no: int) -> str:
    left = page('left', '始める前に<br>確認しておきたいこと', '''<table class="sheet compact-sheet full-sheet"><tr><th>確認すること</th><th>見るポイント</th></tr><tr><td>スマホ</td><td>デュアルSIM対応<br>（物理2枚 / 物理＋eSIM）</td></tr><tr><td>申し込み</td><td>初期費用の有無</td></tr></table>''', page_no)
    right_body = '''<div class="warn"><span class="ic"><i class="fa-solid fa-triangle-exclamation"></i></span>契約時には事務手数料など<br><span class="em">初期費用</span>がかかる場合も</div><div class="visual support-illustration"><img src="public/images/irasutoya/kaden_tenin16_woman_ojigi.png" alt="契約前に確認する案内イメージ"></div>'''
    right = page('right', '対応端末と<br>初期費用を確認', right_body, page_no + 1, tab=True)
    return spread(slide_id, left, right, RED)


def mineo_link(slide_id: str, page_no: int) -> str:
    left = page('left', '限定リンクなら<br>事務手数料が無料', logo_lockup('public/images/logo/Mineo_logo.png', 'mineo', '当チャンネル限定リンク') + '<div class="fee-flow"><span>通常</span><strong>3,300円</strong><i class="fa-solid fa-arrow-right"></i><span>限定リンク</span><strong class="free">0円</strong></div><div class="lead" style="text-align:center">申し込みリンクは<br>概要欄・固定コメントへ</div>', page_no)
    right = page('right', '申し込み前の<br>費用をチェック', rows(['通常の申し込みでは事務手数料がかかる', 'リンクは概要欄・固定コメントに掲載'], numbered=True) + '<div class="note" style="text-align:center">申し込み前に条件を確認してください</div>', page_no + 1, tab=True)
    return spread(slide_id, left, right, GREEN, price=True)


def channel_principle(slide_id: str, page_no: int) -> str:
    left = page('left', '当チャンネルの考え方', '<div class="bigicon"><i class="fa-solid fa-coins"></i></div><div class="emph">2枚目は<br><span class="big">安さで選ぶ</span></div><div class="lead" style="text-align:center">出番が少ない予備回線は<br>ランニングコストを抑える</div>', page_no)
    right = page('right', '2枚持ちを<br>シンプルに考える', '<div class="sim-equation"><span>楽天モバイル<br><small>メイン</small></span><b>＋</b><span>安い2枚目<br><small>予備</small></span><b>＝</b><strong>安心</strong></div><div class="emph">考えるのは<br><span class="big">この組み合わせだけ</span></div>', page_no + 1, tab=True)
    return spread(slide_id, left, right, RED)


def special(slide_id: str, display: str, page_no: int) -> str:
    if slide_id == '13-4':
        left = page('left', '', '<div class="bigicon"><i class="fa-solid fa-bell"></i></div><div class="big-title cta-title">値上げ・改悪・終了の<br><span class="em">速報</span>を見逃さない！</div>', page_no)
        right = page('right', 'チャンネル登録で安心', '<div class="bigicon"><i class="fa-solid fa-square-plus"></i></div><div class="lead" style="text-align:center">料金・サービスの変化を<br><span class="em">毎週お届け</span>します</div><div class="note" style="text-align:center">見逃したくない方は登録ボタンをタップ</div>', page_no + 1, tab=True)
        return spread(slide_id, left, right, GREEN)
    if slide_id == '19':
        left = page('left', '', '<div class="bigicon"><i class="fa-solid fa-circle-info"></i></div><div class="big-title">ご注意</div>', page_no)
        right = page('right', 'お申し込み前に', '<div class="warn"><span class="ic"><i class="fa-solid fa-triangle-exclamation"></i></span>料金・回線状況は<br><span class="em">動画投稿時点</span>の情報です</div><div class="lead">必ず各社公式サイトの<br>最新情報を確認してください</div>', page_no + 1, tab=True)
        return spread(slide_id, left, right, RED)
    if slide_id == '20':
        left = page('left', 'コメントで教えてね！', '<div class="bigicon"><i class="fa-solid fa-comments"></i></div><div class="lead" style="text-align:center">あなたの楽天モバイル、<br>つながりやすさはどう？</div>', page_no)
        right = page('right', 'たとえばこんな<br>コメント', rows(['もう2枚持ちしています', 'わたしのエリアの楽天モバイルの電波', 'わかりづらかった点']), page_no + 1, tab=True)
        return spread(slide_id, left, right, RED)
    if slide_id == '21':
        left = page('left', 'スマホ代は大きな固定費', '<div class="bigicon"><i class="fa-solid fa-piggy-bank"></i></div><div class="emph">毎月の見直しで<br><span class="big">暮らしにゆとり</span></div>', page_no)
        right = page('right', '浮いた分を未来へ', '<div class="lead">少しでも多くの方に<br><span class="em">スマホ代の見直し</span>を</div><div class="emph">浮いたお金は<br>貯蓄や好きなことへ</div>', page_no + 1, tab=True)
        return spread(slide_id, left, right, RED)
    if slide_id == '21-1':
        left = page('left', '', '<div class="bigicon"><i class="fa-solid fa-compass"></i></div><div class="big-title cta-title">自分に合う<br><span class="em">1枚</span>が分かる</div>', page_no)
        right = page('right', 'これからも分かりやすく', '<div class="lead">選択肢が多い格安SIMを<br>迷わず選べるように</div><div class="emph">役立つ情報を<br><span class="big">毎週発信中</span></div>', page_no + 1, tab=True)
        return spread(slide_id, left, right, RED)
    if slide_id == '22':
        left = page('left', '', '<div class="bigicon"><i class="fa-solid fa-pen-nib"></i></div><div class="big-title cta-title">ブログ・note<br>でも比較中！</div>', page_no)
        right = page('right', 'リンクは概要欄へ', '<div class="visual blog-image"><img src="public/images/common/ブログ_ヘッダー画像_スライド用.png" alt="ブログの案内"></div><div class="lead" style="text-align:center">格安SIMの料金を<br>さらに詳しく比較しています</div>', page_no + 1, tab=True)
        return spread(slide_id, left, right, RED)
    if slide_id == '23':
        left = page('left', '', '<div class="bigicon"><i class="fa-solid fa-bell"></i></div><div class="big-title cta-title">チャンネル登録<br>よろしくお願いします！</div>', page_no)
        right = page('right', '', '<div class="bigicon">👍　🔔</div><div class="lead" style="text-align:center"><span class="em">ご視聴いただき<br>ありがとうございました！</span></div><div class="note" style="text-align:center">次回もスマホ代節約を一緒に見ていきましょう</div>', page_no + 1, tab=True)
        return spread(slide_id, left, right, RED)
    return generic_spread(slide_id, display, page_no)


def build(display: dict[str, str]) -> list[str]:
    order = list(display)
    pages = 1
    deck: list[str] = []
    ctas = {
        '6-2': ('public/images/thumbnails/35_【2026年10月】楽天モバイルのau回線ローミング終了！？今やるべき3つの対策_サムネ1.png', 'auローミング終了の\n解説動画もチェック！'),
        '11-3': ('public/images/thumbnails/【月最大1GB無料】povo Data Oasis×東京メトロで毎日0円チャージする方法_サムネ1.png', 'povo data oasisを\n詳しく解説！'),
        '12-2': ('public/images/thumbnails/【2026年最新】20GBで1,390円！？日本通信SIMの「SS級」コスパを徹底解剖！メリット・デメリット全公開.png', '日本通信SIMの\n解説動画もチェック！'),
        '13-3': ('public/images/thumbnails/【裏技】mineo歴8年が教える「実質使い放題」の極意！契約前に知らないと損する5つの節約術_サムネ.png', 'mineoの節約術も\nチェック！'),
    }
    chapter_numbers = {'5-0': 1, '7-0': 2, '10-0': 3, '14-0': 4, '17-0': 5}
    for slide_id in order:
        display_text = display[slide_id]
        if slide_id == '1':
            deck.append(std(slide_id, '楽天モバイルユーザーへ速報', '10月から<span>auローミング終了</span>？', ['乗り換えなきゃダメ？', '答えは「2枚持ち」']))
            continue
        if slide_id == '1-2':
            deck.append(std(slide_id, '乗り換えなくても大丈夫', '楽天モバイルに<br><span>「2枚目」</span>を足す技', ['屋内・郊外の不安に備える', 'デュアルSIM']))
            continue
        if slide_id == '2':
            deck.append(std(slide_id, '格安SIM図鑑', '<span>楽天モバイル</span>は残す！<br>2枚持ちで備える', ['用途別・おすすめ3選', '月額を抑えて安心']))
            continue
        if slide_id == '4':
            deck.append(agenda(slide_id, display_text, pages)); pages += 2; continue
        if slide_id in chapter_numbers:
            deck.append(chapter(slide_id, display_text, chapter_numbers[slide_id])); continue
        if slide_id in ctas:
            image, title = ctas[slide_id]
            deck.append(cta(slide_id, display_text, image, title, pages)); pages += 2; continue
        if slide_id == '8':
            deck.append(dual_sim(slide_id, display_text, pages)); pages += 2; continue
        if slide_id == '9':
            deck.append(comparison(slide_id, display_text, pages)); pages += 2; continue
        if slide_id in {'11', '12', '13'}:
            deck.append(carrier_recommendation(slide_id, pages)); pages += 2; continue
        if slide_id == '11-1':
            deck.append(experience_povo(slide_id, pages)); pages += 2; continue
        if slide_id == '12-1':
            deck.append(docomo_reason(slide_id, pages)); pages += 2; continue
        if slide_id == '13-1':
            deck.append(mineo_speed(slide_id, pages)); pages += 2; continue
        if slide_id == '13-2':
            deck.append(mineo_usage(slide_id, pages)); pages += 2; continue
        if slide_id == '15':
            deck.append(preflight(slide_id, pages)); pages += 2; continue
        if slide_id == '15-2':
            deck.append(mineo_link(slide_id, pages)); pages += 2; continue
        if slide_id == '16':
            deck.append(channel_principle(slide_id, pages)); pages += 2; continue
        if slide_id == '18':
            deck.append(summary(slide_id, display_text, pages)); pages += 2; continue
        if slide_id in {'13-4', '19', '20', '21', '21-1', '22', '23'}:
            deck.append(special(slide_id, display_text, pages)); pages += 2; continue
        style = GREEN if slide_id.startswith('13') else BLUE if slide_id.startswith('11') else RED
        deck.append(generic_spread(slide_id, display_text, pages, style)); pages += 2
    return deck


def main() -> None:
    display = read_display()
    deck = build(display)
    document = f'''<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>楽天モバイルを残して備える2枚持ち</title>
<link href="https://fonts.googleapis.com/css2?family=M+PLUS+Rounded+1c:wght@400;500;700;800;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
<link rel="stylesheet" href="templates/spread-base.css">
<style>
body{{--primary-color:#C8102E;--accent-red:#E53935;--text-dark:#212121}}
.slide-container.std{{width:1280px;height:720px;border:10px solid var(--primary-color);background:#fffaf5;box-sizing:border-box;position:relative;overflow:hidden;display:flex;align-items:center;justify-content:center;padding:42px;flex-shrink:0}}
.std-rays{{position:absolute;inset:-35%;background:repeating-conic-gradient(from -12deg at 50% 50%,rgba(200,16,46,.11) 0 6deg,transparent 6deg 13deg)}}
.std-corner{{position:absolute;right:28px;top:28px;background:#fff;color:#9a0c23;border:5px solid #C8102E;border-radius:15px;padding:9px 20px;font-size:38px;font-weight:900;z-index:2}}
.std-copy{{position:relative;z-index:1;width:100%;display:flex;flex-direction:column;align-items:center;text-align:center;margin-top:35px}}
.std-kicker{{font-size:48px;font-weight:900;line-height:1.2;margin-bottom:9px;text-shadow:3px 3px #fff}}
.std-copy h1{{font-size:86px;line-height:1.12;font-weight:900;letter-spacing:-3px;text-shadow:5px 5px #fff;margin:4px 0 22px}}.std-copy h1 span{{color:#E53935;font-size:102px;white-space:nowrap}}
.std-chips{{display:flex;justify-content:center;gap:14px;flex-wrap:wrap;max-width:1100px}}.std-chips span{{font-size:42px;background:#fff;border:5px solid #C8102E;border-radius:999px;padding:8px 23px;box-shadow:0 8px 16px #0002;font-weight:900}}
.page-head{{word-break:auto-phrase;text-wrap:balance;line-height:1.18}}
.page .rows{{gap:14px}}.page .rows li{{padding:18px 24px}}.page .rows .tx{{font-size:40px;line-height:1.28}}.page .rows .ic{{font-size:48px;width:60px}}.page .rows .badge{{width:64px;height:64px;font-size:38px}}
.agenda li{{font-size:42px;gap:17px}}.agenda .num{{width:64px;height:64px;font-size:38px}}.benefits li{{font-size:38px;gap:15px}}.benefits .check{{font-size:48px}}.agenda-answer{{font-size:38px;padding:19px 24px}}.cta-title{{font-size:70px}}.blog-image{{height:330px}}.blog-image img{{width:100%;height:auto;max-height:320px;object-fit:contain}}.page .bigicon{{font-size:190px}}.page .lead{{font-size:42px;padding:24px 28px}}.page .emph{{font-size:45px;padding:27px 30px}}.page .emph .big{{font-size:72px}}
.brand-lockup{{display:flex;align-items:center;justify-content:center;gap:24px;min-height:118px;padding:14px 20px;background:#fff;border:3px solid var(--brand);border-radius:18px;box-shadow:0 5px 12px #00000012}}.brand-lockup img{{max-width:300px;max-height:82px;object-fit:contain}}.brand-lockup span{{font-size:34px;font-weight:900;line-height:1.25;color:var(--ink);text-align:center}}
.compact-sheet{{font-size:42px}}.compact-sheet th,.compact-sheet td{{padding:15px 12px}}.support-illustration{{height:240px}}.support-illustration img{{max-height:230px}}
.full-sheet{{height:100%}}.full-sheet tr{{height:33%}}
.network-pair{{display:flex;align-items:center;justify-content:center;gap:30px;padding:18px 8px}}.network-pair img{{width:235px;height:76px;object-fit:contain}}.network-pair i{{font-size:52px;color:var(--brand)}}
.fee-flow{{display:flex;align-items:center;justify-content:center;gap:16px;flex-wrap:wrap;padding:28px 18px;border:5px solid var(--brand);border-radius:22px;background:var(--brand-soft);font-size:34px;font-weight:900}}.fee-flow strong{{font-size:56px;color:var(--con);white-space:nowrap}}.fee-flow .free{{color:var(--brand-deep)}}.fee-flow i{{font-size:40px;color:var(--brand-deep)}}
.sim-equation{{display:flex;align-items:center;justify-content:center;gap:14px;flex-wrap:wrap;padding:24px 12px;border:5px solid var(--brand);border-radius:22px;background:var(--brand-soft);font-size:38px;font-weight:900;text-align:center;line-height:1.2}}.sim-equation span{{padding:14px 16px;background:#fff;border-radius:15px;box-shadow:0 3px 8px #0002}}.sim-equation small{{font-size:30px;color:var(--ink-soft)}}.sim-equation b{{font-size:52px;color:var(--brand-deep)}}.sim-equation strong{{font-size:58px;color:var(--con)}}
</style></head><body>\n{''.join(deck)}\n</body></html>'''
    OUT.write_text(document, encoding='utf-8')
    print(f'Generated {len(deck)} slides: {OUT}')


if __name__ == '__main__':
    main()
