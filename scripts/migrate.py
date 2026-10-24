"""Read-only migration of research records; native vector PDFs become vector SVGs."""
import sys, json, re, hashlib, shutil, collections, datetime
from pathlib import Path
SITE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(SITE/'.cache/pylibs'))
import fitz
R=Path(r'D:\桌面\637有机化学真题研究工作区')
OUT=SITE/'public'; DATA=OUT/'data'; ASSETS=OUT/'assets'
for p in [DATA,ASSETS,SITE/'audit']:p.mkdir(exist_ok=True,parents=True)
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
issues=[]; cache={}; docs={}
def path(s):
 p=Path(str(s).replace('\\','/'))
 return p if p.is_absolute() else R/p
def asset(s,page=0,clean=False):
 if not s:return None
 f=path(s); key=(str(f),page,clean)
 if key in cache:return cache[key]
 if not f.is_file():issues.append({'kind':'missing_asset','path':str(f)});return None
 if f.suffix.lower() not in ['.svg','.pdf']:return None
 h=hashlib.sha256((str(f)+':'+str(page)+(':clean-native-v1' if clean else '')).encode()).hexdigest()[:18]; dest=ASSETS/(h+'.svg')
 if f.suffix.lower()=='.svg':
  txt=f.read_text(encoding='utf-8')
  if '<image' in txt:issues.append({'kind':'raster_embedded_not_migrated','path':str(f)});return None
  dest.write_text(txt,encoding='utf-8')
 else:
  if dest.exists():
   value='assets/'+dest.name;cache[key]=value;return value
  if str(f) not in docs:
   if len(docs)>=24:docs.pop(next(iter(docs))).close()
   docs[str(f)]=fitz.open(f)
  doc=docs[str(f)]
  if page>=len(doc):issues.append({'kind':'missing_pdf_page','path':str(f),'page':page});return None
  pg=doc[page]
  if clean:
   for b in pg.get_text('dict')['blocks']:
    for ln in b.get('lines',[]):
     text=''.join(sp.get('text','') for sp in ln['spans'])
     if ('PDF' in text and ('印刷' in text or '印制' in text or '印' in text)) or text.startswith('原书') or '本页只做题源第一轮' in text or '原文未统一规定单选或多选' in text:pg.add_redact_annot(ln['bbox'],fill=(1,1,1))
   pg.apply_redactions(images=0,graphics=0)
  rects=[fitz.Rect(b[:4]) for b in pg.get_text('blocks') if len(b)>4 and str(b[4]).strip()]
  rects.extend(fitz.Rect(d['rect']) for d in pg.get_drawings())
  if rects:
   bb=rects[0]
   for b in rects[1:]:bb|=b
   bb=fitz.Rect(bb.x0-8,bb.y0-8,bb.x1+8,bb.y1+8)&pg.rect
   if not bb.is_empty:pg.set_cropbox(bb)
  dest.write_text(pg.get_svg_image(text_as_path=True),encoding='utf-8')
 value='assets/'+dest.name;cache[key]=value;return value
def clean_tex(text):
 text=str(text or '')
 def image(m):
  a=asset(m[1]);return '\n[[asset:'+a+']]\n' if a else '\n【原生图件缺失，待接入】\n'
 text=re.sub(r'\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}',image,text)
 text=re.sub(r'\\(?:noindent|vfill|clearpage|newpage|bigskip|smallskip|medskip)\b',' ',text)
 text=re.sub(r'\\vspace\{[^}]+\}','',text)
 text=re.sub(r'\\(?:begin|end)\{(?:center|minipage)\}(?:\{[^}]+\})?','',text)
 text=text.replace(r'\par','\n').replace(r'\quad',' ').replace(r'\qquad',' ______ ')
 text=re.sub(r'\\\\(?:\[[^]]*\])?','\n',text)
 return text.strip()
classes=read(R/'04_题型与难度分析/2004-2026_逐任务分类候选_v0.14.json')['rows']
byunit={x['task_id']:x for x in classes}; byparent=collections.defaultdict(list)
for x in classes:byparent[x['parent_id']].append(x)
ci=read(R/'12_教学卡片/TEACHING_CARDS_INDEX.json'); cards=[]
for b in ci['batch_summary']:
 for id in b['sequence']:
  f=R/'12_教学卡片/正式内容'/(id+'.json'); c=read(f)
  md=f.with_suffix('.md').read_text(encoding='utf-8')
  cards.append({'id':id,'day':int(c.get('learning_day',b['day'])[1:]),'kind':c.get('kind','method' if '_M_' in id else 'knowledge'),'title':c.get('title',md.splitlines()[0].lstrip('# ').strip()),'body':md,'points':c.get('syllabus_points',[]),'linked':list(dict.fromkeys(c.get('worked_units',[])+c.get('related_units',[])+c.get('transfer_units',[]))),'figures':[a for g in c.get('figures',[]) if (a:=asset(g.get('pdf')))],'source_status':c.get('status'),'sources':c.get('sources',[])})
cardByPoint=collections.defaultdict(list)
for c in cards:
 for p in c['points']:cardByPoint[p].append(c['id'])
edits={f.stem:read(f) for f in (R/'03_独立答案推导/集中疑题').glob('20??-S??-Q??-P??.json')}
qbank=[]; answers={}; scores_unknown=[]
for yr in list(range(2004,2021))+[2022,2023]:
 f=R/f'02_真题逐题拆解/第三轮题干校准/{yr}/THIRD_ROUND.json'
 if not f.exists():issues.append({'kind':'missing_year_stems','year':yr});continue
 ps=read(f)['parents']
 for id,p in sorted(ps.items()):
  af=R/f'03_独立答案推导/第三轮/{yr}/{id}.json'
  if not af.exists():af=R/f'03_独立答案推导/第二轮/{yr}/{id}.json'
  ad=read(af) if af.exists() else {}; unitmap={}
  # Merge by stable independent-unit ID; never add unidentified blank placeholders.
  for roundname in ['第一轮','第二轮','第三轮']:
   earlier=R/f'03_独立答案推导/{roundname}/{yr}/{id}.json'
   if not earlier.exists():continue
   for u in read(earlier).get('units',[]):
    uid=u.get('unit_id') or u.get('task_id') or u.get('id')
    if uid and uid in p.get('unit_ids',[]):unitmap[uid]={**u,'unit_id':uid}
  for uid in p.get('unit_ids',[]):
   if uid not in unitmap and uid in edits:unitmap[uid]={'unit_id':uid,'answer':'原题存在缺损或条件问题，请对照下方独立编辑修订。'}
  units=list(unitmap.values())
  cs=byparent[id]; points=list(dict.fromkeys(p for x in cs for p in x.get('knowledge_point_candidates',[])))
  score=p.get('parent_printed_score'); tx=p.get('question_tex',ad.get('question_tex',''))
  if score is None:
   m=re.search(r'每(?:小)?题\s*(\d+(?:\.\d+)?)分',tx)
   if m:score=float(m[1])
   else:
    # Chapter headings carry section totals, not the score of each following question.
    no=int(id.split('Q')[-1]); start=re.search(r'(?<!\d)'+str(no)+r'[.．、]',tx)
    individual=tx[start.end():] if start else re.sub(r'^(?:\\noindent\s*)?[一二三四五六七八九十][、.．][^\n]*(?:\\par|\n|$)','',tx)
    m=re.search(r'[（(](\d+(?:\.\d+)?)分[）)]',individual)
    if m:score=float(m[1])
   # An independent task can contain several blanks. Do not equate unit count to points.
  if score is None:scores_unknown.append(id)
  typ=cs[0].get('method_family_candidate',cs[0].get('question_type_candidate','综合')) if cs else '综合'
  ds=[x.get('difficulty_candidate','D3') for x in cs]; difficulty=max(ds or ['D3'])
  cids=list(dict.fromkeys(i for pt in points for i in cardByPoint[pt]))
  # Preserve existing candidate classification, and mark its status honestly.
  chapter=(cs[0].get('primary_chapter_candidate') if cs else None) or (cs[0].get('chapter_candidates') or ['C19'])[0]
  chapter_day={'C01':1,'C02':1,'C03':2,'C04':2,'C05':3,'C06':3,'C07':4,'C08':5,'C09':6,'C10':6,'C11':6,'C12':7,'C13':8,'C14':8,'C15':8,'C16':9,'C17':9,'C18':9,'C19':9}
  day=chapter_day.get(chapter,9) if yr<=2012 else (10 if difficulty in ['D1','D2'] else 12 if difficulty=='D3' else 14)
  if yr in [2022,2023]:day=16 if yr==2022 else 17
  raw=clean_tex(tx)
  if p.get('figure'):
   a=asset(p['figure'])
   if a:raw+='\n[[asset:'+a+']]'
  aus=[]
  for u in units:
   uid=u.get('unit_id',''); e=edits.get(uid)
   figures=[]
   for x in ([u.get('vector_pdf')] if u.get('vector_pdf') else [])+(e.get('vector_pdfs',[]) if e else []):
    a=asset(x)
    if a and a not in figures:figures.append(a)
   aus.append({'id':uid,'answer':u.get('answer',''),'derivation':u.get('derivation',[]),'checks':u.get('chemical_checks',[]),'teaching':u.get('teaching',{}),'figures':figures,'editorial':({'question':e.get('editorial_question',''),'answer':e.get('answer',''),'teaching':e.get('teaching',{}),'changes':e.get('changes',e.get('repair_notes',[]))} if e else None)})
  missing=[uid for uid in p.get('unit_ids',[]) if uid not in unitmap]
  answers[id]={'units':aus,'missing':bool(missing) or not aus,'missing_unit_ids':missing,'final_accepted':False}
  if missing or not aus:issues.append({'kind':'missing_answer','id':id,'units':missing})
  edited=any(u.get('editorial') for u in aus);key=None
  if not edited and cs and ('选择' in cs[0].get('question_type_candidate','') or cs[0].get('question_type_candidate')=='choice') and len(aus)==1:
   m=re.match(r'^([A-D])(?:[。．：:、，,\s]|[\u4e00-\u9fff])',aus[0]['answer'])
   if m and not re.search('候选|待核|不唯一|不能.*唯一|条件.*待|原题.*错误',aus[0]['answer']):key=m[1]
  qbank.append({'id':id,'year':yr,'no':int(id.split('Q')[-1]),'section':id.split('-')[1],'type':typ,'score':score,'sectionScore':p.get('section_printed_score'),'raw':raw,'kp':points,'cards':cids,'unitIds':p.get('unit_ids',[]),'difficulty':difficulty,'day':day,'source':{'book':p.get('source_pdf','原卷'),'page':p.get('source_pdf_page')},'edited':edited,'classificationStatus':'candidate','auditStatus':p.get('round_3_status','source_record'),'answerKey':key})
# Split each retained difficulty band into two balanced days, preserving original order.
for lo in [10,12,14]:
 ids=[q for q in qbank if q['day']==lo]
 for i,q in enumerate(ids):q['day']=lo+i%2
for c in cards:
 c['linkedParents']=list(dict.fromkeys(re.sub(r'-P\d+$','',x) for x in c['linked']))
 for q in qbank:
  if q['id'] in c['linkedParents'] and c['id'] not in q['cards']:q['cards'].append(c['id'])
P=R/'13_北大习题集模拟卷'; M=P/'09_正式交付'; mockQ=read(M/'MOCK_QUESTIONS.json')['records']; mockA={x['id']:x for x in read(M/'MOCK_ANSWERS.json')['records']}; mockMarks={x['id']:x for x in read(M/'MOCK_MARKING.json')['records']}
(OUT/'papers').mkdir(exist_ok=True)
for paper in 'ABC':
 for suffix,kind in [('试题','paper'),('详细解析','solutions')]:shutil.copy2(M/f'{paper}卷_{suffix}.pdf',OUT/'papers'/f'mock-{paper}-{kind}.pdf')
sourceCache=read(P/'08_三轮审核/ASSEMBLY_SOURCE_CACHE.json'); pageMaps={}
def question_pages(tex,sid):
 pdf=path(tex).with_suffix('.pdf')
 if not pdf.exists():return []
 if str(pdf) not in pageMaps:
  doc=fitz.open(pdf);mp=collections.defaultdict(list);active=None
  for i,pg in enumerate(doc):
   text=pg.get_text(); match=re.search(r'[ABC]-S\d{2}-Q\d{2}',text[:220])
   if match:active=match[0]
   if active:mp[active].append(i)
  if not mp and len(doc)==1:mp[sid]=[0]
  pageMaps[str(pdf)]=mp;doc.close()
 return [a for n in pageMaps[str(pdf)].get(sid,[]) if (a:=asset(str(pdf),n,True))]
labels=read(P/'08_三轮审核/CHOICE_ANSWER_LABELS.json') if (P/'08_三轮审核/CHOICE_ANSWER_LABELS.json').exists() else {}
for q in mockQ:
 sid=q['id']; paths=sourceCache['paths'].get(sid,{}); stem=question_pages(paths.get('student_tex',''),sid); ans=question_pages(paths.get('teacher_tex',''),sid)
 ev=mockA[sid].get('review_evidence',{}); label=ev.get('answer_label') or ev.get('answer') or '、'.join(ev.get('answer_labels',[]))
 qbank.append({'id':sid,'year':None,'no':int(sid.split('Q')[-1]),'section':q['section'],'type':{'S01':'填空与命名','S02':'选择','S03':'结构推导','S04':'简答','S05':'机理','S06':'合成'}[q['section']],'score':q['score'],'raw':'\n'.join('[[asset:'+x+']]' for x in stem),'kp':q.get('knowledge_topics',[]),'cards':q['teaching_card_ids'],'unitIds':[sid],'difficulty':'强化' if sid[0]=='C' else '综合','day':19+'ABC'.index(sid[0]),'source':{'book':q.get('source_book_id'),'page':q.get('source_id')},'answerKey':label if q['section']=='S02' else None,'auditStatus':'group_three_round_reviewed_whole_paper_pending'})
 answers[sid]={'units':[{'id':sid,'answer':'','derivation':[],'checks':[],'teaching':{'参考采分点':mockMarks[sid]['suggestions']},'figures':ans}],'missing':not ans,'final_accepted':False}
 if not stem or not ans:issues.append({'kind':'missing_mock_vector_pages','id':sid,'stem':len(stem),'answer':len(ans)})
analysis=read(R/'05_四级权重考情分析/2004-2026_知识点原始出现加权_候选.json')
syllabus=read(R/'03_考纲与知识点体系/2027考纲19章_原文条目.json')
titles=['概论与烷烃','烯烃与共轭二烯','环烷烃与炔烃','立体化学','卤代烃','芳香化学与醇酚醚','核磁与红外','醛酮、羧酸衍生物与双官能团','胺、杂环、糖与氨基酸','简单混编Ⅰ','简单混编Ⅱ','中等混编Ⅰ','中等混编Ⅱ','困难混编Ⅰ','困难混编Ⅱ','2022年限时原卷','2023年限时原卷','个性化弱点巩固卷','模拟卷A · 近期型','模拟卷B · 长期综合','模拟卷C · 强化型']
days=[{'day':i+1,'title':t,'ids':[q['id'] for q in qbank if q['day']==i+1],'cards':[c['id'] for c in cards if c['day']==i+1],'minutes':180 if i+1>=16 else None} for i,t in enumerate(titles)]
assert len(cards)==96 and len(days)==21 and not any(q['year']==2021 for q in qbank)
for letter in 'ABC':
 qs=[q for q in qbank if q['id'].startswith(letter+'-')];assert len(qs)==43 and sum(q['score'] for q in qs)==150
source_index={x['id']:x['source_record'] for x in read(M/'SOURCE_INDEX.json')['records']}
for q in qbank:
 if q['id'] in source_index:
  v=source_index[q['id']];v={**v.get('source_record',{}),**v};q['source'].update({'exercise':str(v.get('source_exercise') or v.get('exercise') or v.get('original_question_number') or '')+(' · '+str(v.get('selected_subparts') or v.get('subparts')) if v.get('selected_subparts') or v.get('subparts') else ''),'paper':v.get('source_paper'),'pdfPage':v.get('pdf_page') or v.get('source_pdf_pages') or v.get('pdf_pages') or v.get('source_pages'),'printedPage':v.get('printed_page') or v.get('printed_pages')})
  labels=[o['label'] for o in v.get('options',[]) if isinstance(o,dict) and isinstance(o.get('label'),str)]
  if labels:q['optionLabels']=labels
for q in qbank:
 stems={}
 for u in answers[q['id']]['units']:
  e=u.get('editorial')
  if e and e.get('question'):stems.setdefault(e['question'],[]).append(u['id'])
 if stems:q['editorialStems']=[{'unitIds':ids,'text':text} for text,ids in stems.items()]
# Preserve explicitly reviewed website scoring corrections on future migrations.
score_fixes=read(SITE/'audit/SCORE_CORRECTIONS.json').get('overrides',{}) if (SITE/'audit/SCORE_CORRECTIONS.json').exists() else {}
for q in qbank:
 if q['id'] in score_fixes:q['score']=score_fixes[q['id']]['score'];q['scoreBasis']=score_fixes[q['id']]['basis']
scores_unknown=[q['id'] for q in qbank if q['year'] is not None and q['score'] is None]
save(DATA/'questions.json',qbank);save(DATA/'answers.json',answers);save(DATA/'cards.json',cards);save(DATA/'days.json',days);save(DATA/'analytics.json',analysis);save(DATA/'syllabus.json',syllabus)
audit={'at':datetime.datetime.now().astimezone().isoformat(),'question_parents':len(qbank),'original_parents':len(qbank)-129,'mock_questions':129,'cards':len(cards),'days':len(days),'syllabus_chapters':len(syllabus['chapters']),'native_vector_assets':len(list(ASSETS.glob('*.svg'))),'day_counts':{str(d['day']):len(d['ids']) for d in days},'unknown_original_parent_scores':scores_unknown,'issues':issues,'mock_final_audit_passed':False,'scope':'迁移原始状态，不新增化学终验。候选难度、原题印分缺口、编辑题身份均保留。未复制教材或扫描PDF。'}
save(SITE/'audit/DATA_MIGRATION.json',audit)
print(json.dumps({k:v for k,v in audit.items() if k not in ['unknown_original_parent_scores','issues']},ensure_ascii=False)); print('issues',len(issues),'unknown scores',len(scores_unknown))

# Prefer the site's frozen layout PDFs after optional research migration.
for paper in 'ABC':
 frozen=SITE/'publication/latex'/f'mock-{paper}-solutions.pdf'
 if frozen.exists():shutil.copy2(frozen,SITE/'public/papers'/f'mock-{paper}-solutions.pdf')

# Apply the reviewed marking groups without changing original research files.
import subprocess
subprocess.run([sys.executable,str(SITE/'scripts/review-mock-marking.py')],check=True)
