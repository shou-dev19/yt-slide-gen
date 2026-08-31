#!/usr/bin/env python3
"""Generate the long-44 IIJmio deck from its master scenario CSV.

The CSV remains the source of the on-screen copy.  This generator deliberately
contains presentation mappings (slide ID -> spread component) rather than HTML
that is edited by hand, so later visual revisions are made here and regenerated.
"""
from __future__ import annotations

import csv
import html
from collections import OrderedDict
from pathlib import Path

ROOT = Path("/workspaces/yt-factory/packages/slide-gen")
CSV_PATH = Path("/workspaces/yt-factory/packages/scenario-gen/archive/videos/44_【〜11／4】IIJmioのデータeSIMが最大3ヵ月0円！au回線で2枚目の副回線を持つ方法/long/【〜11／4】IIJmioのデータeSIMが最大3ヵ月0円！au回線で2枚目の副回線を持つ方法.csv")
OUT_PATH = ROOT / "slides.html"
BLUE = "--brand:#1565C0;--brand-deep:#0d47a1;--brand-soft:#e3f0fb"
RED = "--brand:#C8102E;--brand-deep:#9a0c23;--brand-soft:#fde3e7"


def esc(text: str) -> str:
    return html.escape(text, quote=True)


def read_copy() -> OrderedDict[str, str]:
    slides: OrderedDict[str, str] = OrderedDict()
    with CSV_PATH.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            slide_id = row["スライドID"].strip()
            content = row["スライドに表示する内容"].strip()
            if slide_id and slide_id not in slides:
                slides[slide_id] = content
    return slides


def std(kicker: str, title: str, chips: list[str], date: str = "期間限定") -> str:
    chip_html = "".join(f"<span>{esc(x)}</span>" for x in chips)
    return f'''<div class="slide-container std" style="{BLUE}">
  <div class="std-rays"></div><div class="std-date">{esc(date)}</div>
  <div class="std-copy"><div class="std-kicker">{esc(kicker)}</div><h1>{title}</h1><div class="std-chips">{chip_html}</div></div>
</div>'''


def spread(left: str, right: str, *, style: str = BLUE, price: bool = False) -> str:
    cls = "slide-container price-note" if price else "slide-container"
    return f'''<div class="{cls}" style="{style}">
  <div class="book"><div class="spine"></div>
    <div class="page left">{left}</div>
    <div class="page right"><span class="index-tab">格安SIM図鑑</span>{right}</div>
  </div>
</div>'''


def head(title: str, body: str, page_no: int | None = None) -> str:
    no = f'<span class="page-no">― {page_no} ―</span>' if page_no else ""
    return f'<div class="page-head">{title}</div><div class="page-body">{body}</div>{no}'


def rows(items: list[tuple[str, str]], numbered: bool = False) -> str:
    lis = []
    for n, (icon, text) in enumerate(items, 1):
        marker = f'<span class="badge">{n}</span>' if numbered else f'<span class="ic"><i class="fa-solid {icon}"></i></span>'
        lis.append(f'<li>{marker}<div class="tx">{text}</div></li>')
    return '<ul class="rows">' + ''.join(lis) + '</ul>'


def chapter(num: int, title: str, lead: str) -> str:
    return spread(
        f'<div class="divider"><div class="kicker">CHAPTER</div><div class="num">{num}</div><div class="seal">FILE No.{num:02}</div></div>',
        f'<div class="page-body center"><div class="big-title">{title}</div><div class="lead" style="text-align:center">{lead}</div></div>',
    )


def cta(title: str, thumbnail: str, lead_text: str) -> str:
    return spread(
        head("詳しく解説した過去動画", f'<div class="visual"><img src="{thumbnail}" alt="過去動画のサムネイル"></div>'),
        f'<div class="page-body"><div class="bigicon"><i class="fa-solid fa-play"></i></div><div class="big-title cta-title">{title}</div><div class="lead" style="text-align:center">{lead_text}</div></div>',
    )


def evaluation() -> str:
    cards_left = [
        ("SS", "データ料金", "音声2GB 850円・eSIM2GB 440円から", "容量あたりの安さはトップクラス"),
        ("B", "通信品質", "ドコモ回線・au回線を選べる", "お昼は混雑で速度が落ちやすい"),
        ("A", "初期費用", "今だけeSIM初期費用が1,650円引き", "通常は初期費用3,300円"),
    ]
    cards_right = [
        ("S", "通話料", "5分かけ放題 月500円・アプリ不要", "完全かけ放題は月1,400円"),
        ("B", "店舗サポート", "家電量販店でパッケージを買える", "申し込み・サポートはネット中心"),
        ("A", "オプション", "データ繰越・家族シェアに対応", "データeSIMは通話・SMS非対応"),
    ]
    def card(rank: str, name: str, pro: str, con: str) -> str:
        return f'<div class="card"><div class="rank {rank}">{rank}</div><div class="card-name">{name}</div><div class="line pro"><span class="tag">＋</span>{pro}</div><div class="line con"><span class="tag">－</span>{con}</div></div>'
    left_cards = ''.join(card(*x) for x in cards_left)
    right_cards = ''.join(card(*x) for x in cards_right)
    left = f'<div class="head-left"><img class="logo" src="public/images/logo/iijmio_logo.png" alt="IIJmio"><div class="total"><div class="label">総合評価</div><div class="rank A total-rank">A</div></div></div><div class="cards">{left_cards}</div>'
    right = f'<div class="page-head">IIJmioの6観点評価</div><div class="page-body top"><div class="cards">{right_cards}</div><div class="note evaluation-note">※本評価は当チャンネルの独断と偏見による独自評価であり、キャンペーン割引等は考慮していません</div></div>'
    return spread(left, right)


def evaluation_overview() -> str:
    """Render the mandatory fee/radar half of the IIJmio evaluation pair.

    Evaluation narration in the master CSV is currently assigned only to slide
    11.  The presentation still needs its immediately preceding 11-0 spread,
    so it is injected by the renderer instead of making this vital layout
    conditional on a hand-authored CSV row.
    """
    left = (
        '<div class="head-left"><img class="logo" '
        'src="public/images/logo/iijmio_logo.png" alt="IIJmio"></div>'
        '<div class="visual evaluation-radar"><img '
        'src="public/images/charts/IIJmio.png" alt="IIJmioの6観点評価レーダーチャート"></div>'
    )
    right = head(
        "IIJmioの料金プラン",
        '<table class="sheet"><tr><th>プラン</th><th>容量</th><th>月額</th></tr>'
        '<tr><td>データeSIM<br><span class="sub">タイプI</span></td><td>2GB</td><td class="em">440円</td></tr>'
        '<tr><td>データeSIM<br><span class="sub">タイプA</span></td><td>2GB</td><td class="em">740円</td></tr>'
        '<tr><td>音声SIM</td><td>5GB</td><td class="em">950円</td></tr></table>'
        '<div class="lead" style="text-align:center">ドコモ回線・au回線から<br>自分に合う回線を選べる</div>',
    )
    return spread(left, right, price=True)


def make_slides(copy: OrderedDict[str, str]) -> dict[str, str]:
    # Text below is condensed from each CSV cell so it remains readable at 1920x1080.
    result: dict[str, str] = {}
    result["1"] = std("IIJmioデータ専用eSIMの速報", '月額料金が<br><span>最大3ヵ月 0円！</span>', ["申込期間：2026年9月1日〜11月4日"], "2026年9月1日スタート")
    result["2"] = std("楽天モバイルの電波が不安なら", '2枚目に<span>au回線</span>を<br>追加できる！', ["メイン：楽天モバイル", "副回線：IIJmio データeSIM"], "デュアルSIMの新候補")
    result["3"] = std("デュアルSIMの最初の一歩", '<span>最大3ヵ月 0円</span><br>初期費用も半額！', ["通常3,300円 → 今だけ1,650円", "毎月の支払い増が不安な人へ"], "費用を抑えて始める")
    result["4"] = std("格安SIM図鑑", 'IIJmioのデータeSIMが<br><span>最大3ヵ月間 0円！</span>', ["au回線で2枚目の副回線を持つ方法", "11月4日まで"], "今日のテーマ")
    result["5-0"] = chapter(1, "何が・いくら・<br>いつまでお得？", "キャンペーンの中身を<br>先にチェック！")
    result["6"] = spread(
        head("eSIMスタート応援<br>キャンペーン", rows([("fa-calendar-days", "期間：2026年9月1日〜11月4日"), ("fa-sim-card", "対象：IIJmioギガプランのデータ通信専用eSIMを新規申込"), ("fa-gift", "課金開始月から最大3ヵ月間、月額料金を割引")]), 1),
        head("2ギガなら月額0円", '<div class="emph">割引額と月額料金が同じ<br><span class="big">2ギガは 0円</span></div><div class="lead">電話番号なし・通信専用。<br>eSIMなら最短で当日から使える</div>', 2), price=True)
    result["6-2"] = spread(
        head("2ギガの通常月額", '<table class="sheet"><tr><th>回線</th><th>月額</th></tr><tr><td>タイプI<br><span class="sub">ドコモ回線</span></td><td class="em">440円</td></tr><tr><td>タイプA<br><span class="sub">au回線・9/1追加</span></td><td class="em">740円</td></tr></table>', 3),
        head("25ギガには増量特典も", '<div class="emph">最大6ヵ月間<br><span class="big">5GB 増量</span></div><div class="lead">月額割引に加えて<br>たっぷり使いたい人にも特典</div>', 4), price=True)
    result["6-3"] = spread(
        head("最初に払うお金", '<div class="emph">通常の初期費用<br><span class="big">3,300円</span></div><div class="lead">eSIM初期費用割引で<br><span class="em">1,650円引き</span></div>', 5),
        head("今だけ初期費用は1,650円", '<div class="emph">SIMプロファイル発行手数料<br><span class="big">220円 → 0円</span></div><div class="lead">合計で最初に払うのは<br><span class="em">1,650円のみ</span></div><div class="note">適用期間：2026年9月1日〜11月4日</div>', 6), price=True)
    result["6-4"] = spread('<div class="page-body"><div class="bigicon"><i class="fa-solid fa-bell"></i></div><div class="big-title cta-title">キャンペーンの<br><span class="em">開始・終了</span>を逃さない！</div></div>', head("チャンネル登録で安心", '<div class="youtube-subscribe"><span class="youtube-play"></span>チャンネル登録</div><div class="lead" style="text-align:center">格安SIMのお得情報を<br>分かりやすくお届けします</div>', 8))
    # Keep every chapter-title line within the page width.  In particular,
    # 「3ヵ月後はいくら？」 must break at the phrase boundary rather than
    # allowing the browser to split 「いくら」 between lines.
    result["7-0"] = chapter(2, "3ヵ月後は<br>いくら？<br>見落としがちな<br>条件", "契約前に確認したい<br>2つのポイント")
    result["8"] = spread(head("割引終了後の月額", '<table class="sheet"><tr><th>2ギガ eSIM</th><th>月額</th></tr><tr><td>タイプA（au回線）</td><td class="em">740円</td></tr><tr><td>タイプI（ドコモ回線）</td><td class="em">440円</td></tr></table>', 9), head("維持費だけなら他社も", rows([("fa-coins", "povo2.0：ベースプラン 0円"), ("fa-yen-sign", "日本通信SIM：1GB 290円"), ("fa-circle-info", "IIJmioは「毎月使う副回線」向き")]), 10), price=True)
    result["8-2"] = spread(head("見落としがちな条件①", '<div class="bigicon"><i class="fa-solid fa-phone-slash"></i></div><div class="emph">電話番号の通話・SMSは<br><span class="big">使えません</span></div>', 11), head("通信だけを足すSIM", '<div class="lead">通話は今のメイン回線に任せる</div>' + rows([("fa-mobile-screen-button", "IIJmio eSIMはデータ通信専用"), ("fa-arrows-left-right", "つながらない時だけ<br>副回線へ切り替え")]), 12))
    result["9"] = spread(head("見落としがちな条件②", '<div class="bigicon"><i class="fa-solid fa-arrows-left-right"></i></div><div class="warn"><span class="ic"><i class="fa-solid fa-triangle-exclamation"></i></span>ドコモ回線からau回線へ<br><span class="em">あとから変更できません</span></div><div class="lead" style="text-align:center">最初に選ぶ回線タイプが大切</div>', 13), head("変更したいなら新規契約", rows([("fa-file-circle-plus", "タイプAへ変える場合は新規で申し込む"), ("fa-calendar-check", "申込前に回線タイプを必ず確認")]) + '<div class="note">※IIJmio公式お知らせ（2026年8月25日）より</div>', 14))
    result["10-0"] = chapter(3, "IIJmioって<br>どんな格安SIM？", "料金・回線・サポートを<br>6観点で評価")
    result["11-0"] = evaluation_overview()
    result["11"] = evaluation()
    result["11-2"] = cta("IIJmioの解説動画も<br>チェック！", "public/images/thumbnails/【月700円】IIJmio 25GB＋10分かけ放題6ヶ月無料！6月8日までの神キャンペーン_サムネ2.png", "IIJmioって実際どうなの？<br>詳しく知りたい方はこちら")
    result["12-0"] = chapter(4, "自分は<br>向いてる？<br>2枚目の作り方", "申し込む前の確認と<br>自分に合う選び方")
    result["13"] = spread(head("2枚目（デュアルSIM）の作り方", '<div class="emph">今のSIMはそのまま<br><span class="big">eSIMを1つ追加</span></div><div class="lead">QRコードを読み込んで<br>使う回線を選ぶだけ</div>', 21), head("申し込み前に端末を確認", rows([("fa-magnifying-glass", "「機種名 eSIM 対応」で検索"), ("fa-list-check", "IIJmio公式の動作確認済み端末一覧を見る"), ("fa-mobile-screen-button", "eSIM対応端末なら物理SIMと併用できる")]), 22))
    result["13-2"] = cta("楽天モバイルの<br>2枚持ちも<br>詳しく解説！", "public/images/thumbnails/43_【2026年10月】楽天モバイル、繋がらないエリアが拡大？乗り換えずに備える2枚持ちという技_サムネ3.png", "副回線を持つ考え方を<br>過去動画でチェック！")
    result["14"] = spread(head("ほかの2枚目候補との違い", rows([("fa-cart-shopping", "povo2.0：使うたびに自分でトッピングを買う"), ("fa-mobile-screen", "日本通信SIM：ドコモ回線のみ・データ繰越なし")]), 25), head("IIJmioは毎月自動で用意", '<div class="emph">余ったデータは<br><span class="big">翌月に繰り越し</span></div><div class="lead">2026年9月1日から<br><span class="em">au回線も選べる</span></div>', 26))
    result["15"] = spread(head("2枚目の選び方", rows([("fa-shield-heart", "ほとんど使わない保険なら povo2.0"), ("fa-piggy-bank", "毎月の維持費を最優先なら 日本通信SIM")]), 27), head("IIJmioが向く人", '<div class="lead">毎月コンスタントに少量使う<br>au回線を選びたい</div><div class="emph">メイン回線で足りている人は<br><span class="big">無理に持たなくてOK</span></div>', 28))
    result["16"] = spread(head("申し込む前の確認3つ", rows([("fa-mobile-screen-button", "端末がeSIMに対応しているか"), ("fa-tower-cell", "タイプA（au）かタイプI（ドコモ）か"), ("fa-user-check", "自分の使い方にIIJmioが合うか")], numbered=True), 29), head("ここは特に注意", '<div class="warn"><span class="ic"><i class="fa-solid fa-triangle-exclamation"></i></span>回線タイプは<br><span class="em">あとから変更できません</span></div><div class="lead">使う場所・欲しい回線を<br>申し込み前に決めよう</div>', 30))
    result["17-0"] = chapter(5, "今日の内容を<br>おさらい", "IIJmioデータeSIMの<br>要点を4つに整理")
    result["18"] = spread(head("今日のまとめ", rows([("", "2026年9月1日、<br>タイプA（au回線）が追加"), ("", "11月4日までの新規申込で、2ギガは最大3ヵ月 月額0円")], numbered=True), 33), head("費用とその後の月額", rows([("", "今だけ最初に払うのは1,650円のみ"), ("", "3ヵ月後：タイプA 740円／タイプI 440円")], numbered=True), 34), price=True)
    result["19"] = spread('<div class="page-body"><div class="bigicon"><i class="fa-solid fa-circle-info"></i></div><div class="big-title">お申し込み前の<br><span class="em">ご注意</span></div></div>', head("最新情報はIIJmio公式で", '<div class="warn"><span class="ic"><i class="fa-solid fa-triangle-exclamation"></i></span>プラン内容・キャンペーン情報は<br><span class="em">IIJmio公式サイトが正</span>です</div><div class="note">※料金・キャンペーンは動画投稿時点の情報です</div>', 36))
    result["20"] = spread(head("コメントで教えてね！", '<div class="bigicon"><i class="fa-solid fa-comments"></i></div><div class="lead" style="text-align:center">あなたの2枚目は<br>どんな組み合わせ？</div>', 37), head("たとえばこんなコメント", rows([("fa-circle-check", "「2枚目はこの組み合わせで持ってます」"), ("fa-circle-check", "「わたしのエリアの電波」"), ("fa-circle-check", "「わかりづらかった点」")]), 38))
    result["21"] = spread(head("スマホ代は大きな固定費", '<div class="bigicon"><i class="fa-solid fa-piggy-bank"></i></div><div class="emph">少しの見直しで<br><span class="big">毎月のゆとり</span></div>', 39), head("浮いた分を未来へ", '<div class="lead">少しでも多くの方に<br><span class="em">スマホ代の見直し</span>を</div><div class="emph">浮いたぶんは<br>貯蓄などにまわせます</div>', 40))
    result["21-1"] = spread('<div class="page-body"><div class="bigicon"><i class="fa-solid fa-compass"></i></div><div class="big-title cta-title">自分に合う<br><span class="em">1枚</span>が分かる</div></div>', head("これからも分かりやすく", '<div class="lead">あなたに合う格安SIMが分かる<br>そんな動画をつくります</div><div class="emph">役立つ情報を<br><span class="big">これからも発信中</span></div>', 42))
    result["22"] = spread('<div class="page-body"><div class="bigicon"><i class="fa-solid fa-pen-nib"></i></div><div class="big-title cta-title">ブログ・note<br>でも比較中！</div></div>', head("リンクは概要欄へ", '<div class="visual blog-image"><img src="public/images/common/ブログ_ヘッダー画像_スライド用.png" alt="ブログの案内"></div><div class="lead" style="text-align:center">格安SIMの料金を<br>さらに詳しく比較しています</div>', 44))
    result["23"] = spread('<div class="page-body"><div class="bigicon"><i class="fa-solid fa-bell"></i></div><div class="big-title cta-title">チャンネル登録<br>よろしくお願いします！</div></div>', '<div class="page-body"><div class="bigicon">👍　🔔</div><div class="lead" style="text-align:center"><span class="em">ご視聴いただき<br>ありがとうございました！</span></div><div class="note" style="text-align:center">グッドボタンもよろしくお願いします</div></div>')
    expected = set(copy)
    missing = expected - set(result)
    extra = set(result) - expected
    if missing or extra:
        raise ValueError(f"slide mapping mismatch; missing={sorted(missing)}, extra={sorted(extra)}")
    return result


STYLE = '''
<style>
body{--primary-color:#1565C0;--accent-red:#e53935;--text-dark:#212121}
.slide-container.std{width:1280px;height:720px;border:10px solid var(--brand);background:#fffaf5;box-sizing:border-box;position:relative;overflow:hidden;display:flex;align-items:center;justify-content:center;padding:42px;flex-shrink:0}.std-rays{position:absolute;inset:-35%;background:repeating-conic-gradient(from -12deg at 50% 50%,rgba(21,101,192,.12) 0 6deg,transparent 6deg 13deg)}.std-date{position:absolute;right:28px;top:28px;background:#fff;color:var(--brand-deep);border:5px solid var(--brand);border-radius:15px;padding:9px 20px;font-size:38px;font-weight:900;z-index:2}.std-copy{position:relative;z-index:1;width:100%;display:flex;flex-direction:column;align-items:center;text-align:center}.std-kicker{font-size:52px;font-weight:900;line-height:1.2;margin-bottom:14px;text-shadow:3px 3px #fff}.std-copy h1{font-size:88px;line-height:1.13;font-weight:900;letter-spacing:-3px;text-shadow:5px 5px #fff;margin:4px 0 28px}.std-copy h1 span{color:var(--brand-deep);font-size:108px;white-space:nowrap}.std-chips{display:flex;justify-content:center;gap:16px;flex-wrap:wrap;max-width:1160px}.std-chips span{font-size:43px;background:#fff;border:5px solid var(--brand);border-radius:999px;padding:9px 25px;box-shadow:0 8px 16px #0002;font-weight:900}
.page-head{line-height:1.16}.page .rows{gap:14px}.page .rows li{padding:16px 22px}.page .rows .tx{font-size:40px;line-height:1.25}.page .rows .ic{font-size:47px;width:58px}.page .rows .badge{width:62px;height:62px;font-size:37px}.page .lead{font-size:43px;padding:24px 28px}.page .emph{font-size:45px;padding:26px 30px}.page .emph .big{font-size:72px}.page .bigicon{font-size:185px}.cta-title{font-size:70px}.blog-image{height:325px}.blog-image img{width:100%;height:auto;max-height:320px;object-fit:contain}.youtube-subscribe{display:inline-flex;align-self:center;align-items:center;justify-content:center;gap:20px;min-width:520px;padding:23px 38px;border:6px solid #c90024;border-radius:999px;background:#ff0033;color:#fff;font-size:52px;font-weight:900;line-height:1;box-shadow:0 12px 0 #97001b,0 18px 22px #0003}.youtube-play{display:block;width:58px;height:42px;border-radius:10px;background:#fff}.head-left{height:132px}.head-left .logo{height:74px}.evaluation-radar{flex:1;min-height:0}.total-rank{width:82px;height:82px;border-radius:18px;font-size:44px;margin:4px auto}.card{flex:0 0 auto;min-height:150px;padding:13px 20px}.card .rank{width:82px;height:82px;font-size:40px}.card-name{font-size:40px}.card .line{font-size:31px;line-height:1.18}.evaluation-note{font-size:28px;text-align:center;margin-top:12px}.page .sheet{font-size:39px}.page .sheet th,.page .sheet td{padding:14px 12px}.page .sheet .sub{font-size:30px}
</style>'''


def main() -> None:
    copy = read_copy()
    slides = make_slides(copy)
    parts = ["<!doctype html><html lang=\"ja\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"><title>IIJmio データeSIM 最大3ヵ月0円</title>", '<link href="https://fonts.googleapis.com/css2?family=M+PLUS+Rounded+1c:wght@400;500;700;800;900&display=swap" rel="stylesheet"><link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css"><link rel="stylesheet" href="templates/spread-base.css">', STYLE, "</head><body>"]
    for slide_id in copy:
        parts.extend([f"<!-- Slide ID: {slide_id} -->", slides[slide_id]])
    parts.append("</body></html>\n")
    OUT_PATH.write_text("\n".join(parts), encoding="utf-8")
    print(f"generated {len(slides)} slides: {OUT_PATH}")


if __name__ == "__main__":
    main()
