#!/usr/bin/env python3
"""Generate slides-short.html from the scenario CSV for video 36."""

from __future__ import annotations

import csv
import html
import re
from collections import OrderedDict
from pathlib import Path


ROOT = Path("/workspaces/yt-factory/packages/slide-gen")
CSV_PATH = Path("/workspaces/yt-factory/packages/scenario-gen/archive/videos/36_【2026年最新】povo実質月484円プランの全容と3つの注意点/short/【月484円】povo新トッピング安さの仕組み.csv")
LONG_DIR = CSV_PATH.parent.parent / "long"
OUTPUT = ROOT / "slides-short.html"
IMAGES = ROOT / "public/images"


def rel_asset(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(f"Required asset not found: {path}")
    return path.relative_to(ROOT).as_posix()


def load_slides() -> OrderedDict[str, str]:
    slides: OrderedDict[str, str] = OrderedDict()
    with CSV_PATH.open(encoding="utf-8-sig", newline="") as source:
        for row in csv.DictReader(source):
            slide_id = row["スライドID"].strip()
            content = row["スライドに表示する内容"].strip()
            if not slide_id or slide_id.endswith("-0"):
                continue
            if content != "同上":
                if slide_id in slides and slides[slide_id] != content:
                    raise ValueError(f"Slide ID {slide_id} has conflicting display content")
                slides[slide_id] = content
    expected = [str(i) for i in range(1, 7)]
    if list(slides) != expected:
        raise ValueError(f"Expected slide IDs {expected}, got {list(slides)}")
    return slides


def display_text(raw: str) -> str:
    return re.sub(r"^(?:タイトル|テロップ)：", "", raw).strip()


def thumbnail_asset() -> Path:
    long_csvs = sorted(LONG_DIR.glob("*.csv"))
    if len(long_csvs) != 1:
        raise ValueError(f"Expected one long-form CSV in {LONG_DIR}, got {len(long_csvs)}")
    exact = IMAGES / "thumbnails" / f"{long_csvs[0].stem}_サムネ1.png"
    if exact.is_file():
        return exact
    numbered = IMAGES / "thumbnails" / f"{CSV_PATH.parent.parent.name.split('_', 1)[0]}_{long_csvs[0].stem}_サムネ1.png"
    if numbered.is_file():
        return numbered
    return IMAGES / "slides/今すぐ本編動画をチェック.png"


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def frame(
    slide_id: str,
    left: str,
    right: str,
    *,
    classes: str = "",
    show_index: bool = True,
) -> str:
    index = '<div class="index-tab">povo 2.0</div>' if show_index else ""
    return f'''<!-- スライドID: {slide_id} -->
<div class="slide-container {classes}" data-slide-id="{slide_id}" style="--brand:#5b2cff;--brand-deep:#35149c;--brand-soft:#eee9ff">
  <div class="book"><div class="spine"></div>
    <section class="page left">{left}<span class="page-no">{slide_id}</span></section>
    <section class="page right">{right}<span class="page-no">{slide_id}</span></section>
    {index}
  </div>
</div>'''


def render(slides: OrderedDict[str, str]) -> str:
    logo = rel_asset(IMAGES / "logo/Povo_logo.png")
    money = rel_asset(IMAGES / "irasutoya/osatsu_money_yamadumi.png")
    shock = rel_asset(IMAGES / "irasutoya/bikkuri_me_tobideru_man.png")
    subline = rel_asset(IMAGES / "common/複数回線を組み合わせるイメージ図.png")
    savings = rel_asset(IMAGES / "common/スマホ代見直しの節約効果を示すイラスト.png")
    warning = rel_asset(IMAGES / "irasutoya/seikyuusyo_shock.png")
    banner = rel_asset(thumbnail_asset())
    text = {sid: display_text(raw) for sid, raw in slides.items()}

    title, question = [part.strip() for part in text["1"].split("／", 1)]
    calc_match = re.fullmatch(r"12GB\(365日\)5,800円÷12ヶ月＝実質月約484円", text["3"])
    if not calc_match:
        raise ValueError(f"Unexpected calculation text: {text['3']}")
    target_title, target_detail = [part.strip() for part in text["4"].split("／", 1)]
    target_a, target_b = [part.strip() for part in target_detail.split("・", 1)]

    docs = []
    docs.append(frame("1", f'''
      <div class="thumb-top-strip">⚡ 2026年最新 povo新トッピング ⚡</div>
      <div class="thumb-tag">実質 月484円</div>
      <h1 class="big-title thumb-title"><span class="em">povo</span><br>年間プラン</h1>
      <div class="price-punch"><small>月額換算</small><strong>484<em>円</em></strong></div>''', f'''
      <div class="page-body center thumb-right">
        <img class="brand-logo" src="{logo}" alt="povo">
        <div class="question-card">{esc(question)}</div>
        <img class="hero-illust" src="{money}" alt="積み上がったお札">
      </div>''', classes="slide-thumbnail", show_index=False))

    docs.append(frame("2", f'''
      <div class="file-no">CHECK 01</div>
      <h2 class="page-head">安いだけで選ぶ？</h2>
      <div class="page-body choice-left"><div class="bigicon">↔</div><div class="lead choice-lead">安さだけでは<br><span class="em">決められない</span></div><div class="choice-note">使い方との相性をチェック</div></div>''', f'''
      <h2 class="page-head phrase-break">相性が<br>すべて</h2>
      <div class="page-body center">
        <div class="split-verdict"><span class="yes">向いてる人</span><span class="no">向いてない人</span></div>
        <img class="corner-illust" src="{shock}" alt="驚く人">
      </div>'''))

    docs.append(frame("3", f'''
      <div class="file-no">PRICE FILE</div><h2 class="page-head">1年分をまとめ買い</h2>
      <div class="page-body center price-left"><div class="data-chip">12GB</div><div class="period">365日 有効</div><div class="price">5,800円</div><img class="price-illust" src="{savings}" alt="スマホ代を節約するイメージ"></div>''', f'''
      <h2 class="page-head phrase-break">月額に<br>直すと…</h2><div class="page-body center calc-body">
        <div class="formula"><b>5,800円</b><span>÷ 12ヶ月</span></div>
        <div class="equals">＝</div><div class="monthly"><small>実質 月約</small><strong>484<em>円</em></strong></div>
        <div class="note">12GB（365日）トッピング</div>
      </div>'''))

    docs.append(frame("4", f'''
      <div class="file-no">BEST MATCH</div><h2 class="page-head target-head">{esc(target_title)}</h2>
      <div class="page-body target-left">
        <div class="lead target-lead"><span class="em">{esc(target_a)}</span></div>
        <div class="usage-meter"><span class="meter-label">月のデータ量</span><strong>約1GB</strong><div class="meter-track"><i></i></div><small>外であまり使わない人に◎</small></div>
      </div>''', f'''
      <h2 class="page-head">au回線で安定</h2><div class="page-body center">
        <ul class="rows"><li><span class="ic">📶</span><span class="tx">{esc(target_b)}</span></li><li><span class="ic">📱</span><span class="tx">予備・2台目にも</span></li></ul>
        <img class="wide-illust" src="{subline}" alt="複数回線のイメージ">
      </div>'''))

    docs.append(frame("5", f'''
      <div class="warning-banner">⚠ ちょっと待って！</div><div class="page-body center"><div class="warning-mark">!</div><h2 class="warning-title">買う前に<br>知っておくこと</h2></div>''', f'''
      <h2 class="page-head danger phrase-break"><span>トッピングは</span><br><span>入れ替わる</span></h2><div class="page-body center">
        <div class="warn strong">あとで<span class="em">もっとお得</span>な<br>トッピングが出る可能性も</div>
        <div class="decision">今すぐ必要？<br><b>慎重に判断</b></div>
        <img class="corner-illust" src="{warning}" alt="請求に驚く人">
      </div>''', classes="warning-slide"))

    docs.append(frame("6", f'''
      <div class="cta-logo-wrap"><img class="cta-logo" src="{logo}" alt="povo"></div><div class="page-body center cta-copy"><div class="cta-kicker">あなたはどっち？</div><h2>向いてる人<br><span>向いてない人</span></h2><p>詳しい条件は本編で！</p><div class="arrow">→</div></div>''', f'''
      <div class="page-body center"><div class="banner-card"><img class="cta-banner-img" src="{banner}" alt="長尺動画のサムネイル"></div><div class="watch-now">今すぐ本編をチェック</div><div class="bounce-arrow">↓</div></div>''', classes="cta-slide", show_index=False))

    return f'''<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>povo 実質月484円プラン - Shorts Slides</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@700;900&family=M+PLUS+Rounded+1c:wght@700;800;900&family=Noto+Sans+JP:wght@700;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="templates/spread-base.css">
<style>
body{{background:#20202b;gap:48px;padding:48px}} .slide-container{{width:1080px;height:1080px}}
.book{{width:1030px;height:1030px}} .page{{padding:34px 38px 92px;width:50%}} .page-head{{font-size:45px;border-bottom-width:7px;margin-bottom:18px;padding-bottom:12px}}
.page-body{{gap:18px}} .index-tab{{font-size:22px;right:36px}} .file-no{{font-size:20px;padding:5px 15px}} .page-no{{bottom:15px;font-size:20px}}
.lead{{font-size:43px;padding:26px 26px}} .note{{font-size:27px}} .emph{{font-size:36px;padding:25px}} .emph.compact{{font-size:31px}}
.rows{{gap:15px}} .rows li{{padding:18px 20px;gap:13px}} .rows .ic{{font-size:40px;width:48px}} .rows .tx{{font-size:35px}}
img{{object-fit:contain;filter:drop-shadow(0 9px 16px rgba(0,0,0,.14))}}
.slide-thumbnail{{background:repeating-conic-gradient(from 0deg at 52% 48%,rgba(91,44,255,.09) 0deg 2.5deg,transparent 2.5deg 16deg),radial-gradient(ellipse at 52% 48%,#fff 5%,#eee9ff 48%,#cfc2ff 100%);border:25px solid #5b2cff}}
.slide-thumbnail .book{{height:930px;margin-top:50px}} .slide-thumbnail .page{{overflow:visible}} .thumb-top-strip{{position:absolute;top:-50px;left:0;width:980px;background:#5b2cff;color:#fff;font-size:27px;font-weight:900;padding:15px 0;text-align:center;letter-spacing:.04em;z-index:20}}
.thumb-tag{{background:#e63946;color:#fff;font-size:45px;font-weight:900;padding:14px 20px;transform:rotate(-3deg);box-shadow:7px 7px 0 rgba(0,0,0,.23);margin-top:90px;text-align:center;z-index:2}}
.thumb-title{{font-size:82px;text-align:left;margin-top:30px;line-height:1.12}} .price-punch{{margin-top:32px;background:#fff4f5;border:6px solid #e63946;border-radius:20px;padding:14px 18px;text-align:center;box-shadow:6px 7px 0 rgba(176,0,30,.18)}} .price-punch small{{display:block;font-size:24px;font-weight:900;color:#35149c}} .price-punch strong{{display:block;font-size:67px;line-height:1;color:#e63946}} .price-punch em{{font-size:35px;font-style:normal}} .thumb-right{{padding-top:52px;justify-content:flex-start}} .brand-logo{{width:320px;height:105px}} .question-card{{font-size:42px;font-weight:900;line-height:1.35;text-align:center;background:#5b2cff;color:#fff;padding:24px 18px;border-radius:18px;box-shadow:6px 7px 0 #35149c}}
.hero-illust{{height:265px;width:330px;margin-top:26px}} .choice-left{{justify-content:flex-start;align-items:center;gap:22px;padding-top:22px}} .bigicon{{font-size:210px;line-height:.9}} .choice-lead{{width:100%;font-size:47px;text-align:center;padding:28px 20px}} .choice-note{{width:100%;background:#fff;border:4px solid #ddd3ff;border-radius:15px;padding:17px 12px;text-align:center;font-size:26px;font-weight:900;color:#35149c}} .split-verdict{{display:flex;flex-direction:column;gap:28px;width:100%;font-size:43px;font-weight:900;text-align:center;margin-bottom:210px}} .split-verdict span{{padding:27px 10px;border-radius:16px}} .yes{{background:#e8f8ee;color:#168447;border:5px solid #26a65b}} .no{{background:#fff0f1;color:#c52235;border:5px solid #e63946}}
.corner-illust{{position:absolute;right:22px;bottom:55px;height:205px;z-index:2}} .phrase-break{{line-height:1.15}} .phrase-break span{{white-space:nowrap}} .danger{{font-size:35px}} .data-chip{{font-size:80px;font-weight:900;color:#5b2cff}} .period{{font-size:38px;font-weight:900;background:#eee9ff;border-radius:99px;padding:12px 24px}} .price{{font-size:66px;font-weight:900;color:#e63946}} .price-left{{justify-content:flex-start;padding-top:20px;gap:14px}} .price-illust{{height:210px;width:290px;margin-top:8px}}
.calc-body{{text-align:center}} .formula{{display:flex;flex-direction:column;gap:8px;font-size:40px}} .formula b{{font-size:58px;color:#35149c}} .equals{{font-size:50px;font-weight:900}} .monthly{{border:6px solid #e63946;border-radius:20px;padding:18px;background:#fff4f5}} .monthly small{{display:block;font-size:30px;font-weight:900}} .monthly strong{{display:block;font-size:83px;line-height:1;color:#e63946}} .monthly em{{font-size:42px;font-style:normal}}
.target-head{{font-size:42px}} .target-left{{justify-content:flex-start;gap:25px;padding-top:20px}} .target-lead{{font-size:47px;text-align:center;padding:27px 18px}} .usage-meter{{background:#fff;border:4px solid #ddd3ff;border-radius:20px;padding:22px 24px;text-align:center;box-shadow:0 7px 15px rgba(53,20,156,.1)}} .meter-label{{display:block;font-size:25px;font-weight:800;color:#6b6b5e}} .usage-meter strong{{display:block;font-size:60px;line-height:1.2;color:#e63946}} .meter-track{{height:18px;background:#e5e0ef;border-radius:99px;overflow:hidden;margin:10px 0}} .meter-track i{{display:block;width:24%;height:100%;background:linear-gradient(90deg,#5b2cff,#8b6cff);border-radius:99px}} .usage-meter small{{font-size:23px;font-weight:800;color:#6b6b5e}} .sub-badge{{align-self:center;background:#5b2cff;color:#fff;border-radius:99px;padding:13px 30px;font-size:30px;font-weight:900;box-shadow:0 6px 0 #35149c}} .wide-illust{{height:190px;width:100%;margin-top:4px}} .warning-slide{{--brand:#e63946;--brand-deep:#b0001e;--brand-soft:#fff0f0}} .warning-slide .page{{background:linear-gradient(180deg,#fffafa,#fff0f0)}} .warning-banner{{background:#e63946;color:#fff;font-size:35px;font-weight:900;text-align:center;padding:18px;margin:-34px -38px 0}} .warning-mark{{font-size:150px;font-weight:900;color:#fff;background:#e63946;border-radius:50%;width:190px;height:190px;display:flex;align-items:center;justify-content:center;box-shadow:0 9px 0 #b0001e}} .warning-title{{font-size:46px;text-align:center;color:#b0001e}} .danger{{color:#b0001e;border-color:#e63946}} .warn.strong{{font-size:35px;border:7px solid #e63946;background:#fff0f0;padding:26px 20px}} .decision{{font-size:30px;font-weight:800;text-align:center;margin-right:145px}} .decision b{{font-size:39px;color:#e63946}}
.cta-slide{{--brand:#5b2cff;--brand-deep:#ffd400;background:linear-gradient(135deg,#5b2cff,#220b68)}} .cta-slide .book{{background:linear-gradient(135deg,#5b2cff,#220b68)}} .cta-slide .page{{background:linear-gradient(155deg,#5124e6,#250b78);color:#fff}} .cta-logo-wrap{{align-self:flex-start;margin:12px 0 0 12px;background:#fff;border-radius:18px;padding:9px 15px;box-shadow:4px 5px 0 rgba(0,0,0,.18);line-height:0}} .cta-logo{{height:82px;width:270px;filter:none}} .cta-copy{{text-align:center}} .cta-kicker{{font-size:31px;font-weight:900;color:#ffd400}} .cta-copy h2{{font-size:51px;line-height:1.25}} .cta-copy h2 span{{color:#ffd400}} .cta-copy p{{font-size:29px;font-weight:900}} .arrow{{font-size:72px;color:#ffd400;animation:bounceX 1s infinite}} .banner-card{{background:#fff;padding:12px;border-radius:16px;box-shadow:0 12px 25px rgba(0,0,0,.32)}} .cta-banner-img{{width:405px;max-height:400px;display:block;filter:none}} .watch-now{{font-size:29px;font-weight:900;color:#ffd400;text-align:center}} .bounce-arrow{{font-size:60px;color:#ffd400;text-align:center;animation:bounce 1s infinite}} @keyframes bounce{{50%{{transform:translateY(12px)}}}} @keyframes bounceX{{50%{{transform:translateX(12px)}}}}
</style></head><body>{''.join(docs)}</body></html>'''


def main() -> None:
    slides = load_slides()
    OUTPUT.write_text(render(slides), encoding="utf-8")
    print(f"Generated {len(slides)} slides: {OUTPUT}")
    print("Slide IDs:", ", ".join(slides))


if __name__ == "__main__":
    main()
