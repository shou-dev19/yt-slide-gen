#!/usr/bin/env python3
"""Generate the long-form 51 mountain satellite SIM deck from its master CSV."""
from __future__ import annotations

import csv
import html
import re
from pathlib import Path

ROOT = Path('/workspaces/yt-factory/packages/slide-gen')
MASTER = Path('/workspaces/yt-factory/packages/scenario-gen/archive/videos/51_【2026年最新】登山で圏外でも連絡できる格安SIMは？衛星通信が使える4つの選び方/long/【2026年最新】登山で圏外でも連絡できる格安SIMは？衛星通信が使える4つの選び方.csv')
OUT = ROOT / 'slides.html'
RED = ('#C8102E', '#9a0c23', '#fde3e7')
BLUE = ('#1565C0', '#0d47a1', '#e3f0fb')
GREEN = ('#22a73f', '#1c8b34', '#e8f5e6')
COLORS = {'LINEMO': RED, 'ahamo': RED, 'povo2.0': BLUE}
LOGOS = {'LINEMO':'LINEMO_logo.png','ahamo':'Ahamo_logo.png','povo2.0':'Povo_logo.png'}
CHARTS = {'LINEMO':'LINEMO.png','ahamo':'ahamo.png','povo2.0':'povo2.0.png'}

def esc(s: str) -> str:
    return html.escape(s, quote=True)

def split_content(s: str) -> list[str]:
    return [x.strip() for x in re.split(r'[／/｜|]', s) if x.strip()]

def shell(slide_id: str, left_head: str, left_body: str, right_head: str, right_body: str,
          brand=RED, extra='') -> str:
    b, d, soft = brand
    return f'''<!-- Slide ID: {esc(slide_id)} -->
<div class="slide-container {extra}" style="--brand:{b};--brand-deep:{d};--brand-soft:{soft}">
  <div class="book"><div class="spine"></div>
    <div class="page left"><div class="page-head">{left_head}</div><div class="page-body">{left_body}</div></div>
    <div class="page right"><div class="page-head">{right_head}</div><div class="page-body">{right_body}</div></div>
  </div>
</div>'''

def lead(text: str, cls='lead') -> str:
    return f'<div class="{cls}">{esc(text)}</div>'

def rows(items: list[str], icon='fa-solid fa-satellite') -> str:
    lis = ''.join(f'<li><span class="ic {icon}"></span><span class="tx">{esc(x)}</span></li>' for x in items)
    return f'<ul class="rows">{lis}</ul>'

def std(slide_id: str, title: str, kicker: str, extra='') -> str:
    return f'''<!-- Slide ID: {esc(slide_id)} -->
<div class="slide-container std"><div class="std-burst"></div><div class="std-copy">
 <div class="std-kicker">{esc(kicker)}</div><div class="std-title">{title}</div>
 {extra}<div class="std-footer">登山中も、つながる備えを。</div></div></div>'''

def chapter(slide_id: str, content: str) -> str:
    m = re.search(r'第(\d+)章\s*(.*)', content)
    n, title = (m.group(1), m.group(2).strip()) if m else ('', content)
    title = title.rstrip('！。')
    if slide_id == '6-0': title = '衛星通信で<br>何ができる？'
    elif slide_id == '25-0': title = 'お店で相談したい<br>人は？'
    elif slide_id == '27-0': title = '登山する人の<br>4つの選び方'
    elif slide_id == '20-0': title = 'au系で<br>衛星通信を足す方法'
    title_html = title if '<br>' in title else esc(title)
    divider=f'<div class="divider"><div class="kicker">CHAPTER</div><div class="num">{esc(n)}</div><div class="seal">FILE No.{int(n):02d}</div></div>'
    return shell(slide_id, '章の入口', divider, '今回のテーマ', f'<div class="big-title"><span class="em">{title_html}</span></div>{lead("衛星通信を知って、自分に合う備えを選びましょう")}', RED)

def agenda(content: str) -> str:
    seg = split_content(content)
    chapters = [x for x in seg if re.match(r'第\d+章', x)]
    benefit_text=re.search(r'【この動画でわかること】(.*)',content)
    benefits=re.findall(r'[①②③][^①②③]+?(?=\s*[①②③]|$)', benefit_text.group(1)) if benefit_text else []
    agenda_items=[]
    for i, x in enumerate(chapters):
        label=re.sub(r'^第\d+章\s*', '', x)
        agenda_items.append(f'<li><span class="num">{i+1}</span><span>{esc(label)}</span></li>')
    left = '<ul class="agenda">'+''.join(agenda_items)+'</ul>'
    right = '<ul class="benefits">'+''.join(f'<li><span class="check">✓</span><span>{esc(x)}</span></li>' for x in benefits)+'</ul>'
    return shell('5','格安SIM図鑑 もくじ',left,'この動画でわかること',right)

def parse_eval(content: str) -> tuple[str,str,list[tuple[str,str,str,str]]]:
    # Keep the assessment wording from the script; only remove the structural markup.
    bits = content.split('／')
    carrier = bits[1].strip()
    overall = re.search(r'総合:([^／]+)', content).group(1)
    order = ['データ料金','通信品質','初期費用','通話料','店舗サポート','オプション']
    cards=[]
    for name in order:
        # Con text may contain nested parentheses such as （税込）. Stop only
        # at the outer delimiter before the next assessment item or end.
        m = re.search(re.escape(name)+r':(SS|S|A|B|C)（\＋(.*?)／\－(.*?)(?=）(?:／(?:データ料金|通信品質|初期費用|通話料|店舗サポート|オプション):|$))', content)
        if m: cards.append((name,m.group(1),m.group(2),m.group(3)))
    return carrier, overall, cards

def eval_detail(slide_id: str, content: str) -> str:
    carrier, overall, cards = parse_eval(content)
    color = COLORS.get(carrier, RED)
    logo = LOGOS.get(carrier, 'LINEMO_logo.png')
    def card(c):
        name, rank, pro, con = c
        # Preserve complete thoughts and remove only redundant phrasing.
        def compact(s):
            replacements = {
              'お昼の混雑する時間帯でも速度が落ちにくい':'昼の混雑時も速度が落ちにくい',
              'LINEMOベストプランVは':'ベストプランVは',
              'LINEMOベストプランは無料通話が付かず':'ベストプランに無料通話はなく',
              '店頭スマホサポートでお店でも相談できる':'店頭スマホサポートで相談できる',
              '店頭スマホサポートでお店でも相談できる':'店頭スマホサポートで相談できる',
              'LINEMOベストプランVは30GBで2,970円':'ベストプランVは30GB・2,970円',
              'LINEMOベストプランは':'ベストプランは',
              '無制限かけ放題も月1,100円':'無制限かけ放題は月1,100円',
              '5分かけ放題550円は別料金':'5分かけ放題は別料金（月550円）',
              'データ繰越に対応しておらず、余ったデータは翌月に持ち越せない':'データ繰り越し不可。余りは翌月に持ち越せない',
              '3GBまで990円・10GBまで2,090円':'3GBまで990円・10GBまで2,090円',
              '契約事務手数料0円で申し込める':'契約事務手数料0円',
              '5分以内の国内通話が無料で最初から込み':'5分以内の国内通話が無料で込み',
              '対面のサポートはない。2回線目の設定も自分でやる':'対面サポートなし。2回線目も自分で設定',
              '留守番電話や割込通話などの基本オプションは有料':'留守番電話・割込通話は有料',
              '設定した利用量上限に達しても最大1Mbpsの速度で使い続けられる':'上限後も最大1Mbpsで使い続けられる',
              'Opensignal社の2026年4月版レポートでドコモは4キャリア中最下位。混雑時の速度低下の声もある':'2026年4月Opensignalで4キャリア中最下位。混雑時に速度低下との声もある',
              '利用状況によって契約解除料1,100円（税込）がかかる場合がある':'利用状況により契約解除料1,100円（税込）がかかる場合がある',
              '基本はオンライン専用で、店頭サポートは有料':'オンライン専用で、店頭サポートは有料',
              'SNSや動画のデータ消費をカウントしない（カウントフリー）機能は無い':'SNSや動画のカウントフリー機能はない',
              '毎月たくさん使う人は、月額制の格安SIMより割高になりやすい。衛星通信を足すと専用プラン+の月1,650円が別にかかる':'大容量では月額制SIMより割高になりやすい。衛星通信は専用プラン+が月1,650円',
              '基本料0円のまま回線を持てて、データ使い放題24時間330円など必要な日だけ盛れる':'基本料0円で回線を持てる。使い放題24時間330円など必要な日だけ追加できる',
              '180日間トッピングを購入しないと利用停止になる':'180日間トッピングを購入しないと利用停止になる',
            }
            for old, new in replacements.items(): s = s.replace(old, new)
            return s
        return f'<div class="card"><div class="rank {rank}">{rank}</div><div class="card-name">{esc(name)}</div><div class="line pro"><span class="tag">＋</span>{esc(compact(pro))}</div><div class="line con"><span class="tag">－</span>{esc(compact(con))}</div></div>'
    leftcards=''.join(card(c) for c in cards[:3]); rightcards=''.join(card(c) for c in cards[3:])
    b,d,soft=color
    return f'''<!-- Slide ID: {esc(slide_id)} -->
<div class="slide-container price-note" style="--brand:{b};--brand-deep:{d};--brand-soft:{soft}"><div class="book"><div class="spine"></div>
<div class="page left"><div class="head-left"><img class="logo" src="public/images/logo/{logo}" alt="{esc(carrier)}"><div class="total"><div class="label">総合評価</div><div class="grade">{esc(overall)}</div></div></div><div class="cards">{leftcards}</div></div>
<div class="page right"><div class="head-right eval-head-right"><div class="eval-head-title">{esc(carrier)}の評価</div></div><div class="cards">{rightcards}</div><div class="note" style="font-size:28px;text-align:center;">※本評価は当チャンネルの独断と偏見による独自評価であり、キャンペーン割引等は考慮していません</div></div>
</div></div>'''

def eval_plan(slide_id: str, content: str) -> str:
    carrier, overall, cards = parse_eval(content)
    color=COLORS.get(carrier,RED); b,d,soft=color
    chart=CHARTS.get(carrier,'LINEMO.png'); logo=LOGOS.get(carrier,'LINEMO_logo.png')
    data=next((p for n,r,p,c in cards if n=='データ料金'),'料金プランを確認')
    # Script-derived plan summary plus the topic-specific satellite term.
    plans=[data]
    if carrier=='LINEMO': plans += ['衛星通信：月額そのまま（対象プラン）','2026年冬（予定）までは申し込みが必要']
    elif carrier=='ahamo': plans += ['衛星通信：当面、追加料金なし・申し込み不要']
    else: plans += ['衛星通信：専用プラン+ 月額1,650円','申し込み月から3カ月0円']
    labels = ['月額料金','衛星通信の料金','申込条件']
    table='<table class="sheet"><tbody>'+''.join(f'<tr><th>{labels[i] if i < len(labels) else "補足"}</th><td>{esc(p)}</td></tr>' for i,p in enumerate(plans))+'</tbody></table>'
    return f'''<!-- Slide ID: {esc(slide_id)} -->
<div class="slide-container price-note" style="--brand:{b};--brand-deep:{d};--brand-soft:{soft}"><div class="book"><div class="spine"></div>
<div class="page left"><div class="head-left"><img class="logo" src="public/images/logo/{logo}" alt="{esc(carrier)}"></div><div class="visual chart"><img src="public/images/charts/{chart}" alt="{esc(carrier)}の評価チャート"></div></div>
<div class="page right"><div class="page-head">{esc(carrier)}の料金プラン</div><div class="page-body center">{table}</div></div>
</div></div>'''

def generic(slide_id: str, content: str) -> str:
    seg=split_content(content)
    if not seg: seg=[content]
    heading=seg[0]
    # Remove chapter prefix from heading, retaining a concise editorial label.
    heading=re.sub(r'^第\d+章[／ ]*','',heading)
    facts=seg[1:]
    if not facts: facts=[heading]
    # Two-column story: first half gives the core, second half carries conditions/caveats.
    pivot=(len(facts)+1)//2
    left=facts[:pivot]; right=facts[pivot:]
    if not right: right=['選ぶ前に確認','対応機種・利用条件は各社の公式情報で確認']
    def body(items):
        return rows(items, 'fa-solid fa-circle-check')
    price='price-note' if re.search(r'\d[\d,]*円',content) else ''
    custom = {
      '7': ('衛星通信でできること','衛星通信でできないこと・注意点', ['できる：SMSなどのメッセージ','位置情報の共有','YAMAPなど対応アプリのデータ通信'], ['できない：音声通話・110番・119番への電話','使えるアプリは会社・機種で異なる','空が見える場所で利用する']),
      '7-1': ('衛星通信を使うための条件','対応機種と各社の開始時期', ['①空が見える場所にいる','木・岩・建物にさえぎられると利用できない','②スマホが対応機種である'], ['機種・OSは各社ページで確認','au：2025年4月開始','ドコモ・ソフトバンク：2026年4月開始']),
      '9': ('今の回線のまま使えるグループ','もう1回線足すグループ', ['ahamo：当面追加料金なし・申込不要','LINEMO：ベストプラン／ベストプランV。2026年冬（予定）まで申込必要','Y!mobile：シンプル・シンプル2・シンプル3は追加料金なし'], ['povo2.0：専用プラン+を契約','UQ mobile：専用プラン+を契約','今の回線をそのまま使うか、2回線目を足すかで選ぶ']),
      '9-1': ('対象回線とMVNOの注意点','楽天モバイルの提供予定', ['対象はドコモ・au・ソフトバンクのブランド','大手から回線を借りているSIMは対象外','MVNO利用者も第6章の方法で専用プラン+を追加できる'], ['楽天モバイルは2026年度第4四半期に提供予定と発表','料金・対応機種は未発表','最新情報は公式発表を確認']),
      '12': ('LINEMO×衛星通信の特徴','使える機能と注意点', ['衛星通信中もLINEのテキストを送受信できる','位置情報も送受信できる','LINEギガフリーとは別に衛星通信として利用'], ['スタンプ・絵文字・画像・動画は使えない','音声通話・ビデオ通話も不可','2026年冬（予定）まで申込が必要。月額1,650円を全額割引']),
      '21': ('au Starlink Direct 専用プラン+概要','利用条件と回線仕様', ['povo2.0・UQ mobile・他社回線の人が2回線目として契約','au ICカード／eSIMに対応','既存回線と衛星用回線をデュアルSIMで併用'], ['デュアルSIM対応機種が必要','データ通信は月1GB','音声通話には非対応']),
      '22': ('専用プラン+の月額料金','初期費用と還元条件', ['povo2.0・他社回線：月1,650円','申し込んだ月から3カ月0円','UQ mobile コミコミプランバリュー・トクトクプラン2：0円','UQ mobile その他のプラン：4カ月目から550円'], ['事務手数料：4,950円','au Online Shop：3,850円','au PAY残高で還元。1名義につき1回のみ']),
      '23': ('au Starlink Direct SOS','通報の仕組みと注意点', ['SOSはSOSセンター経由で緊急通報受理機関へつながる','センターが通報を代行する仕組み','専用プラン+契約者も対象・追加料金なし'], ['救助活動の実施や成功を保証するものではない','緊急時は状況・位置を正確に伝える','衛星通信の利用条件も事前に確認']),
      '24': ('申し込むタイミングのコツ','シーズンに合わせる活用術', ['事務手数料の還元は1名義1回だけ','最初の契約を登山シーズン直前に合わせる','3カ月0円の期間を登山シーズンに活用'], ['大手から回線を借りているSIMのままでも追加できる','利用開始前に対応機種・空の見える場所を確認','申し込み条件は公式情報で確認']),
      '26': ('店舗で相談できる2社の特徴','料金比較と注意点', ['Y!mobile：シンプル・シンプル2・シンプル3は衛星通信が追加料金なし','UQ mobile：専用プラン+を追加','両社とも当チャンネル評価の店舗サポートはSS'], ['Y!mobile シンプル3M：30GB・月額4,378円','UQ mobile コミコミプランバリュー：35GB・月額3,828円','割引なしでは月額が割高になりやすい']),
      '28-1': ('月額目安（データ少なめ・3GB前後）','月額目安（データ多め・30GB前後）', ['ahamo：3,135円（40GBまで）〔2026年12月1日〜〕','LINEMO：990円','povo2.0：2,640円（3GB 990円＋専用プラン+ 1,650円）','UQ mobile：2,948円（トクトクプラン2・5GB・割引なし）'], ['ahamo：3,135円（40GBまで）','LINEMO：2,970円（ベストプランV）','povo2.0：4,430円（30GB 2,780円＋専用プラン+ 1,650円）','UQ mobile：3,828円（コミコミプランバリュー・35GB・割引なし）','※povo2.0は専用プラン+の3カ月0円終了後']),
    }
    if slide_id in custom:
        lh, rh, litems, ritems = custom[slide_id]
        # Tables suit data comparisons better than prose cards.
        if slide_id == '22':
            lbody = '<table class="sheet"><tbody><tr><th>対象</th><th>月額</th></tr><tr><td>povo2.0・他社回線</td><td>1,650円<br><span class="sub">申込月から3カ月0円</span></td></tr><tr><td>UQ コミコミプランバリュー<br>・トクトクプラン2</td><td>0円</td></tr><tr><td>UQ その他のプラン</td><td>4カ月目から550円</td></tr></tbody></table>'
            rbody = '<table class="sheet"><tbody><tr><th>初期費用</th><td>4,950円</td></tr><tr><th>au Online Shop</th><td>3,850円</td></tr><tr><th>還元条件</th><td>au PAY残高で還元<br><span class="sub">1名義につき1回のみ</span></td></tr></tbody></table>'
        elif slide_id == '26':
            lbody = rows(litems,'fa-solid fa-circle-check')
            rbody = '<table class="sheet"><tbody><tr><th>Y!mobile</th><td>シンプル3M<br>30GB・4,378円</td></tr><tr><th>UQ mobile</th><td>コミコミプランバリュー<br>35GB・3,828円</td></tr><tr><th>条件</th><td>割引なしの月額目安</td></tr></tbody></table>'
        elif slide_id == '28-1':
            def price_table(items, header):
                lines=[]
                for item in items:
                    m=re.match(r'([^：]+)：(.*)',item)
                    if m: lines.append(f'<tr><th>{esc(m.group(1))}</th><td>{esc(m.group(2))}</td></tr>')
                return f'<table class="sheet"><thead><tr><th>会社</th><th>{esc(header)}</th></tr></thead><tbody>'+''.join(lines)+'</tbody></table>'
            lbody=price_table(litems,'少なめ（3GB前後）')
            rbody=price_table(ritems,'多め（30GB前後）')
        elif slide_id == '23':
            lbody=rows(litems[:2],'fa-solid fa-satellite')
            rbody=rows([litems[2]],'fa-solid fa-circle-check')+'<div class="warn"><span class="ic fa-solid fa-triangle-exclamation"></span><span class="em">救助活動の実施や成功を保証するものではありません</span></div>'
        else:
            lbody, rbody = rows(litems,'fa-solid fa-circle-check'), rows(ritems,'fa-solid fa-circle-check')
        return shell(slide_id,esc(lh),lbody,esc(rh),rbody,RED,price)
    if slide_id == '28':
        left=['① 手間なし・データ多め → ahamo','当面無料・申し込み不要／40GBまで月額3,135円（税込）〔2026年12月1日〜〕','② 安さ重視・LINEをよく使う → LINEMO','3GB 月額990円／衛星通信でLINEのテキストを送受信']
        right=['③ 普段は使う分だけ・2回線設定もできる → povo2.0','基本料0円＋専用プラン+（月1,650円）／au系だけのSOS機能','④ お店で相談したい → Y!mobile・UQ mobile','全国のお店で直接相談／Y!mobileは対象プランで追加料金なし']
        return shell(slide_id,'登山する人の4つの選び方',rows(left,'fa-solid fa-person-hiking'),'使い方に合うSIMを選ぶ',rows(right,'fa-solid fa-person-hiking'),RED,'price-note')
    return shell(slide_id,esc(heading),body(left), '補足と確認ポイント',body(right), RED, price)

def summary(slide_id: str, content: str) -> str:
    left=['① 衛星通信は空が見える場所で使う','メッセージ中心。音声通話・110番・119番への電話はできない','格安SIMでも山で連絡する手段を持てる']
    right=['② ahamo・LINEMO・Y!mobileは今の回線のまま使える','povo2.0・UQ mobileは専用プラン+を追加','③ 手間なしならahamo／安さ・LINE重視ならLINEMO','使う分だけならpovo2.0／店舗相談ならY!mobile・UQ mobile']
    return shell(slide_id,'衛星通信の特徴',rows(left,'fa-solid fa-circle-check'),'自分に合う1枚を選ぶ',rows(right,'fa-solid fa-circle-check'),RED)

def footer(slide_id: str, content: str) -> str:
    if '公式サイト' in content:
        left='<div class="bigicon fa-solid fa-circle-info"></div>'+lead('ご注意','big-title')
        right='<div class="warn"><span class="ic fa-solid fa-triangle-exclamation"></span><span class="em">料金・条件は動画投稿時点の情報です</span></div>'+lead('申し込み前に各社公式サイトをご確認ください','note')+lead('LINEMOの詳細はソフトバンクの公式サイト（https://www.linemo.jp/）でご確認ください','note')
        return shell(slide_id,'ご確認ください',left,'公式情報をご確認ください',right)
    if 'コメント' in content:
        return shell(slide_id,'コメントありがとうございます',f'<div class="bigicon fa-solid fa-comment-dots"></div><div class="big-title">あなたの使い方・<br>山での電波を<br>教えてください</div>', 'ぜひ教えてください',rows(['よく行く山での電波状況','あなたの使い方・活用方法','分かりにくかった点や質問'],'fa-solid fa-comment-dots'))
    if 'ブログ' in content or 'note' in content:
        return shell(slide_id,'通信費の見直し情報',rows(['スマホ代は毎月の固定費','見直して浮いた分は貯蓄や運用にも','自分に合う1枚が分かる動画を作っています'],'fa-solid fa-pen-to-square'),'ブログ・noteも公開中',f'<div class="visual blog-visual"><img src="public/images/common/ブログ_ヘッダー画像_スライド用.png" alt="ブログ"></div>{lead("通信費の見直し情報を発信", "lead")}{lead("概要欄からご覧ください", "note")}' )
    return shell(slide_id,'ご視聴ありがとうございました','<div class="big-title">チャンネル登録<br>よろしく<br>お願いします！</div>','応援よろしくお願いします',f'<div class="logos"><span class="fa-solid fa-thumbs-up"></span><span class="fa-solid fa-bell"></span></div>{lead("高評価・チャンネル登録で応援してください")}{lead("ご視聴ありがとうございました！", "emph")}')

def render(slide_id: str, content: str) -> str:
    if slide_id in {'1','2','3'}:
        if slide_id=='1':
            return std(slide_id,'格安SIMにしたら<br><span class="intro-red">山で圏外</span>？<br>連絡できない？','登山中のもしもに備える','<img class="intro-figure" src="public/images/irasutoya/shinpai_man.png" alt="圏外に困る人">')
        if slide_id=='2':
            return std(slide_id,'登山する人に<br>おすすめの<br><span class="intro-red">格安SIM</span>は？','友達からの相談')
        return std(slide_id,'ドコモ・au・ソフトバンク<br><span class="intro-red">衛星通信</span>を開始','格安SIMでも山の連絡手段を持てる','<div class="intro-logos"><img src="public/images/logo/docomo_logo.png" alt="ドコモ"><img src="public/images/logo/au_logo.png" alt="au"><img src="public/images/logo/Softbank_logo.png" alt="ソフトバンク"></div>')
    if slide_id=='4':
        return std(slide_id,'登山で圏外でも<br><span class="intro-red">連絡できる</span>格安SIMは？<br><span class="intro-count">4</span>つの選び方','2026年最新｜格安SIM図鑑')
    if slide_id=='5': return agenda(content)
    if re.fullmatch(r'\d+-0',slide_id) and content.startswith('第'):
        return chapter(slide_id,content)
    if content.startswith('評価見開き／'):
        return eval_plan(slide_id,content) if slide_id.endswith('-0') else eval_detail(slide_id,content)
    if slide_id == '30': return summary(slide_id,content)
    if slide_id == '28' and content.startswith('比較まとめ見開き／'): return generic(slide_id,content)
    if content.startswith('比較まとめ見開き／'): return summary(slide_id,content)
    if slide_id in {'31','32','33','34'}: return footer(slide_id,content)
    if '過去動画もチェック' in content or 'サムネイル表示' in content:
        # Use a matching existing thumbnail as the visual lead.
        name='LINEMO' if 'LINEMO' in content else ('ahamo' if 'ahamo' in content else 'povo')
        path={'LINEMO':'41_【2026年9月】LINEMO','ahamo':'50_【2026年12月】ahamo','povo':'36_【2026年最新】povo'}[name]
        thumbs=sorted((ROOT/'public/images/thumbnails').glob(path+'*_サムネ1.png'))
        img=thumbs[0].name if thumbs else ''
        title = 'povo2.0' if name == 'povo' else name
        topic_note = {'ahamo':'料金改定の注意点や対策を詳しく','povo':'トッピングの活用法や注意点を詳しく'}.get(name,'衛星通信の条件や設定をさらに詳しく')
        return shell(slide_id,'過去動画もチェック',f'<div class="visual"><img src="public/images/thumbnails/{esc(img)}" alt="関連動画"></div>',f'{esc(title)}の解説動画',f'<div class="bigicon fa-solid fa-circle-play"></div><div class="big-title">{esc(title)}の解説動画も<br>チェック！</div>{lead(topic_note, "note")}')
    return generic(slide_id,content)

def main():
    with MASTER.open(encoding='utf-8-sig', newline='') as f:
        rows_csv=list(csv.DictReader(f))
    slides=[]
    seen=set()
    for row in rows_csv:
        sid=(row.get('スライドID') or '').strip()
        content=(row.get('スライドに表示する内容') or '').strip()
        if not sid or sid in seen: continue
        seen.add(sid)
        slides.append(render(sid,content))
    style='''
<style>
.slide-container.std{width:1280px;height:720px;flex-shrink:0;position:relative;overflow:hidden;display:flex;align-items:center;justify-content:center;padding:44px;background:#fff;border:12px solid #C8102E;box-sizing:border-box}
.std-burst{position:absolute;inset:0;background:repeating-conic-gradient(from 0deg at 50% 45%,rgba(200,16,46,.08) 0deg 5deg,transparent 5deg 10deg)}
.std-copy{position:relative;z-index:1;width:100%;display:flex;flex-direction:column;align-items:center;text-align:center;gap:25px}
.std-kicker{font-size:48px;font-weight:900;color:#9a0c23}.std-title{font-size:86px;font-weight:900;line-height:1.17;color:#212121;text-wrap:balance;word-break:auto-phrase}.std-title .intro-red{color:#C8102E;text-decoration:underline;text-decoration-thickness:8px;text-underline-offset:10px}.std-title .intro-count{font-size:1.35em;color:#C8102E}.intro-logos{display:flex;align-items:center;justify-content:center;gap:24px}.intro-logos img{width:210px;height:82px;object-fit:contain;padding:12px 20px;background:#fff;border:3px solid #eee;border-radius:18px;box-shadow:0 8px 18px #0002}.intro-figure{position:absolute;right:55px;bottom:42px;z-index:0;width:auto;height:250px;object-fit:contain}.std-copy{z-index:1}
.std-footer{font-size:42px;font-weight:900;background:#C8102E;color:white;padding:12px 28px;border-radius:14px}
.page-head{font-size:54px}.page-body{gap:16px}.rows{gap:14px}.rows>li{padding:12px 18px;align-items:center}.rows .tx{font-size:39px;font-weight:800;line-height:1.17}.rows .ic{font-size:38px;flex:0 0 52px}
.agenda{gap:10px}.agenda li{font-size:35px;gap:14px}.agenda .num{width:54px;height:54px;font-size:30px}.benefits{gap:20px}.benefits li{font-size:37px}
.divider{margin:auto}.big-title{font-size:76px;text-align:center}.lead{font-size:42px;font-weight:800;text-align:center}.note{font-size:30px;font-weight:700;text-align:center}
.head-left{height:150px;flex:0 0 150px}.head-left .logo{max-width:300px;height:90px}.total .grade{font-size:95px}.cards{gap:8px;justify-content:space-evenly}.card{flex:0 0 auto;grid-template-columns:78px 1fr;gap:3px 12px;padding:8px 14px}.card .rank{width:70px;height:70px;font-size:38px}.card-name{font-size:36px}.card .line{font-size:30px;font-weight:700;white-space:normal;line-height:1.08}.eval-head-right{height:105px;flex:0 0 105px}.eval-head-title{font-size:50px}.page:has(.cards) .cards .card{min-height:0}.page:has(.head-left) .chart img{width:100%;max-height:680px}.page-body:has(.sheet){gap:10px}.page-body:has(.sheet) .sheet{height:100%}.sheet{font-size:34px}.sheet th,.sheet td{padding:20px 16px}.blog-visual{height:auto;flex:0 0 auto}.blog-visual img{width:100%;max-height:420px;object-fit:contain}
.chart{flex:1;display:flex;justify-content:center;align-items:center;min-height:0}.chart img{max-width:100%;max-height:100%;object-fit:contain}.sheet{width:100%;font-size:34px}.sheet th,.sheet td{padding:16px}.visual img{max-width:100%;max-height:500px;object-fit:contain}.blog-visual img{max-height:320px}.page.left:has(.divider){justify-content:center}.page.left:has(.divider) .page-head{display:none}.page.left:has(.divider) .page-body{justify-content:center;align-items:center}.page.left:has(.divider) .divider{margin:0 auto}.logos{display:flex;justify-content:center;gap:70px;font-size:130px;color:var(--brand);padding:28px}
</style>'''
    html_doc='''<!doctype html><html lang="ja"><head><meta charset="utf-8"><title>登山で圏外でも連絡できる格安SIM</title>
<link href="https://fonts.googleapis.com/css2?family=M+PLUS+Rounded+1c:wght@400;500;700;800;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css"><link rel="stylesheet" href="templates/spread-base.css">'''+style+'</head><body>'+ '\n'.join(slides)+'</body></html>'
    OUT.write_text(html_doc,encoding='utf-8')
    print(f'Wrote {OUT} ({len(slides)} slides)')

if __name__=='__main__': main()
