#!/usr/bin/env python3
"""Generate the mineo autumn campaign long-form deck from its master CSV.

The slide copy is read from the CSV's `スライドに表示する内容` column.  Layout
selection is intentionally keyed by slide ID so future visual corrections happen in
this generator and are reproduced by rerunning it, never by hand-editing HTML.
"""
from __future__ import annotations

import csv
import re
from collections import OrderedDict
from html import escape
from pathlib import Path

MASTER_CSV = Path("/workspaces/yt-factory/packages/scenario-gen/archive/videos/47_【〜11／30】mineo 3GB＋データ使い放題が最大6カ月880円！注意点も解説/long/【〜11／30】mineo 3GB＋データ使い放題が最大6カ月880円！注意点も解説.csv")
OUTPUT_HTML = Path("/workspaces/yt-factory/packages/slide-gen/slides.html")

GREEN = "--brand:#22a73f;--brand-deep:#1c8b34;--brand-soft:#e8f5e6"
RED = "--brand:#C8102E;--brand-deep:#9a0c23;--brand-soft:#fde3e7"
LOGO = "public/images/logo/Mineo_logo.png"


def tag(name: str, text: str, cls: str = "", attrs: str = "") -> str:
    class_attr = f' class="{cls}"' if cls else ""
    extra_attr = f" {attrs}" if attrs else ""
    return f"<{name}{class_attr}{extra_attr}>{text}</{name}>"


def rows(items: list[tuple[str, str, str]]) -> str:
    """CSS rows from (Font Awesome icon, main text, optional subtext)."""
    output = []
    for icon, main, sub in items:
        sub_html = f'<span class="sub">{escape(sub)}</span>' if sub else ""
        output.append(f'<li><span class="ic"><i class="fa-solid fa-{icon}"></i></span><div class="tx">{escape(main)}{sub_html}</div></li>')
    return '<ul class="rows">' + "".join(output) + "</ul>"


def body(*parts: str, center: bool = False, top: bool = False) -> str:
    classes = "page-body" + (" center" if center else "") + (" top" if top else "")
    return tag("div", "".join(parts), classes)


def page(head: str, content: str) -> str:
    return f'<div class="page"><div class="page-head">{head}</div>{content}</div>'


def spread(slide_id: str, left_head: str, left: str, right_head: str, right: str, *, price: bool = False) -> str:
    note = " price-note" if price else ""
    return f'''<!-- Slide ID: {slide_id} -->
<div class="slide-container{note}" style="{GREEN}"><div class="book"><div class="spine"></div>{page(left_head, left)}{page(right_head, right)}</div></div>'''


def chapter(slide_id: str, num: str, title: str) -> str:
    """Render a chapter title from semantic lines, never browser-split text."""
    left = '<div class="page"><div class="divider"><div class="kicker">CHAPTER</div><div class="num">' + num + '</div><div class="seal">FILE No.' + num.zfill(2) + '</div></div></div>'
    # A chapter title is intentionally authored as semantic lines.  Each line is
    # non-wrapping so a browser can never split a Japanese word mid-phrase.
    title_html = "".join(f'<span class="semantic-line">{escape(line)}</span>' for line in title.split("\n"))
    right = '<div class="page"><div class="page-body center"><div class="big-title chapter-title">' + title_html + '</div><div class="lead">mineoを選ぶ前に、ポイントを整理します</div></div></div>'
    return f'<!-- Slide ID: {slide_id} -->\n<div class="slide-container" style="{GREEN}"><div class="book"><div class="spine"></div>{left}{right}</div></div>'


def std(slide_id: str, kicker: str, title: str, detail: str) -> str:
    return f'''<!-- Slide ID: {slide_id} -->
<div class="slide-container std{' price-note' if '円' in title + detail else ''}" style="{RED}">
  <div class="sunburst"></div><div class="std-copy"><div class="cover-badge">{escape(kicker)}</div><div class="std-title">{escape(title)}</div><div class="std-detail">{escape(detail)}</div></div>
</div>'''


def campaign_cover() -> str:
    """A magazine-style opening cover with the carrier shown as its real logo."""
    return f'''<!-- Slide ID: 1 -->
<div class="slide-container std price-note intro-cover" style="{RED}">
  <div class="sunburst"></div><div class="cover-ribbon">期間限定</div>
  <img class="intro-illust" src="public/images/irasutoya/money_fueru.png" alt="増えるお金のイラスト">
  <div class="std-copy intro-copy">
    <div class="intro-logo-card"><img src="{LOGO}" alt="mineo"></div>
    <div class="cover-badge">秋のピッタリ割　11/30まで</div>
    <div class="std-title intro-price"><span>マイピタ <b>3GB</b></span><span>月 <strong>880円</strong></span></div>
    <div class="std-detail intro-benefit">最大6カ月間のキャンペーン価格</div>
    <div class="intro-date">申込期間　2026年9月17日 〜 11月30日</div>
  </div>
</div>'''


def campaign_diagram() -> str:
    """Visualize all three campaign benefits instead of collapsing them to a slogan."""
    return '''<!-- Slide ID: 2 -->
<div class="slide-container std campaign-diagram" style="--brand:#C8102E;--brand-deep:#9a0c23;--brand-soft:#fde3e7">
  <div class="sunburst"></div><div class="cover-ribbon">最大6カ月</div>
  <img class="diagram-illust" src="public/images/irasutoya/smartphone04_laugh.png" alt="スマートフォンを見て喜ぶ人のイラスト">
  <div class="std-copy diagram-copy">
    <div class="cover-badge">秋のピッタリ割</div>
    <div class="std-title diagram-title">月額も使い放題も <span>おトク</span></div>
    <div class="campaign-flow" aria-label="秋のピッタリ割の特典図解">
      <div class="flow-card"><div class="flow-num">1</div><div class="flow-label">マイピタ<br>音声通話付き</div><div class="flow-main">月額基本料金<br><b>最大6カ月割引</b></div></div>
      <div class="flow-arrow">＋</div>
      <div class="flow-card zero-card"><div class="flow-num">2</div><div class="flow-label">パケット放題<br>3Mbps</div><div class="flow-main">最大6カ月間<br><b>0円</b></div></div>
      <div class="flow-arrow">＝</div>
      <div class="flow-card unlimited-card"><div class="flow-num">3</div><div class="flow-label">3GBを使い切っても</div><div class="flow-main"><b>最大3Mbps</b><br>データ使い放題</div></div>
    </div>
  </div>
</div>'''


def visual(src: str, alt: str) -> str:
    return f'<div class="visual"><img src="{src}" alt="{escape(alt)}"></div>'


def first_display(rows_for_id: list[dict[str, str]]) -> str:
    for row in rows_for_id:
        value = row["スライドに表示する内容"].strip()
        if value and value != "同上":
            return value
    return ""


def load_displays() -> OrderedDict[str, str]:
    grouped: OrderedDict[str, list[dict[str, str]]] = OrderedDict()
    with MASTER_CSV.open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            slide_id = row["スライドID"].strip()
            if slide_id:
                grouped.setdefault(slide_id, []).append(row)
    return OrderedDict((slide_id, first_display(group)) for slide_id, group in grouped.items())


def split_display(value: str) -> list[str]:
    chunks = [part.strip() for part in value.split("／")]
    if not chunks:
        return chunks
    for prefix in ("テロップ：", "図解：", "タイトル："):
        if chunks[0].startswith(prefix):
            chunks[0] = chunks[0][len(prefix):]
            return chunks
    return chunks[1:] if chunks[0] == "評価見開き" else chunks


def price_table(items: list[str]) -> str:
    data = []
    for item in items:
        if "→" in item:
            plan, prices = item.split(" ", 1)
            before, after = prices.split("→", 1)
            data.append(f"<tr><td>{escape(plan)}</td><td>{escape(before)}</td><td class=\"em\">{escape(after)}</td></tr>")
    return '<table class="sheet"><tr><th>容量</th><th>通常</th><th>最大6カ月</th></tr>' + "".join(data) + "</table>"


def evaluation(content: str) -> str:
    overall_match = re.search(r"総合:([A-Z]+)", content)
    if not overall_match:
        raise ValueError("Evaluation is missing its overall rank")
    overall = overall_match.group(1)
    cards = re.findall(r"／([^／:]+):([A-Z]+)（＋(.*?)／－(.*?)）", content)
    if len(cards) != 6:
        raise ValueError(f"Evaluation must include six criteria, found {len(cards)}")
    def card(c: tuple[str, str, str, str]) -> str:
        name, rank, pro, con = c
        return f'<div class="card"><div class="rank {escape(rank)}">{escape(rank)}</div><div class="card-name">{escape(name)}</div><div class="line pro"><span class="tag">＋</span>{escape(pro)}</div><div class="line con"><span class="tag">－</span>{escape(con)}</div></div>'
    left = '<div class="page"><div class="head-left eval-head"><img class="logo" src="' + LOGO + '" alt="mineo"><div class="total"><div class="label">総合評価</div><div class="grade">' + escape(overall) + '</div></div></div><div class="cards eval-cards">' + "".join(card(x) for x in cards[:3]) + '</div></div>'
    right = '<div class="page"><div class="page-head eval-title">mineoを6観点で評価</div><div class="cards eval-cards">' + "".join(card(x) for x in cards[3:]) + '</div><div class="note eval-note">※本評価は当チャンネルの独断と偏見による独自評価であり、キャンペーン割引等は考慮していません</div></div>'
    return '<!-- Slide ID: 11 -->\n<div class="slide-container price-note" style="' + GREEN + '"><div class="book"><div class="spine"></div>' + left + right + '</div></div>'


def evaluation_intro() -> str:
    """The mandatory N-0 partner: logo/radar on the left, plan screenshots right."""
    left = '<div class="page"><div class="head-left"><img class="logo" src="' + LOGO + '" alt="mineo"></div><div class="page-body"><div class="visual"><img src="public/images/charts/mineo.png" alt="mineoの6観点評価レーダーチャート"></div></div></div>'
    plans = ('<div class="plan-shot"><div>マイピタ（デュアルタイプ）</div><img src="public/images/temp/mineo/mineo_マイピタ_料金表のみ.png" alt="mineo マイピタ料金表"></div>'
             '<div class="plan-shot"><div>マイそく</div><img src="public/images/temp/mineo/mineo_マイそく_料金表のみ.png" alt="mineo マイそく料金表"></div>')
    right = '<div class="page"><div class="page-head plan-title">mineoの料金プラン</div><div class="page-body plan-shots">' + plans + '</div></div>'
    return '<!-- Slide ID: 11-0 -->\n<div class="slide-container price-note" style="' + GREEN + '"><div class="book"><div class="spine"></div>' + left + right + '</div></div>'


def make_slide(slide_id: str, display: str) -> str:
    p = split_display(display)
    if slide_id == "1": return campaign_cover()
    if slide_id == "2": return campaign_diagram()
    if slide_id == "3":
        agenda = '<ul class="agenda"><li><span class="num">1</span>3GBで足りる？</li><li><span class="num">2</span>3Mbpsで何ができる？</li><li><span class="num">3</span>6カ月後はいくら？</li></ul>'
        # Keep the sentence and its emphasis in one inline formatting context.
        # Bare text next to <b> becomes a separate anonymous flex item and can
        # detach the emphasized phrase on narrow lines.
        benefits = '<ul class="benefits"><li><span class="check">✓</span><span class="benefit-text">自分は<b>3GBで足りるか</b></span></li><li><span class="check">✓</span><span class="benefit-text">使い切った後の<b>3Mbps</b>でできること</span></li><li><span class="check">✓</span><span class="benefit-text">割引終了後に<b>戻る料金</b></span></li></ul>'
        return spread(slide_id, "格安SIM図鑑 もくじ", body(agenda), "この動画で分かること", body(benefits))
    if slide_id == "4":
        # The table of contents has already appeared, so this title card must be
        # a book spread (std is reserved solely for slides before the contents).
        left = body(visual(LOGO, "mineo ロゴ"), '<div class="emph">3GB＋使い放題<br><span class="big">最大6カ月 880円</span></div>', center=True)
        right = body('<div class="big-title campaign-title"><span class="semantic-line">【11/30まで】mineo</span><span class="semantic-line">3GB＋使い放題</span><span class="semantic-line"><span class="em">最大6カ月 880円</span></span></div>', '<div class="lead">注意点も含めて分かりやすく解説！</div>', center=True)
        return spread(slide_id, "mineo 秋のピッタリ割", left, "キャンペーンを徹底解説", right, price=True)
    chapters = {
        # The chapter number is already prominent in the left-page divider.  Keep
        # the right-page title to the topic and split only at semantic boundaries.
        "5-0": ("1", "何が・いくら\nいつまで安い？"),
        "7-0": ("2", "3GBで足りる人\n足りない人"),
        "10-0": ("3", "mineoって\nどんな格安SIM？"),
        "12-0": ("4", "自分は対象？\n申し込みの条件"),
        "14-0": ("5", "申し込む前に\n知っておきたい\n2つのこと"),
        "17-0": ("6", "まとめ"),
    }
    if slide_id in chapters: return chapter(slide_id, *chapters[slide_id])
    if slide_id == "6":
        return spread(slide_id, p[0], body('<div class="lead">' + escape(p[1]) + '</div>', '<div class="warn"><span class="ic">⚠</span>' + escape(p[2]) + '</div>'), "コース別の割引額", body(price_table(p[4:])), price=True)
    if slide_id == "6-2":
        return spread(slide_id, p[0], body('<div class="emph">' + escape(p[1]) + '</div>', '<div class="lead">' + escape(p[2]) + '</div>'), "対象と使い放題のしくみ", body(rows([("mobile-screen-button", p[3], ""), ("infinity", p[4], "")])), price=True)
    if slide_id == "6-3":
        return spread(slide_id, p[0], body('<div class="emph">' + escape(p[1]) + '</div>', '<div class="lead">' + escape(p[2]) + '</div>'), "使い方のポイント", body(rows([("clock", p[3], ""), ("mobile-screen-button", p[4], "")])), price=True)
    if slide_id == "6-4":
        return spread(slide_id, "キャンペーン情報を見逃さない", body('<div class="bigicon compact-icon"><i class="fa-solid fa-bell"></i></div><div class="big-title compact-title"><span class="semantic-line">チャンネル登録で</span><span class="semantic-line em">最新情報を</span><span class="semantic-line">チェック！</span></div>', center=True), "開始・終了を毎週お知らせ", body('<div class="lead">' + escape(p[0]) + '</div><div class="emph compact-emph">登録ボタンを押して<br><span class="big">見逃し防止</span></div>', center=True))
    if slide_id == "8":
        return spread(slide_id, p[0], body('<div class="warn"><span class="ic">⚠</span>' + escape(p[1]) + '</div>'), "多くの人はこの組み合わせ", body('<div class="emph">' + escape(p[2]) + '</div>', center=True))
    if slide_id == "8-2":
        return spread(slide_id, p[0], body(rows([("user", p[1], ""), ("battery-full", p[2], "")])), "余ったギガは貯められる", body('<div class="emph">' + escape(p[3]) + '</div>', visual("public/images/temp/mineo/mineo_パスケットを使ったデータ貯金運用のイメージ図.png", "パスケットのイメージ")))
    if slide_id == "8-3":
        return spread(slide_id, p[0], body(rows([("gamepad", p[1], ""), ("bolt", p[2], "")])), "足りないときの備え", body('<div class="lead">' + escape(p[3]) + '</div>', center=True))
    if slide_id == "9":
        return spread(slide_id, p[0], body('<div class="compact-list">' + rows([("comment", x, "") for x in p[1].split("・")]) + '</div>'), "苦しい使い方と注意点", body(rows([("triangle-exclamation", x, "") for x in p[3].split("・")] + [("clock", p[4], "")])))
    if slide_id == "9-2":
        return spread(slide_id, p[0], body('<div class="emph">' + escape(p[1]) + '</div><div class="emph">' + escape(p[2]) + '</div>'), "オプションも通常料金へ", body('<div class="emph">' + escape(p[3]) + '</div><div class="note">' + escape(p[4]) + '</div>'), price=True)
    if slide_id == "11-0": return evaluation_intro()
    if slide_id == "11": return evaluation(display)
    if slide_id in {"11-3", "15-3"}:
        title = "mineoの解説動画もチェック！" if slide_id == "11-3" else "事務手数料の解説動画もチェック！"
        thumbnail = "public/images/thumbnails/【裏技】mineo歴8年が教える「実質使い放題」の極意！契約前に知らないと損する5つの節約術_サムネ.png" if slide_id == "11-3" else "public/images/thumbnails/【2026年最新】mineo10月手数料改定、契約時手数料3,850円もeSIMなら0円_サムネ2.png"
        return spread(slide_id, "過去動画", body(visual(thumbnail, title)), title, body('<div class="bigicon"><i class="fa-solid fa-circle-play"></i></div><div class="lead cta-copy">' + escape(p[0]) + '</div>', center=True))
    if slide_id == "13":
        return spread(slide_id, p[0], body(rows([("file-signature", p[1], ""), ("mobile-screen-button", p[2], "")])), "対象外・期限を確認", body(rows([("user-xmark", p[3], ""), ("building", p[4], ""), ("calendar-xmark", p[5], "")])))
    if slide_id == "13-2":
        return spread(slide_id, p[0], body('<div class="lead">' + escape(p[1]) + '</div><div class="note">' + escape(p[2]) + '</div>'), "15GB以上なら常に無料", body('<div class="emph">' + escape(p[3]) + '</div>', center=True))
    if slide_id == "15":
        return spread(slide_id, "提携サイト限定キャンペーン", body('<div class="lead">' + escape(p[1]) + '</div><div class="emph compact-emph">概要欄の指定リンクから<br><span class="big">事務手数料が無料</span></div>', top=True), "対象外・通常の手数料", body(rows([("circle-xmark", p[4], ""), ("triangle-exclamation", p[3], "")])), price=True)
    if slide_id == "15-2":
        return spread(slide_id, p[0], body('<div class="emph compact-emph">' + escape(p[1]) + '</div><div class="emph compact-emph">' + escape(p[2]) + '</div>', top=True), "SIMカードは発行料に注意", body('<div class="warn"><span class="ic">⚠</span>' + escape(p[3]) + '</div>', center=True), price=True)
    if slide_id == "16":
        return spread(slide_id, p[0], body(rows([("calendar-days", p[1], ""), ("yen-sign", p[2], "")])), "無料期間の終わりに確認", body('<div class="warn"><span class="ic">⚠</span>' + escape(p[3]) + '</div><div class="note">' + escape(p[4]) + '</div>'), price=True)
    if slide_id == "18":
        return spread(slide_id, p[0], body(rows([("calendar", p[1], ""), ("tag", p[2], "")])), "自分の使い方で判断", body(rows([("user-check", p[3], ""), ("rotate", p[4], "")])), price=True)
    if slide_id == "19":
        return spread(slide_id, "ご注意", body('<div class="bigicon"><i class="fa-solid fa-circle-info"></i></div><div class="big-title">ご確認ください</div>', center=True), "申し込み前の最終確認", body('<div class="warn">' + escape(p[0]) + '</div><div class="note">' + escape(p[1]) + '</div>', center=True))
    if slide_id == "20":
        examples = p[0].split("例：", 1)[1] if "例：" in p[0] else p[0]
        return spread(slide_id, "コメントで教えてね！", body('<div class="bigicon"><i class="fa-solid fa-comments"></i></div><div class="big-title">あなたは<br><span class="em">何GB？</span></div>', center=True), "コメント例", body(rows([("comment", x.strip("「」"), "") for x in examples.split("」「")])) )
    if slide_id == "21":
        return spread(slide_id, "スマホ代は大きな固定費", body('<div class="bigicon"><i class="fa-solid fa-wallet"></i></div><div class="big-title">毎月の固定費を<br><span class="em">見直そう</span></div>', center=True), "浮いたぶんは自分のために", body(rows([("piggy-bank", p[1], ""), ("sack-dollar", p[2], "")])))
    if slide_id == "21-1":
        return spread(slide_id, "格安SIM図鑑からのお約束", body('<div class="bigicon"><i class="fa-solid fa-compass"></i></div><div class="big-title">自分に合う<br><span class="em">1枚</span>が分かる</div>', center=True), "これからも続けます", body('<div class="lead">' + escape(p[0]) + '</div>', center=True))
    if slide_id == "22":
        return spread(slide_id, "ブログ・noteでも比較中", body('<div class="bigicon"><i class="fa-solid fa-pen-nib"></i></div><div class="big-title">もっと詳しく<br><span class="em">料金比較</span></div>', center=True), "概要欄からどうぞ", body(visual("public/images/common/ブログ_ヘッダー画像_スライド用.png", "ブログ・noteの案内"), '<div class="lead tight cta-copy">' + escape(p[0]) + '</div>', top=True))
    if slide_id == "23":
        return spread(slide_id, "ご視聴ありがとうございました！", body('<div class="bigicon compact-icon"><i class="fa-solid fa-bell"></i></div><div class="big-title compact-title closing-title"><span class="semantic-line">チャンネル登録</span><span class="semantic-line">よろしくお願いします！</span></div>', center=True), "また次回も一緒に節約", body('<div class="logos"><span style="font-size:128px">👍</span><span style="font-size:128px">🔔</span></div><div class="lead cta-copy">' + escape(p[0]) + '</div>', center=True))
    raise ValueError(f"No layout mapping for slide ID {slide_id}: {display}")


def document(slides: list[str]) -> str:
    return '''<!doctype html>
<html lang="ja"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<link href="https://fonts.googleapis.com/css2?family=M+PLUS+Rounded+1c:wght@400;500;700;800;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
<link rel="stylesheet" href="templates/spread-base.css"><style>
body { --primary-color:#C8102E; --accent-red:#E53935; --text-dark:#212121; }
.slide-container.std{width:1280px;height:720px;border:10px solid var(--primary-color);background:#fff;box-sizing:border-box;position:relative;overflow:hidden;display:flex;align-items:center;justify-content:center;padding:56px;flex-shrink:0}
.sunburst{position:absolute;inset:0;background:repeating-conic-gradient(from 0deg at 50% 48%,rgba(200,16,46,.08) 0deg 5deg,transparent 5deg 10deg);pointer-events:none}.std-copy{position:relative;z-index:1;text-align:center;width:100%}.cover-badge{display:inline-block;background:var(--primary-color);color:#fff;font-size:44px;font-weight:900;padding:10px 32px;border-radius:10px;transform:rotate(-2deg);box-shadow:0 8px 16px rgba(0,0,0,.2)}.std-title{font-size:86px;font-weight:900;line-height:1.22;color:var(--text-dark);text-shadow:4px 4px 0 #fff;margin-top:28px;word-break:auto-phrase;text-wrap:balance}.std-detail{font-size:46px;font-weight:900;line-height:1.35;color:var(--text-dark);margin:28px auto 0;max-width:1080px;word-break:auto-phrase;text-wrap:balance}.cover-ribbon{position:absolute;z-index:2;top:28px;right:28px;padding:10px 24px;background:#f6b600;color:#3b2100;font-size:30px;font-weight:900;text-align:center;white-space:nowrap;transform:rotate(-4deg);border-radius:8px;box-shadow:0 6px 12px rgba(0,0,0,.16)}.intro-logo-card{width:280px;margin:0 auto 8px;padding:12px 28px;background:#fff;border-radius:16px;box-shadow:0 8px 20px rgba(0,0,0,.16)}.intro-logo-card img{display:block;width:100%;height:auto}.intro-copy{padding-bottom:20px}.intro-price{margin-top:14px;font-size:92px;line-height:1.04}.intro-price span{display:block}.intro-price b{color:#22a73f}.intro-price strong{color:var(--primary-color);font-size:128px}.intro-benefit{margin-top:12px;font-size:44px}.intro-date{display:inline-block;margin-top:18px;padding:10px 26px;background:rgba(255,255,255,.92);border:3px solid var(--primary-color);border-radius:999px;color:var(--text-dark);font-size:32px;font-weight:900}.intro-illust{position:absolute;z-index:0;right:38px;bottom:12px;height:250px;width:auto;object-fit:contain}.diagram-copy{padding-top:6px}.diagram-title{margin:12px 0 18px;font-size:76px;line-height:1.08}.diagram-title span{color:var(--primary-color)}.campaign-flow{display:flex;align-items:stretch;justify-content:center;gap:10px;width:100%;padding:0 72px;box-sizing:border-box}.flow-card{width:270px;min-height:286px;box-sizing:border-box;padding:16px 14px 18px;background:rgba(255,255,255,.97);border:5px solid var(--primary-color);border-radius:22px;box-shadow:0 10px 18px rgba(0,0,0,.14);color:var(--text-dark)}.flow-num{display:inline-flex;align-items:center;justify-content:center;width:48px;height:48px;border-radius:50%;background:var(--primary-color);color:#fff;font-size:32px;font-weight:900}.flow-label{min-height:76px;margin-top:8px;color:#555;font-size:30px;font-weight:900;line-height:1.2}.flow-main{margin-top:12px;font-size:34px;font-weight:900;line-height:1.22}.flow-main b{color:var(--primary-color);font-size:42px}.zero-card .flow-main b{font-size:68px}.unlimited-card .flow-main b{font-size:48px}.flow-arrow{align-self:center;color:var(--primary-color);font-size:56px;font-weight:900;text-shadow:2px 2px 0 #fff}.diagram-illust{position:absolute;z-index:0;right:8px;bottom:2px;height:208px;width:auto;object-fit:contain}.page .visual img{max-height:480px}.page-body>.note{font-size:34px}.card{flex:0 0 auto}.card .line{font-size:30px;line-height:1.25}.card-name{font-size:38px}.cards{justify-content:space-evenly}.page .sheet{font-size:34px}.page .sheet th,.page .sheet td{padding:12px}.page .rows .tx{font-size:40px}.page .lead.tight{font-size:38px}.page .logos{gap:32px}.compact-title{font-size:82px}.compact-icon{font-size:220px}.compact-emph{padding:24px 34px}.compact-list{flex:1;min-height:0}.compact-list .rows{gap:9px}.compact-list .rows li{padding:10px 18px;border-left-width:10px}.compact-list .rows .ic{width:54px;font-size:42px}.compact-list .rows .tx{font-size:32px;line-height:1.2}.cta-copy{font-size:32px;line-height:1.25;padding:22px 28px}.semantic-line{display:block;white-space:nowrap}.chapter-title{font-size:78px;line-height:1.22}.campaign-title{font-size:66px;line-height:1.2}.benefits .benefit-text{flex:1;min-width:0}.closing-title{font-size:60px;line-height:1.22}.plan-title{font-size:54px;margin-bottom:12px}.plan-shots{justify-content:flex-start;gap:18px}.plan-shot{font-size:30px;font-weight:900;color:var(--brand-deep);text-align:center}.plan-shot img{display:block;width:100%;max-height:230px;object-fit:contain;margin-top:4px}.eval-head{height:112px;margin-bottom:8px;padding-bottom:8px}.eval-head .logo{height:66px}.eval-head .grade{font-size:72px}.eval-title{font-size:48px;padding-bottom:8px;margin-bottom:8px}.eval-cards{gap:7px;justify-content:space-between}.eval-cards .card{grid-template-columns:76px 1fr;gap:1px 10px;padding:7px 12px;border-left-width:10px}.eval-cards .card .rank{width:68px;height:68px;border-radius:14px;font-size:36px}.eval-cards .card-name{font-size:30px;line-height:1.05}.eval-cards .card .line{font-size:30px;line-height:1.04}.eval-note{font-size:28px!important;line-height:1.12;text-align:center;margin-top:4px}
.intro-logo-card{width:230px;margin:0 auto 6px}.intro-copy{padding-bottom:10px}.intro-price{margin-top:10px;font-size:86px}.intro-price strong{font-size:114px}.intro-benefit{margin-top:8px;font-size:38px}.intro-date{margin-top:10px;padding:7px 22px;font-size:28px}
</style></head><body>''' + "\n".join(slides) + "</body></html>\n"


def main() -> None:
    displays = load_displays()
    slides = []
    for slide_id, value in displays.items():
        slides.append(make_slide(slide_id, value))
    OUTPUT_HTML.write_text(document(slides), encoding="utf-8")
    print(f"Generated {len(slides)} slides: {OUTPUT_HTML}")


if __name__ == "__main__":
    main()
