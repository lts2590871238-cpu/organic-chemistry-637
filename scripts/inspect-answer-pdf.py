import sys,json,re
from pathlib import Path
S=Path(__file__).resolve().parents[1];sys.path.insert(0,str(S/'.cache/pylibs'))
import pymupdf as fitz
for paper in 'ABC':
 d=fitz.open(S/f'public/papers/mock-{paper}-solutions.pdf')
 print(paper,'pages',len(d))
 for i,p in enumerate(d):
  t=p.get_text()
  print(i+1,repr(t[:180]),'tail',repr(t[-100:]))
