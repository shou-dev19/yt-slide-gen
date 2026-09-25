#!/usr/bin/env python3
"""Generate the IIJmio eSIM long-form deck directly from its master scenario CSV."""

from __future__ import annotations

import csv
import html
import re
from pathlib import Path


ROOT = Path("/workspaces/yt-factory/packages/slide-gen")
MASTER = Path("/workspaces/yt-factory/packages/scenario-gen/archive/videos/49_【〜11／4】IIJmioのeSIMは初期費用が半額！12月の値上げ前に申し込むなら今/long/【〜11／4】IIJmioのeSIMは初期費用が半額！12月の値上げ前に申し込むなら今.csv")
OUTPUT = ROOT / "slides.html"
BRAND = "--brand:#1565C0;--brand-deep:#0d47a1;--brand-soft:#e3f0fb"
RED = "--brand:#C8102E;--brand-deep:#9a0c23;--brand-soft:#fde3e7"
def esc(value: str) -> str:
    return html.escape(value, quote=True)


def asset(path: str) -> str:
    return path


def tag(text: str, cls: str = "") -> str:
    return f'<span class="{cls}">{esc(text)}</span>' if cls else esc(text)


def spread(slide_id: str, left: str, right: str, *, brand: str = BRAND, price: bool = False) -> str:
    price_cls = " price-note" if price else ""
    return f'''<!-- Slide ID: {esc(slide_id)} -->
<div class="slide-container{price_cls}" style="{brand}">
  <div class="book"><div class="spine"></div>
    <div class="page left">{left}</div>
    <div class="page right">{right}</div>
  </div>
</div>'''


def page_head(title: str, subtitle: str = "") -> str:
    small = f'<small>{esc(subtitle)}</small>' if subtitle else ""
    return f'<div class="page-head">{esc(title)}{small}</div>'


def rows(items: list[tuple[str, str] | tuple[str, str, str]], icon: str = "fa-circle-check") -> str:
    parts = []
    for item in items:
        badge, text = item[:2]
        sub = item[2] if len(item) > 2 else ""
        if not badge:
            marker = f'<span class="ic"><i class="fa-solid {icon}"></i></span>'
        elif len(badge) == 1:
            marker = f'<span class="badge">{esc(badge)}</span>'
        else:
            icon_by_label = (
                ("fa-tag", ("割引",)) if "割引" in badge else
                ("fa-ban", ("対象外",)) if "対象外" in badge else
                ("fa-link", ("併用",)) if "併用" in badge else
                ("fa-sim-card", ("SIMカード",)) if "SIMカード" in badge else
                ("fa-mobile-screen", ("eSIM",)) if "eSIM" in badge else
                ("fa-arrow-trend-up", ("値上げ",)) if "値上げ" in badge else
                ("fa-circle-check", ())
            )[0]
            marker = f'<span class="ic"><i class="fa-solid {icon_by_label}"></i></span>'
        sub_html = f'<span class="sub">{esc(sub)}</span>' if sub else ""
        parts.append(f'<li>{marker}<div class="tx">{esc(text)}{sub_html}</div></li>')
    return '<ul class="rows">' + "".join(parts) + "</ul>"


def lead(text: str) -> str:
    return f'<div class="lead">{esc(text)}</div>'


def emphasis(text: str, big: str | None = None) -> str:
    if big and big in text:
        before, after = text.split(big, 1)
        return f'<div class="emph">{esc(before)}<span class="big">{esc(big)}</span>{esc(after)}</div>'
    return f'<div class="emph">{esc(text)}</div>'


def body_page(title: str, blocks: list[str], *, subtitle: str = "", centered: bool = False) -> str:
    cls = "page-body center" if centered else "page-body"
    return page_head(title, subtitle) + f'<div class="{cls}">' + "".join(blocks) + "</div>"


def std_slide(slide_id: str, content: str, *, kind: str) -> str:
    if kind == "hook":
        title = "IIJmioの初期費用が\n12月から値上げ"
        kicker = "申込み前に知っておきたいニュース"
        visual = '<div class="std-flow"><span>3,300円</span><b>→</b><strong>3,850円</strong></div>'
        footer = "2026年12月1日 申込み分から"
    elif kind == "announcement":
        title = "初期費用\n550円アップ"
        kicker = "IIJmio公式発表｜2026年9月1日"
        visual = '<div class="std-flow"><span>3,300円</span><b>→</b><strong>3,850円</strong></div>'
        footer = "Web申込み｜12月1日から"
    elif kind == "campaign":
        title = "eSIMなら\n初期費用が半額"
        kicker = "IIJmio eSIM初期費用割引キャンペーン"
        visual = '<div class="std-flow"><span class="strike">3,300円</span><b>−1,650円</b><strong>1,650円</strong></div>'
        footer = "2026年11月4日 23:59まで"
    else:
        title = "IIJmioのeSIM\n初期費用が半額！"
        kicker = "12月の値上げ前に申し込むなら今"
        visual = '<div class="std-flow"><strong>申込期限 11/4</strong><b>｜</b><strong>値上げ前に確認</strong></div>'
        footer = "eSIM割引キャンペーン実施中"
    illustration = {
        "1": ("public/images/irasutoya/seikyuusyo_shock.png", "値上げに驚く人のイラスト"),
        "2": ("public/images/irasutoya/smartphone_talk03_man.png", "スマートフォンでニュースを確認する人のイラスト"),
        "3": ("public/images/irasutoya/osatsu_money_yamadumi.png", "割引をイメージしたお金のイラスト"),
        "4": ("public/images/irasutoya/sns_happy_woman.png", "喜ぶ人のイラスト"),
    }[slide_id]
    art = f'<img class="std-art" src="{esc(asset(illustration[0]))}" alt="{esc(illustration[1])}">'
    return f'''<!-- Slide ID: {esc(slide_id)} -->
<div class="slide-container std" style="--primary-color:#1565C0;--accent-red:#E53935;--text-dark:#212121">
  <div class="std-burst"></div><div class="std-ribbon">IIJmio お申し込み前にチェック</div>
  {art}
  <div class="std-copy"><div class="std-kicker">{esc(kicker)}</div>
    <div class="std-title">{esc(title).replace(chr(10), '<br>')}</div>
    {visual}<div class="std-footer">{esc(footer)}</div>
  </div>
</div>'''


def agenda_slide(slide_id: str, content: str) -> str:
    parts = content.split("／")
    heading = parts[1]
    chapters = [p for p in parts[2:] if p.startswith("第") and "章" in p]
    benefit = next((p for p in parts if p.startswith("【この動画でわかること】")), "")
    benefits = re.sub(r"^【この動画でわかること】", "", benefit)
    benefit_items = [re.sub(r"^[①-⑳]\s*", "", item) for item in re.split(r"\s*(?=[①-⑳])", benefits)]
    li_left = "".join(f'<li><span class="num">{i:02}</span><span>{esc(c)}</span></li>' for i, c in enumerate(chapters, 1))
    li_right = "".join(f'<li><span class="check">✓</span><span>{esc(x.strip())}</span></li>' for x in benefit_items if x.strip())
    left = page_head(heading) + f'<ul class="agenda">{li_left}</ul>'
    right = page_head("この動画でわかること") + f'<ul class="benefits">{li_right}</ul>'
    return spread(slide_id, left, right)


def divider_slide(slide_id: str, content: str) -> str:
    match = re.search(r"第(\d+)章\s*(.*)", content)
    num, title = (match.group(1), match.group(2).strip()) if match else ("", content)
    left = f'''<div class="divider"><div class="kicker">CHAPTER</div><div class="num">{esc(num)}</div><div class="seal">FILE No.{esc(num)}</div></div>'''
    right = f'<div class="page-body center"><div class="big-title">{esc(title)}</div><div class="lead" style="text-align:center">この章のポイントを確認</div></div>'
    return spread(slide_id, left, right)


def generic_slide(slide_id: str, content: str) -> str:
    parts = content.split("／")
    section = parts[0]
    title = parts[1] if len(parts) > 1 else section
    details = parts[2:] if len(parts) > 2 else [section]
    midpoint = (len(details) + 1) // 2
    left_items, right_items = details[:midpoint], details[midpoint:]
    if not right_items:
        right_items = ["ポイントを整理", "申込時は対象プラン・手続き方法を確認"]
    left_blocks = [rows([(str(i + 1), t) for i, t in enumerate(left_items)])]
    right_blocks = [rows([(str(i + midpoint + 1), t) for i, t in enumerate(right_items)])]
    left_title = title if section in ("まとめ", "テロップ", "タイトル") else section
    right_title = "確認ポイント"
    if "まとめ" in section:
        left_title, right_title = "初期費用の推移", "申し込みの選び方"
    if section == "テロップ":
        left_title, right_title = title, "覚えておきたいこと"
    if section.startswith("第"):
        left_title, right_title = title, "対象と注意点"
    return spread(slide_id,
                  body_page(left_title, left_blocks),
                  body_page(right_title, right_blocks))


def pricing_slide(slide_id: str) -> str:
    chart = asset("public/images/charts/IIJmio.png")
    logo = asset("public/images/logo/iijmio_logo.png")
    left = f'''<div class="head-left eval-head"><img class="logo" src="{logo}" alt="IIJmio"><div class="total"><div class="label">総合評価</div><div class="grade">A</div></div></div>
<div class="visual" style="height:auto;flex:1"><img src="{chart}" alt="IIJmio 評価レーダーチャート"></div>'''
    plan_rows = "".join(f"<tr><td>{gb}</td><td>{yen}</td></tr>" for gb, yen in [("2GB", "850円"), ("5GB", "950円"), ("10GB", "1,400円"), ("15GB", "1,600円"), ("25GB", "2,000円")])
    right = body_page("IIJmioの料金プラン", [
        f'<table class="sheet"><thead><tr><th>データ容量</th><th>月額料金</th></tr></thead><tbody>{plan_rows}</tbody></table>',
        '<div class="note">※ドコモ回線・au回線を選択可／税込</div>'
    ], centered=True)
    return spread(slide_id, left, right, price=True)


def evaluation_slide(slide_id: str, content: str) -> str:
    header = re.match(r"評価見開き／([^／]+)／総合:([A-Z]+)／", content)
    if not header:
        raise ValueError(f"Invalid evaluation content for slide {slide_id}")
    company, overall = header.groups()
    criteria = [m.groups() for m in re.finditer(r"([^／:]+):([A-Z]+)（＋(.*?)／－(.*?)(?=／[^／:]+:[A-Z]+（＋|$)", content)]
    criteria = [(name, rank, pro, con[:-1] if con.endswith("）") else con) for name, rank, pro, con in criteria]
    # Keep the rubric's published fixed order even if the source changes order.
    order = {name: i for i, name in enumerate(("データ料金", "通信品質", "初期費用", "通話料", "店舗サポート", "オプション"))}
    criteria.sort(key=lambda item: order.get(item[0], 99))
    logo = asset("public/images/logo/iijmio_logo.png")
    left_cards = "".join(eval_card(*item) for item in criteria[:3])
    right_cards = "".join(eval_card(*item) for item in criteria[3:])
    left = f'<div class="head-left eval-head"><img class="logo" src="{logo}" alt="{esc(company)}"><div class="total"><div class="label">総合評価</div><div class="grade">{esc(overall)}</div></div></div><div class="cards eval-cards">{left_cards}</div>'
    right = f'<div class="page-head eval-title">{esc(company)}を6観点で評価</div><div class="cards eval-cards">{right_cards}</div><div class="note eval-note">※本評価は当チャンネルの独断と偏見による独自評価であり、キャンペーン割引等は考慮していません</div>'
    return spread(slide_id, left, right, price=True)


def eval_card(name: str, rank: str, pro: str, con: str) -> str:
    return f'''<div class="card"><div class="rank {esc(rank)}">{esc(rank)}</div><div class="card-name">{esc(name)}</div>
<div class="line pro"><span class="tag">＋</span>{esc(pro)}</div><div class="line con"><span class="tag">－</span>{esc(con)}</div></div>'''


def special(slide_id: str, content: str) -> str:
    if slide_id in {"1", "2", "3", "4"}:
        return std_slide(slide_id, content, kind={"1": "hook", "2": "announcement", "3": "campaign", "4": "title"}[slide_id])
    if slide_id == "5":
        return agenda_slide(slide_id, content)
    if slide_id.endswith("-0") and not content.startswith("評価見開き／"):
        return divider_slide(slide_id, content)
    if content.startswith("評価見開き／"):
        return pricing_slide(slide_id) if slide_id.endswith("-0") else evaluation_slide(slide_id, content)
    if slide_id == "7":
        return spread(slide_id,
            body_page("初期費用は時期で3段階", [
                '<table class="sheet"><thead><tr><th>申込日</th><th>eSIM</th><th>SIMカード</th></tr></thead><tbody><tr><td>〜11/4</td><td class="em">1,650円</td><td>3,300円</td></tr><tr><td>11/5〜11/30</td><td colspan="2">3,300円</td></tr><tr><td>12/1〜</td><td colspan="2" class="em">3,850円</td></tr></tbody></table>',
                '<div class="note">Web申込みの初期費用（税込）</div>'
            ], centered=True),
            body_page("適用範囲", [rows([("割引", "11月4日まで：ギガプランのeSIM"), ("値上げ", "12月1日から：ギガプラン・eSIMサービス データプラン ゼロのWeb申込み")])]), price=True)
    if slide_id == "7-1":
        return spread(slide_id,
            body_page("eSIMってなに？", [emphasis("契約情報をスマホにダウンロードして使うSIM")], centered=True),
            body_page("電子チケットのような仕組み", [
                '<div class="esim-compare"><div><i class="fa-solid fa-envelope"></i><b>紙のチケット</b><span>郵送で受け取る</span></div><strong>→</strong><div><i class="fa-solid fa-mobile-screen-button"></i><b>電子チケット</b><span>スマホに届く</span></div></div>',
                lead("eSIMは契約情報をスマホにダウンロード")
            ]))
    if slide_id == "7-2":
        return spread(slide_id,
            body_page("速報を見逃さない", ['<div class="bigicon"><i class="fa-solid fa-bell"></i></div>', emphasis("チャンネル登録で値上げ・キャンペーンの速報をチェック")], centered=True),
            body_page("チャンネル登録", ['<div class="subscribe-cta"><span>チャンネル登録</span><i class="fa-solid fa-bell"></i></div>', lead("最新情報を動画でお届けします")], centered=True))
    if slide_id == "9":
        return spread(slide_id,
            body_page("eSIM割引の対象条件", [rows([("1", "IIJmio公式サイトからの新規申込み（他社からの乗り換えも対象）"), ("2", "ギガプランのeSIM（音声・SMS機能付き・データ通信専用）"), ("3", "1人（mioID）1回線まで")])]),
            body_page("対象外・併用条件", [rows([("対象外", "家電量販店・ネットショップのパッケージ経由"), ("併用", "他の初期費用割引との併用不可")])]))
    if slide_id == "9-2":
        return spread(slide_id,
            body_page("初期費用とは別の手数料", [rows([("SIMカード", "SIMカードで申し込む場合：SIMカード発行手数料がかかる"), ("eSIM", "eSIMの場合：SIMプロファイル発行手数料は11月4日まで0円", "SIMプロファイル発行手数料割引キャンペーン（2026年11月4日まで）")])]),
            body_page("eSIMの発行手数料", [emphasis("11月4日まで 0円"), lead("11月5日以降はeSIMでも発行手数料がかかる"), '<div class="note">※金額はIIJmio公式サイトでご確認ください</div>']))
    if slide_id == "9-3":
        return spread(slide_id,
            body_page("値上げの対象外", [emphasis("初期費用が無料のため値上げの対象外"), lead("家電量販店・ネットショップのパッケージ経由")], centered=True),
            body_page("パッケージで申し込む", [rows([("1", "エントリーコード・パスコードを購入"), ("2", "コード経由で手続き"), ("✓", "初期費用が無料のため値上げ対象外")])]))
    if slide_id == "11-5":
        thumb = asset("public/images/thumbnails/IIJmioって実際どうなの？元ユーザーが教える「損しない契約方法」と「お昼の速度」の真実.png")
        return spread(slide_id,
            f'<div class="visual"><img src="{thumb}" alt="IIJmioの過去動画サムネイル"></div>',
            '<div class="page-body center"><div class="bigicon"><i class="fa-solid fa-circle-play"></i></div><div class="big-title">IIJmioの<br>過去動画も<br><span class="em">チェック！</span></div><div class="note">IIJmioの特徴とお昼の速度を解説</div></div>')
    if slide_id == "13":
        return spread(slide_id,
            body_page("初期費用を抑える3つの方法", [rows([("1", "公式キャンペーン中に申し込む（今ならeSIM割引・11月4日まで）"), ("2", "エントリーパッケージを使う（手順が1つ増え、今回のeSIM割引は対象外）")])]),
            body_page("もうひとつの方法", [rows([("3", "提携サイト限定の特典があるSIMを選ぶ（mineoなど）")]), lead("時期や申込経路で、使える特典が変わります")]))
    if slide_id == "13-2":
        return spread(slide_id,
            body_page("ショウの場合", [rows([("昔", "エントリーパッケージを使って乗り換え")])], centered=True),
            body_page("最近の乗り換え方", [rows([("今", "各社公式キャンペーン期間中の乗り換えが中心"), ("＋", "後から付くポイント還元なども活用")])]))
    if slide_id == "13-3":
        return spread(slide_id,
            body_page("方法③ 提携サイト限定の特典", [lead("mineoは概要欄の提携サイト限定リンクから申し込むと事務手数料が無料")], centered=True),
            body_page("申し込み方", [rows([("1", "概要欄の提携サイト限定リンクから申し込む"), ("✓", "別の商品を買う必要なし"), ("∞", "時期を問わず利用できる")])]))
    if slide_id == "15":
        return spread(slide_id,
            body_page("初期費用の推移", [
                '<table class="sheet"><thead><tr><th>申込時期</th><th>eSIM初期費用</th></tr></thead><tbody><tr><td>〜11/4</td><td class="em">1,650円</td></tr><tr><td>11/5〜11/30</td><td>3,300円</td></tr><tr><td>12/1〜</td><td class="em">3,850円</td></tr></tbody></table>',
                '<div class="note">eSIMの発行手数料も11月4日まで0円。SIMカードは発行手数料が別途かかります。</div>'
            ], centered=True),
            body_page("迷ったらキャンペーン中に", [emphasis("公式キャンペーン中の申込みが手軽", "手軽"), lead("最新の対象条件を確認してから手続き")]), price=True)
    if slide_id == "16":
        return spread(slide_id,
            body_page("ご注意", ['<div class="bigicon"><i class="fa-solid fa-circle-exclamation"></i></div>', '<div class="big-title">公式情報を<br>ご確認ください</div>'], centered=True),
            body_page("申込み前に公式サイトへ", ['<div class="warn"><span class="ic">!</span>申し込みの際は必ずIIJmio公式サイトをご確認ください。プラン内容やキャンペーン情報はすべてIIJmio公式サイトの内容が正となります。</div>', '<div class="note">※料金・条件は動画投稿時点の情報です</div>']))
    if slide_id == "17":
        return spread(slide_id,
            body_page("コメントありがとうございます！", ['<div class="bigicon"><i class="fa-regular fa-comments"></i></div>', lead("皆さんの声をお待ちしています")], centered=True),
            body_page("ぜひ教えてください", [rows([("1", "あなたの使い方"), ("2", "エリアの電波状況"), ("3", "わかりにくかった点")])]))
    if slide_id == "18":
        return spread(slide_id,
            body_page("スマホ代の見直し", [lead("見直して浮いた分は貯蓄や運用にも回せます"), lead("初期費用も毎月の料金も見直して節約")], centered=True),
            body_page("これからも動画をお届け", ['<div class="big-title">自分に合う<br><span class="em">1枚</span>が見つかる</div>', lead("役立つ動画をこれからも作っていきます")], centered=True))
    if slide_id == "19":
        return spread(slide_id,
            body_page("ご視聴ありがとうございました！", ['<div class="big-title">ご視聴<br>ありがとう<br>ございました！</div>'], centered=True),
            body_page("チャンネル登録・高評価", ['<div class="logos"><i class="fa-solid fa-thumbs-up" style="font-size:112px;color:var(--brand)"></i><i class="fa-solid fa-bell" style="font-size:112px;color:var(--brand)"></i></div>', lead("チャンネル登録・グッドボタンをよろしくお願いします！")], centered=True))
    return generic_slide(slide_id, content)


def read_scenario() -> list[tuple[str, str]]:
    with MASTER.open(encoding="utf-8-sig", newline="") as f:
        rows_in = csv.DictReader(f)
        required = {"スライドID", "スライドに表示する内容"}
        if not required.issubset(rows_in.fieldnames or []):
            raise ValueError(f"CSV columns missing: {required - set(rows_in.fieldnames or [])}")
        slides: dict[str, str] = {}
        for row in rows_in:
            sid = (row["スライドID"] or "").strip()
            content = (row["スライドに表示する内容"] or "").strip()
            if sid:
                slides.setdefault(sid, content)
        return list(slides.items())


def main() -> None:
    slides = read_scenario()
    ids = [sid for sid, _ in slides]
    if not ids:
        raise ValueError("No slide IDs found in master CSV")
    sections = [special(sid, content) for sid, content in slides]
    doc = f'''<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>IIJmio eSIM初期費用キャンペーン｜格安SIM図鑑</title>
<link href="https://fonts.googleapis.com/css2?family=M+PLUS+Rounded+1c:wght@400;500;700;800;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
<link rel="stylesheet" href="templates/spread-base.css">
<style>
.std{{width:1280px;height:720px;border:10px solid var(--primary-color);box-sizing:border-box;position:relative;overflow:hidden;display:flex;align-items:center;justify-content:center;background:radial-gradient(circle at 50% 45%,#fff 0 42%,#dcecff 43% 100%);flex-shrink:0}}
.std-burst{{position:absolute;inset:-250px;background:repeating-conic-gradient(from 0deg at 50% 48%,rgba(21,101,192,.10) 0deg 4deg,transparent 4deg 10deg);pointer-events:none}}
.std-ribbon{{position:absolute;top:35px;left:-15px;transform:rotate(-4deg);padding:12px 48px;background:#c8102e;color:white;font-size:34px;font-weight:900;box-shadow:0 8px 15px #0003}}
.std-art{{position:absolute;z-index:1;right:34px;bottom:28px;width:150px;height:150px;object-fit:contain;pointer-events:none}}
.std-copy{{position:relative;z-index:1;box-sizing:border-box;width:100%;padding:90px 205px 36px 58px;text-align:center;color:var(--text-dark)}}
.std-kicker{{display:inline-block;padding:10px 24px;border-radius:999px;background:#e3f0fb;color:#0d47a1;font-size:30px;font-weight:900;margin-bottom:14px}}
.std-title{{font-size:76px;font-weight:900;line-height:1.05;color:#142c4d;text-shadow:2px 3px white,4px 5px #fff;}}
.std-flow{{display:flex;justify-content:center;align-items:center;gap:28px;margin:16px auto 8px;font-size:40px;font-weight:900;color:#263238}}
.std-flow strong{{font-size:58px;color:#c8102e}}.std-flow b{{font-size:54px;color:#1565c0}}.std-flow .strike{{text-decoration:line-through;color:#777}}
.std-footer{{font-size:31px;font-weight:900;color:#34495e;margin-top:6px}}
.eval-head .logo{{height:82px}}.eval-cards .card{{flex:0 0 auto;grid-template-columns:84px 1fr;gap:4px 16px;padding:6px 18px}}
.eval-cards .card .rank{{width:78px;height:78px;font-size:42px}}
.eval-cards .card-name{{font-size:38px}}
.eval-cards .card .line{{font-size:30px;line-height:1.1}}
.eval-title{{font-size:54px;margin-bottom:14px}}
.eval-note{{font-size:28px;text-align:center;margin-top:0}}
.agenda{{gap:8px}}
.esim-compare{{display:flex;align-items:center;justify-content:space-evenly;gap:18px}}
.esim-compare>div{{display:flex;flex-direction:column;align-items:center;gap:12px;background:#fff;border:4px solid #e7dcc2;border-radius:20px;padding:24px 30px;font-size:38px;font-weight:900;flex:1}}
.esim-compare i{{font-size:82px;color:var(--brand)}}.esim-compare span{{font-size:32px;color:var(--ink-soft)}}.esim-compare>strong{{font-size:62px;color:var(--brand)}}
.subscribe-cta{{display:flex;align-items:center;justify-content:center;gap:22px;margin:0 auto 30px;padding:24px 34px;width:max-content;background:#e53935;color:#fff;border-radius:18px;box-shadow:0 8px 0 #b71c1c;font-size:48px;font-weight:900}}
.subscribe-cta i{{font-size:48px}}
.page-head{{font-size:56px}}.rows .tx{{font-size:42px;min-width:0;flex:1 1 0;white-space:normal;overflow-wrap:anywhere}}.rows .tx .sub{{white-space:normal;overflow-wrap:anywhere}}.rows li{{padding:20px 24px}}
</style></head><body>
{''.join(sections)}
</body></html>'''
    OUTPUT.write_text(doc, encoding="utf-8")
    print(f"Generated {len(slides)} slides: {OUTPUT}")
    print("Slide IDs: " + ", ".join(ids))


if __name__ == "__main__":
    main()
