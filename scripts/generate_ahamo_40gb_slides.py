#!/usr/bin/env python3
"""Generate the long-form ahamo 40 GB deck from the master scenario CSV.

The scenario's ``スライドに表示する内容`` column is the source of truth.  This
module groups rows by slide ID and maps each group into components supplied by
``templates/spread-base.css``.  The generated HTML must never be hand-edited;
all layout changes belong here.
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
    "39_【2026年8月】ahamoが月額そのままで40GBに増量！？今後の選び方まで徹底解説/long/"
    "【2026年8月】ahamoが月額そのままで40GBに増量！？今後の選び方まで徹底解説.csv"
)
OUTPUT_HTML = PROJECT_ROOT / "slides.html"

EXPECTED_IDS = [
    "1", "2", "3", "4", "5-0", "6", "7", "8", "9-0", "10", "11",
    "12-0", "13", "14", "15-0", "15", "16", "17", "18", "19", "20",
    "21", "22-0", "23", "24", "25", "26", "27", "28",
]

AHAMO_LOGO = "public/images/logo/Ahamo_logo.png"
DOCOMO_LOGO = "public/images/logo/docomo_logo.png"
LINEMO_LOGO = "public/images/logo/LINEMO_logo.png"
POVO_LOGO = "public/images/logo/Povo_logo.png"
RAKUTEN_LOGO = "public/images/logo/Mobile_logo_1line_magenta.png"
DOCOMO_THUMB = (
    "public/images/thumbnails/"
    "【2026年最新】ドコモの通信品質が4キャリア中最下位。乗り換え先4社を比較_サムネ1.png"
)
AHAMO_THUMB = (
    "public/images/thumbnails/"
    "【あなたはどっち？】ahamoで得する人・損する人の違いを分かりやすく解説します！_サムネ.png"
)

BRAND = "--brand:#C8102E;--brand-deep:#9a0c23;--brand-soft:#fde3e7"

CHAPTERS = {
    "5-0": ("1", "何がどれだけ\n増えたの？", "料金据え置きで、容量アップ"),
    "9-0": ("2", "なぜ今この\nタイミングで増量？", "ドコモの発表と競争環境"),
    "12-0": ("3", "申込不要・\n自動適用の注意点", "終了時期は、まだ未発表"),
    "15-0": ("4", "他の格安SIMと比べて\nどう見える？", "容量・料金・通信品質で比較"),
    "22-0": ("5", "まとめ", "増量のポイントを最終確認"),
}


@dataclass
class Slide:
    slide_id: str
    contents: list[str] = field(default_factory=list)
    dialogue: list[str] = field(default_factory=list)

    @property
    def content(self) -> str:
        return self.contents[0] if self.contents else ""


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def clean(value: str) -> str:
    return re.sub(r"^(?:テロップ|タイトル)：", "", value.strip())


def parts(value: str) -> list[str]:
    return [clean(part) for part in value.split("／") if part.strip()]


def load_slides() -> list[Slide]:
    grouped: OrderedDict[str, Slide] = OrderedDict()
    inherited = ""
    with SCENARIO_CSV.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            raw = row["スライドに表示する内容"].strip()
            if raw and raw != "同上":
                inherited = raw
            effective = inherited if raw == "同上" else raw
            slide_id = row["スライドID"].strip()
            if not slide_id:
                continue
            slide = grouped.setdefault(slide_id, Slide(slide_id))
            if effective and effective not in slide.contents:
                slide.contents.append(effective)
            dialogue = row["セリフ"].strip()
            if dialogue:
                slide.dialogue.append(dialogue)
    result = list(grouped.values())
    actual_ids = [slide.slide_id for slide in result]
    if actual_ids != EXPECTED_IDS:
        raise ValueError(f"Unexpected slide IDs: {actual_ids}")
    return result


def page(
    side: str,
    heading: str,
    body: str,
    number: int | None,
    *,
    tab: bool = False,
    small: str = "",
) -> str:
    tab_html = '<span class="index-tab">格安SIM図鑑</span>' if tab else ""
    small_html = f"<small>{esc(small)}</small>" if small else ""
    number_html = f'<span class="page-no">― {number} ―</span>' if number else ""
    heading_html = "<br>".join(esc(line) for line in heading.split("\n"))
    return (
        f'<div class="page {side}">{tab_html}'
        f'<div class="page-head">{heading_html}{small_html}</div>'
        f"{body}{number_html}</div>"
    )


def book(
    slide_id: str,
    left: str,
    right: str,
    *,
    price_note: bool = False,
) -> str:
    extra = " price-note" if price_note else ""
    return (
        f"<!-- Slide ID: {esc(slide_id)} -->\n"
        f'<div class="slide-container{extra}" style="{BRAND}">'
        '<div class="book"><div class="spine"></div>'
        f"{left}{right}</div></div>"
    )


def list_rows(
    items: list[str], *, icons: list[str] | None = None, start: int = 1
) -> str:
    rows = []
    for index, item in enumerate(items):
        if icons:
            marker = (
                '<span class="ic"><i class="fa-solid '
                f'{icons[index % len(icons)]}"></i></span>'
            )
        else:
            marker = f'<span class="badge">{index + start}</span>'
        rows.append(f'<li>{marker}<div class="tx">{esc(item)}</div></li>')
    return '<ul class="rows">' + "".join(rows) + "</ul>"


def logo(src: str, alt: str) -> str:
    return f'<img class="brand-logo" src="{esc(src)}" alt="{esc(alt)}">'


def intro_slide(slide: Slide) -> str:
    sid = slide.slide_id
    if sid == "1":
        return f'''<!-- Slide ID: 1 -->
<div class="slide-container std intro-alert">
  <div class="std-rays"></div><div class="std-ribbon">2026年8月1日から</div>
  <img class="std-brand" src="{AHAMO_LOGO}" alt="ahamo">
  <div class="std-copy">
    <div class="std-kicker">月額料金はそのまま！</div>
    <h1><span>10GB</span> 増量</h1>
    <div class="std-chips"><b>申込不要</b><b>自動適用</b><b>対象者は手続きなし</b></div>
  </div>
  <img class="std-hero" src="public/images/irasutoya/bikkuri_me_tobideru_man.png" alt="速報に驚く人">
</div>'''
    if sid == "2":
        return f'''<!-- Slide ID: 2 -->
<div class="slide-container std intro-title">
  <div class="std-rays"></div><div class="std-ribbon">速報</div>
  <img class="std-brand" src="{AHAMO_LOGO}" alt="ahamo">
  <div class="std-copy">
    <div class="std-kicker">申込不要で8月から</div>
    <h1><span>30GB</span><i class="fa-solid fa-arrow-right"></i><strong>40GB</strong></h1>
    <div class="std-subtitle">月額そのままで、何が変わった？</div>
  </div>
  <img class="std-hero" src="public/images/irasutoya/present_open.png" alt="うれしい増量">
</div>'''
    return f'''<!-- Slide ID: 3 -->
<div class="slide-container std intro-welcome">
  <div class="std-rays"></div>
  <img class="std-brand" src="{AHAMO_LOGO}" alt="ahamo">
  <div class="std-copy">
    <div class="std-kicker">増量の中身と注意点をまるっと解説</div>
    <h1>格安SIM図鑑の<br><span>世界へようこそ！</span></h1>
    <div class="std-chips"><b>料金</b><b>容量</b><b>選び方</b></div>
  </div>
  <img class="std-hero" src="public/images/irasutoya/smartphone04_laugh.png" alt="スマートフォンを使う人">
</div>'''


def agenda_slide(slide: Slide) -> str:
    ps = parts(slide.content)
    chapters = [re.sub(r"^第\d章\s*", "", item) for item in ps if item.startswith("第")]
    joined = " ".join(ps)
    benefits = [x.strip() for x in re.findall(r"[①②]([^①②]+)", joined)][-2:]
    agenda = "".join(
        f'<li><span class="num">{index}</span>{esc(text)}</li>'
        for index, text in enumerate(chapters, 1)
    )
    benefit_html = "".join(
        f'<li><span class="check">✓</span>{esc(text)}</li>' for text in benefits
    )
    left = page("left", "格安SIM図鑑 もくじ", f'<ol class="agenda">{agenda}</ol>', None)
    right_body = (
        f'<ul class="benefits">{benefit_html}</ul>'
        '<div class="emph agenda-answer"><span class="em">結論</span><br>'
        '今の利用者は何もしなくてOK！</div>'
    )
    right = page("right", "この動画でわかること", right_body, None, tab=True)
    return book(slide.slide_id, left, right)


def chapter_slide(slide: Slide) -> str:
    number, title, subtitle = CHAPTERS[slide.slide_id]
    title_html = "<br>".join(esc(line) for line in title.split("\n"))
    left = (
        '<div class="page left"><div class="divider">'
        f'<div class="kicker">CHAPTER</div><div class="num">{number}</div>'
        f'<div class="seal">FILE No.{int(number):02d}</div></div></div>'
    )
    right = (
        '<div class="page right"><span class="index-tab">格安SIM図鑑</span>'
        '<div class="page-body center">'
        f'<div class="big-title chapter-title">{title_html}</div>'
        f'<div class="lead chapter-lead">{esc(subtitle)}</div></div></div>'
    )
    return book(slide.slide_id, left, right)


def before_after(slide: Slide, numbers: tuple[int, int]) -> str:
    ps = parts(slide.content)
    before = next(item for item in ps if item.startswith("Before"))
    after = next(item for item in ps if item.startswith("After"))
    b_size = re.search(r"Before：([^・]+)", before).group(1)
    a_size = re.search(r"After：([^・]+)", after).group(1)
    price = re.search(r"月額([0-9,]+円)", after).group(1)
    title = ps[0]
    left_body = (
        '<div class="page-body center"><div class="state-label before">BEFORE</div>'
        f'<div class="emph capacity old"><span class="big">{esc(b_size)}</span></div>'
        f'<div class="price-lock">月額 {esc(price)}</div></div>'
    )
    right_body = (
        '<div class="page-body center"><div class="state-label after">AFTER</div>'
        f'<div class="emph capacity"><span class="big">{esc(a_size)}</span><br><b>＋10GB</b></div>'
        f'<div class="price-lock">月額 {esc(price)} <strong>据え置き</strong></div></div>'
    )
    left = page("left", title, left_body, numbers[0])
    right = page("right", "8月1日から自動適用", right_body, numbers[1], tab=True)
    return book(slide.slide_id, left, right, price_note=True)


def docomo_mini(slide: Slide, numbers: tuple[int, int]) -> str:
    left_body = '''<div class="page-body center">
      <table class="sheet mini-plan"><thead><tr><th>プラン</th><th>増量前</th><th>増量後</th><th>月額</th></tr></thead>
      <tbody><tr><td>4GBプラン</td><td>4GB</td><td class="em">6GB</td><td class="price">2,750円</td></tr>
      <tr><td>10GBプラン</td><td>10GB</td><td class="em">12GB</td><td class="price">3,850円</td></tr></tbody></table>
      <div class="lead compact-lead">どちらも月額料金は据え置き</div></div>'''
    right_body = f'''<div class="page-body center">
      {logo(DOCOMO_LOGO, "ドコモ")}
      <div class="emph"><span class="big">4つ</span>のプランが対象<br><span class="detail">ahamo・大盛り・mini 2種</span></div>
      <div class="subscribe-box"><i class="fa-solid fa-bell"></i><b>速報を見逃さない！</b><span>チャンネル登録をお願いします</span></div>
    </div>'''
    left = page("left", "ドコモminiも容量アップ", left_body, numbers[0])
    right = page("right", "今回の対象", right_body, numbers[1], tab=True)
    return book(slide.slide_id, left, right, price_note=True)


def purpose_slide(slide: Slide, numbers: tuple[int, int]) -> str:
    ps = parts(slide.content)
    first = re.sub(r"^①", "", ps[1])
    second = re.sub(r"^②", "", ps[2])
    left_body = (
        '<div class="page-body center purpose-body"><div class="bigicon purpose-icon">'
        '<i class="fa-solid fa-gauge-high"></i></div>'
        f'<div class="lead">{esc(first)}</div></div>'
    )
    right_body = (
        '<div class="page-body center purpose-body"><div class="bigicon purpose-icon">'
        '<i class="fa-solid fa-chart-line"></i></div>'
        f'<div class="lead">{esc(second)}</div></div>'
    )
    left = page("left", ps[0], left_body, numbers[0], small="目的①")
    right = page("right", "体感変化を把握", right_body, numbers[1], tab=True, small="目的②")
    return book(slide.slide_id, left, right)


def competition_slide(slide: Slide, numbers: tuple[int, int]) -> str:
    rows = []
    for item in parts(slide.content)[1:]:
        name, values = item.split("：", 1)
        pieces = values.split("・")
        rows.append((name, pieces[0], pieces[1] if len(pieces) > 1 else ""))
    table_rows = "".join(
        f'<tr><td>{esc(name)}</td><td>{esc(capacity)}</td><td>{esc(price)}</td></tr>'
        for name, capacity, price in rows
    )
    left_body = (
        '<div class="page-body center"><div class="warn inference"><span class="ic">'
        '<i class="fa-solid fa-user-pen"></i></span><b>ここからはショウの推測</b><br>'
        '他社との価格競争も背景にあるのでは？</div>'
        '<div class="lead competition-lead">30GBのままでは、近い価格帯で見劣りしていた</div>'
        '<div class="bigicon competition-icon"><i class="fa-solid fa-scale-balanced"></i></div></div>'
    )
    right_body = (
        '<div class="page-body center"><table class="sheet competition-table">'
        '<thead><tr><th>サービス</th><th>容量</th><th>月額</th></tr></thead>'
        f'<tbody>{table_rows}</tbody></table></div>'
    )
    left = page("left", "背景にある価格競争", left_body, numbers[0])
    right = page("right", "近い価格帯の容量", right_body, numbers[1], tab=True)
    return book(slide.slide_id, left, right, price_note=True)


def caution_slide(slide: Slide, numbers: tuple[int, int]) -> str:
    ps = parts(slide.content)
    left_body = (
        '<div class="page-body center"><div class="campaign-name">正式名称</div>'
        f'<div class="lead campaign-title">{esc(ps[1])}</div>'
        '<div class="warn end-date"><span class="ic"><i class="fa-solid fa-calendar-xmark"></i></span>'
        '<span>終了時期は<strong>未発表</strong></span></div></div>'
    )
    future_items = [re.sub(r"^[①②]", "", ps[3]), re.sub(r"^[①②]", "", ps[4])]
    right_body = (
        '<div class="page-body center">'
        + list_rows(future_items, icons=["fa-rotate-left", "fa-arrow-trend-up"])
        + '<div class="emph both-possible">どちらも<span class="em">あり得る</span></div></div>'
    )
    left = page("left", ps[0], left_body, numbers[0])
    right = page("right", "今後の2つの可能性", right_body, numbers[1], tab=True)
    return book(slide.slide_id, left, right)


def mindset_slide(slide: Slide, numbers: tuple[int, int]) -> str:
    ps = parts(slide.content)
    left_body = (
        '<div class="page-body center"><div class="bigicon calendar-icon">'
        '<i class="fa-solid fa-calendar-check"></i></div>'
        '<div class="big-title mindset-title">自動適用でも<br>完全放置はしない</div></div>'
    )
    right_body = (
        '<div class="page-body center"><div class="emph habit"><span class="big">ときどき</span><br>'
        '公式サイトで最新容量を確認</div>'
        '<div class="lead compact-lead">「いつの間にか終了」を防ぐ習慣に</div></div>'
    )
    left = page("left", ps[0], left_body, numbers[0])
    right = page("right", "おすすめの確認習慣", right_body, numbers[1], tab=True)
    return book(slide.slide_id, left, right)


def evaluation_excerpt(slide: Slide, numbers: tuple[int, int]) -> str:
    ps = parts(slide.content)
    scores = [tuple(item.split("：", 1)) for item in ps[1:]]
    cards = "".join(
        '<div class="score-card">'
        f'<div class="rank {esc(rank)}">{esc(rank)}</div><div class="score-name">{esc(name)}</div>'
        '</div>' for name, rank in scores
    )
    left_body = f'''<div class="page-body center">
      {logo(AHAMO_LOGO, "ahamo")}
      <div class="score-stack">{cards}</div>
    </div>'''
    right_body = '''<div class="page-body center">
      <div class="bigicon balance-icon"><i class="fa-solid fa-scale-balanced"></i></div>
      <div class="emph"><span class="big">バランス型</span><br>料金・品質・始めやすさに強み</div>
      <div class="note eval-note">※本評価は当チャンネルの独断と偏見による独自評価であり、キャンペーン割引等は考慮していません</div>
    </div>'''
    left = page("left", "ahamoの独自評価", left_body, numbers[0], small="一部抜粋")
    right = page("right", "ahamoの位置づけ", right_body, numbers[1], tab=True)
    return book(slide.slide_id, left, right)


def linemo_compare(slide: Slide, numbers: tuple[int, int]) -> str:
    left_body = f'''<div class="page-body center">
      {logo(AHAMO_LOGO, "ahamo")}
      <div class="emph compare-cap"><span class="big">40GB</span><br>月額2,970円</div>
    </div>'''
    right_body = f'''<div class="page-body center">
      {logo(LINEMO_LOGO, "LINEMO")}
      <div class="emph compare-cap"><span class="big">30GB</span><br>月額2,970円</div>
      <div class="lead compact-lead"><span class="em">同額で10GB差</span></div>
    </div>'''
    left = page("left", "料金2,970円クラス", left_body, numbers[0])
    # Keep the plan name intact: the page heading's automatic wrap otherwise
    # leaves the final two characters ("ンV") orphaned on a third line.
    right = page("right", "LINEMO\nベストプランV", right_body, numbers[1], tab=True)
    return book(slide.slide_id, left, right, price_note=True)


def quality_position(slide: Slide, numbers: tuple[int, int]) -> str:
    services = [("povo2.0", "SS"), ("LINEMO", "SS"), ("ahamo", "S"), ("楽天モバイル", "A")]
    left_cards = "".join(
        f'<div class="quality-card"><div class="rank {rank}">{rank}</div><b>{esc(name)}</b></div>'
        for name, rank in services
    )
    left_body = f'<div class="page-body center"><div class="quality-stack">{left_cards}</div></div>'
    right_body = '''<div class="page-body center">
      <div class="emph position-text">povo2.0・LINEMOより下<br><span class="big">ahamo：S</span><br>楽天モバイルより上</div>
      <div class="warn"><span class="ic"><i class="fa-solid fa-location-dot"></i></span>エリアによって体感は異なります</div>
    </div>'''
    left = page("left", "通信品質の独自評価", left_body, numbers[0])
    right = page("right", "ahamoの位置づけ", right_body, numbers[1], tab=True)
    return book(slide.slide_id, left, right)


def video_cta(slide: Slide, thumb: str, title: str) -> str:
    left = (
        '<div class="page left"><div class="visual cta-visual">'
        f'<img src="{esc(thumb)}" alt="過去動画のサムネイル"></div></div>'
    )
    right = (
        '<div class="page right"><span class="index-tab">格安SIM図鑑</span>'
        '<div class="page-body center"><div class="bigicon cta-play">'
        '<i class="fa-solid fa-circle-play"></i></div>'
        f'<div class="big-title cta-title">{title}</div>'
        '<div class="lead cta-lead">概要欄・関連動画からチェック！</div></div></div>'
    )
    return book(slide.slide_id, left, right)


def quality_outlook(slide: Slide, numbers: tuple[int, int]) -> str:
    left_body = '''<div class="page-body center flow-body">
      <div class="flow-step"><i class="fa-solid fa-database"></i><b>使える容量が増える</b></div>
      <i class="fa-solid fa-arrow-down flow-arrow"></i>
      <div class="flow-step"><i class="fa-solid fa-users"></i><b>全体の通信量も増える</b></div>
    </div>'''
    right_body = '''<div class="page-body center">
      <div class="bigicon lookout-icon"><i class="fa-solid fa-binoculars"></i></div>
      <div class="warn outlook-warn"><span class="ic"><i class="fa-solid fa-triangle-exclamation"></i></span>
      通信品質への影響は<br><strong>今後の様子を見る必要あり</strong></div>
    </div>'''
    left = page("left", "増量で起こり得ること", left_body, numbers[0])
    right = page("right", "通信品質は大丈夫？", right_body, numbers[1], tab=True)
    return book(slide.slide_id, left, right)


def unlimited_compare(slide: Slide, numbers: tuple[int, int]) -> str:
    left_body = f'''<div class="page-body center">
      {logo(RAKUTEN_LOGO, "楽天モバイル")}
      <div class="emph compare-cap"><span class="big">無制限</span><br>月額3,278円</div>
    </div>'''
    right_body = f'''<div class="page-body center">
      {logo(AHAMO_LOGO, "ahamo")}
      <div class="emph compare-cap"><span class="big">120GB</span><br>月額4,950円</div>
      <div class="warn price-gap"><span class="ic"><i class="fa-solid fa-coins"></i></span>差額 <strong>1,672円</strong></div>
    </div>'''
    left = page("left", "楽天モバイル", left_body, numbers[0])
    right = page("right", "ahamo大盛り", right_body, numbers[1], tab=True)
    return book(slide.slide_id, left, right, price_note=True)


def decision_slide(slide: Slide, numbers: tuple[int, int]) -> str:
    left_body = '''<div class="page-body center">
      <div class="warn opinion"><span class="ic"><i class="fa-solid fa-user-pen"></i></span><b>ショウの見解</b></div>
      <div class="emph ten-gb"><span class="big">110→120GB</span><br>10GB差で足りる人は限定的</div>
      <div class="lead compact-lead">毎月100GB以上なら無制限も比較</div>
    </div>'''
    right_body = f'''<div class="page-body decision-body">
      <div class="decision-row"><b>容量に余裕</b><span>ahamo 40GB</span></div>
      <div class="decision-row"><b>通信品質優先</b><span>povo2.0・LINEMO</span></div>
      <div class="decision-row"><b>データ無制限</b><span>楽天モバイル</span></div>
      <div class="mini-cta"><img src="{AHAMO_THUMB}" alt="ahamoで得する人・損する人"><b>自分に合うタイプは過去動画で！</b></div>
    </div>'''
    left = page("left", "大盛り増量の恩恵", left_body, numbers[0])
    right = page("right", "選び方の軸", right_body, numbers[1], tab=True)
    return book(slide.slide_id, left, right)


def summary_slide(slide: Slide, numbers: tuple[int, int]) -> str:
    ps = parts(slide.content)
    items = [re.sub(r"^[①②③④]", "", item) for item in ps[1:]]
    left_body = '<div class="page-body">' + list_rows(items[:2]) + '</div>'
    right_body = '<div class="page-body">' + list_rows(items[2:], start=3) + '</div>'
    left = page("left", ps[0], left_body, numbers[0], small="①②")
    right = page("right", "今日のまとめ", right_body, numbers[1], tab=True, small="③④")
    return book(slide.slide_id, left, right)


def official_cta(slide: Slide) -> str:
    left = f'''<div class="page left"><div class="page-body center">
      {logo(AHAMO_LOGO, "ahamo")}
      <div class="bigicon link-icon"><i class="fa-solid fa-arrow-pointer"></i></div>
      <div class="lead official-lead">気になったら<br>公式サイトへ</div>
    </div></div>'''
    right = '''<div class="page right"><span class="index-tab">格安SIM図鑑</span>
      <div class="page-body center"><div class="big-title cta-title">ahamoの<br>申し込みはこちら！</div>
      <div class="lead cta-lead">概要欄リンクから<br>最新プランを確認</div></div></div>'''
    return book(slide.slide_id, left, right)


def comments_cta(slide: Slide) -> str:
    examples = re.findall(r"「([^」]+)」", slide.content)
    left = '''<div class="page left"><div class="page-body center">
      <div class="bigicon comment-icon"><i class="fa-solid fa-comments"></i></div>
      <div class="big-title cta-title">コメントで<br>教えてね！</div></div></div>'''
    right_body = '<div class="page-body">' + list_rows(examples, icons=["fa-comment-dots"]) + '</div>'
    right = page("right", "コメント例", right_body, None, tab=True)
    return book(slide.slide_id, left, right)


def information_caution(slide: Slide) -> str:
    left = '''<div class="page left"><div class="page-body center">
      <div class="bigicon info-icon"><i class="fa-solid fa-circle-info"></i></div>
      <div class="big-title">ご注意</div></div></div>'''
    right = '''<div class="page right"><span class="index-tab">格安SIM図鑑</span>
      <div class="page-body center"><div class="warn posting-note"><span class="ic"><i class="fa-solid fa-triangle-exclamation"></i></span>
      料金・データ容量は<br><strong>動画投稿時点</strong>の情報です</div>
      <div class="lead cta-lead">お申し込み前に<br><span class="em">公式サイトの最新情報</span>を確認</div></div></div>'''
    return book(slide.slide_id, left, right)


def blog_cta(slide: Slide) -> str:
    left = '''<div class="page left"><div class="page-body center">
      <div class="bigicon pen-icon"><i class="fa-solid fa-pen-nib"></i></div>
      <div class="big-title blog-title">ブログ・noteも<br>更新中！</div></div></div>'''
    right = '''<div class="page right"><span class="index-tab">格安SIM図鑑</span>
      <div class="page-body center blog-body">
      <img class="blog-image" src="public/images/common/ブログ_ヘッダー画像_スライド用.png" alt="ブログ">
      <div class="lead cta-lead">詳しい格安SIM記事は<br>概要欄リンクからぜひ！</div>
      <div class="note blog-note">動画とあわせて、じっくり読めます</div></div></div>'''
    return book(slide.slide_id, left, right)


def final_cta(slide: Slide) -> str:
    left = '''<div class="page left"><div class="page-body center">
      <div class="bigicon bell-icon"><i class="fa-solid fa-bell"></i></div>
      <div class="big-title final-title">チャンネル登録<br>よろしくお願いします！</div></div></div>'''
    right = '''<div class="page right"><span class="index-tab">格安SIM図鑑</span>
      <div class="page-body center"><div class="emoji-cta"><span>👍</span><span>🔔</span></div>
      <div class="lead thanks">ご視聴いただき<br>ありがとうございました！</div>
      <div class="note final-note">次回も一緒にスマホ代を節約しましょう</div></div></div>'''
    return book(slide.slide_id, left, right)


def stylesheet() -> str:
    return '''
  <style>
    body { --primary-color:#C8102E;--accent-red:#E53935;--text-dark:#212121; }
    .index-tab { transform:translateZ(0);will-change:transform; }
    .slide-container.std {
      width:1280px;height:720px;border:10px solid var(--primary-color);background:#fff9f4;
      box-sizing:border-box;position:relative;overflow:hidden;display:flex;flex-direction:column;
      justify-content:center;align-items:center;padding:38px;flex-shrink:0;color:var(--text-dark);
    }
    .std-rays { position:absolute;inset:0;background:repeating-conic-gradient(from -12deg at 50% 47%,rgba(200,16,46,.09) 0 5deg,transparent 5deg 10deg); }
    .std-ribbon { position:absolute;z-index:3;left:24px;top:30px;background:#C8102E;color:#fff;font-size:44px;font-weight:900;padding:10px 42px;transform:rotate(-3deg);box-shadow:0 9px 18px #0004; }
    .std-brand { position:absolute;z-index:2;top:36px;right:48px;width:265px;height:82px;object-fit:contain;background:#fff;padding:12px 22px;border-radius:18px;box-shadow:0 9px 22px #0002; }
    .std-copy { position:relative;z-index:2;width:100%;text-align:center;display:flex;flex-direction:column;align-items:center; }
    .std-kicker { font-size:50px;font-weight:900;margin-bottom:8px;text-shadow:3px 3px #fff; }
    .std-copy h1 { font-size:106px;line-height:1.08;font-weight:900;letter-spacing:-3px;text-shadow:5px 5px #fff;margin:8px 0 22px; }
    .std-copy h1 span,.std-copy h1 strong { color:#E53935;font-size:132px;font-style:normal;white-space:nowrap; }
    .std-copy h1 i { font-size:78px;color:#555;margin:0 24px;vertical-align:15px; }
    .std-subtitle { font-size:46px;font-weight:900;background:#fff;border:5px solid #C8102E;border-radius:18px;padding:12px 30px;box-shadow:0 9px 20px #0002; }
    .std-chips { display:flex;justify-content:center;gap:20px;flex-wrap:wrap; }
    .std-chips b { font-size:44px;background:#fff;border:5px solid #C8102E;border-radius:999px;padding:8px 24px;box-shadow:0 8px 16px #0002; }
    .std-hero { position:absolute;z-index:0;right:12px;bottom:0;width:285px;height:300px;object-fit:contain;filter:drop-shadow(0 14px 15px #0003);opacity:.92; }
    .intro-alert .std-copy h1 span { font-size:170px }.intro-alert .std-copy{margin-top:45px}.intro-alert .std-kicker{font-size:62px}
    .intro-title .std-copy{margin-top:58px}.intro-title .std-copy h1{font-size:94px}.intro-title .std-hero{width:250px;height:260px}
    .intro-welcome .std-brand{left:48px;right:auto}.intro-welcome .std-kicker{font-size:48px}.intro-welcome .std-copy h1{font-size:88px}.intro-welcome .std-copy h1 span{font-size:98px}
    .chapter-title { font-size:82px }.chapter-lead{margin-top:28px;text-align:center}
    .agenda li { font-size:44px;gap:20px }.agenda .num{width:72px;height:72px;font-size:42px}.benefits li{font-size:45px}.benefits .check{font-size:54px}.agenda-answer{font-size:44px;padding:24px}
    .state-label{font-size:42px;font-weight:900;letter-spacing:5px;padding:8px 28px;border-radius:999px}.state-label.before{background:#777;color:#fff}.state-label.after{background:var(--brand);color:#fff}
    .capacity{width:100%;padding:26px}.capacity.old{border-color:#999;background:#eee}.capacity.old .big{color:#666;text-decoration:line-through}.capacity b{font-size:46px;color:var(--con)}
    .price-lock{font-size:48px;font-weight:900}.price-lock strong{color:var(--con)}
    .brand-logo{max-width:500px;width:auto;height:94px;object-fit:contain}.compact-lead{font-size:44px;padding:24px;text-align:center}
    .mini-plan th,.mini-plan td{padding:13px 8px}.mini-plan td:first-child,.mini-plan .price{white-space:nowrap}.mini-plan .price{font-weight:900}.subscribe-box{width:100%;background:#fff;border:5px solid var(--brand);border-radius:22px;padding:22px;text-align:center;display:grid;grid-template-columns:95px 1fr;align-items:center;box-shadow:0 8px 18px #0002}.subscribe-box i{grid-row:1/3;font-size:76px;color:var(--brand)}.subscribe-box b{font-size:43px}.subscribe-box span{font-size:32px;font-weight:800}
    .purpose-body{gap:16px}.purpose-icon{font-size:170px}.purpose-body .lead{font-size:42px;padding:25px}
    .inference{font-size:42px}.competition-lead{font-size:39px;padding:21px;text-align:center}.competition-icon{font-size:145px}.competition-table{font-size:34px}.competition-table th,.competition-table td{padding:13px 10px}.competition-table td:first-child{font-size:30px}
    .campaign-name{font-size:40px;font-weight:900;color:var(--ink-soft)}.campaign-title{text-align:center}.end-date{font-size:44px;display:flex;align-items:center;justify-content:center}.end-date strong{font-size:62px;color:var(--con)}.both-possible{font-size:46px;padding:24px}
    .calendar-icon{font-size:195px}.mindset-title{font-size:72px}.habit{width:100%}.habit .big{font-size:100px}
    .score-stack{width:100%;display:flex;flex-direction:column;gap:18px}.score-card{display:flex;align-items:center;gap:28px;background:#fff;border:4px solid #e7dcc2;border-left:14px solid var(--brand);border-radius:18px;padding:16px 26px}.score-card .rank{width:90px;height:90px;border-radius:18px;font-size:46px;flex:none}.score-name{font-size:48px;font-weight:900}.balance-icon{font-size:155px}.eval-note{font-size:28px;text-align:center}.compare-cap{width:100%;padding:26px}.price-gap{font-size:42px;width:100%;text-align:center}
    .quality-stack{width:100%;display:grid;grid-template-columns:1fr 1fr;gap:20px}.quality-card{background:#fff;border:4px solid #e7dcc2;border-radius:20px;padding:22px;display:flex;align-items:center;gap:20px}.quality-card .rank{width:90px;height:90px;border-radius:18px;font-size:42px;flex:none}.quality-card b{font-size:38px}.position-text{font-size:42px;width:100%}.position-text .big{font-size:78px}
    .cta-visual img{width:100%;max-height:620px}.cta-play{font-size:175px}.cta-title{font-size:72px}.cta-lead{font-size:44px;text-align:center;padding:24px}
    .flow-body{gap:10px}.flow-step{width:100%;background:#fff;border:5px solid var(--brand);border-radius:22px;padding:30px;display:flex;align-items:center;justify-content:center;gap:25px}.flow-step i{font-size:68px;color:var(--brand)}.flow-step b{font-size:45px}.flow-arrow{font-size:64px;color:var(--brand)}.lookout-icon{font-size:190px}.outlook-warn{font-size:42px;text-align:center}.outlook-warn strong{color:var(--con)}
    .opinion{width:100%;font-size:43px;text-align:center}.ten-gb{font-size:40px;padding:27px}.ten-gb .big{font-size:76px}.decision-body{gap:12px}.decision-row{display:grid;grid-template-columns:230px 1fr;align-items:center;border:4px solid #e7dcc2;border-left:14px solid var(--brand);border-radius:17px;background:#fff;padding:15px 20px}.decision-row b{font-size:33px;color:var(--brand-deep)}.decision-row span{font-size:34px;font-weight:900}.mini-cta{display:grid;grid-template-columns:250px 1fr;align-items:center;gap:18px;background:var(--brand-soft);border-radius:17px;padding:12px}.mini-cta img{width:250px;height:140px;object-fit:cover;border-radius:12px}.mini-cta b{font-size:31px;text-align:center}
    .link-icon,.comment-icon,.info-icon,.pen-icon,.bell-icon{font-size:210px}.official-lead{width:100%;font-size:48px;text-align:center;padding:24px}.posting-note{font-size:46px;text-align:center}.posting-note strong{font-size:58px;color:var(--con)}
    .blog-title{font-size:82px}.blog-body{gap:14px}.blog-image{width:100%;height:auto;max-height:390px;object-fit:contain;border-radius:18px;filter:drop-shadow(0 12px 20px #0003)}.blog-note,.final-note{font-size:30px;text-align:center}.final-title{font-size:66px}.emoji-cta{display:flex;gap:70px;justify-content:center}.emoji-cta span{font-size:130px}.thanks{font-size:56px;text-align:center;color:var(--brand-deep)}
  </style>'''


def render_slide(slide: Slide, page_numbers: tuple[int, int] | None) -> str:
    sid = slide.slide_id
    if sid in {"1", "2", "3"}:
        return intro_slide(slide)
    if sid == "4":
        return agenda_slide(slide)
    if sid in CHAPTERS:
        return chapter_slide(slide)
    if sid == "24":
        return official_cta(slide)
    if sid == "25":
        return comments_cta(slide)
    if sid == "26":
        return information_caution(slide)
    if sid == "27":
        return blog_cta(slide)
    if sid == "28":
        return final_cta(slide)
    assert page_numbers is not None
    if sid in {"6", "7"}:
        return before_after(slide, page_numbers)
    if sid == "8":
        return docomo_mini(slide, page_numbers)
    if sid == "10":
        return purpose_slide(slide, page_numbers)
    if sid == "11":
        return competition_slide(slide, page_numbers)
    if sid == "13":
        return caution_slide(slide, page_numbers)
    if sid == "14":
        return mindset_slide(slide, page_numbers)
    if sid == "15":
        return evaluation_excerpt(slide, page_numbers)
    if sid == "16":
        return linemo_compare(slide, page_numbers)
    if sid == "17":
        return quality_position(slide, page_numbers)
    if sid == "18":
        return video_cta(slide, DOCOMO_THUMB, "ドコモの通信品質を<br>過去動画で詳しく解説")
    if sid == "19":
        return quality_outlook(slide, page_numbers)
    if sid == "20":
        return unlimited_compare(slide, page_numbers)
    if sid == "21":
        return decision_slide(slide, page_numbers)
    if sid == "23":
        return summary_slide(slide, page_numbers)
    raise ValueError(f"No renderer for slide {sid}")


def generate() -> tuple[int, list[str]]:
    slides = load_slides()
    rendered: list[str] = []
    page_number = 1
    special_ids = {"1", "2", "3", "4", *CHAPTERS, "24", "25", "26", "27", "28"}
    for slide in slides:
        if slide.slide_id in special_ids:
            numbers = None
        else:
            numbers = (page_number, page_number + 1)
            page_number += 2
        rendered.append(render_slide(slide, numbers))

    document = f'''<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>【2026年8月】ahamoが月額そのままで40GBに増量</title>
  <link href="https://fonts.googleapis.com/css2?family=M+PLUS+Rounded+1c:wght@400;500;700;800;900&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
  <link rel="stylesheet" href="templates/spread-base.css">
{stylesheet()}
</head>
<body>
{chr(10).join(rendered)}
</body>
</html>
'''
    OUTPUT_HTML.write_text(document, encoding="utf-8")
    return len(slides), [slide.slide_id for slide in slides]


if __name__ == "__main__":
    count, slide_ids = generate()
    print(f"Generated {count} slides: {OUTPUT_HTML}")
    print("Slide IDs:", ", ".join(slide_ids))
