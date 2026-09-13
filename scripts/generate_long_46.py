#!/usr/bin/env python3
"""Generate the long-form deck for video 46 from its master scenario CSV.

The scenario master is the source of truth for IDs and display directions.
Filesystem paths are absolute for reliable generation, while generated asset
URLs are always project-relative so the deck remains portable.
"""
from __future__ import annotations

import csv
import html
import re
from collections import OrderedDict
from pathlib import Path

ROOT = Path("/workspaces/yt-factory/packages/slide-gen")
MASTER = Path("/workspaces/yt-factory/packages/scenario-gen/archive/videos/46_格安SIM総合満足度No.1は日本通信SIM！サポート満足度No.1はイオンモバイル/long/格安SIM総合満足度No.1は日本通信SIM！サポート満足度No.1はイオンモバイル.csv")
OUTPUT = ROOT / "slides.html"

RED = "--brand:#C8102E;--brand-deep:#9a0c23;--brand-soft:#fde3e7"
BLUE = "--brand:#1565C0;--brand-deep:#0d47a1;--brand-soft:#e3f0fb"
GREEN = "--brand:#22a73f;--brand-deep:#1c8b34;--brand-soft:#e8f5e6"
PURPLE = "--brand:#7b3fa1;--brand-deep:#5b267d;--brand-soft:#f1e4f7"


def e(value: str) -> str:
    return html.escape(value, quote=True)


def asset(*parts: str) -> str:
    """Validate a local asset and return its portable HTML URL.

    Never expose the absolute path used for validation in generated markup:
    the slide capture pipeline permits only ``public/``-relative asset URLs.
    """
    relative = Path("public/images").joinpath(*parts)
    path = ROOT / relative
    if not path.is_file():
        raise FileNotFoundError(path)
    return relative.as_posix()


def load_slides() -> OrderedDict[str, str]:
    """Return first explicit display direction per non-empty slide ID."""
    slides: OrderedDict[str, str] = OrderedDict()
    with MASTER.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            sid = row["スライドID"].strip()
            display = row["スライドに表示する内容"].strip()
            if sid and sid not in slides:
                slides[sid] = display
            elif sid and display and display != "同上":
                # Prefer a concrete direction over an inherited "同上" marker.
                if slides[sid] == "同上":
                    slides[sid] = display
    return slides


def page(head: str, body: str, right: bool = False) -> str:
    tab = '<span class="index-tab">格安SIM図鑑</span>' if right else ""
    heading = f'<div class="page-head">{head}</div>' if head else ""
    return f'<div class="page {"right" if right else "left"}">{tab}{heading}{body}</div>'


def spread(sid: str, left: str, right: str, brand: str = RED, price: bool = False) -> str:
    classes = "slide-container price-note" if price else "slide-container"
    return f'''<!-- Slide ID: {sid} -->
<div class="{classes}" style="{brand}"><div class="book"><div class="spine"></div>{left}{right}</div></div>'''


def body(content: str, cls: str = "") -> str:
    return f'<div class="page-body {cls}">{content}</div>'


def lead(text: str, tight: bool = False) -> str:
    return f'<div class="lead{" tight" if tight else ""}">{text}</div>'


def emph(text: str) -> str:
    return f'<div class="emph">{text}</div>'


def title_lines(*lines: str, variant: str = "") -> str:
    """Render a display title as intentional Japanese phrase lines.

    Big CTA and chapter titles use a much larger typeface than body copy.  A
    browser cannot infer an acceptable break point for every compound word at
    that size, so the generator supplies the semantic phrase boundaries.  Each
    line is kept intact; the compact variant is reserved for a phrase that is
    too long for a page at the normal display-title size.
    """
    class_name = f"title-line {variant}".strip()
    return "".join(f'<span class="{class_name}">{e(line)}</span>' for line in lines)


def rows(items: list[tuple[str, str, str]]) -> str:
    entries = []
    for icon, text, sub in items:
        marker = f'<i class="ic fa-solid {icon}"></i>' if icon.startswith("fa-") else f'<span class="badge">{icon}</span>'
        suffix = f'<span class="sub">{sub}</span>' if sub else ""
        entries.append(f'<li>{marker}<div class="tx">{text}{suffix}</div></li>')
    return '<ul class="rows">' + ''.join(entries) + '</ul>'


def divider(number: int, title: str, subtitle: str, brand: str = RED) -> str:
    return spread(
        f"{number}-0",
        page("", '<div class="divider"><div class="kicker">CHAPTER</div><div class="num">%s</div><div class="seal">FILE No.%02d</div></div>' % (number, number)),
        page("", body(f'<div class="big-title">{title}</div>{lead(subtitle)}'), True),
        brand,
    )


def std(sid: str, kicker: str, title: str, chips: list[str], brand: str = RED) -> str:
    chip_html = ''.join(f'<span>{chip}</span>' for chip in chips)
    return f'''<!-- Slide ID: {sid} -->
<div class="slide-container std" style="{brand}"><div class="std-rays"></div><div class="std-copy"><div class="std-badge">格安SIM図鑑｜利用者満足度調査</div><div class="std-kicker">{kicker}</div><h1>{title}</h1><div class="std-chips">{chip_html}</div></div></div>'''


def evaluation(sid: str, direction: str, carrier: str, logo: str, brand: str, details: list[tuple[str, str, str, str]]) -> str:
    """Render the scenario's evaluation direction as six readable cards.

    The direction supplies rank data; card copy is a compact restatement of its
    pro/con clauses so the 30px minimum type rule remains intact.
    """
    overall = re.search(r"総合:([A-Z]+)", direction)
    grade = overall.group(1) if overall else "A"
    cards = []
    for name, rank, pro, con in details:
        cards.append(f'''<div class="card"><div class="rank {rank}">{rank}</div><div class="card-name">{name}</div><div class="line pro"><span class="tag">＋</span>{pro}</div><div class="line con"><span class="tag">－</span>{con}</div></div>''')
    left_cards, right_cards = ''.join(cards[:3]), ''.join(cards[3:])
    logo_img = asset("logo", logo)
    left = f'''<div class="page left"><div class="head-left"><img class="logo" src="{logo_img}" alt="{carrier}"><div class="total"><div class="label">総合評価</div><div class="grade">{grade}</div></div></div><div class="cards">{left_cards}</div></div>'''
    right = f'''<div class="page right"><span class="index-tab">格安SIM図鑑</span><div class="page-head">{carrier}の評価</div><div class="cards">{right_cards}</div><div class="note eval-note">※本評価は当チャンネルの独断と偏見による独自評価であり、キャンペーン割引等は考慮していません</div></div>'''
    return spread(sid, left, right, brand)


def render(slides: OrderedDict[str, str]) -> list[str]:
    # Each entry is keyed by the scenario's own slide ID.  `display` is passed
    # into content-specific renderers, retaining the CSV as the input contract.
    display = slides
    out: list[str] = []
    out.append(std("1", "その比較、何を信じればいい？", "格安SIMの比較で<br><strong>迷っていませんか？</strong>", ["比較サイトや動画が多すぎる", "選ぶ基準を利用者の声から整理"], RED))
    out.append(std("1-2", "格安SIM利用者本人に聞いた", "満足度調査で<br><strong>1位が発表！</strong>", ["総合満足度 No.1", "サポート満足度 No.1 は別の会社"], BLUE))
    out.append(std("2", "利用者の声から2社を徹底比較", "総合No.1は<br><strong>日本通信SIM</strong><br>サポートNo.1はイオンモバイル", ["コスパ重視なら？", "店舗サポート重視なら？"], RED))
    out.append(spread("3", page("格安SIM図鑑 もくじ", body('<ul class="agenda"><li><span class="num">1</span>調査の中身</li><li><span class="num">2</span>日本通信SIM</li><li><span class="num">3</span>イオンモバイル</li><li><span class="num">4</span>どっちを選ぶ？</li><li><span class="num">5</span>まとめ</li></ul>')), page("この動画でわかること", body('<ul class="benefits"><li><span class="check">✓</span>調査の中身がわかる</li><li><span class="check">✓</span>日本通信SIMが総合1位の理由</li><li><span class="check">✓</span>イオンモバイルがサポート1位の理由</li></ul>'), True), RED))
    out.append(divider(4, title_lines("『格安SIMアワード』", "ってどんな調査？", variant="compact"), "利用者本人の声で選ばれた結果", BLUE))
    out.append(spread("4-1", page("調査のポイント", body(rows([("fa-users", "格安SIM利用者本人へのアンケート", "満足度・継続意向・コスパを調査"), ("fa-calendar-check", "2026年9月3日に発表", "株式会社イード『格安SIMアワード2026上半期』")]))), page("MVNO部門の総合1位", body(emph('日本通信SIMが<br><span class="big">3部門で1位</span>') + lead('総合満足度・継続意向・コストパフォーマンス', True) + '<div class="note" style="font-size:30px;line-height:1.1">出典：株式会社イード（2026年9月3日発表）</div>', "top"), True), BLUE))
    out.append(spread("4-2", page("もう一つの最優秀", body('<div class="logos"><img src="%s" alt="イオンモバイル" style="max-width:560px;height:82px"></div>' % asset("logo", "aeonmobile_logo.png") + emph('イオンモバイルが<br><span class="big">サポート満足度 1位</span>'))), page("強みは通信品質も", body(rows([("1", "サポート全体満足度で最優秀", "イオンモール等で対面相談できる"), ("2", "通信速度（品質）でも最優秀", "部門ごとに強みが異なる結果")])), True), PURPLE))
    out.append(divider(5, '日本通信SIM<br><span class="em">総合満足度 No.1</span>', "コスパを重視する人の有力候補", BLUE))
    out.append(evaluation("6-0", display["6-0"], "日本通信SIM", "nihon_tsushin.jpg", BLUE, [
        ("データ料金", "SS", "20GB 月額1,390円", "容量は少なめの選択肢"),
        ("通信品質", "B", "ドコモ回線でエリアが広い", "混雑時間は速度が落ちやすい"),
        ("初期費用", "B", "解約金0円・縛りなし", "初期費用3,300円が基本"),
        ("通話料", "S", "20GB以上は通話定額が無料付帯", "完全かけ放題は月額1,600円"),
        ("店舗サポート", "C", "オンラインで手続き完結", "対面サポートはなし"),
        ("オプション", "C", "料金体系がシンプル", "追加オプションは少なめ"),
    ]))
    out.append(spread("6", page("合理的シンプル290", body(emph('1GBで<br><span class="big">月額 290円</span>') + lead('サブ回線として持つ選択肢にも', True), "center")), page("始めやすさも魅力", body(rows([("fa-ban", "最低利用期間なし", "合わなければ気軽に見直せる"), ("fa-yen-sign", "契約解除料 0円", "コスパと始めやすさを両立")])), True), BLUE, True))
    out.append(spread("6-1", page("日本通信SIMの通話料", body(emph('<span class="big">11円</span> / 30秒') + lead('20GB以上のプランは<br>5分・月70分のかけ放題が無料付帯', True), "center")), page("通話する人にも高コスパ", body(rows([("1", "5分かけ放題 または 月70分", "20GB以上のプランで無料付帯"), ("2", "基本通話料は11円 / 30秒", "毎月の通話コストも抑えやすい")])), True), BLUE, True))
    out.append(spread("6-2", page("詳しい解説は過去動画で", body('<div class="visual"><img src="%s" alt="日本通信SIMの過去動画サムネイル"></div>' % asset("thumbnails", "【2026年最新】20GBで1,390円！？日本通信SIMの「SS級」コスパを徹底解剖！メリット・デメリット全公開.png"))), page("日本通信SIMを徹底解剖", body('<div class="bigicon cta-icon"><i class="fa-solid fa-play"></i></div><div class="big-title">%s</div>' % title_lines("料金プランも", "詳しくチェック！", variant="cta"), "top"), True), BLUE))
    out.append(divider(7, 'イオンモバイル<br><span class="em">サポート満足度 No.1</span>', "店舗で相談したい人の有力候補", PURPLE))
    out.append(evaluation("8-0", display["8-0"], "イオンモバイル", "aeonmobile_logo.png", PURPLE, [
        ("データ料金", "A", "0.5〜100GBを細かく選べる", "大容量帯は割高になりやすい"),
        ("通信品質", "B", "ドコモ・au回線を選べる", "混雑時間は速度が落ちやすい"),
        ("初期費用", "A", "解約金0円・縛りなし", "初期費用3,300円が基本"),
        ("通話料", "S", "専用アプリなしで11円/30秒", "無料通話付きプランはなし"),
        ("店舗サポート", "S", "イオンモール等で対面相談", "全地域に店舗があるわけではない"),
        ("オプション", "S", "繰り越し・容量帯が豊富", "選択肢が多く迷いやすい"),
    ]))
    out.append(spread("8", page("容量も回線も選べる", body(rows([("fa-layer-group", "0.5GB 803円〜100GB 6,358円", "10段階の容量帯から選択"), ("fa-signal", "ドコモ回線・au回線から選べる", "日本通信SIMはドコモ回線のみ")]))), page("データ繰り越しに対応", body(emph('余ったデータは<br><span class="big">翌月へ繰り越し</span>') + lead('月によって使う量が変わる人にも安心', True), "center"), True), PURPLE, True))
    out.append(spread("8-1", page("店舗サポートが強み", body('<div class="bigicon"><i class="fa-solid fa-store"></i></div>' + lead('イオンモール等の実店舗で<br>対面相談できる', True), "center")), page("事前に近くの店舗を確認", body(rows([("1", "サポート全体満足度で最優秀", "困ったときに相談できる安心感"), ("2", "全国どの地域にもあるわけではない", "最寄りのイオンモバイル取扱店を確認")])), True), PURPLE))
    out.append(spread("8-2", page("家族での料金も解説", body('<div class="visual"><img src="%s" alt="イオンモバイルの過去動画サムネイル"></div>' % asset("thumbnails", "【月額800円〜】家族4人で乗り換えると衝撃の安さに！イオンモバイルの料金プランと5つのメリットを徹底解説.png"))), page("イオンモバイルもチェック", body('<div class="bigicon cta-icon"><i class="fa-solid fa-play"></i></div><div class="big-title">家族の料金も<br>過去動画で！</div>', "top"), True), PURPLE))
    out.append(divider(9, 'あなたは<br><span class="em">どっちを選ぶ？</span>', "使い方に合わせて選び分けよう", RED))
    out.append(spread("10-0", page("第5章", '<div class="divider"><div class="kicker">CHAPTER</div><div class="num">5</div><div class="seal">FINAL SUMMARY</div></div>'), page("", body('<div class="big-title">今日の<br><span class="em">まとめ</span></div>' + lead('利用者の声から、あなたに合う1枚を選ぼう')), True), RED))
    out.append(spread("11", page("今日のまとめ", body(rows([("1", "総合満足度1位は日本通信SIM", "『格安SIMアワード2026上半期』"), ("2", "サポート満足度No.1はイオンモバイル", "店舗で相談できる強み")]))), page("選ぶ軸はこの2つ", body(rows([("fa-yen-sign", "コスパ重視なら 日本通信SIM", "20GB 月額1,390円・通話も高コスパ"), ("fa-store", "サポート重視なら イオンモバイル", "実店舗で対面相談できる")])), True), RED))
    out.append(spread("11-2", page("もう一方の調査結果", body('<div class="logos"><img src="%s" alt="povo2.0"></div>' % asset("logo", "Povo_logo.png") + lead('オンライン専用プラン＋サブブランドでは<br>povo2.0が全部門で最優秀', True))), page("povo2.0の独壇場", body(rows([("1", "総合満足度・継続意向", "通信速度（品質）・コスパも最優秀"), ("2", "サポート全体満足度も最優秀", "今回はMVNO部門に絞って解説")])), True), BLUE))
    out.append(spread("12", page("ご注意", body('<div class="bigicon"><i class="fa-solid fa-circle-info"></i></div><div class="big-title">お申し込み前に<br>最新情報を確認</div>', "center")), page("料金・調査結果について", body('<div class="warn"><i class="ic fa-solid fa-triangle-exclamation"></i>料金・調査結果は動画投稿時点の情報です</div>' + lead('お申し込み前に<br>各社公式サイトの最新情報をご確認ください', True)), True), RED))
    out.append(spread("13", page("コメントで教えてね！", body('<div class="bigicon"><i class="fa-solid fa-comments"></i></div><div class="big-title">%s</div>' % title_lines("あなたの体験を", "聞かせて！"), "center")), page("こんなコメントを募集中", body(rows([("1", "日本通信SIMを使っています", "使い心地や料金の感想"), ("2", "イオンモバイルの店舗で相談しました", "サポートの感想・わかりづらかった点")])), True), RED))
    out.append(spread("14", page("スマホ代は大きな固定費", body(emph('毎月の見直しで<br><span class="big">未来が変わる</span>') + lead('少しでも多くの方に見直してほしい', True), "center")), page("浮いたお金は自分のために", body('<div class="bigicon cta-icon"><i class="fa-solid fa-piggy-bank"></i></div><div class="big-title">貯蓄や<br>好きなことへ</div>', "top"), True), GREEN))
    out.append(spread("14-1", page("これからも役立つ動画を", body('<div class="bigicon"><i class="fa-solid fa-compass"></i></div><div class="big-title">自分に合う<br>1枚がわかる</div>', "center")), page("選択肢が多いからこそ", body(lead('格安SIM選びで迷わないための<br>情報を、これからも発信します') + rows([("fa-lightbulb", "料金・使い方・サポートを整理", "あなたに合う選択を後押し")])), True), GREEN))
    out.append(spread("15", page("ブログ・noteでも比較中", body('<div class="bigicon"><i class="fa-solid fa-pen-nib"></i></div><div class="big-title">料金比較を<br>もっと詳しく</div>', "center")), page("概要欄からチェック", body('<div class="visual blog-image"><img src="%s" alt="ブログのヘッダー画像"></div>' % asset("common", "ブログ_ヘッダー画像_スライド用.png") + lead('ブログ・noteでも格安SIMの料金を比較中', True) + '<div class="note">概要欄のリンクからぜひ！</div>'), True), BLUE))
    out.append(spread("16", page("最後までご視聴", body('<div class="bigicon"><i class="fa-solid fa-bell"></i></div><div class="big-title">ありがとう<br>ございました！</div>', "center")), page("また次回の動画で！", body('<div class="subscribe-icons"><i class="fa-solid fa-thumbs-up"></i><i class="fa-solid fa-bell"></i></div><div class="big-title">%s</div>' % title_lines("チャンネル登録", "高評価も", "よろしく！", variant="cta"), "top"), True), RED))
    return out


STYLE = r'''<style>
.slide-container.std{width:1280px;height:720px;border:10px solid var(--brand);background:#fff;box-sizing:border-box;position:relative;overflow:hidden;display:flex;align-items:center;justify-content:center;padding:40px;flex-shrink:0}
.std-rays{position:absolute;inset:-40%;background:repeating-conic-gradient(from 0deg,transparent 0 12deg,rgba(200,16,46,.09) 12deg 18deg);z-index:0}.std-copy{position:relative;z-index:1;width:100%;text-align:center}.std-badge,.std-kicker{display:inline-block;background:var(--brand);color:#fff;font-size:38px;font-weight:900;padding:10px 25px;border-radius:999px;margin:4px}.std-kicker{background:#fff;color:var(--brand-deep);border:4px solid var(--brand)}.std-copy h1{font-size:78px;line-height:1.16;color:#242424;font-weight:900;margin:13px 0}.std-copy h1 strong{color:var(--brand-deep)}.std-chips{display:flex;justify-content:center;gap:14px;flex-wrap:wrap}.std-chips span{font-size:34px;font-weight:900;background:#fff;padding:12px 22px;border-radius:12px;box-shadow:0 5px 14px rgba(0,0,0,.15)}
.eval-note{font-size:28px!important;text-align:center;margin-top:12px}.page .cards{min-height:0}.card{flex:0 0 auto}.eval-note+.cards{flex:1}.blog-image{height:300px}.blog-image img{width:100%;height:auto;max-height:300px;object-fit:contain}.subscribe-icons{display:flex;gap:75px;justify-content:center;color:var(--brand);font-size:150px;line-height:1}.cta-icon{font-size:140px}.std .logos img{height:90px}
/* Long display titles are emitted by title_lines() as semantic, unbreakable phrases. */
.big-title{word-break:auto-phrase;text-wrap:balance}.big-title .title-line{display:block;white-space:nowrap;word-break:keep-all}.big-title .title-line.compact{font-size:76px;line-height:1.3;letter-spacing:-.03em}.big-title .title-line.cta{font-size:90px;line-height:1.26}
</style>'''


def main() -> None:
    slides = load_slides()
    expected = set(slides)
    rendered = render(slides)
    actual = re.findall(r"<!-- Slide ID: ([0-9-]+) -->", "\n".join(rendered))
    if len(actual) != len(set(actual)):
        raise ValueError("duplicate slide IDs in generated deck")
    if set(actual) != expected:
        raise ValueError(f"ID mismatch; missing={expected-set(actual)}, extra={set(actual)-expected}")
    document = f'''<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<link href="https://fonts.googleapis.com/css2?family=M+PLUS+Rounded+1c:wght@400;500;700;800;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
<link rel="stylesheet" href="templates/spread-base.css">{STYLE}</head><body>
{chr(10).join(rendered)}
</body></html>'''
    OUTPUT.write_text(document, encoding="utf-8")
    print(f"Generated {len(actual)} slides: {OUTPUT}")


if __name__ == "__main__":
    main()
