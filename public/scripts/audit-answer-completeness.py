import json, collections
from pathlib import Path
S=Path(__file__).resolve().parents[1]
R=Path('D:/桌面/637有机化学真题研究工作区')
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
answers=read(S/'public/data/answers.json')
print('Website',len(answers),sum(len(a['units']) for a in answers.values()))
qs=read(S/'public/data/questions.json'); print('q schema',type(qs))
types=collections.Counter(); cases=[];ek=collections.Counter()
for q in qs:
 a=answers.get(q['id'],{}); types[q.get('type','?')]+=1
 for u in a.get('units',[]):
  if u.get('editorial'):
   ek.update(u['editorial'].keys())
  if '机理' in str(q.get('type')) or '机理' in str(q.get('typeLabel')):
   cases.append({'q':q['id'],'qkeys':list(q),'unit':u})
print('types',types,'editorial keys',ek,'mechanisms',len(cases))
print(json.dumps(cases[:2],ensure_ascii=False)[:14000])
print('Mechanism lengths',[(c['q'],c['unit']['id'],len(c['unit']['derivation']),len(c['unit']['figures']),bool(c['unit'].get('editorial'))) for c in cases])
print('Mock mechanism example',json.dumps(answers['A-S05-Q01'],ensure_ascii=False)[:8000])
print('Editorial example',json.dumps(next(u for a in answers.values() for u in a['units'] if u.get('editorial')),ensure_ascii=False)[:9000])
(S/'audit/ANSWER_COMPLETENESS_INVENTORY.json').write_text(json.dumps({'types':types,'editorial_keys':ek,'mechanisms':cases},ensure_ascii=False,indent=2),encoding='utf-8')
for folder in ['第一轮','第二轮','第三轮','集中疑题']:
 fs=list((R/'03_独立答案推导'/folder).rglob('20??-S??-Q??*.json'));ks=collections.Counter();uks=collections.Counter()
 for f in fs:
  d=read(f);ks.update(d.keys())
  for u in d.get('units',[]):uks.update(u.keys())
 print(folder,len(fs),'top',dict(ks),'units',dict(uks))
 if folder=='集中疑题' and fs:
  print('Sample',fs[0].name,json.dumps(read(fs[0]),ensure_ascii=False)[:7000])
