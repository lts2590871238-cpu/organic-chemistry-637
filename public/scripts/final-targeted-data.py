"""Site-only final scheduling/score repair; immutable chemistry payloads are checked."""
from pathlib import Path
import collections, copy, hashlib, json
S=Path(__file__).resolve().parents[1]
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,x): p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
qfile=S/'public/data/questions.json';dfile=S/'public/data/days.json'
baseline=S/'audit/TARGETED_BEFORE.json'
if not baseline.exists():
    write(baseline,{'questions':read(qfile),'days':read(dfile),
        'protected':{str(p.relative_to(S)):hashlib.sha256(p.read_bytes()).hexdigest()
          for folder in ['public/assets','public/papers'] for p in (S/folder).glob('*') if p.is_file()}|
          {f'public/data/{name}.json':hashlib.sha256((S/f'public/data/{name}.json').read_bytes()).hexdigest()
           for name in ['answers','cards','analytics','syllabus']}})
b=read(baseline);qs=copy.deepcopy(b['questions']);days=copy.deepcopy(b['days'])
pool=[q for q in qs if 2013<= (q['year'] or 0)<=2020]
assert len(pool)==324 and all(10<=q['day']<=15 for q in pool)
overrides={}
def group(level,reason,ids):
    for id in ids.split():
        assert id not in overrides,id
        overrides[id]={'difficulty':level,'reason':reason}
group('D3','绝对构型/桥环编号/糖投影需结合结构读取，并非仅背常用名。', '''2013-S01-Q01 2013-S01-Q03 2013-S01-Q07 2013-S01-Q08
2014-S01-Q01 2014-S01-Q03 2014-S01-Q06 2014-S01-Q08 2014-S01-Q09
2015-S01-Q04 2015-S01-Q06 2015-S01-Q07 2015-S01-Q10
2018-S01-Q01 2018-S01-Q03 2018-S01-Q06 2018-S01-Q08 2018-S01-Q10
2019-S01-Q01 2019-S01-Q03 2019-S01-Q04 2019-S01-Q05 2019-S01-Q06
2020-S01-Q04 2020-S01-Q08 2020-S01-Q10 2020-S02-Q01 2020-S02-Q08''')
group('D3','现有推导需串联官能团变化、区域选择或两种条件比较，超过单步直接反应判断。', '''2013-S02-Q02 2013-S02-Q06 2013-S02-Q07
2014-S02-Q01 2014-S02-Q02 2014-S02-Q04 2014-S02-Q05 2014-S02-Q09
2015-S02-Q01 2015-S02-Q03 2015-S02-Q05 2015-S02-Q06 2015-S02-Q07
2016-S01-Q03 2016-S01-Q04 2016-S01-Q07 2016-S01-Q10 2016-S01-Q11
2017-S02-Q02 2017-S02-Q03 2017-S02-Q05 2017-S02-Q07 2017-S02-Q09
2018-S02-Q04 2018-S02-Q05 2018-S02-Q06 2018-S02-Q09
2019-S02-Q02 2019-S02-Q04 2019-S02-Q05 2019-S02-Q11 2019-S02-Q18
2020-S02-Q05 2020-S02-Q10''')
group('D4','现有解答含多步定位/保护、立体继承、成环或竞争分支；原先按填空题统一D2明显低估。', '''2013-S02-Q05 2013-S02-Q08
2014-S02-Q06 2014-S02-Q07 2014-S02-Q08
2015-S02-Q04 2015-S02-Q08 2015-S02-Q09
2016-S01-Q01 2016-S01-Q02 2016-S01-Q05 2016-S01-Q06 2016-S01-Q08
2017-S02-Q01 2017-S02-Q04 2017-S02-Q08
2018-S02-Q01 2018-S02-Q02 2018-S02-Q07 2018-S02-Q08
2019-S02-Q06 2019-S02-Q09 2019-S02-Q10 2019-S02-Q12 2019-S02-Q13
2020-S02-Q03''')
group('D3','排序需同时核对介质/反应模型、谱学或多个电子效应，保留已有适用边界。', '''2013-S03-Q03 2013-S03-Q05 2014-S03-Q07 2014-S03-Q10
2015-S03-Q04 2015-S03-Q06 2015-S03-Q07 2016-S02-Q02 2016-S02-Q05 2016-S02-Q06
2017-S03-Q04 2017-S03-Q07 2017-S03-Q09 2018-S03-Q07 2018-S03-Q10
2019-S03-Q02 2019-S03-Q04 2020-S03-Q02 2020-S03-Q04''')
group('D4','须区分整体手性/构象锁定、多个碱性位点或酸酐双峰比较口径，选项短不等于推理简单。',
      '2019-S03-Q01 2019-S03-Q06 2020-S01-Q14 2020-S03-Q08 2017-S03-Q08')
group('D4','串联成环或逆开环/异位再闭环需逐步追踪碳骨架和电子流。',
      '2013-S04-Q01 2016-S05-Q02 2017-S05-Q02 2018-S05-Q02 2020-S06-Q03')
group('D2','基础链反应的引发/传递/终止，按既有完整弯箭即可直接练习。','2015-S05-Q01')
group('D2','Br2桥式加成的固定两步及反式关系，适合作简单机理入门。','2019-S06-Q02')
group('D2','常规pKa差与单步平衡式，采用已有明确修订口径，不涉及多步结构推断。','2017-S04-Q03')
group('D2','两个甲基单峰与对位芳环对称的常规一维NMR识别，适作简单结构入门。','2020-S04-Q02')
group('D2','苯酰化后常规格氏加成的两项核心转化，无保护或迂回定位。','2019-S07-Q01')
group('D3','已知转化串联或有限谱学/立体证据的整合，无困难合成的多分支设计。', '''2013-S05-Q01 2013-S05-Q02
2014-S04-Q01 2014-S04-Q02 2014-S04-Q03 2014-S04-Q06
2015-S04-Q01 2017-S04-Q01 2017-S04-Q05 2017-S04-Q06
2018-S04-Q01 2018-S04-Q03 2018-S04-Q04 2018-S04-Q06 2019-S08-Q01 2020-S04-Q03''')
group('D3','现成反应模板构成的有限路线；保留关键选择性要求，不再因合成题型一律D4。',
      '2013-S07-Q01 2015-S06-Q02 2016-S06-Q03 2018-S06-Q03 2020-S07-Q02')
group('D3','简答实际要求投影互换、整体对称或gauche效应比较，需要多项依据而非单一概念复述。',
      '2013-S06-Q01 2013-S06-Q02 2019-S04-Q03 2020-S05-Q02')
group('D4','椅式翻转同时比较叔丁基与两个甲基的位阻，现有推导明确需要非加和相互作用判断。','2016-S04-Q03')
byid={q['id']:q for q in qs};ans=read(S/'public/data/answers.json');reviews=[]
for id,v in overrides.items():
    q=byid[id];assert q in pool
    reviews.append({'id':id,'old':q['difficulty'],'new':v['difficulty'],'reason':v['reason'],
      'basis':'既有答案/结构推导人工编排复核；原v0.14候选主要按题型判级，非学生实测难度。',
      'answer_excerpt':' / '.join(u['answer'] for u in ans[id]['units'])[:450]})
    q['difficulty']=v['difficulty']
# Estimate working time, not empirical student timing. Keep whole dependent parents.
def minutes(q):
    base={'D2':3,'D3':7,'D4':12}[q['difficulty']]
    if q['type'] in ['结构推导','多步合成','反应机理']:base+=4
    return base+min(8,max(0,len(q['unitIds'])-1)*2)
families=['选择判断','命名与绘结构','填空待细分','反应产物填空','排序比较','概念简答','实验与试剂','反应机理','结构推导','多步合成']
for level,daypair in [('D2',[10,11]),('D3',[12,13]),('D4',[14,15])]:
    bins={d:[] for d in daypair};times={d:0 for d in daypair};points={d:0 for d in daypair}
    for typ in families:
        items=sorted([q for q in pool if q['difficulty']==level and q['type']==typ],key=lambda q:(-minutes(q),q['id']))
        for q in items:
            dest=min(daypair,key=lambda d:(sum(x['type']==typ for x in bins[d]),times[d],points[d],len(bins[d]),d))
            bins[dest].append(q);times[dest]+=minutes(q);points[dest]+=q['score'] or 0;q['day']=dest
    # Swap whole same-type parents only: retain type coverage while balancing
    # both estimated work and reliably known points (never invent missing scores).
    left,right=daypair
    def imbalance():
        return abs(times[left]-times[right])/max(1,sum(times.values()))*2+abs(points[left]-points[right])/max(1,sum(points.values()))
    for _ in range(60):
        best=None;value=imbalance()
        for a in bins[left]:
            for z in bins[right]:
                if a['type']!=z['type']:continue
                dt=minutes(z)-minutes(a);dp=(z['score'] or 0)-(a['score'] or 0)
                candidate=abs(times[left]-times[right]+2*dt)/max(1,sum(times.values()))*2+abs(points[left]-points[right]+2*dp)/max(1,sum(points.values()))
                if candidate<value-1e-9:best=(a,z,dt,dp);value=candidate
        if best is None:break
        a,z,dt,dp=best;bins[left].remove(a);bins[right].remove(z);bins[left].append(z);bins[right].append(a)
        a['day']=right;z['day']=left;times[left]+=dt;times[right]-=dt;points[left]+=dp;points[right]-=dp
    for day in daypair:
        items=bins[day]
        if level=='D2':items.sort(key=lambda q:(families.index(q['type']),q['year'],q['id']))
        else:
            queues={t:sorted([q for q in items if q['type']==t],key=lambda q:q['id']) for t in families};items=[]
            while any(queues.values()):
                for t in families:
                    if queues[t]:items.append(queues[t].pop(0))
        days[day-1]['ids']=[q['id'] for q in items];days[day-1]['minutes']=times[day]
        days[day-1]['title']={'D2':'简单递进','D3':'中等混编','D4':'困难混编'}[level]+('Ⅰ' if day==daypair[0] else 'Ⅱ')
assert collections.Counter(q['id'] for q in pool)==collections.Counter(id for d in days[9:15] for id in d['ids'])
# Day 8/9 navigation reuses the exact primary chapter used by the existing
# migration; do not move a single question or infer chapters from wrong answers.
R=Path(r'D:\桌面\637有机化学真题研究工作区')
classes=read(R/'04_题型与难度分析/2004-2026_逐任务分类候选_v0.14.json')['rows']
primary={}
for row in classes:
    primary.setdefault(row['parent_id'],row.get('primary_chapter_candidate') or (row.get('chapter_candidates') or ['C19'])[0])
labels={'C13':'醛酮','C14':'羧酸及其衍生物','C15':'双官能团化合物','C16':'胺及含氮化合物','C17':'杂环','C18':'糖','C19':'氨基酸与肽'}
methods={'C13':['M-CARBONYL_羰基加成合成','D08_M_缩合与共轭加成'],'C14':['D08_M_酰基反应与互变'],'C15':['D08_M_缩合与共轭加成'],
 'C16':['D09_M_含氮酸碱与反应位点','D09_M_重氮合成与保护顺序'],'C17':['D09_M_含氮酸碱与反应位点'],'C18':['D09_M_糖投影及反应追踪'],'C19':['D09_M_含氮酸碱与反应位点']}
for day,codes in [(8,['C13','C14','C15']),(9,['C16','C17','C18','C19'])]:
    sections=[{'title':labels[code],'ids':[id for id in days[day-1]['ids'] if primary[id]==code],'methodCards':methods[code]} for code in codes]
    assert sorted(id for section in sections for id in section['ids'])==sorted(days[day-1]['ids'])
    days[day-1]['sections']=[section for section in sections if section['ids']]
# Independently visible blank counts. Q02 and Q07 are deliberately unresolved:
# an unlabelled arrow is not assigned points simply to make the section sum 31.
counts={1:1,3:1,4:1,5:1,6:2,8:1,9:1,10:1,11:2,12:1,13:2,14:1,15:1,16:1,17:2,18:1,19:1,20:1,21:3,22:2}
score_review=[]
for n,count in counts.items():
    id=f'2023-S02-Q{n:02}';byid[id]['score']=count
    byid[id]['scoreBasis']='2023原页二：每空1分；逐空核对独立作答位置，见audit/TARGETED_SCORE_REVIEW.json。'
    score_review.append({'id':id,'blank_count':count,'points':count,'source_printed_page':95 if n<=5 else 96 if n<=17 else 97})
write(S/'audit/TARGETED_SCORE_REVIEW.json',{'2023':{'verified_blank_parents':score_review,'unresolved':['2023-S02-Q02','2023-S02-Q07'],'section_printed_total':31,'verified_section_points':sum(counts.values()),'reason':'Q02/Q07未标空的箭头节点与作答范围无法唯一对应；不凭合计倒推。','sources':['补传扫描_20261016_预览/2023-P02-350.png','全卷OCR草稿/页图_300dpi/2023/2023-P03_A017.jpg','全卷OCR草稿/页图_300dpi/2023/2023-P04_A018.jpg']},'2022':{'known_points':110,'unallocated_points':40,'unresolved':[f'2022-S06-Q{n:02}' for n in range(1,6)],'reason':'已整理THIRD_ROUND及清晰补传P04/P05未提供五题独立印分；保留未知，不均分。'}})
def stats(questions,plans):
    return [{'day':day,'questions':len(a:=[q for q in questions if q['day']==day]),'types':dict(collections.Counter(q['type'] for q in a)),
      'difficulty':dict(collections.Counter(q['difficulty'] for q in a)),'estimated_minutes':sum(minutes(q) for q in a),'known_points':sum(q['score'] or 0 for q in a),'unknown_score_questions':sum(q['score'] is None for q in a)} for day in range(10,16)]
write(S/'audit/TARGETED_SCHEDULE.json',{'before':stats(b['questions'],b['days']),'after':stats(qs,days),'difficulty_corrections':reviews,
 'original_difficulty_basis':'04_题型与难度分析/2004-2026_逐任务分类候选_v0.14.json：D2单一基础/D3机制/D4综合，原以题型作为代理；只作逐项有依据纠正。',
 'minutes_basis':'编排估计：D2/3/4基础3/7/12分钟；机理/推导/合成加4；每个额外关联小问加2、最多加8。非学生实测，不按题型独立判难度。',
 'same_parent_set':True,'duplicate_ids':[],'missing_ids':[]})
for q in qs:
    old=next(x for x in b['questions'] if x['id']==q['id']);changes={k for k in q if q.get(k)!=old.get(k)}
    assert changes<=({'day','difficulty'} if q in pool else {'score','scoreBasis'} if q['id'] in {x['id'] for x in score_review} else set()),(q['id'],changes)
write(qfile,qs);write(dfile,days)
print(json.dumps({'after':stats(qs,days),'2023_known':sum(q['score'] or 0 for q in qs if q['year']==2023),'corrections':len(reviews)},ensure_ascii=False))
