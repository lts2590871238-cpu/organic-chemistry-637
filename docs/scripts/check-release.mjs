// Verify deployable static files without accessing any research directory.
import fs from 'node:fs'
import path from 'node:path'
import assert from 'node:assert/strict'
import crypto from 'node:crypto'
const root=path.resolve(import.meta.dirname,'..'), docs=path.join(root,'docs')
const hash=file=>crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex')
const checked=[]
for(const folder of ['data','assets','papers']){
  for(const name of fs.readdirSync(path.join(root,'public',folder))){
    const original=path.join(root,'public',folder,name)
    if(!fs.statSync(original).isFile())continue
    const deployed=path.join(docs,folder,name)
    assert(fs.existsSync(deployed),`${folder}/${name} missing in docs`)
    assert.equal(hash(original),hash(deployed),`${folder}/${name} differs`)
    checked.push(`${folder}/${name}`)
  }
}
assert(fs.existsSync(path.join(docs,'.nojekyll')))
const index=fs.readFileSync(path.join(docs,'index.html'),'utf8')
for(const match of index.matchAll(/(?:src|href)="([^"]+)"/g)){
  const url=match[1]
  if(/^(?:https?:|data:|#)/.test(url))continue
  assert(!url.startsWith('/'),`Root-absolute URL breaks GitHub project path: ${url}`)
  assert(fs.existsSync(path.resolve(docs,url)),`HTML asset missing: ${url}`)
}
const all=[]
function walk(dir){for(const e of fs.readdirSync(dir,{withFileTypes:true})){
  const p=path.join(dir,e.name);if(e.isDirectory())walk(p);else all.push(p)
}}
walk(docs)
assert(!all.some(p=>/\.exe$|\.zip$|扫描|邢其毅主编|有机化学考研辅导/.test(path.basename(p))))
assert(all.every(p=>fs.statSync(p).size<100*1024*1024),'A static file exceeds GitHub 100MiB')
const report={at:new Date().toISOString(),static_files:all.length,
  public_files_byte_identical_in_docs:checked.length,relative_entry_assets:true,
  no_bundled_scans_or_full_textbooks_by_filename:true,all_files_below_100MiB:true,
  scope:'Static deployment integrity; filename screening is not a copyright determination.'}
fs.writeFileSync(path.join(root,'audit/RELEASE_STATIC_CHECKS.json'),JSON.stringify(report,null,2))
console.log(JSON.stringify(report))
