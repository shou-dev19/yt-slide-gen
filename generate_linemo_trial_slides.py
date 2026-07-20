#!/usr/bin/env python3
"""Generate the LINEMO Trial Campaign 2 long-form slide deck from its CSV."""

from __future__ import annotations

import csv
import html
import re
from pathlib import Path


ROOT = Path("/workspaces/yt-factory/packages/slide-gen")
CSV_PATH = Path("/workspaces/yt-factory/packages/scenario-gen/archive/videos/37_LINEMOトライアルキャンペーン2/long/【7月31日まで】LINEMOが実質無料で試せるトライアルキャンペーン2.csv")
OUTPUT_PATH = ROOT / "slides.html"
BRAND = "--brand:#06c755;--brand-deep:#008f3c;--brand-soft:#e3f9ec"


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def load_slide_copy() -> tuple[list[str], dict[str, str]]:
    """Resolve 同上 per CSV row and return first display copy for each slide ID."""
    ids: list[str] = []
    copy: dict[str, str] = {}
    last_copy = ""
    with CSV_PATH.open(encoding="utf-8-sig", newline="") as stream:
        for row in csv.DictReader(stream):
            shown = row["スライドに表示する内容"].strip()
            if shown and shown != "同上":
                last_copy = shown
            slide_id = row["スライドID"].strip()
            if slide_id:
                if slide_id not in ids:
                    ids.append(slide_id)
                copy.setdefault(slide_id, last_copy)
    return ids, copy


def spread(slide_id: str, left: str, right: str, *, price: bool = False, numbered: bool = True) -> str:
    cls = "slide-container price-note" if price else "slide-container"
    page_no = int(re.match(r"\d+", slide_id).group()) * 2
    lno = f'<span class="page-no">― {page_no - 1} ―</span>' if numbered else ""
    rno = f'<span class="page-no">― {page_no} ―</span>' if numbered else ""
    return f'''<!-- Slide ID: {slide_id} -->
<div class="{cls}" style="{BRAND}"><div class="book"><div class="spine"></div>
  <div class="page left">{left}{lno}</div>
  <div class="page right"><span class="index-tab">格安SIM図鑑</span>{right}{rno}</div>
</div></div>'''


def head(title: str, small: str = "") -> str:
    suffix = f"<small>{esc(small)}</small>" if small else ""
    return f'<div class="page-head">{title}{suffix}</div>'


def body(content: str, mode: str = "") -> str:
    return f'<div class="page-body {mode}">{content}</div>'


def emph(label: str, big: str, tail: str = "") -> str:
    return f'<div class="emph">{label}<span class="big">{big}</span>{tail}</div>'


def rows(items: list[tuple[str, str, str]]) -> str:
    lis = "".join(
        f'<li><span class="badge">{badge}</span><div class="tx">{title}<span class="sub">{sub}</span></div></li>'
        for badge, title, sub in items
    )
    return f'<ul class="rows">{lis}</ul>'


def divider(slide_id: str, chapter: str, title: str, lead: str) -> str:
    left = body(f'<div class="divider"><span class="kicker">CHAPTER</span><span class="num">{chapter}</span><span class="seal">FILE No.{int(chapter):02}</span></div>', "center")
    right = body(f'<div class="big-title">{title}</div><div class="lead tight">{lead}</div>', "center")
    return spread(slide_id, left, right, numbered=False)


def std(slide_id: str, kicker: str, title: str, sub: str, image: str) -> str:
    return f'''<!-- Slide ID: {slide_id} -->
<div class="slide-container std"><div class="burst"></div><div class="breaking">{kicker}</div>
  <div class="std-main"><div class="std-copy"><img class="std-logo" src="public/images/logo/LINEMO_logo.png" alt="LINEMO"><div class="std-title">{title}</div><div class="std-sub">{sub}</div></div>
  <img class="std-art" src="{image}" alt=""></div>
</div>'''


def evaluation() -> str:
    cards = [
        ("S", "データ料金", "3GB 990円／30GB 2,970円", "データ繰越なし"),
        ("SS", "通信品質", "お昼も速度が落ちにくい", "特になし"),
        ("C", "初期費用", "今ならキャンペーン対象", "通常3,850円"),
        ("B", "通話料", "5分無料プランあり", "かけ放題は別料金"),
        ("A", "店舗サポート", "店頭スマホサポート", "サポートは有料"),
        ("A", "オプション", "LINEギガフリー", "基本オプションは有料"),
    ]
    def card(c: tuple[str, str, str, str]) -> str:
        rank, name, pro, con = c
        return f'<div class="card"><span class="rank {rank}">{rank}</span><div class="card-name">{name}</div><div class="line pro"><span class="tag">＋</span>{pro}</div><div class="line con"><span class="tag">－</span>{con}</div></div>'
    left = f'<div class="head-left"><img class="logo" src="public/images/logo/LINEMO_logo.png" alt="LINEMO"><div class="total">総合評価 <span class="rank A">A</span></div></div><div class="eval-visual"><img src="public/images/charts/LINEMO.png" alt="LINEMOレーダーチャート"></div><div class="lead tight">通信品質は最高評価の<span class="em">SS</span></div>'
    right = head("LINEMO 独自評価") + f'<div class="cards">{"".join(card(c) for c in cards)}</div><div class="note eval-note">※本評価は当チャンネルの独断と偏見による独自評価であり、キャンペーン割引等は考慮していません</div>'
    return spread("13-1", left, right, price=True)


def build_slides() -> dict[str, str]:
    thumb_lock = "public/images/thumbnails/【2026年7月】ソフトバンク・ワイモバイル・LINEMOに1年縛り復活！気軽に試せる格安SIM3選_サムネ1.png"
    thumb_linemo = "public/images/thumbnails/LINE使い放題で月990円！LINEMO(ラインモ)のメリット・デメリットを徹底解説【ahamo・povo・楽天モバイル比較】.png"
    slides: dict[str, str] = {}
    slides["1"] = std("1", "7月31日まで", '初期費用も<br><span>2ヶ月分の月額も<br>まるっと0円!?</span>', "LINEMOトライアルキャンペーン2｜さらに解約金まで無料", "public/images/irasutoya/business_man2_3_surprise.png")
    slides["2"] = std("2", "完全ノーリスク級", 'LINEMOを<span>実質無料</span>で試す', "トライアルキャンペーン2を徹底解説", "public/images/irasutoya/present_open.png")
    slides["3"] = spread("3", head("格安SIM図鑑 もくじ") + body('<ol class="agenda agenda-fill"><li><span class="num">1</span>特典とお得額</li><li><span class="num">2</span>完全ノーリスクの理由</li><li><span class="num">3</span>LINEMOをおさらい</li><li><span class="num">4</span>対象者と申込方法</li><li><span class="num">5</span>まとめ</li></ol>'), head("この動画でわかること") + body('<ul class="benefits benefits-fill"><li><span class="check">✓</span>3つの無料特典を<br>正確に理解</li><li><span class="check">✓</span>自分が対象か<br>すぐ分かる</li><li><span class="check">✓</span>申し込み手順と<br>注意点が分かる</li></ul>'))
    slides["4"] = spread("4", head("先に結論") + body(emph("初期費用・月額・解約金", "3つとも0円", "ベストプランなら") + '<div class="lead tight">合わなくても<span class="em">2ヶ月以内なら<br>費用をかけずに撤退</span></div>', "center"), head("初心者にこそチャンス") + body(rows([("1", "初期費用", "契約事務手数料が無料"), ("2", "2ヶ月分の月額", "ベストプランなら無料"), ("3", "期間中の解約金", "合わなくても撤退しやすい")])))
    slides["5-0"] = divider("5-0", "1", "キャンペーンの<br><span class=\"nowrap\">中身は？</span>", "何が・いくらお得になるかを整理")
    slides["5-1"] = spread("5-1", head("LINEMOトライアル<br>キャンペーン2") + body(emph("2026年・期間限定", "7/1〜7/31", "この1ヶ月に申し込み") + '<div class="lead tight">申込月の<span class="em">翌月末までに開通</span></div>', "center"), head("対象プランと開通期限") + body(rows([("A", "LINEMOベストプラン", "期間中に申し込み"), ("B", "LINEMOベストプランV", "期間中に申し込み"), ("✓", "共通の開通期限", "申込月の翌月末まで")])), price=True)
    slides["6"] = spread("6", head("特典3点セット") + body(rows([("1", "契約事務手数料", "3,850円 → 無料"), ("2", "月額基本料", "2,090円×2ヶ月 → 無料"), ("3", "解除料など", "割引期間中は無料")])) , head("割引対象期間") + body(rows([("START", "開通した月", "ここから割引スタート"), ("1", "1ヶ月目", "月額基本料が無料"), ("2", "2ヶ月目", "月額＋期間中の解除料も無料")])) , price=True)
    slides["7"] = spread("7", head("ベストプランVの場合") + body(emph("通常月額", "2,970円", "30GB＋5分通話定額") + '<div class="lead tight">大容量プランも<span class="em">割引対象</span></div><div class="note support-note">30GBと5分以内の国内通話定額はそのまま利用できます</div>', "center"), head("割引後の月額") + body(emph("2,970円 − 2,090円", "880円", "2ヶ月間") + '<div class="lead tight">2ヶ月合計でも<span class="em">1,760円</span></div><div class="warn support-warn"><span class="ic"><i class="fa-solid fa-circle-info"></i></span>無料ではなく、月額基本料から<br><span class="em">毎月2,090円を割引</span></div>', "center"), price=True)
    slides["8"] = spread("8", head("今回いちばんのポイント") + body('<div class="bigicon"><i class="fa-solid fa-door-open"></i></div><div class="lead">合わなければ<span class="em">2ヶ月以内に解約</span></div>', "center"), head("解除料も無料対象") + body(emph("初期費用＋月額＋解約金", "すべて0円", "ベストプランの場合"), "center"), price=True)
    slides["9-0"] = divider("9-0", "2", "なぜ<br><span class=\"nowrap\">完全ノーリスク？</span>", "途中でやめる費用まで確認")
    slides["9"] = spread("9", head("契約解除料 <small>2026年7月〜</small>") + body('<div class="bigicon mini"><i class="fa-solid fa-calendar-xmark"></i></div><div class="warn warn-large"><span class="ic"><i class="fa-solid fa-triangle-exclamation"></i></span>回線開通から<br><span class="em">12ヶ月以内</span>の解約で発生</div>', "center"), head("プラン別の解除料") + body('<table class="sheet sheet-large"><tr><th>プラン</th><th>解除料</th></tr><tr><td>ベストプラン</td><td class="em">990円</td></tr><tr><td>ベストプランV</td><td class="em">1,100円</td></tr></table><div class="lead tight">いわゆる<span class="em">「1年縛り復活」</span>の仕組み</div>'), price=True)
    slides["9-2"] = spread("9-2", head("過去動画もチェック") + body(f'<div class="visual"><img src="{thumb_lock}" alt="1年縛り復活の解説動画"></div>', "center"), head("解除料なしで試せる<br>格安SIMも紹介") + body('<div class="bigicon"><i class="fa-solid fa-circle-play"></i></div><div class="lead tight">ソフトバンク・ワイモバイル・LINEMOの<span class="em">1年縛り</span>を詳しく解説</div>', "center"), numbered=False)
    slides["10"] = spread("10", head("今回のキャンペーンなら") + body(emph("開通から2ヶ月以内", "解約金0円", "の対象") + '<div class="lead tight">実際に使ってから<br><span class="em">続けるか決められる</span></div>', "center"), head("だから試しやすい") + body(rows([("0", "初期費用", "0円"), ("0", "2ヶ月分の月額", "0円"), ("0", "契約解除料", "0円")])) , price=True)
    slides["11"] = spread("11", head("期間限定です") + body('<div class="bigicon mini"><i class="fa-solid fa-hourglass-half"></i></div><div class="emph"><span class="big">7月31日まで</span></div><div class="lead tight">詳しい適用条件は<br><span class="em">次の章で確認</span></div>', "center"), head("適用条件を必ず確認") + body('<div class="warn warn-large"><span class="ic"><i class="fa-solid fa-triangle-exclamation"></i></span>内容は予告なく<br>変更・終了する場合があります</div><div class="lead tight">申し込み直前に<br><span class="em">公式の最新情報</span>をチェック</div>', "center"), numbered=False)
    slides["12"] = spread("12", head("速報を見逃さない") + body('<div class="bigicon mini"><i class="fa-solid fa-bell"></i></div><div class="big-title compact">チャンネル登録で<br>見逃さない！</div>', "center"), head("最新情報をいち早く") + body('<div class="lead lead-large">キャンペーンの<br><span class="em">変更・終了情報</span>も<br>すばやくお届け</div><div class="subscribe-pill"><i class="fa-brands fa-youtube"></i> 登録して待つ</div>', "center"), numbered=False)
    slides["13-0"] = divider("13-0", "3", "LINEMOって<br><span class=\"nowrap\">どんな格安SIM？</span>", "独自評価で特徴をおさらい")
    slides["13-1"] = evaluation()
    slides["13-2"] = spread("13-2", head("LINEMO 詳細解説") + body(f'<div class="visual"><img src="{thumb_linemo}" alt="LINEMO詳細解説動画"></div>', "center"), head('<span class="nowrap head-nowrap">メリット・デメリットも</span>') + body('<div class="bigicon"><i class="fa-solid fa-circle-play"></i></div><div class="lead tight">LINEギガフリーや他社比較まで詳しく解説</div>', "center"), numbered=False)
    slides["14-0"] = divider("14-0", "4", "自分は<br>対象になる？", "3パターンの申し込み方法を確認")
    slides["14"] = spread("14", head("対象になる3パターン") + body(rows([("1", "新規契約", "新しい番号で申し込み"), ("2", "ソフトバンク系から乗り換え", "ソフトバンク・ワイモバイル"), ("3", "LINEMO内でプラン変更", "旧プランからベストプラン系へ")])) , head("自分のルートを選ぶ") + body('<div class="bigicon mini"><i class="fa-solid fa-route"></i></div><ul class="route-list"><li>新しい番号で契約</li><li>ソフトバンク系から乗り換え</li><li>LINEMO内でプラン変更</li></ul><div class="lead tight">ルートごとに<span class="em">入口が違う</span>ので注意</div>', "center"))
    slides["15"] = spread("15", head("① 新規契約") + body(rows([("1", "専用申込URLへ", "キャンペーンページから進む"), ("2", "対象プランを申し込む", "7月31日まで"), ("3", "翌月末までに開通", "期限を過ぎない")])) , head("最重要ポイント") + body(emph("必ず", "専用URL", "経由で申し込む"), "center"))
    slides["16"] = spread("16", head("② ソフトバンク系から<br>LINEMOへ乗り換え") + body(rows([("1", "先にエントリー", "専用フォームを利用"), ("2", "届いた専用URLへ", "メールを確認"), ("3", "対象プラン申込・開通", "翌月末まで")]), "compact-rows") , head("順番を守る") + body('<div class="flow"><b>エントリー</b><i class="fa-solid fa-arrow-right"></i><b>専用URL</b><i class="fa-solid fa-arrow-right"></i><b>申込</b></div><div class="warn">先に通常ページから申し込まない</div>', "center"))
    slides["17"] = spread("17", head("③ LINEMO既存ユーザー") + body(rows([("1", "専用フォームでエントリー", "スマホ／ミニプラン利用者"), ("2", "対象プランへ変更申込", "ベストプラン系へ")]) + '<div class="warn support-warn"><span class="ic"><i class="fa-solid fa-user-lock"></i></span><span class="em">SoftBank IDでログイン</span><br><span class="warn-sub">プラン変更する回線の電話番号でログインしてください</span></div>') , head("同月内に両方完了") + body(emph("エントリー＋変更申込", "同じ月", "に完了"), "center"))
    slides["18"] = spread("18", head("申し込み前の注意点") + body(rows([("!", "オンライン専用", "実店舗サポートは基本なし"), ("!", "通話定額は別途加入", "必要な人だけ追加"), ("!", "21時以降の変更申込", "翌日受付になる場合あり")])) , head("最後に公式で確認") + body(rows([("!", "他特典と併用不可の場合", "適用条件を確認"), ("!", "内容変更の可能性", "申込直前に最新情報を見る")])) )
    slides["19-0"] = divider("19-0", "5", "まとめ", "重要ポイントを最後におさらい")
    slides["20"] = spread("20", head("今日のまとめ <small>①②</small>") + body(rows([("1", "7月31日まで", "事務手数料3,850円＋2ヶ月分月額が無料"), ("2", "期間中の解除料も無料", "2ヶ月以内なら実質ノーリスクで試せる")]), "summary-fill") , head("今日のまとめ <small>③④</small>") + body(rows([("3", "対象は3パターン", "新規・ソフトバンク系・プラン変更"), ("4", "通信品質はSS評価", "初心者でも安心できる品質")]) + '<div class="lead tight">まず使ってから<br><span class="em">続けるか判断できる</span></div>', "summary-fill") , price=True)
    slides["21"] = spread("21", head("LINEMOに申し込む") + body('<div class="bigicon"><i class="fa-solid fa-arrow-pointer"></i></div><div class="big-title compact">概要欄リンクへ</div>', "center"), head("ブログも確認") + body('<img class="blog-banner" src="public/images/common/ブログ_ヘッダー画像_スライド用.png" alt="ブログ"><div class="lead tight">条件を整理してから申し込み</div>', "center"), numbered=False)
    slides["22"] = spread("22", head("コメントで教えてね！") + body('<div class="bigicon"><i class="fa-solid fa-comments"></i></div><div class="big-title compact">あなたはどう思う？</div>', "center"), head("コメント例") + body(rows([("💬", "LINEMO気になってました", ""), ("💬", "このキャンペーンで試します", ""), ("💬", "解約金まで無料とは！", "")])) , numbered=False)
    slides["23"] = spread("23", head("ご注意") + body('<div class="bigicon"><i class="fa-solid fa-circle-info"></i></div><div class="big-title caution-copy">必ず公式情報を<br>ご確認ください</div>', "center"), head("投稿時点の情報です") + body('<div class="warn">料金・プラン・キャンペーンは変更される場合があります</div><div class="lead tight">お申し込み前に<span class="em">公式サイトの最新情報</span>をご確認ください</div>', "center"), numbered=False)
    slides["24"] = spread("24", head("ブログ・noteも更新中") + body('<div class="bigicon"><i class="fa-solid fa-pen-nib"></i></div><div class="big-title compact">詳しい記事も！</div>', "center"), head("概要欄からチェック") + body('<img class="blog-banner" src="public/images/common/ブログ_ヘッダー画像_スライド用.png" alt="ブログ"><div class="lead tight">格安SIM選びをもっと詳しく解説</div>', "center"), numbered=False)
    slides["25"] = spread("25", head("チャンネル登録") + body('<div class="bigicon"><i class="fa-solid fa-bell"></i></div><div class="big-title compact">よろしく<br>お願いします！</div>', "center"), head("ご視聴<br><span class=\"nowrap\">ありがとうございました！</span>") + body('<div class="reaction-icons">👍 🔔</div><div class="lead">高評価も動画制作の励みになります</div><div class="note">次回も一緒にスマホ代を節約しましょう！</div>', "center"), numbered=False)
    return slides


def main() -> None:
    ids, csv_copy = load_slide_copy()
    slides = build_slides()
    missing = [slide_id for slide_id in ids if slide_id not in slides]
    extra = [slide_id for slide_id in slides if slide_id not in ids]
    if missing or extra:
        raise SystemExit(f"slide mapping mismatch: missing={missing}, extra={extra}")
    # Verify every mapped slide originates in a non-empty CSV display instruction chain.
    if any(not csv_copy.get(slide_id) for slide_id in ids):
        raise SystemExit("one or more slide IDs have no resolved display copy")
    css = '''
<style>
body{--primary-color:#06c755;--accent-red:#e53935;--text-dark:#202124}
.slide-container.std{width:1280px;height:720px;border:10px solid var(--primary-color);background:#fff;position:relative;overflow:hidden;display:flex;align-items:center;justify-content:center;padding:42px}
.std .burst{position:absolute;inset:-35%;background:repeating-conic-gradient(from -10deg,rgba(6,199,85,.12) 0 8deg,transparent 8deg 17deg);animation:none}
.breaking{position:absolute;z-index:2;top:28px;left:28px;background:#e53935;color:#fff;font-size:34px;font-weight:900;padding:10px 28px;transform:rotate(-4deg);box-shadow:0 8px 0 #9f1717}
.std-main{position:relative;z-index:1;width:100%;height:100%;display:grid;grid-template-columns:2.2fr 1fr;align-items:center;gap:30px}.std-copy{display:flex;flex-direction:column;gap:20px;align-items:flex-start}.std-logo{width:310px;max-height:90px;object-fit:contain;background:#fff;padding:12px 22px;border-radius:18px;box-shadow:0 8px 24px #0002}.std-title{font-size:72px;line-height:1.2;font-weight:900;color:#202124;text-shadow:0 4px #fff}.std-title span{color:#e53935;font-size:92px}.std-sub{font-size:40px;font-weight:900;background:#fff;border-left:14px solid #06c755;padding:18px 25px;box-shadow:0 8px 24px #0002}.std-art{width:100%;max-height:430px;object-fit:contain;filter:drop-shadow(0 16px 10px #0003)}
.big-title.compact{font-size:72px}.subscribe-pill{font-size:54px;font-weight:900;color:#fff;background:#e62117;padding:22px 42px;border-radius:999px;box-shadow:0 8px 0 #a71610}.flow{display:flex;align-items:center;justify-content:center;gap:22px;font-size:34px}.flow b{background:var(--brand-soft);border:4px solid var(--brand);border-radius:18px;padding:24px 20px}.blog-banner{width:100%;height:auto;max-height:320px;object-fit:contain;border-radius:18px;box-shadow:0 10px 24px #0003}.reaction-icons{font-size:110px;letter-spacing:30px}.eval-visual{height:390px;display:flex;justify-content:center}.eval-visual img{height:100%;max-width:100%;object-fit:contain}.eval-note{font-size:22px!important;text-align:center;margin-top:8px}.right .cards{display:grid!important;grid-template-columns:repeat(2,minmax(0,1fr))!important;grid-template-rows:repeat(3,minmax(0,1fr));gap:10px!important;min-height:0}.right .card{min-height:0!important;padding:10px!important;grid-template-columns:64px 1fr!important;column-gap:12px!important}.right .card .rank{width:60px!important;height:60px!important;font-size:30px!important;border-radius:12px!important}.right .card-name{font-size:25px!important}.right .card .line{font-size:18px!important}.head-left .logo{max-width:330px!important;max-height:82px!important}.head-left{margin-bottom:12px!important}
.nowrap{white-space:nowrap;font-size:.92em}.bigicon.mini{font-size:170px}.warn-large{font-size:48px;line-height:1.45;padding:34px}.sheet-large{font-size:52px}.sheet-large th,.sheet-large td{padding:28px 18px}.lead-large{font-size:58px!important;line-height:1.5!important}.agenda-fill li{font-size:60px}.benefits-fill li{font-size:60px}.route-list{list-style:none;width:100%;display:flex;flex-direction:column;gap:14px;margin:0;padding:0}.route-list li{font-size:35px;font-weight:800;padding:15px 20px;background:#fff;border-left:10px solid var(--brand);border-radius:12px;box-shadow:0 5px 14px #0002}.summary-fill .rows li{padding:30px 22px}.summary-fill .rows .tx{font-size:51px}.summary-fill .rows .tx .sub{font-size:36px}.compact-rows .rows{gap:10px}.compact-rows .rows li{padding:15px 18px}.compact-rows .rows .tx{font-size:43px}.compact-rows .rows .tx .sub{font-size:30px}.std-title{font-size:68px}.std-title span{font-size:78px;line-height:1.12}.std-sub{font-size:31px}
.head-nowrap{font-size:.82em}.support-note{font-size:30px!important;text-align:center;line-height:1.5}.support-warn{font-size:34px!important;line-height:1.35!important;padding:22px!important;text-align:center}.warn-sub{font-size:29px}.caution-copy{font-size:58px!important;line-height:1.35!important}
</style>'''
    document = f'''<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>LINEMOトライアルキャンペーン2</title><link href="https://fonts.googleapis.com/css2?family=M+PLUS+Rounded+1c:wght@400;500;700;800;900&display=swap" rel="stylesheet"><link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css"><link rel="stylesheet" href="templates/spread-base.css">{css}</head><body>{''.join(slides[slide_id] for slide_id in ids)}</body></html>'''
    OUTPUT_PATH.write_text(document, encoding="utf-8")
    print(f"generated {len(ids)} slides -> {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
