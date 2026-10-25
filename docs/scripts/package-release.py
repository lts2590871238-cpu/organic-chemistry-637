"""Package the self-contained website, excluding local runtimes and caches."""
from pathlib import Path
import datetime
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '封存交付'
OUT.mkdir(exist_ok=True)
EXCLUDE = {'.cache', 'node_modules', '.git', '封存交付', '.idea', '.vscode', '__pycache__'}

def digest(data):
    return hashlib.sha256(data).hexdigest()

files = sorted(p for p in ROOT.rglob('*') if p.is_file()
    and not any(part in EXCLUDE for part in p.relative_to(ROOT).parts)
    and p.suffix not in {'.log', '.tsbuildinfo', '.pyc'}
    and p.name != 'RELEASE_MANIFEST.json')
records = [{'path':p.relative_to(ROOT).as_posix(), 'bytes':p.stat().st_size,
            'sha256':digest(p.read_bytes())} for p in files]
manifest = ROOT / 'RELEASE_MANIFEST.json'
manifest.write_text(json.dumps({'release':'2026-10-24-frozen',
    'at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),
    'files':records, 'scope':'Website code, deployable docs, data, native vectors, selected mock PDFs and audit records. No local runtime or user browser storage.'},
    ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
archive=OUT/'organic-chemistry-637_20261024_封存.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in files+[manifest]:
        z.write(p,'organic-chemistry-637/'+p.relative_to(ROOT).as_posix())
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    for row in records:
        assert digest(z.read('organic-chemistry-637/'+row['path']))==row['sha256'],row['path']
    assert z.read('organic-chemistry-637/docs/.nojekyll')==b''
checksum=digest(archive.read_bytes())
archive.with_suffix('.zip.sha256').write_text(checksum+'  '+archive.name+'\n',encoding='utf-8')
print(json.dumps({'archive':str(archive),'files':len(records)+1,'bytes':archive.stat().st_size,
                  'sha256':checksum,'zip_crc_and_all_manifest_hashes_passed':True},ensure_ascii=False))
