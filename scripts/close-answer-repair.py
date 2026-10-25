import json,hashlib,datetime
from pathlib import Path
S=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
now=datetime.datetime.now().astimezone().isoformat()
before=read(S/'audit/ANSWER_REPAIR_BEFORE.json');answers=read(S/'public/data/answers.json')
for pid,a in answers.items():
 for u in a['units']:
  old=next(v for v in before['answers'][pid]['units'] if v['id']==u['id'])
  exclude={'figures','completeSolutionSource'}
  assert {k:v for k,v in u.items() if k not in exclude}=={k:v for k,v in old.items() if k not in exclude},u['id']
for name,digest in before['protected'].items():assert hashlib.sha256((S/name).read_bytes()).hexdigest()==digest,name
checks=read(S/'audit/FUNCTION_CHECKS.json')['checks'];assert len(checks)==25 and all(c['passed'] for c in checks)
source=read(S/'audit/ANSWER_SOURCE_RESTORATION.json');mock=read(S/'audit/ANSWER_PAGE_RESTORATION.json');render=read(S/'audit/ANSWER_RENDER_CHECKS.json')
save(S/'audit/ANSWER_REPAIR_CLOSEOUT.json',{'at':now,'parents':len(answers),'units':render['units'],'research':source['counts'],'mock_questions':mock['questions'],'mock_native_pages':mock['native_svg_pages'],'mock_multi_page_questions':mock['multi_page_questions'],'function_checks':len(checks),'katex_errors':render['katexErrors'],'source_issues':source['issues'],'unrelated_data_hashes_unchanged':True,'answer_text_and_marking_unchanged':True,'browser_verified':['2004-S02-Q03：五步讲解、五图与末步酸化可放大','2004-S01-Q02-P06：修订版全部教学正文可见，原候选独立折叠','C-S05-Q03：两页完整机理，末页3/4/5步和目标产物可辨；移除多余下节标题'],'chemical_final_acceptance_changed':False,'build':'passed','lint':'passed'})
report='''# 答案缺步显示修复报告

## 检查范围与原因

全站884道父题、1287个小问。历年题1158单元逐字段对照研究区第二/三轮及集中修订记录，答案、推导、化学检查和教学文字无丢失差异。网站原来只接`vector_pdf`，漏掉`extra_vector_pdfs`等后续图；修订版`editorial.teaching`也未渲染。模拟题原迁移的题号分页识别存在续页漏接。

## 已修复

- 188个历年小问图件有补接/次序调整，其中186个增加图件，44个属于机理小问。1725份引用原生图文件读取无缺失，新增557份原生SVG。
- 169个修订小问的完整基础说明、分步推导、验算和参考采分讲解恢复显示；原候选与待核说明独立保留，避免两版混用。
- 三卷129题全部接回正式LaTeX详细解析的143页原生矢量内容，13题跨页均完整接入；剔除下一大题标题造成的空续页。
- 所有图按顺序标明“解析图n/N”，可放大；全部1287小问服务端实际渲染，无KaTeX报错。未将扫描教材图用于正式答案。

## 验证与边界

25项现有及新增检查通过；build、lint通过（本机用既有pnpm执行同名package脚本）；docs与public静态资源重新核对。实际浏览器核对了Claisen完整五图、修订教学、C卷五步机理末页。

本次是全量源记录对照和漏接修复，不冒称重新独立复算全部题。既有原题/编辑身份、未决边界和终验状态保持原样。题干、训练安排、分值、96卡、考情及六PDF文件均未改；答案文字和采分字段亦逐项确认未被覆盖。研究目录与母版只读。

## 文件

修改：`src/components/OrganicQuestion.tsx`、`src/lib/organic.ts`、`public/data/answers.json`、`scripts/check-functions.mjs`、断点/审计与docs构建产物。

新增：`src/components/AnswerUnit.tsx`、原生答案续图、`scripts/restore-research-answer-figures.py`、`scripts/restore-complete-mock-answers.py`等盘点和修复脚本；证据见`audit/ANSWER_SOURCE_RESTORATION.json`、`ANSWER_PAGE_RESTORATION.json`、`ANSWER_RENDER_CHECKS.json`、`ANSWER_REPAIR_CLOSEOUT.json`。

上传必须包括本次新增的public/assets及重新构建的docs；旧缓存页面请强制刷新。不要重新运行全量migrate.py覆盖当前已修训练安排；需要复查时直接使用本次定点脚本。
'''
(S/'答案缺步修复报告.md').write_text(report,encoding='utf-8')
p=read(S/'PROJECT_PROGRESS.json');p['at']=now;p['phase']='全站答案漏接修复完成；待用户GitHub Desktop上传';p['answer_display_repair']=read(S/'audit/ANSWER_REPAIR_CLOSEOUT.json');save(S/'PROJECT_PROGRESS.json',p)
(S/'CONTINUE_HERE.md').write_text('# 全站答案漏接修复完成\n\n'+now+'\n\n全站884父题1287单元检查完毕。历年188小问恢复/调整全部后续图，169修订正文恢复显示；三卷129题143原生页接入，13跨页完整。25项检查、lint/build及代表题浏览器核验通过。原题/编辑状态、未知分值和旧终验不变。\n\n读取答案缺步修复报告.md与audit/ANSWER_REPAIR_CLOSEOUT.json。docs已重建；准备用户自行GitHub Desktop上传。不重跑migrate.py，不重复重做化学题或卡片。研究区与母版只读。\n',encoding='utf-8')
print('Answer repair report and checkpoints saved')
