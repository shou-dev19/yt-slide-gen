#!/usr/bin/env python3
"""Generate the LINEMO satellite/overseas long-form slide deck from its master CSV.

The master CSV is the source of slide order and visible copy.  This generator resolves
"同上", parses the slash-delimited display instructions, maps those instructions onto
the reusable components in templates/spread-base.css, and refuses to emit an HTML deck
whose Slide ID set differs from the scenario.
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
    "41_【2026年9月】LINEMOが月額そのままで衛星通信＆海外無制限！？今やるべき2つのこと/"
    "long/【2026年9月】LINEMOが月額そのままで衛星通信＆海外無制限！？今やるべき2つのこと.csv"
)
OUTPUT_PATH = ROOT / "slides.html"

BRAND = "--brand:#06c755;--brand-deep:#008f3c;--brand-soft:#e3f9ec"
LINEMO_LOGO = "public/images/logo/LINEMO_logo.png"
LINEMO_CHART = "public/images/charts/LINEMO.png"
OVERSEAS_IMAGE = "public/images/common/海外利用のイメージ図.png"
BLOG_IMAGE = "public/images/common/ブログ_ヘッダー画像_スライド用.png"
PAST_THUMBNAIL = (
    "public/images/thumbnails/"
    "LINE使い放題で月990円！LINEMO(ラインモ)のメリット・デメリットを徹底解説"
    "【ahamo・povo・楽天モバイル比較】.png"
)


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def strip_chapter(value: str) -> str:
    return re.sub(r"^第\d章\s*", "", value).strip()


def strip_number(value: str) -> str:
    return re.sub(r"^[①②③④⑤⑥]\s*", "", value).strip()


@dataclass(frozen=True)
class ScenarioSlide:
    slide_id: str
    instructions: tuple[str, ...]

    def parts(self, index: int = 0) -> list[str]:
        return [part.strip() for part in self.instructions[index].split("／") if part.strip()]


def load_scenario() -> OrderedDict[str, ScenarioSlide]:
    """Load slide order and all distinct resolved display instructions per ID."""
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
            resolved = last_instruction if shown == "同上" else shown or last_instruction
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


def numbered_rows(items: list[tuple[str, str, str]], *, icons: bool = False) -> str:
    entries: list[str] = []
    for badge, title, sub in items:
        marker = (
            f'<span class="ic"><i class="fa-solid {esc(badge)}"></i></span>'
            if icons
            else f'<span class="badge">{esc(badge)}</span>'
        )
        sub_html = f'<span class="sub">{esc(sub)}</span>' if sub else ""
        entries.append(f'<li>{marker}<div class="tx">{esc(title)}{sub_html}</div></li>')
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
    pattern = re.compile(
        r"([^／]+):([A-Z]+)（＋(.*?)／－(.*?)）(?=／[^／]+:[A-Z]+（|$)"
    )
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
        left_class: str = "",
        right_class: str = "",
    ) -> str:
        classes = "slide-container price-note" if price else "slide-container"
        if numbered:
            left_no = f'<span class="page-no">― {self.page_number} ―</span>'
            right_no = f'<span class="page-no">― {self.page_number + 1} ―</span>'
            self.page_number += 2
        else:
            left_no = right_no = ""
        left_page = "page left" + (f" {left_class}" if left_class else "")
        right_page = "page right" + (f" {right_class}" if right_class else "")
        markup = f'''<!-- Slide ID: {slide_id} -->
<div class="{classes}" style="{BRAND}"><div class="book"><div class="spine"></div>
  <div class="{left_page}">{left}{left_no}</div>
  <div class="{right_page}"><span class="index-tab">格安SIM図鑑</span>{right}{right_no}</div>
</div></div>'''
        self.add_raw(slide_id, markup)
        return markup

    def divider(self, slide_id: str, chapter: str, raw_title: str, lead: str) -> None:
        title = strip_chapter(raw_title)
        title_markup = {
            "9月1日から何が変わるの？": "9月1日から<br>何が変わるの？",
            "衛星でつながるってどういうこと？": "衛星でつながるって<br>どういうこと？",
            "海外のデータ通信が毎月最大7日間で使える": "海外のデータ通信が<br>毎月最大7日間で使える",
            "LINEMOを図鑑で評価": "LINEMOを<br>図鑑で評価",
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
    art: str,
) -> str:
    chips_html = "".join(f"<b>{esc(chip)}</b>" for chip in chips)
    return f'''<!-- Slide ID: {slide_id} -->
<div class="slide-container std"><div class="std-rays"></div><div class="std-ribbon">{esc(ribbon)}</div>
  <img class="std-brand" src="{LINEMO_LOGO}" alt="LINEMO">
  <div class="std-copy"><div class="std-kicker">{esc(kicker)}</div><h1>{title}</h1>
    <div class="std-chips">{chips_html}</div>
  </div>
  <div class="orbit"><i class="fa-solid fa-satellite-dish"></i><i class="fa-solid fa-plane"></i></div>
  <img class="std-hero" src="{art}" alt="驚く人">
</div>'''


def build_deck(scenario: OrderedDict[str, ScenarioSlide]) -> Deck:
    expected_ids = [
        "1", "2", "4", "5-0", "6", "7", "8-0", "9", "10", "11", "11-3",
        "12-0", "13", "14", "15", "16-0", "17-0", "17", "17-5", "18-0",
        "19", "20", "21", "22", "23", "24",
    ]
    if list(scenario) != expected_ids:
        raise ValueError(f"Unexpected scenario Slide IDs: {list(scenario)}")

    deck = Deck(scenario)

    hook = scenario["1"].parts()
    deck.add_raw(
        "1",
        std_slide(
            "1",
            "2026年9月1日から",
            strip_number(hook[0].replace("テロップ：速報 ", "")),
            '<span>月額そのまま</span>で<br>衛星通信 ＆ 海外<span>7日間</span>',
            ["既存ユーザーも対象", "圏外の保険", "海外データ無制限"],
            "public/images/irasutoya/business_man2_3_surprise.png",
        ),
    )

    title_text = scenario["2"].instructions[0].removeprefix("タイトル：")
    deck.add_raw(
        "2",
        std_slide(
            "2",
            "LINEMO サービス拡充",
            "知らないと損する注意点までやさしく解説",
            '<span>衛星通信</span>と<br><span>海外無制限</span>が追加',
            ["9月に申し込む", "海外は7日以内", "今やるべき2つ"],
            "public/images/irasutoya/present_open.png",
        ).replace("知らないと損する注意点までやさしく解説", esc(title_text)),
    )

    agenda = scenario["4"].parts()
    chapters = [strip_chapter(item) for item in agenda[2:7]]
    benefit_text = agenda[7].replace("【この動画でわかること】", "")
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
        head(esc(agenda[1])) + f'<ol class="agenda agenda-five">{agenda_html}</ol>',
        head("この動画でわかること")
        + f'<ul class="benefits benefit-two">{benefit_html}</ul>'
        + '<div class="emph agenda-answer">今やることは<span class="big">2つ</span><br>衛星の申込 ＋ 海外は7日以内</div>',
        numbered=False,
    )

    deck.divider("5-0", "1", scenario["5-0"].instructions[0], "月額そのままで、2つの特典を追加")

    service = scenario["6"].parts()
    deck.spread(
        "6",
        head("追加サービス", "①")
        + body(
            '<div class="bigicon service-icon"><i class="fa-solid fa-satellite-dish"></i></div>'
            f'<div class="lead service-lead">{esc(strip_number(service[2]))}</div>'
            '<div class="emph old-price"><span class="big">月額1,650円</span><br>→ 全額割引</div>',
            "center",
        ),
        head("追加サービス", "②")
        + body(
            '<div class="bigicon service-icon"><i class="fa-solid fa-earth-asia"></i></div>'
            f'<div class="lead service-lead">{esc(strip_number(service[3]))}</div>'
            '<div class="emph"><span class="big">最大7日間</span><br>追加料金なし</div>',
            "center service-page",
        ),
        price=True,
    )

    target = scenario["7"].parts()
    deck.spread(
        "7",
        head("対象プランは2つ")
        + body(
            f'<img class="feature-logo" src="{LINEMO_LOGO}" alt="LINEMO">'
            + numbered_rows([
                ("1", target[2], "3GBまで990円／10GBまで2,090円"),
                ("2", target[3], "30GB・5分通話無料込みで2,970円"),
            ]),
        ),
        head("既存ユーザーも対象")
        + body(
            '<div class="bigicon user-icon"><i class="fa-solid fa-users"></i></div>'
            '<div class="emph"><span class="big">契約し直し不要</span></div>'
            '<div class="lead centered-lead">月額料金は据え置き<br>既存ユーザーにも適用</div>',
            "center target-page",
        ),
        price=True,
    )

    deck.divider("8-0", "2", scenario["8-0"].instructions[0], "圏外で使えること・使えないこと")

    satellite = scenario["9"].parts()
    deck.spread(
        "9",
        head("SoftBank Starlink Direct")
        + body(
            '<div class="satellite-diagram">'
            '<i class="fa-solid fa-satellite"></i><span class="signal">⋮⋮⋮</span>'
            '<i class="fa-solid fa-mobile-screen-button"></i></div>'
            f'<div class="lead centered-lead">{esc(satellite[2])}</div>',
            "center",
        ),
        head("特別な機械はいらない")
        + body(
            numbered_rows([
                ("fa-mobile-screen-button", satellite[3], "普段のスマホをそのまま利用"),
                ("fa-mountain-sun", satellite[4], "山・海など地上の電波が届かない場所"),
            ], icons=True)
            + '<div class="warn sky-warn"><span class="ic"><i class="fa-solid fa-cloud-sun"></i></span>空が見える場所が基本</div>',
        ),
    )

    can_do = scenario["10"].parts(0)
    cannot_do = scenario["10"].parts(1)
    deck.spread(
        "10",
        head("できること", "メッセージ中心")
        + body(
            numbered_rows([
                ("fa-comment-sms", "SMS", "電話番号で送る短いメッセージ"),
                ("fa-comments", "RCS（＋メッセージ）", "写真・スタンプにも対応するSMSの進化版"),
                ("fa-paper-plane", "国際SMS", "海外あてのSMS"),
                ("fa-mobile-screen", "一部の対象アプリ", "LINE・PayPay・災害用伝言板など"),
            ], icons=True),
            "compact-rows",
        ),
        head("できないこと", "重要な3点")
        + body(
            numbered_rows([
                ("fa-phone-slash", cannot_do[2], "圏外で電話できる機能ではない"),
                ("fa-video-slash", cannot_do[3], "動画視聴・大容量通信は対象外"),
                ("fa-building", "遮へい物がある場所", "利用不可・不安定になる場合あり"),
            ], icons=True),
            "compact-rows",
        ),
    )

    timing = scenario["11"].parts()
    deck.spread(
        "11",
        head("2026年9月1日〜冬")
        + body(
            '<div class="season autumn">AUTUMN</div>'
            '<div class="emph action-box"><span class="big">申込が必要</span><br>月額1,650円を全額割引</div>'
            '<div class="warn action-warn"><span class="ic"><i class="fa-solid fa-triangle-exclamation"></i></span>申し込まないと使えません</div>',
            "center",
        ),
        head("2026年冬以降", "予定")
        + body(
            '<div class="season winter">WINTER</div>'
            '<div class="emph action-box"><span class="big">申込不要</span><br>追加料金なし</div>'
            '<div class="lead centered-lead">対応機種・OSは<br>公式サイトで確認</div>',
            "center",
        ),
        price=True,
    )

    deck.spread(
        "11-3",
        body(
            '<div class="bigicon subscribe-icon"><i class="fa-solid fa-bell"></i></div>'
            '<div class="big-title subscribe-title">速報を<br>見逃さない！</div>',
            "center",
        ),
        head("条件変更も<br>すばやくお届け")
        + body(
            '<div class="lead subscribe-copy">申込期限・対象条件・新サービスの変更を分かりやすく解説</div>'
            '<div class="youtube-pill"><i class="fa-brands fa-youtube"></i> チャンネル登録</div>',
            "center",
        ),
        numbered=False,
    )

    deck.divider("12-0", "3", scenario["12-0"].instructions[0], "海外旅行は「7日以内」が重要")

    overseas = scenario["13"].parts()
    deck.spread(
        "13",
        head("海外あんしん定額<br>「定額国L」")
        + body(
            f'<div class="visual overseas-visual"><img src="{OVERSEAS_IMAGE}" alt="海外利用のイメージ"></div>'
            '<div class="note source-note">対象の国・地域は2026年8月7日時点。渡航前に公式サイトで確認</div>',
        ),
        head("海外データ無制限")
        + body(
            '<div class="emph"><span class="big">200以上</span><br>の国・地域が対象</div>'
            + numbered_rows([
                ("1", strip_number(overseas[3]), "旅行先に合わせて選択"),
            ]),
            "center travel-overview",
        ),
    )

    overseas_value = scenario["14"].parts(0)
    overseas_conditions = scenario["14"].parts(1)
    deck.spread(
        "14",
        head("毎月の無料枠")
        + body(
            '<div class="emph trip-value"><span class="big">最大7日間</span><br>6,860円分が追加料金なし</div>'
            '<div class="bigicon plane-icon"><i class="fa-solid fa-plane-departure"></i></div>'
            '<div class="lead centered-lead">約1週間の旅行なら<br>データ通信料0円の計算</div>',
            "center benefit-page",
        ),
        head("利用前に必要なこと")
        + body(
            numbered_rows([
                ("1", overseas_conditions[2].replace("への加入が必要", "へ加入"), "渡航前に設定"),
                ("2", overseas_conditions[3].replace("が必要", ""), "専用サイトで利用開始"),
            ])
            + f'<div class="warn"><span class="ic"><i class="fa-solid fa-phone-slash"></i></span>{esc(overseas_conditions[4])}</div>',
            "conditions-page",
        ),
        price=True,
    )

    autumn_limit = scenario["15"].parts(0)
    winter_limit = scenario["15"].parts(1)
    speed_limit = scenario["15"].parts(2)
    deck.spread(
        "15",
        head("9月〜冬は選び方に注意")
        + body(
            '<table class="sheet travel-table"><thead><tr><th>選ぶプラン</th><th>割引</th></tr></thead><tbody>'
            '<tr><td>1〜7日間<br><span class="sub">980〜6,860円</span></td><td class="em">対象</td></tr>'
            '<tr><td>8〜31日間<br><span class="sub">7,840〜30,380円</span></td><td>対象外</td></tr>'
            '</tbody></table>'
            '<div class="warn autumn-trap"><span class="ic"><i class="fa-solid fa-triangle-exclamation"></i></span>秋は<span class="em">7日以内</span>を選ぶ</div>',
            "center",
        ),
        head("冬以降 ＋ 速度ルール")
        + body(
            '<div class="lead winter-all">冬以降：1〜31日間の全プランで<br><span class="em">最大7日間分が無料</span></div>'
            '<div class="emph speed-box"><span class="big">24時間で10GB</span><br>超過後は次の区切りまで最大4.5Mbps</div>'
            '<div class="note speed-note">4.5Mbpsは地図・SNS・標準画質動画の利用が目安</div>',
            "center speed-page",
        ),
        price=True,
    )

    deck.divider("16-0", "4", scenario["16-0"].instructions[0], "6観点で強みと注意点をチェック")

    carrier, overall, cards = parse_evaluation(scenario["17-0"].instructions[0])
    deck.spread(
        "17-0",
        '<div class="head-left plan-head">'
        f'<img class="logo" src="{LINEMO_LOGO}" alt="{esc(carrier)}">'
        f'<span class="file-no">{esc(carrier)}</span></div>'
        f'<div class="visual plan-chart"><img src="{LINEMO_CHART}" alt="LINEMOレーダーチャート"></div>',
        head("LINEMOの料金プラン")
        + body(
            '<table class="sheet linemo-plan-table"><thead><tr><th>プラン</th><th>データ容量</th><th>月額</th></tr></thead><tbody>'
            '<tr><td rowspan="2">LINEMO<br>ベストプラン</td><td>3GBまで</td><td class="em">990円</td></tr>'
            '<tr><td>10GBまで</td><td class="em">2,090円</td></tr>'
            '<tr><td>LINEMO<br>ベストプランV</td><td>30GB</td><td class="em">2,970円</td></tr>'
            '</tbody></table>'
            '<div class="lead plan-lead">小容量から30GBまで<br>使い方に合わせて選べる</div>',
            "center plan-body",
        ),
        price=True,
        left_class="plan-page",
        right_class="plan-page",
    )

    deck.spread(
        "17",
        '<div class="head-left eval-head">'
        f'<img class="logo" src="{LINEMO_LOGO}" alt="{esc(carrier)}">'
        f'<div class="total"><div class="label">総合評価</div><div class="grade">{esc(overall)}</div></div></div>'
        f'<div class="cards three-cards">{evaluation_card(*cards[0])}{evaluation_card(*cards[1])}{evaluation_card(*cards[2])}</div>',
        f'<div class="cards three-cards">{evaluation_card(*cards[3])}{evaluation_card(*cards[4])}{evaluation_card(*cards[5])}</div>'
        '<div class="note eval-note">※本評価は当チャンネルの独断と偏見による独自評価であり、キャンペーン割引等は考慮していません</div>',
        price=True,
        left_class="eval-page eval-detail-page",
        right_class="eval-page eval-detail-page",
    )

    deck.spread(
        "17-5",
        f'<div class="visual cta-visual"><img src="{PAST_THUMBNAIL}" alt="LINEMOの過去動画サムネイル"></div>',
        body(
            '<div class="bigicon cta-play"><i class="fa-solid fa-circle-play"></i></div>'
            '<div class="big-title cta-title">LINEMOの<br>詳しい特徴も解説</div>'
            '<div class="lead centered-lead">メリット・デメリットは<br>過去動画もチェック！</div>',
            "center",
        ),
        numbered=False,
    )

    deck.divider("18-0", "5", scenario["18-0"].instructions[0], "得する人と、今やるべき2つ")

    winners = scenario["19"].parts(0)
    no_rush = scenario["19"].parts(1)
    deck.spread(
        "19",
        head("今回の拡充で得をする人")
        + body(
            numbered_rows([
                ("1", "LINEMOの対象2プランを利用中", "いまの契約のまま対象"),
                ("2", "キャンプ・登山・釣りに行く", "圏外でのメッセージが保険に"),
                ("3", "年1〜2回、海外へ行く", "毎月最大7日間分が無料"),
            ]),
            "compact-rows",
        ),
        head("急いで乗り換えなくていい人")
        + body(
            '<div class="bigicon home-icon"><i class="fa-solid fa-house-signal"></i></div>'
            f'<div class="lead centered-lead">{esc(no_rush[2])}</div>'
            '<div class="emph insurance-box">衛星通信は<span class="big">もしもの保険</span><br>これ目当てで慌てなくてOK</div>',
            "center who-page",
        ),
    )

    other_carriers = scenario["20"].parts()
    deck.spread(
        "20",
        head("衛星との直接通信", "各社の開始時期")
        + body(
            '<div class="timeline">'
            '<div class="timeline-item done"><span>2025年4月</span><b>au</b></div>'
            '<div class="timeline-arrow"><i class="fa-solid fa-arrow-down"></i></div>'
            '<div class="timeline-item done"><span>2026年4月</span><b>ソフトバンク・ドコモ</b></div>'
            '<div class="timeline-arrow"><i class="fa-solid fa-arrow-down"></i></div>'
            '<div class="timeline-item future"><span>2026年内予定</span><b>楽天モバイル</b></div>'
            '</div>',
            "center",
        ),
        head("LINEMOの強み")
        + body(
            f'<img class="feature-logo large" src="{LINEMO_LOGO}" alt="LINEMO">'
            '<div class="emph low-price"><span class="big">月990円〜</span><br>衛星通信が追加料金なし</div>'
            '<div class="lead centered-lead">衛星通信そのものは<br>LINEMOだけの機能ではない</div>',
            "center linemo-strength",
        ),
        price=True,
    )

    summary = scenario["21"].parts()
    deck.spread(
        "21",
        head("今日のまとめ", "①②")
        + body(
            numbered_rows([
                ("1", strip_number(summary[1]), "既存ユーザーにも適用"),
                ("2", strip_number(summary[2]), "9月〜冬は月額1,650円を全額割引"),
            ]),
            "compact-rows",
        ),
        head("まとめ③・結論")
        + body(
            numbered_rows([
                ("3", strip_number(summary[3]), "冬までは7日間以内のプランが対象"),
            ])
            + '<div class="emph final-actions">今やることは<span class="big">2つ</span><br>①衛星の申込　②海外は7日以内</div>',
            "summary-page",
        ),
        price=True,
    )

    caution = scenario["22"].instructions[0]
    official = scenario["22"].instructions[1]
    deck.spread(
        "22",
        body(
            '<div class="bigicon info-icon"><i class="fa-solid fa-circle-info"></i></div>'
            '<div class="big-title caution-title">ご注意</div>',
            "center",
        ),
        head("投稿時点の情報です")
        + body(
            '<div class="warn posting-warn"><span class="ic"><i class="fa-solid fa-triangle-exclamation"></i></span>料金・サービス内容・提供時期・条件は変わる可能性があります</div>'
            '<div class="lead official-lead">詳細は<span class="em">LINEMO公式サイト</span>で確認<br>概要欄にリンクがあります</div>',
            "center",
        ),
        numbered=False,
    )

    comment_instruction = scenario["23"].instructions[0]
    deck.spread(
        "23",
        head("コメントで教えてね！")
        + body(
            numbered_rows([
                ("fa-comment-dots", "キャンプでいつも圏外", ""),
                ("fa-comment-dots", "海外でSIMを買うのが面倒", ""),
                ("fa-comment-dots", "LINEMOを使っています", ""),
            ], icons=True),
        ),
        head("ブログ・note")
        + body(
            f'<img class="blog-image" src="{BLOG_IMAGE}" alt="ブログ・note">'
            '<div class="lead blog-lead">詳しい格安SIM記事は<br>概要欄リンクからぜひ！</div>'
            '<div class="note blog-note">動画とあわせて、じっくり読めます</div>',
            "center blog-page",
        ),
        numbered=False,
    )

    deck.spread(
        "24",
        body(
            '<div class="bigicon bell-icon"><i class="fa-solid fa-bell"></i></div>'
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
body{--primary-color:#06c755;--accent-red:#e53935;--text-dark:#202124}
.slide-container.std{width:1280px;height:720px;border:10px solid var(--primary-color);background:#f9fff9;box-sizing:border-box;position:relative;overflow:hidden;display:flex;align-items:center;justify-content:center;padding:42px;color:var(--text-dark)}
.std-rays{position:absolute;inset:-35%;background:repeating-conic-gradient(from -12deg at 50% 50%,rgba(6,199,85,.13) 0 6deg,transparent 6deg 13deg)}
.std-ribbon{position:absolute;z-index:4;left:22px;top:28px;background:#e53935;color:#fff;font-size:44px;font-weight:900;padding:10px 38px;transform:rotate(-3deg);box-shadow:0 9px 0 #a92222}
.std-brand{position:absolute;z-index:3;right:46px;top:32px;width:270px;height:82px;object-fit:contain;background:#fff;padding:12px 24px;border-radius:18px;box-shadow:0 9px 22px #0002}
.std-copy{position:relative;z-index:3;width:100%;display:flex;flex-direction:column;align-items:center;text-align:center;margin-top:62px}
.std-kicker{font-size:48px;font-weight:900;margin-bottom:8px;text-shadow:3px 3px #fff;max-width:1040px;line-height:1.25}
.std-copy h1{font-size:88px;line-height:1.08;font-weight:900;letter-spacing:-3px;text-shadow:5px 5px #fff;margin:8px 0 22px}
.std-copy h1 span{color:#e53935;font-size:104px;white-space:nowrap}
.std-chips{display:flex;justify-content:center;gap:16px;flex-wrap:wrap}
.std-chips b{font-size:44px;background:#fff;border:5px solid #06c755;border-radius:999px;padding:7px 22px;box-shadow:0 8px 16px #0002}
.std-hero{position:absolute;z-index:1;right:8px;bottom:-18px;width:245px;height:285px;object-fit:contain;filter:drop-shadow(0 14px 15px #0003);opacity:.88}
.orbit{position:absolute;z-index:1;left:35px;bottom:28px;width:260px;height:190px;border:5px dashed #06c755;border-radius:50%;transform:rotate(-12deg);display:flex;justify-content:space-around;align-items:center;color:#06a94a;font-size:70px;opacity:.82}
.orbit i:last-child{color:#1689d4;font-size:62px;transform:rotate(28deg)}
.agenda-five{gap:10px}.agenda-five li{font-size:44px;gap:18px}.agenda-five .num{width:70px;height:70px;font-size:40px}
.benefit-two{gap:18px}.benefit-two li{font-size:48px}.agenda-answer{padding:22px 28px}.agenda-answer .big{font-size:78px}
.chapter-title{font-size:88px}.chapter-lead{font-size:48px;text-align:center;margin-top:24px}
.service-icon{font-size:180px}.service-lead{font-size:48px;text-align:center;padding:22px}.old-price{padding:24px}.old-price .big{font-size:72px}
.feature-logo{width:100%;height:95px;object-fit:contain}.feature-logo.large{height:120px}.user-icon{font-size:190px}.centered-lead{text-align:center}.satellite-diagram{display:flex;align-items:center;justify-content:center;gap:42px;font-size:180px;color:var(--brand)}.satellite-diagram .signal{font-size:110px;letter-spacing:12px;color:#1689d4;transform:rotate(90deg)}.sky-warn{text-align:center}
.compact-rows .rows{gap:10px}.compact-rows .rows li{padding:14px 20px}.compact-rows .rows .ic{width:70px}.service-page .service-icon{font-size:150px}.service-page .emph{padding:24px}.target-page .user-icon{font-size:140px}.target-page .emph,.target-page .lead{padding:24px}
.season{font-size:42px;font-weight:900;letter-spacing:8px;border-radius:999px;padding:10px 38px}.season.autumn{background:#ef8b2c;color:#fff}.season.winter{background:#3f87c8;color:#fff}.action-box{width:100%;padding:30px}.action-warn{text-align:center}
.subscribe-icon{font-size:230px}.subscribe-title{font-size:80px}.subscribe-copy{text-align:center}.youtube-pill{font-size:58px;font-weight:900;color:#fff;background:#e62117;padding:24px 42px;border-radius:999px;box-shadow:0 9px 0 #a71610}
.overseas-visual{height:auto;flex:1}.overseas-visual img{max-height:560px}.source-note{font-size:30px;text-align:center}.trip-value{padding:28px}.trip-value .big{font-size:88px}.plane-icon{font-size:150px}.travel-overview .emph{padding:24px}.travel-overview .rows{gap:10px}.travel-overview .rows li{padding:14px 20px}.benefit-page .plane-icon{font-size:120px}.benefit-page .lead{padding:22px}.conditions-page{gap:14px}.conditions-page .rows{gap:10px}.conditions-page .rows li{padding:14px 20px}.conditions-page .warn{padding:24px 28px}.travel-table th,.travel-table td{padding:20px 14px}.autumn-trap{text-align:center}.winter-all{text-align:center}.speed-box{padding:28px}.speed-box .big{font-size:76px}.speed-note{font-size:30px;text-align:center}.speed-page{gap:14px}.speed-page .lead,.speed-page .emph{padding:22px 28px}
.plan-page,.eval-page{padding-left:42px;padding-right:42px}.plan-head,.eval-head{height:122px}.plan-head .logo,.eval-head .logo{height:72px}.plan-head .file-no{margin-left:auto}.plan-chart{height:570px}.plan-chart img{max-width:100%;max-height:100%;object-fit:contain;filter:drop-shadow(0 8px 15px #0002)}.plan-body{gap:24px}.linemo-plan-table{font-size:38px}.linemo-plan-table th,.linemo-plan-table td{padding:19px 12px}.plan-lead{font-size:46px;text-align:center;padding:22px 28px}.eval-head .total .grade{font-size:80px}.three-cards{justify-content:space-between;gap:8px;min-height:0}.eval-detail-page .eval-card{flex:0 0 auto;min-height:0;grid-template-columns:82px 1fr;gap:2px 14px;padding:10px 14px}.eval-detail-page .card .rank{width:72px;height:72px;border-radius:16px;font-size:38px}.eval-detail-page .card-name{font-size:36px}.eval-detail-page .card .line{font-size:36px;line-height:1.13}.eval-note{font-size:28px;text-align:center;margin-top:8px}.cta-visual img{max-height:650px}.cta-play{font-size:180px}.cta-title{font-size:72px}
.home-icon{font-size:170px}.insurance-box{padding:28px}.insurance-box .big{font-size:68px}.who-page .home-icon{font-size:100px}.who-page .lead{padding:20px}.who-page .insurance-box{padding:16px}.timeline{width:100%;display:flex;flex-direction:column;align-items:center}.timeline-item{width:100%;display:grid;grid-template-columns:260px 1fr;align-items:center;border:5px solid var(--brand);background:#fff;border-radius:20px;padding:19px 24px}.timeline-item span{font-size:38px;font-weight:900;color:var(--brand-deep)}.timeline-item b{font-size:44px}.timeline-item.future{border-style:dashed}.timeline-arrow{font-size:46px;color:var(--brand)}.low-price{padding:28px}.linemo-strength .feature-logo.large{height:70px}.linemo-strength .emph,.linemo-strength .lead{padding:18px}.final-actions{padding:28px}.final-actions .big{font-size:76px}.summary-page{gap:14px}.summary-page .rows{flex:0 0 auto}.summary-page .rows li{padding:14px 20px}.summary-page .final-actions{padding:20px}
.info-icon{font-size:230px}.caution-title{font-size:100px}.posting-warn{text-align:center}.official-lead{text-align:center}.blog-image{width:100%;height:auto;max-height:320px;object-fit:contain;border-radius:18px;filter:drop-shadow(0 12px 20px #0003)}.blog-lead{text-align:center;padding:24px}.blog-note,.final-note{font-size:30px;text-align:center}.blog-page{gap:14px}.blog-page .blog-image{max-height:280px}.blog-page .blog-lead{padding:20px}.bell-icon{font-size:210px}.final-title{font-size:68px}.emoji-cta{display:flex;gap:70px;justify-content:center}.emoji-cta span{font-size:130px}.thanks{font-size:56px;text-align:center;color:var(--brand-deep)}
</style>
"""


def validate_assets() -> None:
    relative_assets = [
        LINEMO_LOGO,
        LINEMO_CHART,
        OVERSEAS_IMAGE,
        BLOG_IMAGE,
        PAST_THUMBNAIL,
        "public/images/irasutoya/business_man2_3_surprise.png",
        "public/images/irasutoya/present_open.png",
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

    document = f'''<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>【2026年9月】LINEMO 衛星通信＆海外データ通信</title>
<link href="https://fonts.googleapis.com/css2?family=M+PLUS+Rounded+1c:wght@400;500;700;800;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
<link rel="stylesheet" href="templates/spread-base.css">{CSS}</head><body>
{"".join(deck.slides[slide_id] for slide_id in scenario)}
</body></html>'''
    OUTPUT_PATH.write_text(document, encoding="utf-8")
    print(f"generated {len(deck.slides)} slides -> {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
