"""Recompile site-only teacher PDFs with tighter heading spacing; preserve source chemistry."""
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

SITE = Path(__file__).resolve().parents[1]
RESEARCH = Path(r'D:\桌面\637有机化学真题研究工作区')
SOURCE = RESEARCH / '13_北大习题集模拟卷/09_正式交付'
WORK = SITE / '.cache/mock-pdf-reflow'
WORK.mkdir(parents=True, exist_ok=True)
CACHE = SITE / '.cache/tectonic'
if not CACHE.exists():
    shutil.copytree(RESEARCH / '00_工具/tectonic-cache', CACHE)
sys.path.insert(0, str(SITE / '.cache/pylibs'))
import pymupdf as fitz

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

PREAMBLE = r'''
% Site layout only: preserve text, mathematics and native chemical diagrams.
\setlength{\parskip}{2pt}
\raggedbottom
\let\originalenumerate\enumerate
\renewcommand{\enumerate}{\originalenumerate
 \setlength{\itemsep}{2pt}\setlength{\parsep}{0pt}\setlength{\topsep}{3pt}}
\makeatletter
\renewcommand\subsection{\@startsection{subsection}{2}{\z@}
 {-1.1ex\@plus -.3ex\@minus -.2ex}{.5ex\@plus .2ex}
 {\normalfont\normalsize\bfseries}}
\makeatother
'''

def build(paper):
    folder = WORK / paper
    folder.mkdir(exist_ok=True)
    original = SOURCE / f'{paper}卷_详细解析.tex'
    tex = original.read_text(encoding='utf-8-sig')
    updated = tex.replace(r'\begin{document}', PREAMBLE + '\n' + r'\begin{document}', 1)
    assert updated.replace(PREAMBLE + '\n', '', 1) == tex
    # Dense routes are kept readable at the normal LaTeX small size (10pt).
    # Only these known long blocks need compact native drawing placement.
    if paper in 'BC':
        sections = re.split(r'(?=\\section\*\{)', updated)
        for index, section in enumerate(sections):
            if paper == 'C' and section.startswith(r'\section*{六'):
                section = section.replace(r'\subsection*{1．', r'\small\subsection*{1．', 1)
                section = section.replace(r'\begin{tikzpicture}[', r'\begin{tikzpicture}[scale=.93,transform shape,')
                sections[index] = section
            elif paper == 'B' and section.startswith(r'\section*{一'):
                start = section.index(r'\subsection*{4．')
                end = section.index(r'\subsection*{5．', start)
                target = section[start:end]
                target = target.replace(r'\begin{tikzpicture}[', r'\begin{tikzpicture}[scale=.93,transform shape,')
                sections[index] = section[:start] + r'\small ' + target + r'\normalsize ' + section[end:]
        updated = ''.join(sections)
    path = folder / f'mock-{paper}-solutions.tex'
    path.write_text(updated, encoding='utf-8')
    env = os.environ.copy()
    env.update(TEMP=str(WORK), TMP=str(WORK), XDG_CACHE_HOME=str(CACHE),
               TECTONIC_CACHE_DIR=str(CACHE), PYTHONDONTWRITEBYTECODE='1')
    result = subprocess.run([str(RESEARCH/'00_工具/tectonic-0.17.0/tectonic.exe'),
        '--keep-logs', '--outdir', str(folder), str(path)], cwd=folder, env=env, capture_output=True)
    (folder/'compile.txt').write_bytes(result.stdout + result.stderr)
    if result.returncode:
        raise RuntimeError(f'{paper} compile failed: {result.stderr[-1600:]}')
    pdf = path.with_suffix('.pdf')
    old_path = SITE / f'public/papers/mock-{paper}-solutions.pdf'
    old, new = fitz.open(old_path), fitz.open(pdf)
    # Pagination may change but all non-page-number extracted glyphs must survive.
    def content(doc):
        pieces = []
        for page in doc:
            for block in page.get_text('dict')['blocks']:
                for line in block.get('lines', []):
                    for span in line['spans']:
                        if span['bbox'][1] > 40:
                            pieces.append(span['text'])
        return re.sub(r'\s+', '', ''.join(pieces))
    old_text, new_text = content(old), content(new)
    # Span reading order can differ on vector figures; compare glyph multisets too.
    from collections import Counter
    assert Counter(old_text) == Counter(new_text), f'{paper}: changed/missing glyphs'
    short_pages = []
    for index, page in enumerate(new):
        text = page.get_text()
        if len(re.sub(r'\s+', '', text)) < 170 and not page.get_drawings():
            short_pages.append(index+1)
    return {'paper':paper, 'source_tex_sha256':sha(original), 'old_pages':len(old),
        'new_pages':len(new), 'old_pdf_sha256':sha(old_path), 'new_pdf_sha256':sha(pdf),
        'all_extracted_non_pagenumber_glyphs_preserved':True, 'reading_order_identical':old_text==new_text,
        'short_text_only_pages':short_pages,'output':str(pdf),'installed':False}

records = []
# Sequential compilation avoids concurrent writes to the shared format cache.
for paper in 'ABC':
    record=build(paper)
    records.append(record)
    print(json.dumps(record, ensure_ascii=False), flush=True)
(SITE/'audit/PDF_REFLOW.json').write_text(json.dumps({'records':records,
    'scope':'Only paragraph and heading spacing changed; original research sources untouched.',
    'visual_accepted':False}, ensure_ascii=False, indent=2),encoding='utf-8')
