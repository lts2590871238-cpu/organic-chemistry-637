"""Restore every native solution page; never change question/scoring data."""
import sys,json,re,hashlib,datetime
from pathlib import Path
S=Path(__file__).resolve().parents[1];sys.path.insert(0,str(S/'.cache/pylibs'))
import pymupdf as fitz
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
anspath=S/'public/data/answers.json';answers=read(anspath);questions=read(S/'public/data/questions.json')
baseline=S/'audit/ANSWER_REPAIR_BEFORE.json'
if not baseline.exists():
 save(baseline,{'answers':answers,'protected':{str(p.relative_to(S)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (S/'public/data').glob('*.json') if p!=anspath}})
records=[]
for paper in 'ABC':
 doc=fitz.open(S/f'public/papers/mock-{paper}-solutions.pdf');starts=[];sections=[]
 for pi,pg in enumerate(doc):
  for block in pg.get_text('dict')['blocks']:
   for ln in block.get('lines',[]):
    text=''.join(sp['text'] for sp in ln['spans'])
    if re.match(r'^[一二三四五六]、',text.strip()):sections.append((pi,ln['bbox'][1]-3))
    m=re.fullmatch(r'(\d+)．（(\d+)\s*分）',text.strip())
    if m:starts.append((pi,ln['bbox'][1]-3,int(m[1]),int(m[2])))
 qs=[q for q in questions if q['id'].startswith(paper+'-')]
 assert len(starts)==len(qs)==43,(paper,len(starts))
 for idx,(pi,y,no,score) in enumerate(starts):
  q=qs[idx];assert int(q['id'].split('Q')[1])==no and q['score']==score,(q['id'],no,score)
  endpi,endy=starts[idx+1][:2] if idx+1<len(starts) else (len(doc)-1,doc[-1].rect.height-35)
  # A following section heading belongs to the next question, not a continuation.
  for boundary in sections:
   if (pi,y)<boundary<(endpi,endy):endpi,endy=boundary;break
  refs=[];texts=[];pages=[]
  for page in range(pi,endpi+1):
   pg=doc[page];top=y if page==pi else 48;bottom=endy if page==endpi else pg.rect.height-35
   if bottom<=top:continue
   clip=fitz.Rect(45,top,pg.rect.width-45,bottom)
   text=pg.get_text(clip=clip).strip()
   paths=[x for x in pg.get_drawings() if fitz.Rect(x['rect']).intersects(clip)]
   if not text and not paths:continue
   rects=[]
   for block in pg.get_text('dict')['blocks']:
    for ln in block.get('lines',[]):
     box=fitz.Rect(ln['bbox'])
     if clip.contains(box):rects.append(box)
   rects.extend(fitz.Rect(x['rect'])&clip for x in paths)
   if not rects:continue
   bb=rects[0]
   for box in rects[1:]:bb|=box
   clip=fitz.Rect(bb.x0-6,bb.y0-6,bb.x1+6,bb.y1+6)&clip
   assert not pg.get_images(),('not native',paper,page)
   # Page crop retains the actual compiled native paths, not screenshots.
   cropdoc=fitz.open();cropdoc.insert_pdf(doc,from_page=page,to_page=page)
   cp=cropdoc[0];cp.set_cropbox(clip)
   svg=cp.get_svg_image(text_as_path=True);assert '<image' not in svg
   name='answer'+hashlib.sha256((paper+':'+str(idx)+':'+str(page)+':'+svg).encode()).hexdigest()[:18]+'.svg'
   ref='assets/'+name;(S/'public'/ref).write_text(svg,encoding='utf-8');refs.append(ref);texts.append(text);pages.append(page+1);cropdoc.close()
  assert refs,q['id']
  u=answers[q['id']]['units'][0]
  old=u['figures'];u['figures']=refs
  u['completeSolutionSource']={'pdf':f'papers/mock-{paper}-solutions.pdf','pages':pages,'nativeVector':True}
  records.append({'id':q['id'],'pages':pages,'figures_before':len(old),'figures_after':len(refs),'source_text_characters':sum(map(len,texts)),'first_text':texts[0][:100],'last_text':texts[-1][-160:]})
 doc.close()
save(anspath,answers)
used={ref for a in answers.values() for u in a['units'] for ref in u['figures']}
assetdir=(S/'public/assets').resolve()
for p in assetdir.glob('answer*.svg'):
 assert p.resolve().parent==assetdir
 if 'assets/'+p.name not in used:p.unlink()
used={ref for a in answers.values() for u in a['units'] for ref in u['figures']}
assetdir=(S/'public/assets').resolve()
for p in assetdir.glob('answer*.svg'):
 assert p.resolve().parent==assetdir
 if 'assets/'+p.name not in used:p.unlink()
save(S/'audit/ANSWER_PAGE_RESTORATION.json',{'at':datetime.datetime.now().astimezone().isoformat(),'records':records,'questions':len(records),'multi_page_questions':sum(len(r['pages'])>1 for r in records),'native_svg_pages':sum(r['figures_after'] for r in records),'note':'既有原生LaTeX解析的全页接入；非重新化学终验，不采用教材扫描。'})
print(json.dumps({'restored_questions':len(records),'multi_page':sum(len(r['pages'])>1 for r in records),'native_pages':sum(r['figures_after'] for r in records)},ensure_ascii=False))
