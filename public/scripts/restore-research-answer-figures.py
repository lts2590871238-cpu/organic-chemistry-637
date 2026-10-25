"""Compare all current historical units; restore omitted native diagram fields/pages."""
import sys,json,hashlib,datetime,collections
from pathlib import Path
S=Path(__file__).resolve().parents[1];R=Path('D:/桌面/637有机化学真题研究工作区')
sys.path.insert(0,str(S/'.cache/pylibs'))
import pymupdf as fitz
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
answers=read(S/'public/data/answers.json');baseline=read(S/'audit/ANSWER_REPAIR_BEFORE.json')['answers']
questions={q['id']:q for q in read(S/'public/data/questions.json')}
issues=[];rows=[];assetcache={};counts=collections.Counter();rendered=0
def paths(u):
 result=[]
 for key in ['vector_pdf','extra_vector_pdfs','shared_vector_pdf','nitrosation_native_preparation_pdfs','vector_pdfs']:
  value=u.get(key,[])
  for p in value if isinstance(value,list) else [value]:
   if isinstance(p,str) and p.lower().endswith(('.pdf','.svg')) and p not in result:result.append(p)
 return result
def assets(source):
 global rendered
 f=Path(source.replace('\\','/'));f=f if f.is_absolute() else R/f
 if str(f) in assetcache:return assetcache[str(f)]
 if not f.exists():issues.append({'kind':'missing_source','path':source});return []
 out=[]
 if f.suffix=='.svg':
  txt=f.read_text(encoding='utf-8')
  if '<image' in txt:issues.append({'kind':'raster_source','path':source});return []
  name=hashlib.sha256((str(f)+':0').encode()).hexdigest()[:18]+'.svg';(S/'public/assets'/name).write_text(txt,encoding='utf-8');out=['assets/'+name]
 else:
  d=fitz.open(f)
  for pi,p in enumerate(d):
   if p.get_images():issues.append({'kind':'raster_source','path':source,'page':pi+1});continue
   rects=[fitz.Rect(b[:4]) for b in p.get_text('blocks') if len(b)>4 and str(b[4]).strip()]
   rects += [fitz.Rect(x['rect']) for x in p.get_drawings()]
   if not rects:continue
   bb=rects[0]
   for b in rects[1:]:bb|=b
   bb=fitz.Rect(bb.x0-8,bb.y0-8,bb.x1+8,bb.y1+8)&p.rect
   if not bb.is_empty:p.set_cropbox(bb)
   txt=p.get_svg_image(text_as_path=True);assert '<image' not in txt
   name=hashlib.sha256((str(f)+':'+str(pi)).encode()).hexdigest()[:18]+'.svg';dest=S/'public/assets'/name
   if not dest.exists():dest.write_text(txt,encoding='utf-8');rendered+=1
   out.append('assets/'+name)
  d.close()
 assetcache[str(f)]=out;return out
for pid,a in answers.items():
 if not questions[pid].get('year'):continue
 year=pid[:4];maps={};files=[]
 for rnd in ['第二轮','第三轮']:
  f=R/f'03_独立答案推导/{rnd}/{year}/{pid}.json'
  if not f.exists():continue
  d=read(f);files.append(str(f.relative_to(R)))
  for u in d.get('units',[]):maps[u['unit_id']]=u
 for u in a['units']:
  uid=u['id'];source=maps.get(uid);old=next(x for x in baseline[pid]['units'] if x['id']==uid)
  refs=[];ps=[];diff=[]
  if source:
   ps=paths(source)
   for key,src in [('answer','answer'),('derivation','derivation'),('checks','chemical_checks'),('teaching','teaching')]:
    if src in source and u.get(key)!=source[src]:diff.append(key)
  efile=R/f'03_独立答案推导/集中疑题/{uid}.json'
  if efile.exists():
   e=read(efile);ps+=paths(e)
   if u.get('editorial'):
    for key in ['question','answer','teaching']:
     src='editorial_question' if key=='question' else key
     if u['editorial'].get(key)!=e.get(src):diff.append('editorial.'+key)
  for p in dict.fromkeys(ps):refs.extend(assets(p))
  refs=list(dict.fromkeys(refs))
  for ref in u['figures']:
   if ref not in refs:refs.append(ref)
  u['figures']=refs;counts['units']+=1
  if source:counts['compared_with_round2_or_3']+=1
  if u.get('editorial'):counts['editorial_teaching_restored_to_renderer']+=1
  if refs!=old['figures']:counts['units_with_figure_changes']+=1
  if '机理' in questions[pid]['type'] and refs!=old['figures']:counts['mechanism_units_with_figure_changes']+=1
  rows.append({'id':uid,'parent':pid,'type':questions[pid]['type'],'source_files':files,'source_vectors':list(dict.fromkeys(ps)),'before':old['figures'],'after':refs,'text_differences':diff,'derivation_steps':len(u['derivation']),'teaching_sections':len(u['teaching']),'editorial_teaching_sections':len(u.get('editorial',{}).get('teaching',{})) if u.get('editorial') else 0})
save(S/'public/data/answers.json',answers)
save(S/'audit/ANSWER_SOURCE_RESTORATION.json',{'at':datetime.datetime.now().astimezone().isoformat(),'counts':counts,'new_native_svgs':rendered,'unique_source_files':len(assetcache),'issues':issues,'records':rows,'scope':'逐单元对照已有源记录，补全遗漏图字段和所有页；不重新宣称化学终验。'})
print(json.dumps({'counts':counts,'new_native_svgs':rendered,'source_files':len(assetcache),'issues':issues,'text_differences':[(r['id'],r['text_differences']) for r in rows if r['text_differences']]},ensure_ascii=False))
