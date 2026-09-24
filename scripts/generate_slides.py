#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_slides.py

台本 CSV からスライド用 HTML (slides.html) を生成するジェネレータ。
デザイン・レイアウト規則（spread-base.css）に準拠し、CSS 部品へ台本内容を流し込む。
"""

import os
import re
import csv
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SLIDE_GEN_DIR = os.path.dirname(SCRIPT_DIR)
OUTPUT_HTML_PATH = os.path.join(SLIDE_GEN_DIR, "slides.html")

DEFAULT_CSV_PATH = "/workspaces/yt-factory/packages/scenario-gen/archive/videos/48_【決定版】mineoのプラン選びは3択でいい。歴8年が教える実質使い放題の選び方/long/【決定版】mineoのプラン選びは3択でいい。歴8年が教える実質使い放題の選び方.csv"

def build_head():
    return """<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <link href="https://fonts.googleapis.com/css2?family=M+PLUS+Rounded+1c:wght@400;500;700;800;900&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
  <link rel="stylesheet" href="templates/spread-base.css">
  <style>
    /* std (導入スライド 1280x720) スタイル */
    .slide-container.std {
      width: 1280px;
      height: 720px;
      border: 10px solid var(--primary-color, #C8102E);
      background: #ffffff;
      box-sizing: border-box;
      position: relative;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      padding: 40px;
      flex-shrink: 0;
    }
    .sunburst {
      position: absolute;
      inset: 0;
      background: repeating-conic-gradient(from 0deg at 50% 45%, rgba(200, 16, 46, 0.05) 0deg 5deg, transparent 5deg 10deg);
      pointer-events: none;
      z-index: 0;
    }
    .cover-badge {
      display: inline-block;
      background: var(--primary-color, #C8102E);
      color: #fff;
      font-weight: 900;
      font-size: 44px;
      padding: 8px 28px;
      border-radius: 8px;
      transform: rotate(-2deg);
      box-shadow: 0 8px 16px rgba(0,0,0,0.2);
    }
    .std-copy {
      position: relative;
      z-index: 1;
      width: 100%;
      text-align: center;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 20px;
    }
    .title-main {
      font-size: 78px;
      font-weight: 900;
      color: #212121;
      line-height: 1.25;
      text-shadow: 3px 3px 0 #fff;
      word-break: auto-phrase;
      text-wrap: balance;
    }

    /* 文字入りバッジ（YES/OFF/期間 など）は78px角に収まるサイズへ */
    .rows .badge.txt { font-size: 30px; }

    /* 目次 7章ぶんを内容領域に収める */
    .agenda li { font-size: 50px; }
    .agenda .num { width: 72px; height: 72px; font-size: 44px; }

    /* 評価見開き用スタイル（#47 の確定寸法を踏襲。±文言は台本どおりのまま収める） */
    .eval-head { height: 112px; margin-bottom: 8px; padding-bottom: 8px; }
    .eval-head .logo { height: 66px; object-fit: contain; }
    .eval-head .grade { font-size: 72px; }
    .eval-title { font-size: 48px; padding-bottom: 8px; margin-bottom: 8px; }
    .eval-cards { gap: 7px; justify-content: space-between; }
    .eval-cards .card { grid-template-columns: 76px 1fr; gap: 4px 10px; padding: 9px 12px; border-left-width: 10px; }
    .eval-cards .card .rank { width: 68px; height: 68px; border-radius: 14px; font-size: 36px; }
    .eval-cards .card-name { font-size: 30px; line-height: 1.05; }
    .eval-cards .card .line { font-size: 30px; line-height: 1.15; }
    .eval-note { font-size: 28px !important; line-height: 1.12; text-align: center; margin-top: 4px; }
  </style>
</head>
<body>
"""

def generate_slides():
    csv_path = DEFAULT_CSV_PATH
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Script CSV not found: {csv_path}")

    # スライドHTMLを順番に構築
    slides_html = []
    slides_html.append(build_head())

    # 1. Slide 1 (std)
    slides_html.append("""  <!-- Slide ID: 1 -->
  <div class="slide-container std" style="--primary-color:#C8102E;">
    <div class="sunburst"></div>
    <div class="std-copy" style="padding-right:230px;">
      <div class="cover-badge">格安SIM選びの悩み</div>
      <div class="title-main" style="font-size:86px;">
        mineoのプラン、<br><span style="color:#C8102E;">多すぎて選べない…</span>
      </div>
      <div style="display:flex;gap:16px;justify-content:center;align-items:center;flex-wrap:wrap;max-width:900px;">
        <span style="background:#fde3e7;border:3px solid #C8102E;color:#9a0c23;font-size:38px;font-weight:900;padding:8px 20px;border-radius:12px;">マイピタ 5コース</span>
        <span style="background:#fde3e7;border:3px solid #C8102E;color:#9a0c23;font-size:38px;font-weight:900;padding:8px 20px;border-radius:12px;">パケット放題 1M・3M</span>
        <span style="background:#fde3e7;border:3px solid #C8102E;color:#9a0c23;font-size:38px;font-weight:900;padding:8px 20px;border-radius:12px;">マイそく</span>
      </div>
    </div>
    <img src="public/images/irasutoya/pose_atama_kakaeru_woman.png" style="position:absolute;right:40px;bottom:30px;height:270px;z-index:1;object-fit:contain;" alt="頭を抱える女性">
  </div>
""")

    # 2. Slide 2 (std)
    slides_html.append("""  <!-- Slide ID: 2 -->
  <div class="slide-container std" style="--primary-color:#C8102E;">
    <div class="sunburst"></div>
    <div class="std-copy" style="padding-right:230px;">
      <div class="cover-badge">全プラン徹底比較</div>
      <div class="title-main" style="font-size:86px;">
        料金を全部並べると…<br><span style="color:#C8102E;">3つに絞れる！</span>
      </div>
      <div style="display:flex;gap:24px;justify-content:center;align-items:center;margin-top:10px;">
        <div style="background:#fff;border:4px solid #C8102E;border-radius:16px;padding:16px 24px;box-shadow:0 8px 16px rgba(0,0,0,0.1);text-align:center;">
          <div style="font-size:28px;font-weight:900;color:#9a0c23;">選択肢①</div>
          <div style="font-size:38px;font-weight:900;color:#212121;">3GB＋使い放題</div>
        </div>
        <div style="background:#fff;border:4px solid #C8102E;border-radius:16px;padding:16px 24px;box-shadow:0 8px 16px rgba(0,0,0,0.1);text-align:center;">
          <div style="font-size:28px;font-weight:900;color:#9a0c23;">選択肢②</div>
          <div style="font-size:38px;font-weight:900;color:#212121;">15GB</div>
        </div>
        <div style="background:#fff;border:4px solid #C8102E;border-radius:16px;padding:16px 24px;box-shadow:0 8px 16px rgba(0,0,0,0.1);text-align:center;">
          <div style="font-size:28px;font-weight:900;color:#9a0c23;">選択肢③</div>
          <div style="font-size:38px;font-weight:900;color:#212121;">30GB以上</div>
        </div>
      </div>
    </div>
    <img src="public/images/irasutoya/pose_naruhodo_woman.png" style="position:absolute;right:30px;bottom:25px;height:260px;z-index:1;object-fit:contain;" alt="なるほど女性">
  </div>
""")

    # 3. Slide 3 (std)
    slides_html.append("""  <!-- Slide ID: 3 -->
  <div class="slide-container std" style="--primary-color:#22a73f;">
    <div class="sunburst" style="background:repeating-conic-gradient(from 0deg at 50% 45%, rgba(34, 167, 63, 0.06) 0deg 5deg, transparent 5deg 10deg);"></div>
    <div class="std-copy">
      <div class="cover-badge" style="background:#1c8b34;">mineo歴8年・ショウ</div>
      <div class="title-main" style="font-size:86px;">
        いまもメイン回線はmineo<br><span style="color:#1c8b34;">「実質使い放題」</span>で運用中
      </div>
      <div style="display:flex;gap:20px;justify-content:center;align-items:center;">
        <div style="background:#e8f5e6;border:3px solid #22a73f;border-radius:14px;padding:12px 24px;font-size:40px;font-weight:900;color:#1c8b34;">
          mineo歴8年
        </div>
        <div style="background:#e8f5e6;border:3px solid #22a73f;border-radius:14px;padding:12px 24px;font-size:40px;font-weight:900;color:#1c8b34;">
          ギガを使い切っても止まらない
        </div>
      </div>
    </div>
  </div>
""")

    # 4. Slide 4 (std - タイトル)
    slides_html.append("""  <!-- Slide ID: 4 -->
  <div class="slide-container std" style="--primary-color:#22a73f;">
    <div class="sunburst" style="background:repeating-conic-gradient(from 0deg at 50% 45%, rgba(34, 167, 63, 0.08) 0deg 5deg, transparent 5deg 10deg);"></div>
    <div class="std-copy">
      <div style="display:flex;align-items:center;gap:18px;">
        <img src="public/images/logo/Mineo_logo.png" style="height:70px;object-fit:contain;background:#fff;padding:6px 16px;border-radius:10px;box-shadow:0 4px 10px rgba(0,0,0,0.1);" alt="mineo">
        <div class="cover-badge" style="background:#1c8b34;">【決定版】</div>
      </div>
      <div class="title-main" style="font-size:86px;">
        mineoのプラン選びは<br><span style="color:#1c8b34;">3択でいい。</span>
      </div>
      <div style="font-size:46px;font-weight:900;color:#212121;background:rgba(255,255,255,0.9);padding:10px 32px;border-radius:12px;border:3px solid #22a73f;">
        歴8年が教える実質使い放題の選び方
      </div>
    </div>
  </div>
""")

    # 5. Slide 5 (見開き - 目次)
    slides_html.append("""  <!-- Slide ID: 5 -->
  <div class="slide-container" style="--brand:#22a73f;--brand-deep:#1c8b34;--brand-soft:#e8f5e6;">
    <div class="book">
      <div class="spine"></div>
      <div class="page left">
        <div class="page-head">格安SIM図鑑 もくじ</div>
        <ul class="agenda" style="gap:10px;">
          <li><span class="num">1</span>mineoってどんなSIM？</li>
          <li><span class="num">2</span>実質使い放題のカラクリ</li>
          <li><span class="num">3</span>全組み合わせの料金比較</li>
          <li><span class="num">4</span>歴8年ショウの使い方</li>
          <li><span class="num">5</span>独自評価</li>
          <li><span class="num">6</span>3択の選び方</li>
          <li><span class="num">7</span>まとめ</li>
        </ul>
      </div>
      <div class="page right">
        <div class="page-head">この動画でわかること</div>
        <div class="page-body center">
          <ul class="benefits">
            <li>
              <span class="check">✓</span>
              <span>全コース×パケット放題の料金と、<b>3択に絞れる理由</b></span>
            </li>
            <li>
              <span class="check">✓</span>
              <span>自分にピッタリ合う<b>1つの選び方</b></span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
""")

    # 6. Slide 6-0 (見開き - 章扉 第1章)
    slides_html.append("""  <!-- Slide ID: 6-0 -->
  <div class="slide-container" style="--brand:#22a73f;--brand-deep:#1c8b34;--brand-soft:#e8f5e6;">
    <div class="book">
      <div class="spine"></div>
      <div class="page left">
        <div class="divider">
          <div class="kicker">CHAPTER</div>
          <div class="num">1</div>
          <div class="seal">FILE No.01</div>
        </div>
      </div>
      <div class="page right">
        <div class="page-body center">
          <div class="big-title">mineoって<br><span class="em">どんな格安SIM？</span></div>
          <div class="lead">大手3キャリア対応＆2つの基本プランを整理！</div>
        </div>
      </div>
    </div>
  </div>
""")

    # 7. Slide 7 (見開き - mineoとは)
    slides_html.append("""  <!-- Slide ID: 7 -->
  <div class="slide-container" style="--brand:#22a73f;--brand-deep:#1c8b34;--brand-soft:#e8f5e6;">
    <div class="book">
      <div class="spine"></div>
      <div class="page left">
        <div class="page-head">mineo（マイネオ）とは？</div>
        <div class="page-body">
          <div class="lead"><span class="em">3つの回線から選べる</span>格安SIM</div>
          <ul class="rows">
            <li><span class="ic"><i class="fa-solid fa-signal"></i></span><div class="tx">ドコモ回線</div></li>
            <li><span class="ic"><i class="fa-solid fa-signal"></i></span><div class="tx">au回線</div></li>
            <li><span class="ic"><i class="fa-solid fa-signal"></i></span><div class="tx">ソフトバンク回線</div></li>
          </ul>
        </div>
      </div>
      <div class="page right">
        <div class="page-head">プランは2種類</div>
        <div class="page-body">
          <ul class="rows">
            <li>
              <span class="badge">A</span>
              <div class="tx"><span class="em">マイピタ</span><span class="sub">毎月使えるギガの量を選ぶ</span></div>
            </li>
            <li>
              <span class="badge">B</span>
              <div class="tx"><span class="em">マイそく</span><span class="sub">通信の速さを選ぶ（平日12時台は速度が落ちる・パケット放題は対象外）</span></div>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
""")

    # 8. Slide 7-2 (見開き, price-note - マイピタ料金)
    slides_html.append("""  <!-- Slide ID: 7-2 -->
  <div class="slide-container price-note" style="--brand:#22a73f;--brand-deep:#1c8b34;--brand-soft:#e8f5e6;">
    <div class="book">
      <div class="spine"></div>
      <div class="page left">
        <div class="page-head">マイピタ 基本月額料金</div>
        <div class="page-body">
          <table class="sheet">
            <thead>
              <tr>
                <th>コース容量</th>
                <th>月額（税込）</th>
              </tr>
            </thead>
            <tbody>
              <tr><td>3GB</td><td><span class="em">1,298円</span></td></tr>
              <tr><td>7GB</td><td>1,518円</td></tr>
              <tr><td>15GB</td><td>1,958円</td></tr>
              <tr><td>30GB</td><td>2,178円</td></tr>
              <tr><td>50GB</td><td>2,948円</td></tr>
            </tbody>
          </table>
          <div class="note">※音声通話付きの料金</div>
        </div>
      </div>
      <div class="page right">
        <div class="page-head">マイピタの安心機能</div>
        <div class="page-body">
          <div class="emph">余ったギガは<br><span class="big">翌月へ繰り越し</span></div>
          <ul class="rows">
            <li>
              <span class="badge"><i class="fa-solid fa-check"></i></span>
              <div class="tx">使い切れなかったギガが無駄にならない</div>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
""")

    # 9. Slide 8-0 (見開き - 章扉 第2章)
    slides_html.append("""  <!-- Slide ID: 8-0 -->
  <div class="slide-container" style="--brand:#22a73f;--brand-deep:#1c8b34;--brand-soft:#e8f5e6;">
    <div class="book">
      <div class="spine"></div>
      <div class="page left">
        <div class="divider">
          <div class="kicker">CHAPTER</div>
          <div class="num">2</div>
          <div class="seal">FILE No.02</div>
        </div>
      </div>
      <div class="page right">
        <div class="page-body center">
          <div class="big-title">実質使い放題の<br><span class="em">カラクリ</span></div>
          <div class="lead">ギガがゼロになっても止まらない独自機能の全貌</div>
        </div>
      </div>
    </div>
  </div>
""")

    # 10. Slide 9 (見開き, price-note - パケット放題とは)
    slides_html.append("""  <!-- Slide ID: 9 -->
  <div class="slide-container price-note" style="--brand:#22a73f;--brand-deep:#1c8b34;--brand-soft:#e8f5e6;">
    <div class="book">
      <div class="spine"></div>
      <div class="page left">
        <div class="page-head">パケット放題とは？</div>
        <div class="page-body">
          <div class="lead">ギガを使い切っても、<br>決まった速さで<span class="em">データ通信が使い放題！</span></div>
          <div class="note">※Mbps＝通信速度の単位</div>
        </div>
      </div>
      <div class="page right">
        <div class="page-head">コース別のパケット放題料金</div>
        <div class="page-body">
          <table class="sheet">
            <thead>
              <tr>
                <th>マイピタコース</th>
                <th>1Mbps</th>
                <th>3Mbps</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>3GB・7GB</td>
                <td><span class="em">無料</span></td>
                <td>月額 385円</td>
              </tr>
              <tr>
                <td>15GB・30GB・50GB</td>
                <td>―</td>
                <td><span class="em">無料</span></td>
              </tr>
            </tbody>
          </table>
          <div class="lead">15GB以上は<span class="em">3Mbps無料</span></div>
        </div>
      </div>
    </div>
  </div>
""")

    # 11. Slide 9-2 (見開き - 公式利用目安)
    slides_html.append("""  <!-- Slide ID: 9-2 -->
  <div class="slide-container" style="--brand:#22a73f;--brand-deep:#1c8b34;--brand-soft:#e8f5e6;">
    <div class="book">
      <div class="spine"></div>
      <div class="page left">
        <div class="page-head">最大1Mbpsの利用目安</div>
        <div class="page-body">
          <table class="sheet">
            <thead>
              <tr>
                <th>使い方</th>
                <th>目安</th>
              </tr>
            </thead>
            <tbody>
              <tr><td>メール・LINE・決済</td><td><span class="em">◎</span></td></tr>
              <tr><td>音楽ストリーミング</td><td><span class="em">◎</span></td></tr>
              <tr><td>テキストサイト・SNS</td><td>○</td></tr>
              <tr><td>画像SNS</td><td>△</td></tr>
              <tr><td>動画 低画質（144p）</td><td>○</td></tr>
              <tr><td>動画 標準画質（360p）</td><td>△</td></tr>
            </tbody>
          </table>
        </div>
      </div>
      <div class="page right">
        <div class="page-head">最大3Mbpsの利用目安</div>
        <div class="page-body">
          <table class="sheet">
            <thead>
              <tr>
                <th>使い方</th>
                <th>目安</th>
              </tr>
            </thead>
            <tbody>
              <tr><td>動画 高画質（720p）</td><td><span class="em">○</span></td></tr>
              <tr><td>ビデオ会議</td><td><span class="em">○</span></td></tr>
            </tbody>
          </table>
          <div class="lead">3Mbpsなら<span class="em">高画質動画も○</span></div>
          <div class="note" style="font-size:28px;text-align:right;">※出典：mineo公式サイト</div>
        </div>
      </div>
    </div>
  </div>
""")

    # 12. Slide 9-3 (見開き - mineoスイッチ)
    slides_html.append("""  <!-- Slide ID: 9-3 -->
  <div class="slide-container" style="--brand:#22a73f;--brand-deep:#1c8b34;--brand-soft:#e8f5e6;">
    <div class="book">
      <div class="spine"></div>
      <div class="page left">
        <div class="page-head">mineoスイッチ</div>
        <div class="page-body">
          <ul class="rows">
            <li>
              <span class="badge">ON</span>
              <div class="tx">パケット放題の速さで使う<span class="sub" style="color:var(--brand-deep);font-weight:900;">ギガが減らない</span></div>
            </li>
            <li>
              <span class="badge txt">OFF</span>
              <div class="tx">ふつうの速さで使う<span class="sub">ギガが減る</span></div>
            </li>
          </ul>
          <div class="lead">mineoアプリから<br><span class="em">いつでも切り替えOK</span></div>
        </div>
      </div>
      <div class="page right">
        <div class="page-head">ONのときの注意点</div>
        <div class="page-body">
          <div class="warn">
            <span class="ic"><i class="fa-solid fa-triangle-exclamation"></i></span>
            ONの通信量が<span class="em">3日間で10GB</span>を超えると…
          </div>
          <ul class="rows">
            <li>
              <span class="badge">!</span>
              <div class="tx">翌日は最大200kbpsに制限</div>
            </li>
            <li>
              <span class="badge"><i class="fa-solid fa-check"></i></span>
              <div class="tx">ギガが残っていれば<span class="em">OFFで回避</span>できる</div>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
""")

    # 13. Slide 10-0 (見開き - 章扉 第3章)
    slides_html.append("""  <!-- Slide ID: 10-0 -->
  <div class="slide-container" style="--brand:#22a73f;--brand-deep:#1c8b34;--brand-soft:#e8f5e6;">
    <div class="book">
      <div class="spine"></div>
      <div class="page left">
        <div class="divider">
          <div class="kicker">CHAPTER</div>
          <div class="num">3</div>
          <div class="seal">FILE No.03</div>
        </div>
      </div>
      <div class="page right">
        <div class="page-body center">
          <div class="big-title">全組み合わせの<br><span class="em">料金比較</span></div>
          <div class="lead">マイピタ×パケット放題 全パターンの月額を完全網羅！</div>
        </div>
      </div>
    </div>
  </div>
""")

    # 14. Slide 11 (見開き, price-note - 組み合わせ別の月額)
    slides_html.append("""  <!-- Slide ID: 11 -->
  <div class="slide-container price-note" style="--brand:#22a73f;--brand-deep:#1c8b34;--brand-soft:#e8f5e6;">
    <div class="book">
      <div class="spine"></div>
      <div class="page left">
        <div class="page-head">小容量コース（3GB・7GB）</div>
        <div class="page-body">
          <table class="sheet">
            <thead>
              <tr>
                <th>コース</th>
                <th>1Mbps（無料）</th>
                <th>3Mbps（+385円）</th>
              </tr>
            </thead>
            <tbody>
              <tr><td>3GB</td><td><span class="em">1,298円</span></td><td><span class="em">1,683円</span></td></tr>
              <tr><td>7GB</td><td>1,518円</td><td>1,903円</td></tr>
            </tbody>
          </table>
          <div class="lead">最安1,298円で実質使い放題！<br><span class="em">3Mbpsでも月1,683円！</span></div>
        </div>
      </div>
      <div class="page right">
        <div class="page-head">15GB以上のコース</div>
        <div class="page-body">
          <table class="sheet">
            <thead>
              <tr>
                <th>コース</th>
                <th>月額</th>
                <th>3Mbps</th>
              </tr>
            </thead>
            <tbody>
              <tr><td>15GB</td><td><span class="em">1,958円</span></td><td><span class="em">無料</span></td></tr>
              <tr><td>30GB</td><td>2,178円</td><td>無料</td></tr>
              <tr><td>50GB</td><td>2,948円</td><td>無料</td></tr>
            </tbody>
          </table>
          <div class="note">※50GBはパスケットも無料</div>
        </div>
      </div>
    </div>
  </div>
""")

    # 15. Slide 11-2 (見開き, price-note - 7GB vs 15GB)
    slides_html.append("""  <!-- Slide ID: 11-2 -->
  <div class="slide-container price-note" style="--brand:#22a73f;--brand-deep:#1c8b34;--brand-soft:#e8f5e6;">
    <div class="book">
      <div class="spine"></div>
      <div class="page left">
        <div class="page-head">7GB＋3Mbps vs 15GB</div>
        <div class="page-body">
          <table class="sheet">
            <thead>
              <tr>
                <th></th>
                <th>7GB＋3Mbps</th>
                <th>15GB</th>
              </tr>
            </thead>
            <tbody>
              <tr><td>月額</td><td>1,903円</td><td>1,958円</td></tr>
              <tr><td>ギガ</td><td>7GB</td><td><span class="em">15GB</span></td></tr>
              <tr><td>3Mbps</td><td>385円</td><td><span class="em">無料</span></td></tr>
            </tbody>
          </table>
        </div>
      </div>
      <div class="page right">
        <div class="page-head">差はたった55円</div>
        <div class="page-body">
          <div class="emph">差は<span class="big">55円</span><br>ギガは<span class="em">8GB増える</span></div>
          <div class="lead">3Mbpsを付けるなら<br><span class="em">15GBのほうがお得</span></div>
        </div>
      </div>
    </div>
  </div>
""")

    # 16. Slide 11-3 (見開き, price-note - プラン選びは3択)
    slides_html.append("""  <!-- Slide ID: 11-3 -->
  <div class="slide-container price-note" style="--brand:#22a73f;--brand-deep:#1c8b34;--brand-soft:#e8f5e6;">
    <div class="book">
      <div class="spine"></div>
      <div class="page left">
        <div class="page-head">mineo選びは「この3択」！</div>
        <div class="page-body">
          <ul class="rows">
            <li>
              <span class="badge">①</span>
              <div class="tx">3GB＋パケット放題<span class="sub">1Mbpsなら1,298円・3Mbpsなら1,683円</span></div>
            </li>
            <li>
              <span class="badge">②</span>
              <div class="tx">15GB（3Mbps無料）<span class="sub">1,958円・3Mbps無料</span></div>
            </li>
            <li>
              <span class="badge">③</span>
              <div class="tx">30GB以上（大容量）<span class="sub">高速通信をたくさん使う人</span></div>
            </li>
          </ul>
        </div>
      </div>
      <div class="page right">
        <div class="page-head">迷うのはこの3つだけ</div>
        <div class="page-body">
          <div class="emph">選ぶのは<br><span class="big">この3つだけ</span></div>
          <div class="lead">自分に合う1つの選び方は<br><span class="em">第6章</span>で解説</div>
        </div>
      </div>
    </div>
  </div>
""")

    # 17. Slide 11-4 (見開き - チャンネル登録案内)
    slides_html.append("""  <!-- Slide ID: 11-4 -->
  <div class="slide-container" style="--brand:#22a73f;--brand-deep:#1c8b34;--brand-soft:#e8f5e6;">
    <div class="book">
      <div class="spine"></div>
      <div class="page left">
        <div class="divider">
          <div class="bigicon"><i class="fa-solid fa-bell"></i></div>
          <div class="big-title" style="font-size:72px;">最新情報を<br><span class="em">見逃さない！</span></div>
        </div>
      </div>
      <div class="page right">
        <div class="page-head">チャンネル登録で</div>
        <div class="page-body">
          <div class="lead">料金・キャンペーンの<br><span class="em">変更を見逃さない！</span></div>
          <ul class="rows">
            <li><span class="badge"><i class="fa-solid fa-yen-sign"></i></span><div class="tx">料金の変更</div></li>
            <li><span class="badge"><i class="fa-solid fa-gift"></i></span><div class="tx">キャンペーン情報</div></li>
          </ul>
        </div>
      </div>
    </div>
  </div>
""")

    # 18. Slide 12-0 (見開き - 章扉 第4章)
    slides_html.append("""  <!-- Slide ID: 12-0 -->
  <div class="slide-container" style="--brand:#22a73f;--brand-deep:#1c8b34;--brand-soft:#e8f5e6;">
    <div class="book">
      <div class="spine"></div>
      <div class="page left">
        <div class="divider">
          <div class="kicker">CHAPTER</div>
          <div class="num">4</div>
          <div class="seal">FILE No.04</div>
        </div>
      </div>
      <div class="page right">
        <div class="page-body center">
          <div class="big-title">歴8年ショウの<br><span class="em">使い方</span></div>
          <div class="lead">メイン回線で愛用中！月1,683円の実質使い放題ルーティン</div>
        </div>
      </div>
    </div>
  </div>
""")

    # 19. Slide 13 (見開き, price-note - ショウの使い方)
    slides_html.append("""  <!-- Slide ID: 13 -->
  <div class="slide-container price-note" style="--brand:#22a73f;--brand-deep:#1c8b34;--brand-soft:#e8f5e6;">
    <div class="book">
      <div class="spine"></div>
      <div class="page left">
        <div class="page-head">ショウの使い方</div>
        <div class="page-body">
          <div class="emph">マイピタ3GB＋3Mbps<br><span class="big">月1,683円</span></div>
          <ul class="rows">
            <li><span class="badge"><i class="fa-solid fa-star"></i></span><div class="tx">mineo歴8年・メイン回線</div></li>
          </ul>
        </div>
      </div>
      <div class="page right">
        <div class="page-head">ギガが減らない理由</div>
        <div class="page-body">
          <ul class="rows">
            <li><span class="badge">1</span><div class="tx">ふだんは<span class="em">スイッチON</span></div></li>
            <li><span class="badge">2</span><div class="tx">高速の3GBは<span class="em">ほとんど減らない</span></div></li>
            <li><span class="badge">3</span><div class="tx">余ったギガは<span class="em">パスケット</span>に貯まる<span class="sub">パスケットは月110円</span></div></li>
          </ul>
        </div>
      </div>
    </div>
  </div>
""")

    # 20. Slide 13-2 (見開き - ショウの場合 ゲームとスイッチ)
    slides_html.append("""  <!-- Slide ID: 13-2 -->
  <div class="slide-container" style="--brand:#22a73f;--brand-deep:#1c8b34;--brand-soft:#e8f5e6;">
    <div class="book">
      <div class="spine"></div>
      <div class="page left">
        <div class="page-head">ゲームをよく遊んだ頃</div>
        <div class="page-body">
          <div class="warn">
            <span class="ic"><i class="fa-solid fa-gamepad"></i></span>
            最大3Mbpsだと<br><span class="em">ゲーム画面が固まる</span>ことも
          </div>
          <div class="lead">そんなときは<br><span class="em">スイッチOFFで高速通信</span></div>
        </div>
      </div>
      <div class="page right">
        <div class="page-head">ギガが足りない月は</div>
        <div class="page-body">
          <ul class="rows">
            <li><span class="badge">1</span><div class="tx">OFFで遊ぶと<span class="em">3GBを消費</span></div></li>
            <li><span class="badge">2</span><div class="tx">足りなくなったら<br><span class="em">パスケットから引き出す</span></div></li>
          </ul>
        </div>
      </div>
    </div>
  </div>
""")

    # 21. Slide 14-0 (見開き - 章扉 第5章)
    slides_html.append("""  <!-- Slide ID: 14-0 -->
  <div class="slide-container" style="--brand:#22a73f;--brand-deep:#1c8b34;--brand-soft:#e8f5e6;">
    <div class="book">
      <div class="spine"></div>
      <div class="page left">
        <div class="divider">
          <div class="kicker">CHAPTER</div>
          <div class="num">5</div>
          <div class="seal">FILE No.05</div>
        </div>
      </div>
      <div class="page right">
        <div class="page-body center">
          <div class="big-title">格安SIM図鑑の<br><span class="em">独自評価</span></div>
          <div class="lead">6つの観点からmineoの実力を徹底チェック！</div>
        </div>
      </div>
    </div>
  </div>
""")

    # 22. Slide 15 (見開き, price-note - mineo 独自評価 Layout B)
    slides_html.append("""  <!-- Slide ID: 15 -->
  <div class="slide-container price-note" style="--brand:#22a73f;--brand-deep:#1c8b34;--brand-soft:#e8f5e6;">
    <div class="book">
      <div class="spine"></div>
      <div class="page left">
        <div class="head-left eval-head">
          <img class="logo" src="public/images/logo/Mineo_logo.png" alt="mineo">
          <div class="total">
            <div class="label">総合評価</div>
            <div class="grade">S</div>
          </div>
        </div>
        <div class="cards eval-cards">
          <div class="card">
            <div class="rank SS">SS</div>
            <div class="card-name">データ料金</div>
            <div class="line pro"><span class="tag">＋</span>15GB 1,958円・30GB 2,178円でパケット放題3Mbpsが無料。3GB・7GBにも1Mbpsが無料で付く</div>
            <div class="line con"><span class="tag">－</span>特になし</div>
          </div>
          <div class="card">
            <div class="rank A">A</div>
            <div class="card-name">通信品質</div>
            <div class="line pro"><span class="tag">＋</span>回線をau・ドコモ・ソフトバンクの3つから選べる</div>
            <div class="line con"><span class="tag">－</span>平日のお昼など、混雑する時間帯は速度が落ちやすい傾向がある</div>
          </div>
          <div class="card">
            <div class="rank A">A</div>
            <div class="card-name">初期費用</div>
            <div class="line pro"><span class="tag">＋</span>提携サイト限定リンクなら契約事務手数料が無料。2026年10月1日以降はeSIMの発行料も0円</div>
            <div class="line con"><span class="tag">－</span>通常の申し込みでは契約事務手数料がかかる。SIMカードで申し込む場合は発行料がかかる</div>
          </div>
        </div>
      </div>
      <div class="page right">
        <div class="page-head eval-title">mineoを6観点で評価</div>
        <div class="cards eval-cards">
          <div class="card">
            <div class="rank A">A</div>
            <div class="card-name">通話料</div>
            <div class="line pro"><span class="tag">＋</span>かけ放題オプションや、少しだけ話す人向けの10分通話パックがある</div>
            <div class="line con"><span class="tag">－</span>基本料金に無料通話分は含まれておらず、電話をよく使うなら別途オプション料金がかかる</div>
          </div>
          <div class="card">
            <div class="rank A">A</div>
            <div class="card-name">店舗サポート</div>
            <div class="line pro"><span class="tag">＋</span>一部の店舗や、ユーザー同士のコミュニティで相談できる</div>
            <div class="line con"><span class="tag">－</span>基本はWEB中心</div>
          </div>
          <div class="card">
            <div class="rank SS">SS</div>
            <div class="card-name">オプション</div>
            <div class="line pro"><span class="tag">＋</span>パケット放題・パスケット・mineoスイッチを組み合わせて、自分に合った「実質使い放題」を作れる</div>
            <div class="line con"><span class="tag">－</span>特になし</div>
          </div>
        </div>
        <div class="note eval-note">※本評価は当チャンネルの独断と偏見による独自評価であり、キャンペーン割引等は考慮していません</div>
      </div>
    </div>
  </div>
""")

    # 23. Slide 16 (見開き, price-note - 事務手数料無料キャンペーン)
    slides_html.append("""  <!-- Slide ID: 16 -->
  <div class="slide-container price-note" style="--brand:#22a73f;--brand-deep:#1c8b34;--brand-soft:#e8f5e6;">
    <div class="book">
      <div class="spine"></div>
      <div class="page left">
        <div class="page-head">提携サイト限定</div>
        <div class="page-body">
          <div class="emph">契約事務手数料が<span class="big">無料</span></div>
          <div class="lead">概要欄・固定コメントの<br>指定リンクから<span class="em">新規で<br>申し込んだ場合のみ</span></div>
          <div class="note" style="font-size:28px;">※法人名義・お試し200MBコース・マイそくスーパーライトは対象外</div>
        </div>
      </div>
      <div class="page right">
        <div class="page-head">これとは別に</div>
        <div class="page-body">
          <ul class="rows">
            <li>
              <span class="badge"><i class="fa-solid fa-sim-card"></i></span>
              <div class="tx">2026年10月1日以降<br><span class="em">eSIM発行料が0円</span><span class="sub">mineo公式の料金改定</span></div>
            </li>
          </ul>
          <div class="note">※eSIMはドコモ回線・au回線のみ</div>
        </div>
      </div>
    </div>
  </div>
""")

    # 24. Slide 17-0 (見開き - 章扉 第6章)
    slides_html.append("""  <!-- Slide ID: 17-0 -->
  <div class="slide-container" style="--brand:#22a73f;--brand-deep:#1c8b34;--brand-soft:#e8f5e6;">
    <div class="book">
      <div class="spine"></div>
      <div class="page left">
        <div class="divider">
          <div class="kicker">CHAPTER</div>
          <div class="num">6</div>
          <div class="seal">FILE No.06</div>
        </div>
      </div>
      <div class="page right">
        <div class="page-body center">
          <div class="big-title">あなたはどれ？<br><span class="em">3択の選び方</span></div>
          <div class="lead">2つの質問でわかる！あなたに最適なコース診断</div>
        </div>
      </div>
    </div>
  </div>
""")

    # 25. Slide 18 (見開き, price-note - 3択の選び方)
    slides_html.append("""  <!-- Slide ID: 18 -->
  <div class="slide-container price-note" style="--brand:#22a73f;--brand-deep:#1c8b34;--brand-soft:#e8f5e6;">
    <div class="book">
      <div class="spine"></div>
      <div class="page left">
        <div class="page-head">質問①</div>
        <div class="page-body">
          <ul class="rows">
            <li>
              <span class="badge">Q1</span>
              <div class="tx">外で高画質の動画やオンラインゲームを<span class="em">毎日たっぷり</span>使う？</div>
            </li>
            <li>
              <span class="badge txt" style="background:var(--con);">YES</span>
              <div class="tx"><span class="em">30GB以上</span></div>
            </li>
            <li>
              <span class="badge" style="background:var(--brand-deep);">NO</span>
              <div class="tx">質問②へ</div>
            </li>
          </ul>
        </div>
      </div>
      <div class="page right">
        <div class="page-head">質問②</div>
        <div class="page-body">
          <ul class="rows">
            <li>
              <span class="badge">Q2</span>
              <div class="tx">速さが必要な通信（スイッチOFF）が<span class="em">毎月3GBを超える</span>？</div>
            </li>
            <li>
              <span class="badge txt" style="background:var(--con);">YES</span>
              <div class="tx"><span class="em">15GB</span></div>
            </li>
            <li>
              <span class="badge" style="background:var(--brand-deep);">NO</span>
              <div class="tx"><span class="em">3GB＋パケット放題</span></div>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
""")

    # 26. Slide 18-2 (見開き, price-note - 3GB＋パケット放題の選び方)
    slides_html.append("""  <!-- Slide ID: 18-2 -->
  <div class="slide-container price-note" style="--brand:#22a73f;--brand-deep:#1c8b34;--brand-soft:#e8f5e6;">
    <div class="book">
      <div class="spine"></div>
      <div class="page left">
        <div class="page-head">3GB＋パケット放題</div>
        <div class="page-body">
          <ul class="rows">
            <li>
              <span class="badge">1M</span>
              <div class="tx">LINE・音楽・決済が中心<span class="sub">→ 1Mbps（無料）</span><span class="em">1,298円</span></div>
            </li>
            <li>
              <span class="badge">3M</span>
              <div class="tx">SNSの画像や動画も見る<span class="sub">→ 3Mbps（月385円）</span><span class="em">1,683円</span></div>
            </li>
          </ul>
        </div>
      </div>
      <div class="page right">
        <div class="page-head">足りない月は</div>
        <div class="page-body center">
          <div class="emph">追加チャージもできる<br><span class="big">100MB 55円</span></div>
        </div>
      </div>
    </div>
  </div>
""")

    # 27. Slide 19-0 (見開き - 章扉 おまけ)
    slides_html.append("""  <!-- Slide ID: 19-0 -->
  <div class="slide-container" style="--brand:#22a73f;--brand-deep:#1c8b34;--brand-soft:#e8f5e6;">
    <div class="book">
      <div class="spine"></div>
      <div class="page left">
        <div class="divider">
          <div class="kicker">SPECIAL</div>
          <div class="num" style="font-size:200px;">おまけ</div>
          <div class="seal">期間限定</div>
        </div>
      </div>
      <div class="page right">
        <div class="page-body center">
          <div class="big-title">11月30日までの<br><span class="em">期間限定情報！</span></div>
          <div class="lead">秋のピッタリ割<br><span class="em">キャンペーン</span></div>
        </div>
      </div>
    </div>
  </div>
""")

    # 28. Slide 20 (見開き, price-note - 秋のピッタリ割)
    slides_html.append("""  <!-- Slide ID: 20 -->
  <div class="slide-container price-note" style="--brand:#22a73f;--brand-deep:#1c8b34;--brand-soft:#e8f5e6;">
    <div class="book">
      <div class="spine"></div>
      <div class="page left">
        <div class="page-head">秋のピッタリ割</div>
        <div class="page-body">
          <table class="sheet">
            <thead>
              <tr><th>コース</th><th>通常</th><th>割引後</th></tr>
            </thead>
            <tbody>
              <tr><td>3GB</td><td>1,298円</td><td><span class="em">880円</span></td></tr>
              <tr><td>7GB</td><td>1,518円</td><td><span class="em">990円</span></td></tr>
              <tr><td>15GB</td><td>1,958円</td><td><span class="em">990円</span></td></tr>
              <tr><td>30GB</td><td>2,178円</td><td><span class="em">1,320円</span></td></tr>
              <tr><td>50GB</td><td>2,948円</td><td><span class="em">2,090円</span></td></tr>
            </tbody>
          </table>
          <div class="note">※音声通話付き・最大6カ月間</div>
        </div>
      </div>
      <div class="page right">
        <div class="page-head">対象と条件</div>
        <div class="page-body">
          <ul class="rows">
            <li><span class="badge txt">期間</span><div class="tx">2026年11月30日までの申し込み</div></li>
            <li><span class="badge txt">対象</span><div class="tx">新規申し込み、またはシングル→デュアル変更</div></li>
            <li><span class="badge txt">注意</span><div class="tx">1回線につき1回まで<span class="sub">法人名義は対象外</span></div></li>
          </ul>
        </div>
      </div>
    </div>
  </div>
""")

    # 29. Slide 20-2 (見開き, price-note - パケット放題＆10分通話パック割引)
    slides_html.append("""  <!-- Slide ID: 20-2 -->
  <div class="slide-container price-note" style="--brand:#22a73f;--brand-deep:#1c8b34;--brand-soft:#e8f5e6;">
    <div class="book">
      <div class="spine"></div>
      <div class="page left">
        <div class="page-head">パケット放題 3Mbps</div>
        <div class="page-body">
          <div class="emph">月385円 → <span class="big">0円</span><br>最大6カ月間</div>
          <div class="lead">3GB・7GBコースが対象</div>
        </div>
      </div>
      <div class="page right">
        <div class="page-head">10分通話パック</div>
        <div class="page-body">
          <div class="emph">月110円 → <span class="big">無料</span><br>最大6カ月間</div>
          <div class="lead">毎月最大10分の通話が割引</div>
          <div class="note" style="font-size:28px;">※いずれも2026年11月30日までの申し込みが対象</div>
        </div>
      </div>
    </div>
  </div>
""")

    # 30. Slide 20-3 (見開き - 過去動画CTA)
    slides_html.append("""  <!-- Slide ID: 20-3 -->
  <div class="slide-container" style="--brand:#22a73f;--brand-deep:#1c8b34;--brand-soft:#e8f5e6;">
    <div class="book">
      <div class="spine"></div>
      <div class="page left">
        <div class="page-head">秋のピッタリ割</div>
        <div class="page-body">
          <div class="visual">
            <img src="public/images/thumbnails/47_【〜11／30】mineo 3GB＋データ使い放題が最大6カ月880円！注意点も解説_サムネ1.png" alt="秋のピッタリ割の解説動画サムネイル">
          </div>
        </div>
      </div>
      <div class="page right">
        <div class="page-head">過去動画もチェック</div>
        <div class="page-body center">
          <div class="bigicon"><i class="fa-solid fa-circle-play"></i></div>
          <div class="lead" style="margin-top:20px;">詳しい解説は<br><span class="em">過去動画もチェック！</span></div>
        </div>
      </div>
    </div>
  </div>
""")

    # 31. Slide 21-0 (見開き - 章扉 第7章)
    slides_html.append("""  <!-- Slide ID: 21-0 -->
  <div class="slide-container" style="--brand:#22a73f;--brand-deep:#1c8b34;--brand-soft:#e8f5e6;">
    <div class="book">
      <div class="spine"></div>
      <div class="page left">
        <div class="divider">
          <div class="kicker">CHAPTER</div>
          <div class="num">7</div>
          <div class="seal">FILE No.07</div>
        </div>
      </div>
      <div class="page right">
        <div class="page-body center">
          <div class="big-title">今回の<br><span class="em">まとめ</span></div>
          <div class="lead">mineoのプラン選びは3択で迷いゼロ！</div>
        </div>
      </div>
    </div>
  </div>
""")

    # 32. Slide 22 (見開き, price-note - 今日のまとめ)
    slides_html.append("""  <!-- Slide ID: 22 -->
  <div class="slide-container price-note" style="--brand:#22a73f;--brand-deep:#1c8b34;--brand-soft:#e8f5e6;">
    <div class="book">
      <div class="spine"></div>
      <div class="page left">
        <div class="page-head">mineo選びの「結論3択」</div>
        <div class="page-body">
          <ul class="rows">
            <li>
              <span class="badge">①</span>
              <div class="tx">3GB＋パケット放題<span class="sub">1Mbpsなら1,298円・3Mbpsなら1,683円</span></div>
            </li>
            <li>
              <span class="badge">②</span>
              <div class="tx">15GB<span class="sub">1,958円・3Mbps無料</span></div>
            </li>
            <li>
              <span class="badge">③</span>
              <div class="tx">30GB以上<span class="sub">高速通信をたくさん使う人</span></div>
            </li>
          </ul>
        </div>
      </div>
      <div class="page right">
        <div class="page-head">決め手は2つ</div>
        <div class="page-body">
          <ul class="rows">
            <li><span class="badge">1</span><div class="tx">外で高画質動画やオンラインゲームを<span class="em">毎日使うか</span></div></li>
            <li><span class="badge">2</span><div class="tx">速い通信が<span class="em">毎月3GBを超えるか</span></div></li>
          </ul>
        </div>
      </div>
    </div>
  </div>
""")

    # 33. Slide 23 (見開き - ご注意)
    slides_html.append("""  <!-- Slide ID: 23 -->
  <div class="slide-container" style="--brand:#22a73f;--brand-deep:#1c8b34;--brand-soft:#e8f5e6;">
    <div class="book">
      <div class="spine"></div>
      <div class="page left">
        <div class="divider">
          <div class="bigicon"><i class="fa-solid fa-circle-info"></i></div>
          <div class="big-title">ご注意</div>
        </div>
      </div>
      <div class="page right">
        <div class="page-head">お申し込みの際は</div>
        <div class="page-body">
          <div class="lead">必ず<span class="em">mineo公式サイト</span>を<br>ご確認ください</div>
          <div class="note">プラン内容やキャンペーン情報は、すべてmineo公式サイトの内容が正となります</div>
          <div class="note" style="font-size:28px;">※料金・キャンペーンは動画投稿時点のものです</div>
        </div>
      </div>
    </div>
  </div>
""")

    # 34. Slide 24 (見開き - コメント大募集)
    slides_html.append("""  <!-- Slide ID: 24 -->
  <div class="slide-container" style="--brand:#22a73f;--brand-deep:#1c8b34;--brand-soft:#e8f5e6;">
    <div class="book">
      <div class="spine"></div>
      <div class="page left">
        <div class="divider">
          <div class="bigicon"><i class="fa-solid fa-comments"></i></div>
          <div class="big-title">コメント<br><span class="em">大募集！</span></div>
        </div>
      </div>
      <div class="page right">
        <div class="page-head">コメントで教えてね</div>
        <div class="page-body">
          <ul class="rows">
            <li><span class="badge"><i class="fa-solid fa-comment"></i></span><div class="tx">「わたしは〇GB＋パケット放題で足りてます」</div></li>
            <li><span class="badge"><i class="fa-solid fa-comment"></i></span><div class="tx">わたしのエリアの電波</div></li>
            <li><span class="badge"><i class="fa-solid fa-comment"></i></span><div class="tx">わかりにくかった点</div></li>
          </ul>
        </div>
      </div>
    </div>
  </div>
""")

    # 35. Slide 25 (見開き - スマホ代見直し)
    slides_html.append("""  <!-- Slide ID: 25 -->
  <div class="slide-container" style="--brand:#22a73f;--brand-deep:#1c8b34;--brand-soft:#e8f5e6;">
    <div class="book">
      <div class="spine"></div>
      <div class="page left">
        <div class="page-head">スマホ代は</div>
        <div class="page-body">
          <div class="emph">毎月かかる<br><span class="big">大きな固定費</span></div>
          <div class="lead">少しでも多くの方に<br><span class="em">見直してほしい</span></div>
        </div>
      </div>
      <div class="page right">
        <div class="page-head">浮いたぶんは</div>
        <div class="page-body center">
          <div class="bigicon"><i class="fa-solid fa-piggy-bank"></i></div>
          <div class="lead"><span class="em">貯蓄など</span>にまわせます</div>
        </div>
      </div>
    </div>
  </div>
""")

    # 36. Slide 25-1 (見開き - チャンネルの想い)
    slides_html.append("""  <!-- Slide ID: 25-1 -->
  <div class="slide-container" style="--brand:#22a73f;--brand-deep:#1c8b34;--brand-soft:#e8f5e6;">
    <div class="book">
      <div class="spine"></div>
      <div class="page left">
        <div class="divider">
          <div class="bigicon"><i class="fa-solid fa-book-open"></i></div>
          <div class="big-title">格安SIM図鑑の<br><span class="em">お約束</span></div>
        </div>
      </div>
      <div class="page right">
        <div class="page-head">これからも</div>
        <div class="page-body center">
          <div class="lead">この動画を見れば<br><span class="em">自分に合う格安SIMが分かる</span><br>そんな動画を作っていきます！</div>
        </div>
      </div>
    </div>
  </div>
""")

    # 37. Slide 26 (見開き - ブログ・note案内)
    slides_html.append("""  <!-- Slide ID: 26 -->
  <div class="slide-container" style="--brand:#22a73f;--brand-deep:#1c8b34;--brand-soft:#e8f5e6;">
    <div class="book">
      <div class="spine"></div>
      <div class="page left">
        <div class="divider">
          <div class="bigicon"><i class="fa-solid fa-pen-nib"></i></div>
          <div class="big-title">ブログ・noteも<br><span class="em">公開中！</span></div>
        </div>
      </div>
      <div class="page right">
        <div class="page-head">ブログ・noteでも</div>
        <div class="page-body">
          <div style="text-align:center;"><img src="public/images/common/ブログ_ヘッダー画像_スライド用.png" style="max-height:320px;width:100%;object-fit:contain;border-radius:14px;box-shadow:0 8px 18px rgba(0,0,0,0.15);" alt="ブログヘッダー"></div>
          <div class="lead">格安SIMの料金を<br><span class="em">詳しく比較中！</span></div>
          <div class="note">概要欄のリンクからぜひ！</div>
        </div>
      </div>
    </div>
  </div>
""")

    # 38. Slide 27 (見開き - チャンネル登録・グッドボタン)
    slides_html.append("""  <!-- Slide ID: 27 -->
  <div class="slide-container" style="--brand:#22a73f;--brand-deep:#1c8b34;--brand-soft:#e8f5e6;">
    <div class="book">
      <div class="spine"></div>
      <div class="page left">
        <div class="divider">
          <div class="bigicon"><i class="fa-solid fa-bell"></i></div>
          <div class="big-title" style="font-size:88px;">チャンネル登録<br><span class="em">グッドボタン</span><br>よろしくね！</div>
        </div>
      </div>
      <div class="page right">
        <div class="page-body center">
          <div class="logos" style="margin-bottom:10px;"><i class="fa-solid fa-thumbs-up" style="font-size:110px;color:var(--brand);"></i><i class="fa-solid fa-bell" style="font-size:110px;color:var(--brand-deep);"></i></div>
          <div class="lead" style="text-align:center;">ご視聴頂き<br><span class="em">ありがとうございました！</span></div>
        </div>
      </div>
    </div>
  </div>
""")

    slides_html.append("</body>\n</html>\n")

    full_html = "\n".join(slides_html)

    # 書き込み
    with open(OUTPUT_HTML_PATH, "w", encoding="utf-8") as f:
        f.write(full_html)
    print(f"[OK] Successfully wrote slides HTML to {OUTPUT_HTML_PATH}")

    # 検証: スライドIDの一致確認
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)
        csv_ids = []
        seen = set()
        for row in reader:
            if not row: continue
            sid = row[5]
            if not sid: continue
            if sid not in seen:
                seen.add(sid)
                csv_ids.append(sid)

    html_ids = re.findall(r"<!-- Slide ID: ([0-9-]+) -->", full_html)

    print(f"CSV Slide IDs count:  {len(csv_ids)}")
    print(f"HTML Slide IDs count: {len(html_ids)}")

    diff_missing_in_html = set(csv_ids) - set(html_ids)
    diff_extra_in_html = set(html_ids) - set(csv_ids)

    if diff_missing_in_html:
        print(f"[ERROR] Missing in HTML: {diff_missing_in_html}")
    if diff_extra_in_html:
        print(f"[ERROR] Extra in HTML: {diff_extra_in_html}")

    if not diff_missing_in_html and not diff_extra_in_html:
        print("[OK] Slide IDs perfectly match between CSV and HTML!")
    else:
        sys.exit(1)

    # 検証: プレースホルダ文言のチェック
    dummy_patterns = ["ここにテキスト", "TODO", "lorem ipsum", "サンプル", "XXX"]
    for pat in dummy_patterns:
        if pat in full_html:
            print(f"[ERROR] Found placeholder '{pat}' in generated HTML!")
            sys.exit(1)
    print("[OK] No placeholder text found in generated HTML.")

if __name__ == "__main__":
    generate_slides()
