#!/usr/bin/env python3
"""Generate video 45 from the master CSV; edit this generator, never slides.html.

Run: python3 /workspaces/yt-factory/packages/slide-gen/scripts/generate_his45_slides.py
Capture with npm --prefix /workspaces/yt-factory/packages/slide-gen run capture-slides-html -- --local-only.
Slide IDs 18-0/18/18-1 were renumbered in the master CSV (minimal cell diff only)
to add the required radar-chart+pricing pair (18-0) before the 6-axis evaluation
detail (18); the former 18 (evaluation wrap-up) moved to 18-1. All image paths
are relative (public/images/...) per generate-html-slides SKILL.md §4.
"""
import csv
import hashlib
import html
import json
import re
from pathlib import Path

ROOT = Path('/workspaces/yt-factory/packages/slide-gen')
MASTER = Path('/workspaces/yt-factory/packages/scenario-gen/archive/videos/45_【9月17日開始】HISモバイル新プラン自由自在3.0！30GB1,999円は買いか/long/【9月17日開始】HISモバイル新プラン自由自在3.0！30GB1,999円は買いか.csv')
OUTPUT = ROOT / 'slides.html'
ASSETS = ROOT / 'public/images'
RATINGS = Path('/workspaces/yt-factory/shared/sim_evaluations.json')
GROUPS = {}
for row in csv.DictReader(MASTER.open(encoding='utf-8-sig', newline='')):
    sid = row['スライドID'].strip()
    if not sid:
        continue
    group = GROUPS.setdefault(sid, {'contents': [], 'dialogue': []})
    content = row['スライドに表示する内容'].strip()
    if content and content != '同上' and content not in group['contents']:
        group['contents'].append(content)
    group['dialogue'].append(row['セリフ'])


def esc(text):
    return html.escape(str(text))


def txt(text):
    """Preserve numeric units and carrier names through Japanese line wrapping."""
    value = esc(text)
    return re.sub(r'(?:\d+月\d+日|移行方法|月?[\d,]+(?:[〜・][\d,]+)?(?:\.\d+)?(?:GB|MB|Mbps|円|分|日間)|HISモバイル|日本通信SIM|楽天モバイル|自由自在[23]\.0)',
                  r'<span style="white-space:nowrap">\g<0></span>', value)


def source(sid):
    return '／'.join(GROUPS[sid]['contents'])


def parts(sid):
    return re.sub(r'^(テロップ：|タイトル：)', '', source(sid)).split('／')


def excerpt(sid, needle, replacement=None):
    """Source-keyed editing: fail if a later CSV revision invalidates the layout."""
    assert needle in source(sid), (sid, needle)
    return replacement if replacement is not None else needle


def div(cls, content, style=''):
    return f'<div class="{cls}"' + (f' style="{style}"' if style else '') + f'>{content}</div>'


def lead(text): return div('lead', txt(text))
def warn(text): return div('warn', txt(text))
def note(text): return div('note', txt(text), 'font-size:28px')
def emph(label, big=None): return div('emph', txt(label) + (f'<br><span class="big">{txt(big)}</span>' if big else ''), 'padding:28px 44px')
def title(text):
    # Final phrase breaks selected after inspecting every rendered slide.
    breaks = {
        '自由自在3.0で何が変わったのか': ['自由自在3.0で', '何が', '変わったのか'],
        '30GB「2,000円の壁」が破られた': ['30GB', '2,000円の壁が', '破られた'],
        '他の格安SIMと比べて本当に安いのか': ['他の格安SIMと', '比べて本当に', '安いのか'],
        'HISモバイルの独自評価': ['HISモバイルの', '独自評価'],
        'HISモバイルの解説動画': ['HISモバイルの', '解説動画'],
        '日本通信SIMの解説動画': ['日本通信SIMの', '解説動画'],
        '楽天モバイルの2枚持ち3選': ['楽天モバイルの', '2枚持ち3選'],
        '9月17日の受付開始': ['9月17日の', '受付開始'],
        '予備回線の選び方': ['予備回線の', '選び方'],
        '貯蓄・資産運用に': ['貯蓄・', '資産運用に'],
        'チャンネル登録よろしくお願いします！': ['チャンネル登録', 'よろしく', 'お願いします！'],
    }
    return div('big-title', '<br>'.join(txt(line) for line in breaks.get(text, [text])))
def icon(name): return div('bigicon', f'<i class="fa-solid fa-{name}"></i>')


def img(rel, alt, cls='', style=''):
    p = ASSETS / rel
    assert p.is_file(), p
    return f'<img src="public/images/{esc(rel)}" alt="{esc(alt)}" class="{cls}" style="{style}">'


def logo(name='HISモバイル'):
    names = {'HISモバイル':'hismobile_logo.png', '日本通信SIM':'nihon_tsushin.jpg', 'mineo':'Mineo_logo.png', 'povo2.0':'Povo_logo.png', '楽天モバイル':'Mobile_logo_1line_magenta.png'}
    return div('logos', img('logo/' + names[name], name))


def rows(items):
    return '<ul class="rows">' + ''.join(f'<li><span class="badge">{i}</span><div class="tx">{txt(x)}</div></li>' for i,x in enumerate(items,1)) + '</ul>'


def sheet(headers, data, compact=False):
    cell_style = ' style="padding:8px 18px"' if compact else ''
    return '<table class="sheet"><thead><tr>' + ''.join(f'<th{cell_style}>{txt(x)}</th>' for x in headers) + '</tr></thead><tbody>' + ''.join('<tr>'+''.join(f'<td{cell_style}>{txt(x)}</td>' for x in row)+'</tr>' for row in data) + '</tbody></table>'


def page(side, heading, blocks, body_class=''):
    return div('page '+side, ('<span class="index-tab">格安SIM図鑑</span>' if side=='right' else '') + (div('page-head', txt(heading)) if heading else '') + div('page-body '+body_class, ''.join(blocks)))


def spread(sid, lh, left, rh, right):
    return page('left', lh, left) + page('right', rh, right)


CHAPTER_LEADS = ['料金の変更点と新特典を確認','割引条件なしの通常料金で比較','容量・通話・繰越で選ぶ','6つの観点でメリットと注意点','使い方に合う2枚目を選ぶ','自分に合う選択をおさらい']
THUMB_KEYS = {'16-2':'【2026年最新】20GBで1,390円', '18-5':'旅行会社のSIMと侮るな', '24-2':'43_'}


def intro(sid):
    p = parts(sid)
    if sid == '1':
        kicker=excerpt(sid,'HISモバイル新プラン「自由自在3.0」登場','新プラン「自由自在3.0」登場')
        headline=excerpt(sid,'30GBがまさかの1,999円？','30GBがまさかの')+'<br><strong>1,999円？</strong>'
        chips=['毎月のスマホ代、どこまで下がる？']
    elif sid == '2':
        kicker=excerpt(sid,'公式発表2026-08-28','2026年8月28日 公式発表')
        headline=excerpt(sid,'2026年9月17日10:00受付開始予定','9月17日 10:00')+'<br><strong>受付開始予定</strong>'
        chips=['2026年 新プラン「自由自在3.0」']
    elif sid == '3':
        kicker=p[0]+'｜自分の使い方がカギ'
        headline=excerpt(sid,'毎月コンスタントに30GBを使う人には良いプラン','毎月30GB使う人に')+'<br><strong>有力な選択肢！</strong>'
        chips=['20GBで足りる人・大容量を使う人','他のSIMの方が安い可能性も']
    else:
        kicker=excerpt(sid,'【9月17日受付開始予定】','9月17日 受付開始予定')
        headline='自由自在3.0<br><strong>30GB 1,999円</strong>'
        chips=[excerpt(sid,'契約するべきか？','契約するべき？ 料金・比較・独自評価')]
    return div('std-rays','')+div('std-copy', logo()+div('std-kicker',txt(kicker))+f'<h1>{headline}</h1>'+div('std-chips',''.join(f'<span>{txt(c)}</span>' for c in chips)))


def radar_price_pair(sid):
    left=div('page left',div('head-left',img('logo/hismobile_logo.png','HISモバイル','logo'))+div('visual evaluation-radar',img('charts/HISモバイル.png','HISモバイルの6観点評価レーダーチャート')))
    table=sheet(['容量','月額'],[['3GB','770円'],['20GB','1,699円'],['30GB','1,999円']])
    right=div('page right','<span class="index-tab">格安SIM図鑑</span>'+div('page-head','HISモバイルの料金プラン')+div('page-body',table+div('lead tight',txt('契約期間の縛りなし・解約金0円'))))
    return left+right


def evaluation(sid):
    raw=source(sid)
    entries=re.findall(r'([^／]+?):(SS|S|A|B|C)（＋(.*?)／－(.*?)）',raw)
    assert len(entries)==6
    rating=next(r for r in json.loads(RATINGS.read_text()) if r['name']=='HISモバイル')
    keys=['data_price','quality','initial_cost','call_charges','support','options']
    # Source prose is retained in the audit report; summarize cards per skill §10.2.
    compact = [
        ('3GB770円・20GB1,699円・30GB1,999円', '20GB・50GBは日本通信SIMが割安'),
        ('ドコモ回線で大手並みのエリア', '昼・夕方は低速化しやすい。ドコモのみ'),
        ('契約解除料0円で始めやすい', '事務手数料3,300円は平均的'),
        ('9円/30秒・20GBと30GBは6分無料', '無制限1,480円。6分無料は2.0から'),
        ('提携修理店などで契約後の有償支援', '全国の専売店で全対応はできない'),
        ('新特典：海外4GB・15日間・年1回無料', 'eSIM対応端末が必要。繰越は非対応'),
    ]
    cards=[]
    for (name,rank,pro,con),key,(pro,con) in zip(entries,keys,compact):
        rank=rating['scores'][key]
        cards.append(div('card',div('rank '+rank,rank)+div('card-name',txt(name))+div('line pro','<span class="tag">＋</span>'+txt(pro))+div('line con','<span class="tag">－</span>'+txt(con)), 'flex:0 0 auto;grid-template-columns:104px 1fr;gap:3px 14px;padding:10px 16px'))
    head=div('head-left',img('logo/hismobile_logo.png','HISモバイル','logo')+div('total',div('label','総合評価')+div('grade',rating['overall'])), 'height:146px;flex-shrink:0')
    left=div('page left',head+div('cards',''.join(cards[:3])))
    right=div('page right','<span class="index-tab">格安SIM図鑑</span>'+div('cards',''.join(cards[3:]),'margin-top:52px')+note('※本評価は当チャンネルの独断と偏見による独自評価であり、キャンペーン割引等は考慮していません'))
    return left+right


def render(sid):
    p=parts(sid)
    if sid in ('1','2','3','4'): return intro(sid)
    if re.fullmatch(r'第\d章 .+',source(sid)):
        match=re.fullmatch(r'第(\d)章 (.+)',source(sid)); n=int(match[1])
        badge=div('divider',div('kicker','CHAPTER')+div('num',n)+div('seal',f'FILE No.{n:02}'))
        return div('page left',badge)+page('right','',[title(match[2]),lead(CHAPTER_LEADS[n-1])])
    if sid in THUMB_KEYS:
        name={'16-2':'日本通信SIM','18-5':'HISモバイル','24-2':'楽天モバイル'}[sid]
        candidates=sorted((ASSETS/'thumbnails').glob(THUMB_KEYS[sid]+'*.png'))
        assert candidates
        visual=div('visual',img(str(candidates[0].relative_to(ASSETS)),p[0]),'height:auto')
        return spread(sid,'過去動画でくわしく',[visual,lead('徹底解説をチェック！')],'',[icon('play'),title(name+'の'+('2枚持ち3選' if sid=='24-2' else '解説動画')),note('概要欄からチェックできます')])
    if sid=='5':
        labels=['自由自在3.0の変更点','30GB「2,000円の壁」','他の格安SIMとの比較','HISモバイル独自評価','楽天モバイルの予備回線','まとめ']
        agenda='<ul class="agenda">'+''.join(f'<li><span class="num">{n}</span>{txt(x)}</li>' for n,x in enumerate(labels,1))+'</ul>'
        benefits='<ul class="benefits">'+''.join('<li><span class="check">✓</span>'+txt(x)+'</li>' for x in ['新プランの全料金と変更点がわかる','自分は乗り換えるべきかがわかる'])+'</ul>'
        return spread(sid,'格安SIM図鑑 もくじ',[agenda],'わかること',[benefits,warn('値下げの中心は20GB・30GB。受付開始は9月17日予定')])
    if sid=='6-1':return spread(sid,p[1],[logo(),lead(excerpt(sid,'旅行会社のH.I.S.グループが運営するMVNO'))],'通信のしくみ',[rows(['設備・システムは日本通信が提供','ドコモ回線のみ。回線は選べない']),lead('自由自在3.0は9月17日受付開始予定')])
    if sid=='7':
        stable=re.findall(r'(100MB|1GB|3GB|7GB) ([\d,]+円)',source(sid))
        change=re.findall(r'(10GB|20GB|30GB) ([\d,]+円)→([\d,]+円)（▲([\d,]+円)）',source(sid))
        return spread(sid,'小容量は据え置き',[sheet(['容量','月額料金'],stable),lead('100MB〜7GBは変化なし')],'10GB以上は値下げ',[sheet(['容量','2.0 → 3.0'],[(a,b+' → '+c) for a,b,c,d in change]),lead('30GBは毎月971円の値下げ')])
    if sid=='8':return spread(sid,'新特典：海外eSIM',[logo(),lead(p[2]),lead('1電話番号につき年1回無料。新規・既存とも対象')],'年1回、無料に',[emph('海外130以上の国・地域','4GB・15日間'),warn('提供開始は10月1日予定。9月17日とは別日')])
    if sid=='9':return spread(sid,'既存ユーザーの移行',[icon('triangle-exclamation'),emph('自由自在2.0 → 3.0','公式案内待ち')],'まだ確定していません',[warn('MyHISモバイルの「サービス変更」から無料移行できる可能性'),lead('正式な手順・適用条件は公式発表を待つ'),note('※無料での移行は現時点で公式未確定')])
    if sid=='11':
        data=[['HISモバイル','1,999円'],['ahamo','2,970円'],['LINEMO','2,970円'],['UQ mobile','4,048円'],['Y!mobile','4,378円']]
        for row in data:
            assert row[0] in source(sid) and row[1] in source(sid)
        return spread(sid,'30GB帯の通常料金',[sheet(['サービス','月額'],data),note('LINEMO：ベストプランV／UQ mobile：トクトクプラン2／Y!mobile：シンプル3M')],'条件なしで1,999円',[lead('30GBを他社で契約中なら検討の余地あり'),warn('条件付き割引後はUQ mobile 2,728円・Y!mobile 1,958円'),note('※ahamoは増量キャンペーンで現在40GB。終了時期は未発表。左表は割引条件なしの通常料金')])
    if sid=='13':return spread(sid,'容量で比べると',[sheet(['月間容量','HISモバイル','日本通信SIM'],[['20GB','1,699円','1,390円'],['大容量','1,999円\n30GB','2,178円\n50GB']]),lead('日本通信SIMなら＋179円で＋20GB')],'繰越・予備回線',[lead('mineo 30GB 2,178円。繰越対応・3Mbps使い放題が無料'),sheet(['予備回線','月額・容量'],[['日本通信SIM','290円・1GB'],['HISモバイル','280円・100MB']])])
    if sid=='14':return spread(sid,'通話込みで比べる',[logo(),emph('20GB・30GBに付帯','6分かけ放題'),lead('超過分は9円／30秒')],'他社の無料通話',[sheet(['サービス','無料通話／超過分'],[['日本通信SIM','5分または70分／11円・30秒'],['ahamo・LINEMO','5分／22円・30秒']], compact=True),warn('20GB以上・月2,000円未満の無料通話：HISモバイルと日本通信SIM')])
    if sid=='15':return spread(sid,'HISモバイルの強み',[icon('earth-asia'),emph('HIS Travel eSIM','海外4GB')],'海外旅行もカバー',[lead('15日間・年1回無料'),rows(['日本通信SIM・mineoにはない特典','IIJmio・イオンモバイルにもない特典'])])
    if sid=='16':return spread(sid,'HISモバイルが合う人',[logo(),emph('毎月21〜30GB','通話も少し'),lead('年1回の海外旅行もお得に')],'日本通信SIMが合う人',[logo('日本通信SIM'),emph('毎月使う容量が','11〜20GB'),lead('31〜50GB使う人にもおすすめ')])
    if sid=='18-0':return radar_price_pair(sid)
    if sid=='18':return evaluation(sid)
    if sid=='18-1':return spread(sid,'今回変わった評価',[icon('gift'),emph('海外eSIMが新たに付帯','オプション')],'土台は変わらず',[rows(['通信品質は従来どおり','初期費用も従来どおり']),lead('特典の追加と、基本性能を分けて考える')])
    if sid=='19':return spread(sid,'続報を見逃さない',[icon('bell'),title('9月17日の受付開始')],'チャンネル登録',[div('subscribe', '▶ チャンネル登録'),lead('受付開始と移行方法の続報をお届けします')])
    if sid=='21':return spread(sid,'前回の「2枚持ち3選」',[logo('楽天モバイル'),title('予備回線の選び方'),note('当チャンネル #43／2026年8月26日公開')],'目的で選ぶ3社',[rows(['通信品質ならpovo2.0','安さなら日本通信SIM','回線を選ぶならmineo'])])
    if sid=='22':return spread(sid,'HISモバイルの提案',[logo('楽天モバイル'),emph('ドコモ回線を追加','月280円〜'),logo()],'予備回線として',[lead('楽天モバイルに、月280円からドコモ回線をプラス'),warn('狙いは9月30日のKDDIローミング終了'),note('※HISモバイル発表会での提案の趣旨')])
    if sid=='23':return spread(sid,'維持費・データ量',[rows(['維持コスト：povo2.0 基本料0円','安さ＋実用量：日本通信SIM 290円で1GB']),lead('HISモバイルは280円で100MB')],'回線・通話で選ぶ',[rows(['回線を選べる：mineo','通話も使う：HISモバイル 9円／30秒']),lead('予備回線で何を重視するかが決め手')])
    if sid=='24':return spread(sid,'予備回線の結論',[logo('楽天モバイル'),lead('基本の候補は前回の3選'),lead('povo2.0・日本通信SIM・mineo')],'HISモバイルは？',[icon('plane-departure'),lead('年に1回は海外旅行へ行く人なら選択肢に入る'),note('海外eSIM特典を使うかどうかで判断')])
    if sid=='26':return spread(sid,'新プランをおさらい',[emph('2026年9月17日','10:00'),lead('自由自在3.0 受付開始予定')],'変更点はこの2つ',[emph('20GB 1,699円','30GB 1,999円'),lead('新たに海外eSIMが年1回無料に')])
    if sid=='27':return spread(sid,'1,999円の安さを理解',[logo(),emph('毎月30GBを使うなら','有力候補'),warn('昼・夕方は低速化。繰越なし・ドコモ回線のみ')],'自分は乗り換える？',[lead('容量・通話・海外旅行で自分に合うか判断'),warn('価格だけで決めず、通信品質と使い方を確認')])
    if sid=='28':return spread(sid,'申し込みは待って！',[icon('hand'),warn(excerpt(sid,'自由自在2.0への申込は待ってください'))],'30GBの月額',[emph('今、自由自在2.0なら','2,970円'),emph('9月17日の3.0開始後','1,999円'),note('※受付開始予定。既存契約の移行方法は公式案内待ち')])
    if sid=='29':return spread(sid,'今やることは1つ',[emph('毎月のデータ使用量を','確認しよう'),lead('9月17日、移行方法が判明次第このチャンネルでお届け')],'使い方で選ぼう',[rows(['21〜30GB＋通話・海外旅行：HISモバイル','11〜20GB・31〜50GB：日本通信SIM','回線選択・実質使い放題：mineo'])])
    if sid=='30':return spread(sid,'',[icon('circle-info'),title('ご注意')],'最新は公式サイトへ',[warn(p[0]),lead(p[1]),note('料金・プラン・キャンペーンの条件を申込前に確認')])
    if sid=='31':return spread(sid,'ブログ・noteも',[icon('pen-nib'),title('解説中！'),lead('リンクは概要欄から')],'コメントも募集中',[div('visual',img('common/ブログ_ヘッダー画像_スライド用.png','格安SIM図鑑のブログ','','width:100%;height:auto;max-height:280px'),'height:auto'),lead('使い方・エリアの通信品質・わかりづらかった点を教えてね！')])
    if sid=='32':return spread(sid,'固定費を見直そう',[icon('piggy-bank'),emph('スマホ代を見直して','毎月のゆとり')],'浮いた分を未来へ',[title('貯蓄・資産運用に'),lead('自分に合うプランで、固定費を抑えよう')])
    if sid=='33':return spread(sid,'',[icon('bell'),title('チャンネル登録よろしくお願いします！')],'',[div('logos',icon('thumbs-up')+icon('bell')),lead('ご視聴いただきありがとうございました！'),note('グッドボタンもよろしくお願いします')])
    raise ValueError('No layout: '+sid)


CSS = '''
.slide-container.std { width:1280px;height:720px;border:10px solid var(--brand);background:#fffaf5;padding:34px; }
.std-rays { position:absolute;inset:-35%;background:repeating-conic-gradient(from -12deg at 50% 50%,#005bac12 0 6deg,transparent 6deg 13deg); }
.std-copy { position:relative;width:100%;display:flex;flex-direction:column;align-items:center;text-align:center;gap:16px; }
.std-copy .logos {background:white;border-radius:18px;padding:14px 34px;box-shadow:0 8px 18px #0002;}
.std-copy .logos img {height:64px;max-width:380px;}
.std-kicker {font-size:48px;font-weight:900;line-height:1.25;}
.std-copy h1 {font-size:86px;line-height:1.14;font-weight:900;text-shadow:4px 4px white;}
.std-copy h1 strong {font-size:108px;color:#c8102e;}
.std-chips {display:flex;flex-wrap:wrap;gap:12px;justify-content:center;}
.std-chips > span {font-size:44px;font-weight:900;background:white;border:4px solid var(--brand);border-radius:20px;padding:10px 24px;line-height:1.2;}
.subscribe {align-self:center;padding:26px 34px;border-radius:999px;background:#e90033;color:white;font-size:52px;font-weight:900;box-shadow:0 9px #a50020;}
'''


def main():
    slides=[]
    for sid in GROUPS:
        content=render(sid)
        is_intro=sid in ('1','2','3','4')
        price=bool(re.search(r'[\d,]+円',re.sub('<[^>]+>','',content))) or sid in THUMB_KEYS
        classes='slide-container'+(' std' if is_intro else '')+(' price-note' if price else '')
        if not is_intro:content=div('book',div('spine','')+content)
        slides.append(f'<!-- Slide ID: {sid} -->\n'+div(classes,content,'--brand:#005bac;--brand-deep:#00447f;--brand-soft:#e3f0fb'))
    document='<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HISモバイル 自由自在3.0｜格安SIM図鑑</title>'
    document+='<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=M+PLUS+Rounded+1c:wght@700;800;900&amp;display=swap"><link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">'
    document+=f'<link rel="stylesheet" href="templates/spread-base.css"><style>{CSS}</style></head><body>\n'
    document+='\n'.join(slides)+'\n</body></html>\n'
    ids=re.findall(r'<!-- Slide ID: ([\d-]+) -->',document)
    assert ids==list(GROUPS), 'CSV/HTML ID mismatch'
    OUTPUT.write_text(document)
    report={'master':str(MASTER),'master_sha256':hashlib.sha256(MASTER.read_bytes()).hexdigest(),'html':str(OUTPUT),'generator':str(Path(__file__).resolve()),'slide_count':len(ids),'std_count':4,'spread_count':len(ids)-4,'id_changes':{'18-0(旧)':'18','18(旧・まとめ)':'18-1'},'source_groups':GROUPS,'ids':ids,'notes':['18-0=レーダーチャート+料金プラン、18=6観点評価詳細、18-1=評価まとめ。SKILL.mdの必須N-0/Nペアルールに準拠。','画像パスはすべて public/images/... からの相対パス。']}
    (ROOT/'out/generation-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(f'Generated {len(ids)} slides: {OUTPUT}\nCSV/HTML IDs match; CSV unchanged.')


if __name__=='__main__':main()
