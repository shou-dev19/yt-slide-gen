#!/usr/bin/env python3
"""Generate slides.html for video 38 from its scenario CSV.

The CSV remains the source of truth for on-slide copy.  This generator only
selects the appropriate spread-base.css components for each slide type.
"""

from __future__ import annotations

import csv
import html
import re
from collections import OrderedDict
from dataclasses import dataclass, field
from pathlib import Path


PROJECT_ROOT = Path("/workspaces/yt-factory/packages/slide-gen")
SCENARIO_CSV = Path(
    "/workspaces/yt-factory/packages/scenario-gen/archive/videos/"
    "38_【2026年最新】格安SIMの無制限プラン比較！最安は月250円/long/"
    "【2026年最新】格安SIMの無制限プラン比較！最安は月250円.csv"
)
OUTPUT_HTML = Path("/workspaces/yt-factory/packages/slide-gen/slides.html")

BRANDS = {
    "red": ("#C8102E", "#9a0c23", "#fde3e7"),
    "green": ("#22a73f", "#1c8b34", "#e8f5e6"),
    "blue": ("#1565C0", "#0d47a1", "#e3f0fb"),
}

CHAPTERS = {
    "4-0": ("1", "「無制限」にも種類がある", "3つの仕組みを先に整理"),
    "5-0": ("2", "楽天モバイル", "速度保証型"),
    "7-0": ("3", "mineo「マイそく」", "低速定額型"),
    "9-0": ("4", "povo2.0", "都度トッピング型"),
    "12-0": ("5", "まとめ", "あなた向きの無制限は？"),
}

LOGOS = {
    "楽天モバイル": "public/images/logo/Mobile_logo_1line_magenta.png",
    "mineo（マイそく）": "public/images/logo/Mineo_logo.png",
    "povo2.0": "public/images/logo/Povo_logo.png",
}

CHARTS = {
    "楽天モバイル": "public/images/charts/楽天モバイル.png",
    "mineo（マイそく）": "public/images/charts/mineo.png",
    "povo2.0": "public/images/charts/povo2.0.png",
}

THUMBNAILS = {
    "6-3": "public/images/thumbnails/【2025年最新】楽天モバイルは繋がらない？1年以上使って分かった本音メリット・デメリットを全公開！_サムネ.png",
    "8-6": "public/images/thumbnails/【裏技】mineo歴8年が教える「実質使い放題」の極意！契約前に知らないと損する5つの節約術_サムネ.png",
    "11-3": "public/images/thumbnails/36_【2026年最新】povo実質月484円プランの全容と3つの注意点_サムネ1.png",
    "11-7": "public/images/thumbnails/【2026年最新】最強の2枚持ちおすすめ格安SIM組み合わせ3選！_サムネ1.png",
}

CTA_HEADLINES = {
    "6-3": "楽天モバイルは本当に繋がる？<br>1年使った本音レビュー",
    "8-6": "mineoの実質使い放題<br>極意は過去動画で！",
    "11-3": "povoのトッピング活用術<br>過去動画で徹底解説！",
    "11-7": "2枚持ちの組み合わせは<br>専用動画で解説！",
}

MANUAL_HEADINGS = {
    "6-2": "データ無制限だからできる\n「自宅Wi-Fi」がわりの使い方",
    "8-5": "ショウはマイピタ3Mbpsの\nパケット放題を普段使い",
    "10": "povo2.0は\n「都度トッピング型」",
    "11-2": "povo2.0は\n「サブ回線」として持つ人が多い",
    "11-4": "デュアルSIM（2枚持ち）で\nいいとこ取り",
    "13-1": "⑤povoは基本料0円だから\n2枚持ちが効く",
}

MANUAL_RIGHT_HEADINGS = {
    "4-1": "代表SIM・料金・速度",
}

# The terse on-slide fields below leave important context in the dialogue only.
# Keep that context visual by distributing four decision points across the spread
# instead of falling back to a decorative icon plus a single small card.
DIALOGUE_DETAIL_OVERRIDES = {
    # Split the three mechanisms and their concrete examples into matching
    # three-row pages.  This keeps the taxonomy readable while carrying the
    # representative price/speed facts stated later in the same scenario.
    "4-1": [
        "速度保証型｜速度制限なしで使い放題",
        "低速定額型｜最大速度を抑えて定額",
        "都度トッピング型｜使う日だけ購入",
        "楽天モバイル｜月額3,278円｜速度制限なし",
        "mineo マイそく｜月額250円〜｜最大32kbps〜5Mbps",
        "povo2.0｜24時間330円｜au回線品質",
    ],
    "4-2": [
        "まず自分の使い方をイメージする",
        "動画をよく見る人→速度を重視",
        "SNS・テキスト中心→安さを重視",
        "安さだけで選ぶと「思っていたのと違う」になりやすい",
    ],
    "6-1": [
        "電話をよく使う人にも向いている",
        "楽天モバイルショップで対面相談できる",
        "対面で相談できるのが安心材料",
        "店舗数は大手キャリアほど多くない",
    ],
    "8-1": [
        "プレミアムは最大5Mbpsで高画質動画もOK",
        "平日12時台はプレミアム以外 最大32kbps",
        "プレミアムも平日12時台は最大200kbps",
        "3日間で10GB以上使うと速度制限",
    ],
    "8-2": [
        "通常3,300円の事務手数料が無料",
        "初期費用をぐっと抑えられる",
        "SIMカード発行料440円は別途必要",
        "乗り換え時は概要欄の限定リンクを活用",
    ],
    "8-3": [
        "マイピタはデータ容量が決まったプラン",
        "契約容量までは高速通信",
        "容量を使い切るとパケット放題へ",
        "低速でも追加料金なしで実質使い放題",
    ],
    "8-4": [
        "3GB・7GBは最大1Mbps",
        "15GB・30GB・50GBは最大3Mbps",
        "普段は契約容量分の高速通信",
        "使い切ったあとも無料で実質使い放題",
    ],
    "8-5": [
        "ショウ自身も3Mbpsを普段使い",
        "標準画質の動画なら問題なく見られる",
        "常に爆速でなくても意外と困らない",
        "マイそくと違い平日12時台の速度制限なし",
    ],
    "11-1": [
        "データ使い放題24時間は330円",
        "必要な日だけトッピングを購入",
        "使わない日は基本料0円で待機",
        "180日間なにも購入しないと利用停止",
    ],
    "11-2": [
        "旅行・帰省など単発でガッツリ使う日に",
        "ここぞという日だけデータを追加",
        "普段使いのメイン回線よりサブ回線向き",
        "月極めではなくピンポイントで頼れる",
    ],
    "13-1": [
        "楽天モバイル＋povoで“いいとこ取り”",
        "mineo＋povoで“いいとこ取り”",
        "安さだけに飛びつかない",
        "まず自分の使い方を振り返る",
    ],
    "13-2": [
        "一番安いものをなんとなく選ばない",
        "価格だけでなく通信品質も確認",
        "使い勝手をなるべく落とさない",
        "自分に合うSIMで無理のない固定費削減",
    ],
}


@dataclass
class Slide:
    slide_id: str
    contents: list[str] = field(default_factory=list)
    dialogue: list[str] = field(default_factory=list)

    @property
    def content(self) -> str:
        for value in self.contents:
            if value.startswith("評価見開き"):
                return value
        return self.contents[0] if self.contents else ""


def e(value: str) -> str:
    return html.escape(value, quote=True)


def clean_content(value: str) -> str:
    return re.sub(r"^(?:テロップ|タイトル)：", "", value.strip())


def split_content(value: str) -> list[str]:
    return [clean_content(part) for part in value.split("／") if part.strip()]


def brand_style(name: str) -> str:
    brand, deep, soft = BRANDS[name]
    return f"--brand:{brand};--brand-deep:{deep};--brand-soft:{soft}"


def load_slides() -> list[Slide]:
    grouped: OrderedDict[str, Slide] = OrderedDict()
    inherited_content = ""
    with SCENARIO_CSV.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            raw_content = row["スライドに表示する内容"].strip()
            if raw_content and raw_content != "同上":
                inherited_content = raw_content
            effective_content = inherited_content if raw_content == "同上" else raw_content
            slide_id = row["スライドID"].strip()
            if not slide_id:
                continue
            slide = grouped.setdefault(slide_id, Slide(slide_id))
            if effective_content and effective_content not in slide.contents:
                slide.contents.append(effective_content)
            dialogue = row["セリフ"].strip()
            if dialogue:
                slide.dialogue.append(dialogue)
    return list(grouped.values())


def page(
    side: str,
    heading: str,
    body: str,
    page_no: int | None,
    *,
    right_tab: bool = False,
    heading_small: str = "",
    heading_size: int | None = None,
) -> str:
    tab = '<span class="index-tab">格安SIM図鑑</span>' if right_tab else ""
    small = f"<small>{e(heading_small)}</small>" if heading_small else ""
    number = f'<span class="page-no">― {page_no} ―</span>' if page_no is not None else ""
    heading_markup = "<br>".join(e(part) for part in heading.split("\n"))
    heading_style = f' style="font-size:{heading_size}px"' if heading_size else ""
    return (
        f'<div class="page {side}">{tab}'
        f'<div class="page-head"{heading_style}>{heading_markup}{small}</div>'
        f"{body}{number}</div>"
    )


def book(
    slide_id: str,
    left: str,
    right: str,
    *,
    brand: str = "red",
    price_note: bool = False,
) -> str:
    extra = " price-note" if price_note else ""
    return (
        f"<!-- Slide ID: {e(slide_id)} -->\n"
        f'<div class="slide-container{extra}" style="{brand_style(brand)}">'
        '<div class="book"><div class="spine"></div>'
        f"{left}{right}</div></div>"
    )


def rows(items: list[str], *, icons: list[str] | None = None, font_size: int = 44) -> str:
    rendered = []
    for index, item in enumerate(items):
        if icons:
            marker = f'<span class="ic"><i class="fa-solid {icons[index % len(icons)]}"></i></span>'
        else:
            marker = f'<span class="badge">{index + 1}</span>'
        rendered.append(
            f'<li>{marker}<div class="tx" style="font-size:{font_size}px">{e(item)}</div></li>'
        )
    return '<ul class="rows">' + "".join(rendered) + "</ul>"


def feature_body(items: list[str], *, icons: list[str], font_size: int = 43) -> str:
    """Use large CSS emphasis components when a page has only 1–3 points."""
    if len(items) == 1:
        return (
            '<div class="page-body feature-body single-feature">'
            f'<div class="bigicon feature-icon"><i class="fa-solid {icons[0]}"></i></div>'
            f'<div class="emph feature-emph" style="font-size:{font_size}px">{e(items[0])}</div>'
            "</div>"
        )
    blocks = []
    for index, item in enumerate(items):
        blocks.append(
            f'<div class="emph feature-emph" style="font-size:{font_size}px">'
            f'<i class="fa-solid {icons[index % len(icons)]}" style="color:var(--brand);margin-right:16px"></i>'
            f"{e(item)}</div>"
        )
    return '<div class="page-body feature-body feature-grid">' + "".join(blocks) + "</div>"


def standard_intro(slide: Slide) -> str:
    slide_id = slide.slide_id
    if slide_id == "1":
        return f"""<!-- Slide ID: 1 -->
<div class="slide-container std">
  <div class="sunburst"></div><div class="corner-accent"></div>
  <div class="std-grid">
    <div class="std-copy">
      <div class="cover-badge">迷子、続出！</div>
      <div class="std-kicker">同じ「無制限」なのに…</div>
      <h1>結局どれが<br><span>お得なの？</span></h1>
      <div class="logo-strip"><img src="{LOGOS['楽天モバイル']}"><img src="{LOGOS['mineo（マイそく）']}"><img src="{LOGOS['povo2.0']}"></div>
    </div>
    <img class="std-hero" src="public/images/irasutoya/pose_atama_kakaeru_woman.png" alt="プラン選びに迷う人">
  </div>
</div>"""
    if slide_id == "2":
        return f"""<!-- Slide ID: 2 -->
<div class="slide-container std price-note">
  <div class="sunburst"></div>
  <div class="cover-badge">2026年 最新比較</div>
  <div class="std-grid title-grid">
    <div class="std-copy">
      <div class="std-kicker">3つの無制限を徹底比較</div>
      <h1><span>月250円</span>から<br>本当の使い放題まで</h1>
      <div class="price-flow"><b>楽天モバイル</b><strong>3,278円</strong><i>vs</i><b>mineo</b><strong>250円〜</strong><i>vs</i><b>povo</b><strong>1日330円</strong></div>
    </div>
    <img class="std-hero compact" src="public/images/irasutoya/bikkuri_me_tobideru_man.png" alt="価格差に驚く人">
  </div>
</div>"""

    parts = split_content(slide.content)
    chapters = [p for p in parts[1:] if p.startswith("第")]
    benefits_text = " ".join(parts)
    benefits = re.findall(r"[①②③④⑤]([^①②③④⑤]+)", benefits_text)
    clean_chapters = [re.sub(r"^第\d章\s*", "", chapter) for chapter in chapters]
    agenda_items = "".join(
        f"<li><span>{index}</span>{e(chapter)}</li>"
        for index, chapter in enumerate(clean_chapters, 1)
    )
    benefit_items = "".join(f"<li><i class=\"fa-solid fa-circle-check\"></i>{e(x.strip())}</li>" for x in benefits[-2:])
    return f"""<!-- Slide ID: 3 -->
<div class="slide-container std agenda-std">
  <div class="sunburst"></div>
  <div class="agenda-title"><span>格安SIM図鑑</span> 本日のもくじ</div>
  <div class="agenda-columns">
    <ol>{agenda_items}</ol>
    <div class="benefit-card"><b>この動画でわかること</b><ul>{benefit_items}</ul></div>
  </div>
</div>"""


def chapter_slide(slide: Slide) -> str:
    number, title, subtitle = CHAPTERS[slide.slide_id]
    brand = "green" if slide.slide_id == "7-0" else "blue" if slide.slide_id == "9-0" else "red"
    left = (
        '<div class="page left"><div class="divider">'
        '<div class="kicker">CHAPTER</div>'
        f'<div class="num">{e(number)}</div>'
        f'<div class="seal">FILE No.{int(number):02d}</div>'
        "</div></div>"
    )
    title_markup = "mineo<br>「マイそく」" if slide.slide_id == "7-0" else e(title)
    right = (
        '<div class="page right"><span class="index-tab">格安SIM図鑑</span>'
        '<div class="page-body center">'
        f'<div class="big-title">{title_markup}</div>'
        f'<div class="lead" style="margin-top:42px;text-align:center">{e(subtitle)}</div>'
        "</div></div>"
    )
    return book(slide.slide_id, left, right, brand=brand)


def parse_evaluation(content: str) -> tuple[str, str, list[tuple[str, str, str, str]]]:
    header = re.match(r"評価見開き／([^／]+)／総合:(SS|S|A|B|C)", content)
    if not header:
        raise ValueError(f"Invalid evaluation content: {content}")
    company, total = header.groups()
    pattern = re.compile(
        r"／([^／:]+):(SS|S|A|B|C)（＋(.*?)／－(.*?)）(?=／[^／:]+:(?:SS|S|A|B|C)（|$)"
    )
    aspects = pattern.findall(content)
    if len(aspects) != 6:
        raise ValueError(f"Expected six evaluation aspects for {company}, got {len(aspects)}")
    return company, total, aspects


def compact_eval(text: str) -> str:
    replacements = (
        ("データ無制限で月額", "データ無制限・月額"),
        ("と、速度保証型の中では手が届きやすい水準", "。速度保証型では手頃"),
        ("mineoの低速定額型と比べると", "低速定額型より"),
        ("場合もある", "ことも"),
        ("速度制限が無く、", "速度制限なし。"),
        ("動画やSNSも気にせず使える", "動画・SNSも容量を気にせず使える"),
        ("エリアによっては大手キャリアと体感差が出ることもある", "場所によって大手回線と体感差"),
        ("契約事務手数料などが抑えられていて始めやすい", "事務手数料を抑えて始めやすい"),
        ("楽天モバイルショップで対面相談ができる", "ショップで対面相談できる"),
        ("店舗数は大手キャリアほど多くはない", "店舗は大手ほど多くない"),
        ("海外ローミングなどオプションが充実", "海外ローミングなどが充実"),
        ("データシェアやデータ繰り越しはできない", "シェア・繰り越し不可"),
        ("オンラインでのサポート体制が整っている", "オンラインサポートが充実"),
        ("実店舗サポートは基本無いと考えた方がよい", "実店舗サポートは基本なし"),
        ("事務手数料0円・契約解除料0円・最低利用期間なし", "事務手数料・解除料0円、縛りなし"),
        ("データ使い放題24時間330円など必要な日だけ盛れる", "24時間330円など必要な日だけ追加"),
        ("買い忘れると低速・180日間購入がないと利用停止", "未購入時は低速・180日購入なしで停止"),
        ("専用アプリ経由だと", "専用アプリなら"),
        ("かけ放題オプションは有料", "かけ放題は有料"),
        ("当チャンネル限定リンクでは事務手数料がタダ", "限定リンクなら事務手数料0円"),
        ("基本的に", "通常"),
        ("特になし", "大きな弱点なし"),
    )
    for before, after in replacements:
        text = text.replace(before, after)
    return text


def evaluation_card(item: tuple[str, str, str, str]) -> str:
    name, rank, pro, con = item
    return (
        '<div class="card">'
        f'<div class="rank {e(rank)}">{e(rank)}</div>'
        f'<div class="card-name">{e(name)}</div>'
        f'<div class="line pro"><span class="tag">＋</span>{e(compact_eval(pro))}</div>'
        f'<div class="line con"><span class="tag">－</span>{e(compact_eval(con))}</div>'
        "</div>"
    )


def evaluation_slide(slide: Slide, page_numbers: tuple[int, int]) -> str:
    company, total, aspects = parse_evaluation(slide.content)
    brand = "green" if company.startswith("mineo") else "blue" if company.startswith("povo") else "red"
    left_body = (
        '<div class="head-left">'
        f'<img class="logo" src="{e(LOGOS[company])}" alt="{e(company)}">'
        f'<div class="total"><div class="label">総合評価</div><div class="grade">{e(total)}</div></div></div>'
        f'<div class="cards">{"".join(evaluation_card(item) for item in aspects[:3])}</div>'
    )
    right_body = (
        '<div class="head-right">'
        f'<img src="{e(CHARTS[company])}" alt="{e(company)}の評価チャート"></div>'
        f'<div class="cards">{"".join(evaluation_card(item) for item in aspects[3:])}</div>'
        '<div class="note eval-note">※本評価は当チャンネルの独断と偏見による独自評価であり、キャンペーン割引等は考慮していません</div>'
    )
    left = f'<div class="page left eval-page">{left_body}<span class="page-no">― {page_numbers[0]} ―</span></div>'
    right = (
        '<div class="page right eval-page"><span class="index-tab">格安SIM図鑑</span>'
        f'{right_body}<span class="page-no">― {page_numbers[1]} ―</span></div>'
    )
    return book(slide.slide_id, left, right, brand=brand, price_note=True)


def cta_slide(slide: Slide) -> str:
    headline = CTA_HEADLINES[slide.slide_id]
    brand = "green" if slide.slide_id == "8-6" else "blue" if slide.slide_id.startswith("11-") else "red"
    left = (
        '<div class="page left"><div class="visual">'
        f'<img src="{e(THUMBNAILS[slide.slide_id])}" alt="関連動画のサムネイル">'
        "</div></div>"
    )
    if slide.slide_id == "11-3":
        right = (
            '<div class="page right"><span class="index-tab">格安SIM図鑑</span>'
            '<div class="page-head">過去動画で徹底解説</div>'
            '<div class="page-body cta-detail">'
            '<div class="big-title cta-title">povoの<br>トッピング活用術</div>'
            + rows(
                ["トッピングの詳しい選び方", "月額料金を抑えるコツ"],
                icons=["fa-circle-check", "fa-coins"],
                font_size=40,
            )
            + '<div class="lead" style="text-align:center">概要欄・関連動画からチェック！</div>'
            "</div></div>"
        )
        return book(slide.slide_id, left, right, brand=brand)
    right = (
        '<div class="page right"><span class="index-tab">格安SIM図鑑</span>'
        '<div class="page-body center">'
        '<div class="bigicon" style="font-size:190px"><i class="fa-solid fa-circle-play"></i></div>'
        f'<div class="big-title cta-title">{headline}</div>'
        '<div class="lead" style="text-align:center">概要欄・関連動画からチェック！</div>'
        "</div></div>"
    )
    return book(slide.slide_id, left, right, brand=brand)


def combination_slide(slide: Slide, page_numbers: tuple[int, int]) -> str:
    parts = split_content(slide.content)
    is_rakuten = slide.slide_id == "11-5"
    first_logo = LOGOS["楽天モバイル"] if is_rakuten else LOGOS["mineo（マイそく）"]
    title = parts[0]
    left_body = (
        '<div class="page-body center">'
        f'<div class="logos"><img src="{e(first_logo)}"><span class="plus">＋</span><img src="{e(LOGOS["povo2.0"])}"></div>'
        f'<div class="emph"><span class="big">いいとこ取り</span><br>{e(title.replace("おすすめ①", "").replace("おすすめ②", ""))}</div>'
        "</div>"
    )
    right_body = '<div class="page-body">' + rows(parts[1:], icons=["fa-sim-card", "fa-bolt", "fa-coins"], font_size=42) + "</div>"
    left = page("left", "おすすめの2枚持ち", left_body, page_numbers[0])
    right = page("right", "使い分けのポイント", right_body, page_numbers[1], right_tab=True)
    return book(slide.slide_id, left, right, brand="blue", price_note=any("円" in p for p in parts))


def special_slide(slide: Slide) -> str | None:
    sid = slide.slide_id
    parts = split_content(slide.content)
    if sid == "11-8":
        left = (
            '<div class="page left"><div class="page-body center">'
            '<div class="bigicon"><i class="fa-solid fa-bell"></i></div>'
            '<div class="big-title cta-title">チャンネル登録<br>お願いします！</div></div></div>'
        )
        right = (
            '<div class="page right"><span class="index-tab">格安SIM図鑑</span>'
            '<div class="page-body center"><div class="logos emoji-logos"><span>📱</span><span>⚡</span><span>💰</span></div>'
            f'<div class="lead" style="text-align:center">{e(parts[-1])}</div>'
            '<div class="note" style="text-align:center">料金・キャンペーン改定も、わかりやすく速報します</div>'
            "</div></div>"
        )
        return book(sid, left, right, brand="blue")
    if sid == "14":
        left = (
            '<div class="page left"><div class="page-body center">'
            '<div class="bigicon"><i class="fa-solid fa-arrow-pointer"></i></div>'
            '<div class="big-title cta-title">気になるSIMへ<br>一歩進もう</div></div></div>'
        )
        right = (
            '<div class="page right"><span class="index-tab">格安SIM図鑑</span><div class="page-body center">'
            f'<div class="logos compact-logos"><img src="{LOGOS["楽天モバイル"]}"><img src="{LOGOS["mineo（マイそく）"]}"><img src="{LOGOS["povo2.0"]}"></div>'
            '<div class="emph">各社の<span class="em">公式サイト</span>は<br>概要欄リンクから</div>'
            "</div></div>"
        )
        return book(sid, left, right, brand="red")
    if sid == "15":
        examples = re.findall(r"「([^」]+)」", slide.content)
        left = (
            '<div class="page left"><div class="page-body center">'
            '<div class="bigicon"><i class="fa-solid fa-comments"></i></div>'
            '<div class="big-title cta-title">あなたの声を<br>教えてください！</div></div></div>'
        )
        right = (
            '<div class="page right"><span class="index-tab">格安SIM図鑑</span>'
            '<div class="page-head">コメント例</div><div class="page-body">'
            + rows(examples, icons=["fa-comment-dots"], font_size=42)
            + "</div></div>"
        )
        return book(sid, left, right, brand="red")
    if sid == "16":
        left = (
            '<div class="page left"><div class="page-body center">'
            '<div class="bigicon" style="color:#f0a020"><i class="fa-solid fa-circle-info"></i></div>'
            '<div class="big-title">ご注意</div></div></div>'
        )
        right = (
            '<div class="page right"><span class="index-tab">格安SIM図鑑</span>'
            '<div class="page-body center">'
            f'<div class="warn"><span class="ic"><i class="fa-solid fa-triangle-exclamation"></i></span>{e(parts[0])}</div>'
            '<div class="lead" style="text-align:center">お申し込み前に<br><span class="em">各社公式の最新情報</span>をご確認ください</div>'
            "</div></div>"
        )
        return book(sid, left, right, brand="red")
    if sid == "17":
        left = (
            '<div class="page left"><div class="page-body center blog-promo-body">'
            '<div class="bigicon blog-icon"><i class="fa-solid fa-pen-nib"></i></div>'
            '<div class="big-title blog-cta-title">ブログ・noteも<br>更新中！</div>'
            '<div class="lead blog-summary">動画より詳しい<br>格安SIM記事を掲載</div>'
            "</div></div>"
        )
        right = (
            '<div class="page right"><span class="index-tab">格安SIM図鑑</span>'
            '<div class="page-body center blog-visual-body">'
            '<img class="blog-header" src="public/images/common/ブログ_ヘッダー画像_スライド用.png" alt="ブログ">'
            '<div class="lead blog-link">格安SIMに関する詳しい記事は<br>概要欄リンクからぜひ！</div>'
            '<div class="note blog-note">ブログ・noteでじっくり読めます</div>'
            "</div></div>"
        )
        return book(sid, left, right, brand="green")
    if sid == "18":
        left = (
            '<div class="page left"><div class="page-body center">'
            '<div class="bigicon"><i class="fa-solid fa-bell"></i></div>'
            '<div class="big-title cta-title">チャンネル登録<br>よろしくお願いします！</div></div></div>'
        )
        right = (
            '<div class="page right"><span class="index-tab">格安SIM図鑑</span>'
            '<div class="page-body center"><div class="logos emoji-logos"><span>👍</span><span>🔔</span></div>'
            '<div class="lead thanks">最後までご視聴いただき<br>ありがとうございました！</div>'
            '<div class="note" style="text-align:center">次回も一緒にスマホ代を節約しましょう</div>'
            "</div></div>"
        )
        return book(sid, left, right, brand="red")
    return None


def general_slide(slide: Slide, page_numbers: tuple[int, int]) -> str:
    parts = split_content(slide.content)
    if not parts:
        parts = [slide.slide_id]
    title, details = parts[0], parts[1:]
    title = MANUAL_HEADINGS.get(slide.slide_id, title)
    details = DIALOGUE_DETAIL_OVERRIDES.get(slide.slide_id, details)
    brand = "green" if slide.slide_id.startswith(("7", "8")) else "blue" if slide.slide_id.startswith(("9", "10", "11")) else "red"
    price_note = "円" in slide.content or any("円" in item for item in details)

    if slide.slide_id == "6-2":
        left_body = '<div class="page-body">' + rows(details[:2], icons=["fa-wifi", "fa-house"], font_size=43) + "</div>"
        right_body = (
            '<div class="page-body center"><div class="visual mini-visual">'
            '<img src="public/images/irasutoya/internet_modem_router.png" alt="自宅Wi-Fi"></div>'
            f'<div class="lead" style="text-align:center">{e(details[-1])}</div></div>'
        )
        left = page("left", title, left_body, page_numbers[0], heading_size=52)
        right = page("right", "固定回線がわりにも", right_body, page_numbers[1], right_tab=True)
        return book(slide.slide_id, left, right, brand=brand, price_note=price_note)

    if slide.slide_id == "11-4":
        left_body = (
            '<div class="page-body center"><div class="visual mini-visual">'
            '<img src="public/images/common/複数回線を組み合わせるイメージ図.png" alt="デュアルSIM"></div>'
            f'<div class="emph"><span class="big">2枚持ち</span><br>{e(details[0])}</div></div>'
        )
        right_body = feature_body(details[1:], icons=["fa-sim-card", "fa-zero"], font_size=44)
        left = page("left", title, left_body, page_numbers[0], heading_size=52)
        right = page("right", "povo2.0を足す理由", right_body, page_numbers[1], right_tab=True)
        return book(slide.slide_id, left, right, brand=brand, price_note=True)

    if slide.slide_id in {"13", "13-3"}:
        midpoint = (len(details) + 1) // 2
        left_body = '<div class="page-body">' + rows(details[:midpoint], font_size=40) + "</div>"
        right_body = '<div class="page-body">' + rows(details[midpoint:], font_size=40) + "</div>"
        left = page("left", title, left_body, page_numbers[0], heading_small="①")
        right = page("right", title, right_body, page_numbers[1], right_tab=True, heading_small="②")
        return book(slide.slide_id, left, right, brand=brand, price_note=price_note)

    if not details:
        details = [title]
    midpoint = max(1, (len(details) + 1) // 2)
    left_items, right_items = details[:midpoint], details[midpoint:]
    if not right_items:
        right_items = [details[-1]]
    max_len = max(len(item) for item in details)
    font_size = 38 if max_len > 42 or len(details) >= 4 else 44
    if slide.slide_id == "4-1":
        left_icons = ["fa-gauge-high", "fa-gauge-simple-low", "fa-cart-plus"]
        right_icons = ["fa-tower-cell", "fa-leaf", "fa-calendar-day"]
    else:
        icons = ["fa-circle-check", "fa-bolt", "fa-coins", "fa-triangle-exclamation"]
        left_icons = icons
        right_icons = icons[midpoint:] or icons
    left_body = feature_body(left_items, icons=left_icons, font_size=font_size)
    right_body = feature_body(right_items, icons=right_icons, font_size=font_size)
    left = page(
        "left",
        title,
        left_body,
        page_numbers[0],
        heading_small="ポイント",
        heading_size=52 if slide.slide_id in {"4-1", "11-2"} else None,
    )
    right = page(
        "right",
        MANUAL_RIGHT_HEADINGS.get(slide.slide_id, "押さえておきたいこと"),
        right_body,
        page_numbers[1],
        right_tab=True,
        heading_size=50 if slide.slide_id == "4-1" else None,
    )
    return book(slide.slide_id, left, right, brand=brand, price_note=price_note)


def stylesheet() -> str:
    return """
  <style>
    body { --primary-color:#C8102E;--accent-red:#E53935;--text-dark:#212121; }
    .slide-container.std {
      width:1280px;height:720px;border:10px solid var(--primary-color);background:#fff9f5;
      box-sizing:border-box;position:relative;overflow:hidden;display:flex;flex-direction:column;
      justify-content:center;align-items:center;padding:42px;flex-shrink:0;color:var(--text-dark);
    }
    .sunburst { position:absolute;inset:0;background:repeating-conic-gradient(from 0deg at 54% 44%,rgba(200,16,46,.085) 0 5deg,transparent 5deg 10deg); }
    .corner-accent { position:absolute;right:-120px;top:-120px;width:360px;height:360px;background:#C8102E;transform:rotate(45deg);opacity:.92; }
    .std-grid { position:relative;z-index:1;width:100%;display:grid;grid-template-columns:minmax(0,1.75fr) minmax(260px,.65fr);align-items:center;gap:20px; }
    .std-copy h1 { font-size:91px;line-height:1.12;font-weight:900;margin:18px 0 24px;text-shadow:4px 4px 0 #fff;letter-spacing:-2px; }
    .std-copy h1 span { color:var(--accent-red);font-size:116px;white-space:nowrap; }
    .std-kicker { font-size:38px;font-weight:900;margin-top:20px; }
    .cover-badge { position:relative;z-index:2;background:#C8102E;color:#fff;font-size:34px;font-weight:900;padding:10px 28px;border-radius:8px;transform:rotate(-2deg);box-shadow:0 8px 16px #0003;align-self:flex-start; }
    .std-hero { width:100%;max-height:440px;object-fit:contain;filter:drop-shadow(0 16px 16px #0003); }
    .std-hero.compact { max-height:350px;align-self:end; }
    .logo-strip { display:flex;align-items:center;gap:16px;background:#fff;border:4px solid #eadfd8;border-radius:18px;padding:14px 20px;box-shadow:0 8px 20px #0002; }
    .logo-strip img { max-width:30%;height:54px;object-fit:contain; }
    .price-flow { display:grid;grid-template-columns:auto auto auto auto auto auto;align-items:center;gap:9px;background:#fff;border:4px solid #C8102E;border-radius:18px;padding:16px;font-size:24px;font-weight:900;box-shadow:0 8px 20px #0002; }
    .price-flow strong { color:#E53935;font-size:32px;white-space:nowrap; }.price-flow i{color:#777}
    .title-grid .std-copy h1 { font-size:72px;line-height:1.2 }.title-grid .std-copy h1 span{font-size:104px}
    .agenda-std { align-items:stretch;justify-content:flex-start;padding:32px 48px; }
    .agenda-title { position:relative;z-index:1;font-size:55px;font-weight:900;border-bottom:8px solid #C8102E;padding-bottom:12px; }
    .agenda-title span { color:#C8102E;font-size:28px;margin-right:22px;letter-spacing:2px; }
    .agenda-columns { position:relative;z-index:1;display:grid;grid-template-columns:1.18fr .82fr;gap:28px;flex:1;padding-top:22px;min-height:0; }
    .agenda-columns ol { list-style:none;display:flex;flex-direction:column;justify-content:space-between;gap:8px; }
    .agenda-columns ol li { background:#fff;border:3px solid #eadfd8;border-left:12px solid #C8102E;border-radius:13px;padding:11px 18px;font-size:31px;font-weight:900;display:flex;align-items:center;gap:16px;box-shadow:0 5px 12px #0001; }
    .agenda-columns ol span { width:49px;height:49px;background:#C8102E;color:#fff;border-radius:12px;display:grid;place-items:center;font-size:28px;flex:none; }
    .benefit-card { background:#fff0e9;border:5px solid #E53935;border-radius:20px;padding:24px;display:flex;flex-direction:column;justify-content:center; }
    .benefit-card b { color:#C8102E;font-size:33px;text-align:center;margin-bottom:18px; }
    .benefit-card ul { list-style:none;display:flex;flex-direction:column;gap:24px; }
    .benefit-card li { font-size:31px;font-weight:900;line-height:1.35;display:flex;gap:12px;align-items:flex-start; }
    .benefit-card i { color:#22a73f;margin-top:5px; }
    .eval-page { padding:24px 42px 250px; }.eval-page .head-left,.eval-page .head-right{height:118px;margin-bottom:10px;padding-bottom:8px}
    .eval-page .head-left .logo{height:66px;max-width:430px}.eval-page .total .grade{font-size:76px}.eval-page .total .label{font-size:23px}
    .eval-page .cards{gap:8px}.eval-page .card{grid-template-columns:82px 1fr;gap:2px 14px;padding:9px 16px;border-left-width:11px}
    .eval-page .card .rank{width:74px;height:74px;font-size:37px;border-radius:15px}.eval-page .card-name{font-size:31px}
    .eval-page .card .line{font-size:23px;line-height:1.12}.eval-page .head-right img{transform:translateX(-54px)}
    .eval-note{font-size:20px!important;text-align:center;line-height:1.25;margin-top:7px}
    .feature-body { gap:22px }
    .feature-grid .feature-emph {
      flex:1 1 0;min-height:0;padding:28px 34px;display:flex;align-items:center;justify-content:center;
    }
    .single-feature { justify-content:space-evenly }
    .single-feature .feature-icon {
      flex:0 0 205px;font-size:185px;display:grid;place-items:center;
    }
    .single-feature .feature-emph {
      flex:1 1 0;max-height:245px;padding:38px;display:grid;place-items:center;
    }
    .cta-title { font-size:68px; }.mini-visual{height:250px}.mini-visual img{max-height:230px}
    .cta-detail { gap:18px }.cta-detail .cta-title{font-size:64px}.cta-detail .rows{gap:14px}
    .cta-detail .rows li{padding:18px 22px}.cta-detail .lead{padding:20px 26px}
    .plus { font-size:72px;font-weight:900;color:var(--brand-deep) }.emoji-logos span{font-size:110px}
    .blog-promo-body { gap:18px }
    .blog-icon { font-size:230px }
    .blog-cta-title { font-size:100px }
    .blog-summary { width:100%;padding:22px 28px;font-size:42px;line-height:1.3;text-align:center }
    .blog-visual-body { gap:12px }
    .blog-header {
      width:100%;height:auto;max-height:540px;object-fit:contain;border-radius:18px;
      filter:drop-shadow(0 12px 20px #0003)
    }
    .blog-link { width:100%;padding:18px 24px;font-size:38px;line-height:1.25;text-align:center }
    .blog-note { font-size:28px;text-align:center }
    .thanks { font-size:57px;text-align:center;color:var(--brand-deep) }
    .compact-logos { gap:28px }.compact-logos img{height:76px;max-width:29%}
  </style>"""


def generate() -> tuple[int, list[str]]:
    slides = load_slides()
    rendered: list[str] = []
    page_no = 1

    for slide in slides:
        sid = slide.slide_id
        if sid in {"1", "2", "3"}:
            rendered.append(standard_intro(slide))
            continue
        if sid in CHAPTERS:
            rendered.append(chapter_slide(slide))
            continue
        special = special_slide(slide)
        if special:
            rendered.append(special)
            continue
        if sid in THUMBNAILS:
            rendered.append(cta_slide(slide))
            continue
        numbers = (page_no, page_no + 1)
        page_no += 2
        if slide.content.startswith("評価見開き"):
            rendered.append(evaluation_slide(slide, numbers))
        elif sid in {"11-5", "11-6"}:
            rendered.append(combination_slide(slide, numbers))
        else:
            rendered.append(general_slide(slide, numbers))

    document = f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>【2026年最新】格安SIMの無制限プラン比較</title>
  <link href="https://fonts.googleapis.com/css2?family=M+PLUS+Rounded+1c:wght@400;500;700;800;900&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
  <link rel="stylesheet" href="templates/spread-base.css">
{stylesheet()}
</head>
<body>
{chr(10).join(rendered)}
</body>
</html>
"""
    OUTPUT_HTML.write_text(document, encoding="utf-8")
    return len(slides), [slide.slide_id for slide in slides]


if __name__ == "__main__":
    count, slide_ids = generate()
    print(f"Generated {count} slides: {OUTPUT_HTML}")
    print("Slide IDs:", ", ".join(slide_ids))
