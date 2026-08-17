#!/usr/bin/env python3
"""Generate the long-form deck about free options turning into paid options.

The master CSV controls slide order and visible copy.  This generator resolves
"同上", parses the slash-delimited display instructions, maps them to the
components in templates/spread-base.css, and refuses to emit a deck whose Slide
ID set differs from the scenario.  HTML must be regenerated from this file; it
is not intended to be edited by hand.
"""

from __future__ import annotations

import csv
import html
import re
from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path


ROOT = Path("/workspaces/yt-factory/packages/slide-gen")
CSV_PATH = Path(
    "/workspaces/yt-factory/packages/scenario-gen/archive/videos/"
    "42_【放置は損】その「無料オプション」終わると毎月いくら？月500円〜1,980円の自動課金/"
    "long/【放置は損】その「無料オプション」終わると毎月いくら？月500円〜1,980円の自動課金.csv"
)
OUTPUT_PATH = ROOT / "slides.html"

BRAND = "--brand:#c8102e;--brand-deep:#981027;--brand-soft:#fde3e7"
MINEO_BRAND = "--brand:#22a73f;--brand-deep:#1c8b34;--brand-soft:#e8f5e6"
BLUE_BRAND = "--brand:#1565c0;--brand-deep:#0d47a1;--brand-soft:#e3f0fb"

MINEO_LOGO = "public/images/logo/Mineo_logo.png"
JAPAN_SIM_LOGO = "public/images/logo/nihon_tsushin.jpg"
BLOG_IMAGE = "public/images/common/ブログ_ヘッダー画像_スライド用.png"
MINEO_CHART = "public/images/charts/mineo.png"
MINEO_PLAN_TABLE = "public/images/temp/mineo/mineo_マイピタ_料金表のみ.png"
MINEO_THUMBNAIL = "public/images/thumbnails/【裏技】mineo歴8年が教える「実質使い放題」の極意！契約前に知らないと損する5つの節約術_サムネ.png"
PAST_THUMBNAIL = "public/images/thumbnails/38_【2026年最新】格安SIMの無制限プラン比較！最安は月250円_サムネ1.png"
HOOK_ART = "public/images/irasutoya/seikyuusyo_shock.png"


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def strip_chapter(value: str) -> str:
    return re.sub(r"^第\d章\s*", "", value).strip()


def strip_number(value: str) -> str:
    return re.sub(r"^[①②③④⑤⑥]\s*", "", value).strip()


def strip_prefix(value: str) -> str:
    return value.removeprefix("テロップ：").removeprefix("タイトル：").strip()


@dataclass(frozen=True)
class ScenarioSlide:
    slide_id: str
    instructions: tuple[str, ...]

    def parts(self, index: int = 0) -> list[str]:
        return [part.strip() for part in self.instructions[index].split("／") if part.strip()]


def load_scenario() -> OrderedDict[str, ScenarioSlide]:
    instruction_map: OrderedDict[str, list[str]] = OrderedDict()
    last_instruction = ""
    with CSV_PATH.open(encoding="utf-8-sig", newline="") as stream:
        for row in csv.DictReader(stream):
            shown = row["スライドに表示する内容"].strip()
            if shown and shown != "同上":
                last_instruction = shown
            slide_id = row["スライドID"].strip()
            if not slide_id:
                continue
            resolved = last_instruction if shown in {"", "同上"} else shown
            bucket = instruction_map.setdefault(slide_id, [])
            if resolved and resolved not in bucket:
                bucket.append(resolved)

    scenario: OrderedDict[str, ScenarioSlide] = OrderedDict()
    for slide_id, instructions in instruction_map.items():
        if not instructions:
            raise ValueError(f"Slide ID {slide_id} has no display instruction")
        scenario[slide_id] = ScenarioSlide(slide_id, tuple(instructions))
    return scenario


def head(title: str, small: str = "") -> str:
    suffix = f"<small>{esc(small)}</small>" if small else ""
    return f'<div class="page-head">{title}{suffix}</div>'


def body(content: str, mode: str = "") -> str:
    classes = "page-body" + (f" {mode}" if mode else "")
    return f'<div class="{classes}">{content}</div>'


def rows(items: list[tuple[str, str, str]], *, icons: bool = False) -> str:
    entries: list[str] = []
    for marker, title, sub in items:
        marker_html = (
            f'<span class="ic"><i class="fa-solid {esc(marker)}"></i></span>'
            if icons
            else f'<span class="badge">{esc(marker)}</span>'
        )
        sub_html = f'<span class="sub">{esc(sub)}</span>' if sub else ""
        entries.append(f'<li>{marker_html}<div class="tx">{esc(title)}{sub_html}</div></li>')
    return f'<ul class="rows">{"".join(entries)}</ul>'


def evaluation_card(name: str, rank: str, pro: str, con: str) -> str:
    return (
        '<div class="card eval-card">'
        f'<div class="rank {esc(rank)}">{esc(rank)}</div>'
        f'<div class="card-name">{esc(name)}</div>'
        f'<div class="line pro"><span class="tag">＋</span>{esc(pro)}</div>'
        f'<div class="line con"><span class="tag">－</span>{esc(con)}</div>'
        "</div>"
    )


def parse_evaluation(instruction: str) -> tuple[str, str, list[tuple[str, str, str, str]]]:
    match = re.match(r"評価見開き／([^／]+)／総合:([A-Z]+)／(.*)", instruction)
    if not match:
        raise ValueError("Evaluation instruction has an unexpected format")
    carrier, overall, remainder = match.groups()
    pattern = re.compile(r"([^／]+):([A-Z]+)（＋(.*?)／－(.*?)）(?=／[^／]+:[A-Z]+（|$)")
    cards = [tuple(group) for group in pattern.findall(remainder)]
    if len(cards) != 6:
        raise ValueError(f"Expected six evaluation cards, found {len(cards)}")
    return carrier, overall, cards


class Deck:
    def __init__(self, scenario: OrderedDict[str, ScenarioSlide]) -> None:
        self.scenario = scenario
        self.slides: dict[str, str] = {}
        self.page_number = 1

    def add_raw(self, slide_id: str, markup: str) -> None:
        if slide_id in self.slides:
            raise ValueError(f"Duplicate Slide ID: {slide_id}")
        self.slides[slide_id] = markup

    def spread(
        self,
        slide_id: str,
        left: str,
        right: str,
        *,
        price: bool = False,
        numbered: bool = True,
        brand: str = BRAND,
        left_class: str = "",
        right_class: str = "",
    ) -> None:
        classes = "slide-container price-note" if price else "slide-container"
        if numbered:
            left_no = f'<span class="page-no">― {self.page_number} ―</span>'
            right_no = f'<span class="page-no">― {self.page_number + 1} ―</span>'
            self.page_number += 2
        else:
            left_no = right_no = ""
        left_page = "page left" + (f" {left_class}" if left_class else "")
        right_page = "page right" + (f" {right_class}" if right_class else "")
        self.add_raw(
            slide_id,
            f'''<!-- Slide ID: {slide_id} -->
<div class="{classes}" style="{brand}"><div class="book"><div class="spine"></div>
  <div class="{left_page}">{left}{left_no}</div>
  <div class="{right_page}"><span class="index-tab">格安SIM図鑑</span>{right}{right_no}</div>
</div></div>''',
        )

    def divider(self, slide_id: str, chapter: str, raw_title: str, lead: str) -> None:
        title = strip_chapter(raw_title)
        title_markup = {
            "その「無料」には終わりがある": "その「無料」には<br>終わりがある",
            "続ける？外す？の判断基準": "続ける？外す？の<br>判断基準",
        }.get(title, esc(title))
        left = body(
            '<div class="divider">'
            '<span class="kicker">CHAPTER</span>'
            f'<span class="num">{esc(chapter)}</span>'
            f'<span class="seal">FILE No.{int(chapter):02}</span>'
            "</div>",
            "center",
        )
        right = body(
            f'<div class="big-title chapter-title">{title_markup}</div>'
            f'<div class="lead chapter-lead">{esc(lead)}</div>',
            "center",
        )
        self.spread(slide_id, left, right, numbered=False)


def std_slide(
    slide_id: str,
    ribbon: str,
    kicker: str,
    title: str,
    chips: list[str],
    *,
    art: str = "",
    price: bool = False,
    kicker_break_before: str = "",
) -> str:
    chips_html = "".join(f"<b>{esc(chip)}</b>" for chip in chips)
    art_html = f'<img class="std-hero" src="{art}" alt="請求に驚く人">' if art else ""
    classes = "slide-container std price-note" if price else "slide-container std"
    if kicker_break_before and kicker_break_before in kicker:
        before, after = kicker.split(kicker_break_before, 1)
        kicker_html = f"{esc(before)}<br>{esc(kicker_break_before + after)}"
    else:
        kicker_html = esc(kicker)
    return f'''<!-- Slide ID: {slide_id} -->
<div class="{classes}"><div class="std-rays"></div><div class="std-ribbon">{esc(ribbon)}</div>
  <div class="std-stamp"><i class="fa-solid fa-receipt"></i> OPTION CHECK</div>
  <div class="std-copy"><div class="std-kicker">{kicker_html}</div><h1>{title}</h1>
    <div class="std-chips">{chips_html}</div>
  </div>{art_html}
</div>'''


def build_deck(scenario: OrderedDict[str, ScenarioSlide]) -> Deck:
    expected_ids = [
        "1", "2", "4", "5-0", "6", "7", "8", "9-0", "10", "11", "12-0",
        "13", "14", "15", "16", "16-2", "17-0", "18-0", "18", "18-5",
        "18-6", "19-0", "20", "21", "22", "23", "24", "25", "26",
    ]
    if list(scenario) != expected_ids:
        raise ValueError(f"Unexpected scenario Slide IDs: {list(scenario)}")

    deck = Deck(scenario)

    hook = strip_prefix(scenario["1"].instructions[0])
    deck.add_raw(
        "1",
        std_slide(
            "1",
            "放置は損",
            hook,
            'その無料<br><span>有料</span>になってない？',
            ["3ヶ月無料", "半年間無料", "自動課金を確認"],
            art=HOOK_ART,
            price=True,
            kicker_break_before="有料になっていませんか？",
        ),
    )

    deck.add_raw(
        "2",
        std_slide(
            "2",
            "無料期間のあとに注意",
            "使う？ 外す？ 自分で判断できる",
            '毎月<span>500円〜1,980円</span><br>そのまま自動課金',
            ["通常料金を知る", "使っているか確認", "ムダ払いを止める"],
            price=True,
        ),
    )

    agenda = scenario["4"].parts()
    chapters = [strip_chapter(item) for item in agenda[2:6]]
    benefit_text = agenda[6].replace("【この動画でわかること】", "")
    benefits = [strip_number(item) for item in re.split(r"(?=[①②])", benefit_text) if item.strip()]
    agenda_html = "".join(
        f'<li><span class="num">{index}</span>{esc(title)}</li>'
        for index, title in enumerate(chapters, 1)
    )
    benefit_html = "".join(
        f'<li><span class="check">✓</span>{esc(item)}</li>' for item in benefits
    )
    deck.spread(
        "4",
        head(esc(agenda[1])) + f'<ol class="agenda agenda-four">{agenda_html}</ol>',
        head("この動画でわかること")
        + f'<ul class="benefits benefit-two">{benefit_html}</ul>'
        + '<div class="emph agenda-answer">やることは<span class="big">2つ</span><br>通常料金を知る ＋ 利用状況を確認</div>',
        numbered=False,
    )

    deck.divider("5-0", "1", scenario["5-0"].instructions[0], "「無料だから安心」の落とし穴")

    free_flow = scenario["6"].parts()
    deck.spread(
        "6",
        head("無料オプションの入口")
        + body(
            '<div class="bigicon gift-icon"><i class="fa-solid fa-gift"></i></div>'
            f'<div class="lead centered">{esc(free_flow[1])}</div>'
            '<div class="emph">無料だから<br><span class="em">とりあえず付ける</span></div>',
            "center compact-center",
        ),
        head("無料期間が終わると")
        + body(
            '<div class="bigicon clock-icon"><i class="fa-solid fa-clock"></i></div>'
            '<div class="flow-arrow"><i class="fa-solid fa-arrow-down"></i></div>'
            f'<div class="warn flow-warn"><span class="ic"><i class="fa-solid fa-triangle-exclamation"></i></span>{esc(free_flow[3].removeprefix("→ "))}</div>',
            "center compact-center",
        ),
    )

    actual_free = scenario["7"].parts()
    deck.spread(
        "7",
        head("無料")
        + body(
            '<div class="status-pill zero"><i class="fa-solid fa-circle-check"></i> 請求</div>'
            '<div class="emph"><span class="big">0円</span></div>'
            '<div class="lead centered">請求そのものがゼロ</div>',
            "center compare-page",
        ),
        head("実質無料の落とし穴")
        + body(
            '<div class="status-pill bill"><i class="fa-solid fa-receipt"></i> 請求</div>'
            '<div class="emph">請求はいったん発生</div>'
            '<div class="warn"><span class="ic"><i class="fa-solid fa-eye-slash"></i></span>有料化しても<br>請求書の見た目は変わりにくい</div>',
            "center compare-page",
        ),
    )

    target = scenario["8"].parts()
    deck.spread(
        "8",
        head("対象になる人")
        + body(
            '<div class="bigicon target-icon"><i class="fa-solid fa-user-check"></i></div>'
            f'<div class="lead centered"><span class="em">{esc(target[1])}</span></div>',
            "center compact-center",
        ),
        head("まずマイページで確認")
        + body(
            rows([
                ("1", "付けたオプション", "契約中のサービス一覧を見る"),
                ("2", target[3].removeprefix("※"), "終了日は人によって違う"),
            ])
            + f'<div class="note centered-note">{esc(target[2])}</div>',
            "compact-rows",
        ),
    )

    deck.divider("9-0", "2", scenario["9-0"].instructions[0], "通常料金を具体例でチェック")

    call_prices = scenario["10"].parts()
    deck.spread(
        "10",
        head("通話料金", "LINEMO")
        + body(
            '<table class="sheet price-table"><thead><tr><th>オプション</th><th>月額</th></tr></thead><tbody>'
            f'<tr><td>{esc(call_prices[2].replace("LINEMO ", "").rsplit(" 月", 1)[0])}</td><td class="em">550円</td></tr>'
            f'<tr><td>{esc(call_prices[3].replace("LINEMO ", "").rsplit(" 月", 1)[0])}</td><td class="em">1,650円</td></tr>'
            '</tbody></table>'
            '<div class="lead centered">無料終了後は<br>毎月の固定費になる</div>',
            "center price-page",
        ),
        head("通話料金", "IIJmio・ahamo")
        + body(
            '<table class="sheet price-table compact-price"><thead><tr><th>会社／オプション</th><th>月額</th></tr></thead><tbody>'
            '<tr><td>IIJmio 5分＋</td><td class="em">500円</td></tr>'
            '<tr><td>IIJmio 10分＋</td><td class="em">700円</td></tr>'
            '<tr><td>IIJmio かけ放題＋</td><td class="em">1,400円</td></tr>'
            '<tr><td>ahamo かけ放題</td><td class="em">1,100円</td></tr>'
            '</tbody></table>'
            f'<div class="note source-note">{esc(call_prices[-1])}</div>',
            "center price-page",
        ),
        price=True,
    )

    data_price = scenario["11"].parts()
    deck.spread(
        "11",
        head("データ増量系", "ahamo")
        + body(
            '<div class="equation">'
            '<div><b>30GB</b><span>月額2,970円</span></div><i class="fa-solid fa-plus"></i>'
            '<div class="hot"><b>大盛り</b><span>月額1,980円</span></div></div>'
            '<div class="flow-arrow"><i class="fa-solid fa-arrow-down"></i></div>'
            '<div class="emph result-box"><span class="big">110GB</span><br>月額4,950円</div>',
            "center data-page",
        ),
        head("使い切れないなら<br>見直し")
        + body(
            '<div class="bigicon data-icon"><i class="fa-solid fa-chart-column"></i></div>'
            '<div class="lead centered">毎月110GBを使うなら価値あり</div>'
            '<div class="warn centered"><span class="ic"><i class="fa-solid fa-triangle-exclamation"></i></span>使わなければ<span class="em">毎月1,980円</span>がムダに</div>'
            f'<div class="note source-note">{esc(data_price[-1])}</div>',
            "center data-page",
        ),
        price=True,
    )

    deck.divider("12-0", "3", scenario["12-0"].instructions[0], "高い・安いではなく、使っているか")

    failure = scenario["13"].parts()
    deck.spread(
        "13",
        head("実はショウも失敗")
        + body(
            '<div class="story-step"><span>1</span><b>かけ放題が6ヶ月無料</b></div>'
            '<div class="flow-arrow"><i class="fa-solid fa-arrow-down"></i></div>'
            '<div class="story-step warn-step"><span>2</span><b>解約を忘れて2ヶ月課金</b></div>',
            "center story-page",
        ),
        head("使わないなら価値なし")
        + body(
            '<div class="bigicon phone-icon"><i class="fa-solid fa-phone-slash"></i></div>'
            f'<div class="lead centered">{esc(failure[3].removeprefix("→ "))}</div>'
            '<div class="emph">詳しい人でも忘れる<br><span class="em">請求額は一度確認</span></div>',
            "center story-page",
        ),
    )

    decision = scenario["14"].parts()
    deck.spread(
        "14",
        head("判断は1つだけ")
        + body(
            '<div class="emph decision-main">そのオプションを<br><span class="big">実際に使っている？</span></div>'
            + rows([
                ("✓", "使っている → 続ける", "払う価値がある"),
                ("×", "付けただけ → 外す", "見直し候補"),
            ]),
            "decision-page",
        ),
        head("先月の利用実績を見る")
        + body(
            rows([
                ("fa-phone", "かけ放題", decision[3].replace("かけ放題の目安：", "")),
                ("fa-database", "データ増量", decision[4].replace("データ増量の目安：", "")),
            ], icons=True)
            + '<div class="lead centered">高いか安いかではなく<br><span class="em">使っているか</span>で決める</div>',
            "decision-page",
        ),
    )

    calendar = scenario["15"].parts()
    deck.spread(
        "15",
        head("解約し忘れ防止")
        + body(
            '<div class="bigicon calendar-icon"><i class="fa-solid fa-calendar-check"></i></div>'
            '<div class="emph"><span class="big">申し込んだ日</span><br>すぐカレンダーへ登録</div>',
            "center habit-page",
        ),
        head("予定名はこれだけ")
        + body(
            '<div class="calendar-card"><span>予定</span><b>オプションを解約する</b></div>'
            f'<div class="lead centered">{esc(calendar[2].removeprefix("※"))}</div>'
            f'<div class="note centered-note">{esc(calendar[3])}</div>',
            "center habit-page",
        ),
    )

    saving = scenario["16"].parts()
    deck.spread(
        "16",
        head("節約はスタート")
        + body(
            '<div class="money-flow"><div><i class="fa-solid fa-mobile-screen-button"></i><b>固定費を下げる</b></div>'
            '<i class="fa-solid fa-arrow-right"></i><div><i class="fa-solid fa-piggy-bank"></i><b>貯蓄・新NISA</b></div></div>'
            '<div class="lead centered">浮いたお金を<br>自分と家族のために使う</div>',
            "center saving-page",
        ),
        head("使わないオプションは逆効果")
        + body(
            '<div class="bigicon leak-icon"><i class="fa-solid fa-wallet"></i></div>'
            f'<div class="warn centered"><span class="ic"><i class="fa-solid fa-triangle-exclamation"></i></span>{esc(saving[2])}</div>'
            '<div class="emph">毎月の固定費を<br><span class="em">もう一度チェック</span></div>',
            "center saving-page",
        ),
    )

    deck.spread(
        "16-2",
        body(
            '<div class="bigicon bell-icon"><i class="fa-solid fa-bell"></i></div>'
            '<div class="big-title subscribe-title">値上げ・改悪の<br>速報を見逃さない</div>',
            "center",
        ),
        head("毎週わかりやすく解説")
        + body(
            '<div class="lead centered">スマホ代を節約する<br>細かいコツもお届け</div>'
            '<div class="youtube-pill"><i class="fa-brands fa-youtube"></i> チャンネル登録</div>',
            "center",
        ),
        numbered=False,
    )

    deck.divider("17-0", "4", scenario["17-0"].instructions[0], "無料期間を気にしない選び方")

    carrier, overall, cards = parse_evaluation(scenario["18-0"].instructions[0])
    deck.spread(
        "18-0",
        '<div class="head-left intro-logo"><img class="logo" src="' + MINEO_LOGO + f'" alt="{esc(carrier)}"></div>'
        + body(
            f'<div class="visual mineo-chart"><img class="radar-chart-image" src="{MINEO_CHART}" alt="mineo 総合評価レーダーチャート"></div>',
            "center",
        ),
        head("mineoの料金プラン")
        + body(
            f'<div class="visual mineo-plan-table"><img src="{MINEO_PLAN_TABLE}" alt="mineo マイピタ料金表"></div>'
            '<div class="lead centered">15GB以上なら<br><span class="em">3Mbps使い放題がずっと無料</span></div>',
            "center mineo-plan-page",
        ),
        price=True,
        brand=MINEO_BRAND,
    )

    deck.spread(
        "18",
        '<div class="head-left eval-head">'
        f'<img class="logo" src="{MINEO_LOGO}" alt="{esc(carrier)}">'
        f'<div class="total"><div class="label">総合評価</div><div class="grade">{esc(overall)}</div></div></div>'
        f'<div class="cards three-cards">{evaluation_card(*cards[0])}{evaluation_card(*cards[1])}{evaluation_card(*cards[2])}</div>',
        f'<div class="cards three-cards">{evaluation_card(*cards[3])}{evaluation_card(*cards[4])}{evaluation_card(*cards[5])}</div>'
        '<div class="note eval-note">※本評価は当チャンネルの独断と偏見による独自評価であり、キャンペーン割引等は考慮していません</div>',
        price=True,
        brand=MINEO_BRAND,
        left_class="eval-page",
        right_class="eval-page",
    )

    deck.spread(
        "18-5",
        f'<div class="visual cta-visual"><img src="{MINEO_THUMBNAIL}" alt="mineoの過去動画サムネイル"></div>',
        body(
            '<div class="bigicon cta-play"><i class="fa-solid fa-circle-play"></i></div>'
            '<div class="big-title cta-title">mineoを<br>もっと詳しく</div>'
            '<div class="lead centered">特徴・使い心地は<br>過去動画もチェック！</div>',
            "center",
        ),
        brand=MINEO_BRAND,
        numbered=False,
    )

    japan = scenario["18-6"].parts()
    deck.spread(
        "18-6",
        '<div class="head-left japan-logo"><img class="logo" src="' + JAPAN_SIM_LOGO + '" alt="日本通信SIM"></div>'
        + body(
            '<div class="emph"><span class="big">通話込み</span><br>5分かけ放題 または 70分無料通話</div>'
            '<div class="lead centered">プラン料金にずっと含まれる</div>',
            "center japan-page",
        ),
        head("対象の2プラン")
        + body(
            '<table class="sheet japan-table"><thead><tr><th>プラン</th><th>容量</th><th>月額</th></tr></thead><tbody>'
            '<tr><td>合理的<br>みんなのプラン</td><td>20GB</td><td class="em">1,390円</td></tr>'
            '<tr><td>合理的<br>50GBプラン</td><td>50GB</td><td class="em">2,178円</td></tr>'
            '</tbody></table>'
            '<div class="note centered-note">単体なら月390円｜無料期間ではなく、ずっと込み</div>',
            "center japan-page",
        ),
        price=True,
        brand=BLUE_BRAND,
    )

    summary_title = scenario["19-0"].instructions[-1]
    deck.divider("19-0", "5", summary_title, "今日からできる4つをおさらい")

    summary = scenario["20"].parts()
    deck.spread(
        "20",
        head("今日のまとめ", "①②")
        + body(
            rows([
                ("1", strip_number(summary[1]), "終了後は通常料金が毎月かかる"),
                ("2", strip_number(summary[2]), "通話系500〜1,650円／データ増量1,980円も"),
            ]),
            "summary-page",
        ),
        head("今日のまとめ", "③④")
        + body(
            rows([
                ("3", strip_number(summary[3]), "実際に使っているかで決める"),
                ("4", strip_number(summary[4]), "無料終了前に見直す予定を入れる"),
            ])
            + '<div class="lead centered">まずはマイページで<br><span class="em">契約中オプションを確認</span></div>',
            "summary-page",
        ),
        price=True,
    )

    companies = scenario["21"].parts()
    deck.spread(
        "21",
        head("今回の具体例について")
        + body(
            '<div class="logos text-logos"><span>LINEMO</span><span>IIJmio</span><span>ahamo</span></div>'
            '<div class="warn centered"><span class="ic"><i class="fa-solid fa-circle-info"></i></span>オプションが「悪い」という話ではありません</div>',
            "center company-note",
        ),
        head("実際に使って良かった<br>オプション")
        + body(
            '<div class="logos brand-logos"><img src="' + MINEO_LOGO + '" alt="mineo"><img src="' + JAPAN_SIM_LOGO + '" alt="日本通信SIM"></div>'
            '<div class="lead centered">ショウが実際に使い<br>良いと感じたオプション</div>'
            '<div class="note centered-note">自分の使い方に合うかで判断してください</div>',
            "center company-note",
        ),
    )

    deck.spread(
        "22",
        f'<div class="visual cta-visual"><img src="{PAST_THUMBNAIL}" alt="過去動画サムネイル"></div>',
        body(
            '<div class="bigicon cta-play"><i class="fa-solid fa-circle-play"></i></div>'
            '<div class="big-title cta-title">おすすめ格安SIMも<br>動画で解説中！</div>'
            '<div class="lead centered">ジャンル別の再生リストも<br>ご用意しています</div>',
            "center",
        ),
        numbered=False,
    )

    caution = strip_prefix(scenario["23"].instructions[0])
    deck.spread(
        "23",
        body(
            '<div class="bigicon info-icon"><i class="fa-solid fa-circle-info"></i></div>'
            '<div class="big-title caution-title">ご注意</div>',
            "center",
        ),
        head("投稿時点の情報です")
        + body(
            f'<div class="warn posting-warn"><span class="ic"><i class="fa-solid fa-triangle-exclamation"></i></span>{esc(caution)}</div>'
            '<div class="lead centered">申し込み前に<br><span class="em">各社公式サイト</span>で確認</div>',
            "center",
        ),
        numbered=False,
    )

    comments = scenario["24"].parts()
    deck.spread(
        "24",
        body(
            '<div class="bigicon comment-icon"><i class="fa-solid fa-comments"></i></div>'
            '<div class="big-title comment-title">コメントで<br>教えてね！</div>',
            "center",
        ),
        head("みんなの体験を募集中")
        + body(
            rows([
                ("fa-comment-dots", "使っていないオプションがあった", ""),
                ("fa-comment-dots", "かけ放題をずっと払ってた", ""),
                ("fa-comment-dots", "カレンダー登録やってみます", ""),
            ], icons=True),
            "comment-page",
        ),
        numbered=False,
    )

    deck.spread(
        "25",
        body(
            '<div class="bigicon pen-icon"><i class="fa-solid fa-pen-nib"></i></div>'
            '<div class="big-title blog-title">ブログ・noteでも<br>詳しく比較</div>',
            "center",
        ),
        head("概要欄リンクからぜひ")
        + body(
            f'<img class="blog-image" src="{BLOG_IMAGE}" alt="ブログ・note">'
            '<div class="lead centered">格安SIMの料金を<br>じっくり読んで比較できます</div>',
            "center blog-page",
        ),
        numbered=False,
    )

    deck.spread(
        "26",
        body(
            '<div class="bigicon final-bell"><i class="fa-solid fa-bell"></i></div>'
            '<div class="big-title final-title">チャンネル登録<br>よろしくお願いします！</div>',
            "center",
        ),
        body(
            '<div class="emoji-cta"><span>👍</span><span>🔔</span></div>'
            '<div class="lead thanks">ご視聴いただき<br>ありがとうございました！</div>'
            '<div class="note final-note">次回も一緒にスマホ代を節約しましょう</div>',
            "center",
        ),
        numbered=False,
    )

    return deck


CSS = r"""
<style>
body{--primary-color:#c8102e;--accent-red:#e53935;--text-dark:#202124}
.slide-container.std{width:1280px;height:720px;border:10px solid var(--primary-color);background:#fffaf5;box-sizing:border-box;position:relative;overflow:hidden;display:flex;align-items:center;justify-content:center;padding:42px;color:var(--text-dark)}
.std-rays{position:absolute;inset:-35%;background:repeating-conic-gradient(from -12deg at 50% 50%,rgba(200,16,46,.11) 0 6deg,transparent 6deg 13deg)}
.std-ribbon{position:absolute;z-index:4;left:22px;top:28px;background:#e53935;color:#fff;font-size:44px;font-weight:900;padding:10px 38px;transform:rotate(-3deg);box-shadow:0 9px 0 #a92222}
.std-stamp{position:absolute;z-index:3;right:34px;top:34px;font-size:44px;font-weight:900;letter-spacing:2px;color:#981027;background:#fff;border:5px solid #c8102e;border-radius:18px;padding:9px 18px;box-shadow:0 8px 18px #0002}
.std-copy{position:relative;z-index:3;width:100%;display:flex;flex-direction:column;align-items:center;text-align:center;margin-top:54px}
.std-kicker{font-size:48px;font-weight:900;margin-bottom:5px;text-shadow:3px 3px #fff;max-width:1050px;line-height:1.25}
.std-copy h1{font-size:88px;line-height:1.08;font-weight:900;letter-spacing:-3px;text-shadow:5px 5px #fff;margin:8px 0 20px}
.std-copy h1 span{color:#e53935;font-size:108px;white-space:nowrap}
.std-chips{display:flex;justify-content:center;gap:14px;flex-wrap:wrap;max-width:1000px}
.std-chips b{font-size:44px;background:#fff;border:5px solid #c8102e;border-radius:999px;padding:7px 20px;box-shadow:0 8px 16px #0002}
.std-hero{position:absolute;z-index:1;right:2px;bottom:-20px;width:260px;height:285px;object-fit:contain;filter:drop-shadow(0 14px 15px #0003)}
.agenda-four{gap:14px}.agenda-four li{font-size:46px;gap:18px}.agenda-four .num{width:72px;height:72px;font-size:40px}
.benefit-two{gap:16px}.benefit-two li{font-size:46px}.agenda-answer{padding:18px 24px;font-size:46px}.agenda-answer .big{font-size:74px}
.chapter-title{font-size:86px}.chapter-lead{font-size:48px;text-align:center;margin-top:24px}
.centered{text-align:center}.centered-note{text-align:center;font-size:30px}.compact-center{gap:14px}.compact-center .emph,.compact-center .lead,.compact-center .warn{padding:22px 28px}
.gift-icon,.clock-icon{font-size:160px}.flow-arrow{font-size:62px;color:var(--brand);text-align:center}.flow-warn{text-align:center}
.compare-page{gap:18px}.compare-page .emph,.compare-page .lead,.compare-page .warn{padding:24px 30px}.status-pill{align-self:center;border-radius:999px;padding:12px 32px;font-size:48px;font-weight:900;color:#fff}.status-pill.zero{background:#2e9e4f}.status-pill.bill{background:#e3603a}
.target-icon{font-size:175px}.compact-rows .rows{gap:10px}.compact-rows .rows li{padding:16px 22px}.compact-rows .rows .tx{font-size:44px}.compact-rows .rows .tx .sub{font-size:32px}
.price-page{gap:16px}.price-page .lead{padding:18px 24px}.price-table{font-size:38px}.price-table th,.price-table td{padding:17px 12px}.compact-price{font-size:34px}.compact-price th,.compact-price td{padding:11px 9px}.source-note{font-size:28px;text-align:center}
.data-page{gap:12px}.equation{display:flex;align-items:center;gap:18px;justify-content:center}.equation>div{background:#fff;border:5px solid var(--brand);border-radius:20px;padding:22px;text-align:center}.equation>div.hot{background:var(--brand-soft)}.equation b{display:block;font-size:52px;color:var(--brand-deep)}.equation span{display:block;font-size:34px}.equation i{font-size:55px;color:var(--brand)}.result-box{padding:20px}.result-box .big{font-size:82px}.data-icon{font-size:130px}.data-page .lead,.data-page .warn{padding:20px 26px}
.story-page{gap:14px}.story-step{width:100%;display:flex;align-items:center;gap:24px;background:#fff;border:5px solid var(--brand);border-radius:20px;padding:26px}.story-step span{width:72px;height:72px;border-radius:16px;background:var(--brand);color:#fff;font-size:46px;font-weight:900;display:flex;align-items:center;justify-content:center}.story-step b{font-size:46px}.story-step.warn-step{border-color:#f0a020;background:#fff5e6}.phone-icon{font-size:145px}.story-page .lead,.story-page .emph{padding:22px 28px}
.decision-page{gap:12px}.decision-main{padding:20px}.decision-main .big{font-size:70px}.decision-page .rows{gap:10px}.decision-page .rows li{padding:16px 22px}.decision-page .rows .tx{font-size:42px}.decision-page .rows .tx .sub{font-size:30px}.decision-page .lead{padding:20px 24px}
.habit-page{gap:16px}.calendar-icon{font-size:160px}.habit-page .emph,.habit-page .lead{padding:22px 28px}.calendar-card{background:#fff;border:6px solid var(--brand);border-radius:22px;overflow:hidden;text-align:center}.calendar-card span{display:block;background:var(--brand);color:#fff;font-size:36px;font-weight:900;padding:10px}.calendar-card b{display:block;font-size:56px;padding:30px;color:var(--brand-deep)}
.saving-page{gap:16px}.money-flow{display:flex;align-items:center;justify-content:center;gap:22px}.money-flow>div{display:flex;flex-direction:column;align-items:center;gap:10px;background:#fff;border:5px solid var(--brand);border-radius:20px;padding:22px}.money-flow>div i{font-size:92px;color:var(--brand)}.money-flow>div b{font-size:38px}.money-flow>i{font-size:56px;color:var(--brand)}.saving-page .lead,.saving-page .warn,.saving-page .emph{padding:20px 26px}.leak-icon{font-size:130px}
.bell-icon{font-size:220px}.subscribe-title{font-size:74px}.youtube-pill{font-size:58px;font-weight:900;color:#fff;background:#e62117;padding:24px 42px;border-radius:999px;box-shadow:0 9px 0 #a71610}
.page-head small{white-space:nowrap}
.intro-logo{height:115px}.intro-logo .logo{height:68px}.mineo-chart{flex:1;min-height:0}.mineo-chart img{max-height:560px}.mineo-plan-page{gap:14px}.mineo-plan-table{height:auto;flex:1;min-height:0}.mineo-plan-table img{max-height:440px}.mineo-plan-page .lead{padding:18px 22px}
.eval-page{padding-left:38px;padding-right:38px}.eval-head{height:110px}.eval-head .logo{height:62px}.eval-head .total .grade{font-size:74px}.three-cards{justify-content:space-between;gap:7px;min-height:0}.eval-card{flex:0 0 auto;min-height:0;grid-template-columns:72px 1fr;gap:1px 12px;padding:8px 12px}.eval-page .card .rank{width:64px;height:64px;border-radius:14px;font-size:34px}.eval-page .card-name{font-size:34px}.eval-page .card .line{font-size:30px;line-height:1.08}.eval-note{font-size:28px;text-align:center;margin-top:6px}
.cta-visual img{max-height:650px}.cta-play{font-size:180px}.cta-title{font-size:72px}
.japan-logo{height:120px}.japan-logo .logo{height:75px}.japan-page{gap:18px}.japan-page .emph,.japan-page .lead{padding:24px 28px}.japan-table{font-size:36px}.japan-table th,.japan-table td{padding:17px 10px}
.summary-page{gap:12px}.summary-page .rows{gap:10px}.summary-page .rows li{padding:14px 18px}.summary-page .rows .tx{font-size:39px}.summary-page .rows .tx .sub{font-size:30px}.summary-page .lead{padding:18px 22px}
.company-note{gap:18px}.text-logos{gap:18px}.text-logos span{background:#fff;border:5px solid var(--brand);border-radius:18px;padding:18px;font-size:43px;font-weight:900}.brand-logos img{height:90px}.company-note .warn,.company-note .lead{padding:24px 28px}
.info-icon{font-size:230px}.caution-title{font-size:100px}.posting-warn{text-align:center}.comment-icon{font-size:220px}.comment-title{font-size:86px}.comment-page .rows{gap:12px}.comment-page .rows li{padding:18px 22px}.comment-page .rows .tx{font-size:40px}.pen-icon{font-size:220px}.blog-title{font-size:72px}.blog-image{width:100%;height:auto;max-height:320px;object-fit:contain;border-radius:18px;filter:drop-shadow(0 12px 20px #0003)}.blog-page{gap:16px}.blog-page .lead{padding:22px 26px}
.final-bell{font-size:210px}.final-title{font-size:68px}.emoji-cta{display:flex;gap:70px;justify-content:center}.emoji-cta span{font-size:130px}.thanks{font-size:56px;text-align:center;color:var(--brand-deep)}.final-note{font-size:30px;text-align:center}
</style>
"""


def validate_assets() -> None:
    relative_assets = [
        MINEO_LOGO,
        JAPAN_SIM_LOGO,
        BLOG_IMAGE,
        MINEO_CHART,
        MINEO_PLAN_TABLE,
        MINEO_THUMBNAIL,
        PAST_THUMBNAIL,
        HOOK_ART,
    ]
    missing = [asset for asset in relative_assets if not (ROOT / asset).is_file()]
    if missing:
        raise FileNotFoundError(f"Missing slide assets: {missing}")


def main() -> None:
    validate_assets()
    scenario = load_scenario()
    deck = build_deck(scenario)
    missing = [slide_id for slide_id in scenario if slide_id not in deck.slides]
    extra = [slide_id for slide_id in deck.slides if slide_id not in scenario]
    if missing or extra:
        raise ValueError(f"Slide mapping mismatch: missing={missing}, extra={extra}")

    for slide_id, slide in scenario.items():
        if any(instruction.startswith("評価見開き／") for instruction in slide.instructions):
            intro_id = slide_id if slide_id.endswith("-0") else f"{slide_id}-0"
            if intro_id not in deck.slides:
                raise ValueError(f"Evaluation is missing its N-0 intro: {slide_id}")
            if 'class="radar-chart-image"' not in deck.slides[intro_id]:
                raise ValueError(f"Evaluation intro is missing its radar chart: {intro_id}")

    document = f'''<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>【放置は損】無料オプション終了後の自動課金</title>
<link href="https://fonts.googleapis.com/css2?family=M+PLUS+Rounded+1c:wght@400;500;700;800;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
<link rel="stylesheet" href="templates/spread-base.css">{CSS}</head><body>
{"".join(deck.slides[slide_id] for slide_id in scenario)}
</body></html>'''
    OUTPUT_PATH.write_text(document, encoding="utf-8")
    print(f"generated {len(deck.slides)} slides -> {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
