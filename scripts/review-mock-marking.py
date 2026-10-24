"""Reconcile existing non-official marking suggestions; never alter chemistry sources."""
import json, hashlib, datetime
from decimal import Decimal
from pathlib import Path
SITE=Path(__file__).resolve().parents[1]
SOURCE=Path(r'D:\桌面\637有机化学真题研究工作区\13_北大习题集模拟卷\09_正式交付\MOCK_MARKING.json')
SPECS={
'A':'''S01-Q01|1 中文系统名|1 英文系统名
S01-Q02|0.75 立体异构体总数8个|0.5 对映体4对|0.75 固定一个异构体时有6个非对映体
S01-Q03|0.75 3305 cm⁻¹为端炔sp C—H伸缩|0.75 2110 cm⁻¹为C≡C伸缩|0.5 620 cm⁻¹为端炔C—H弯曲
S01-Q04|1 五元内酯连接|1 正确翻转的构型
S01-Q05|1 开环后的碳连接|1 醛、酮端点均正确
S01-Q06|0.5 第一步加成产物的结构|0.5 第一步产物名称|0.5 第二步再生醛的结构|0.5 第二步产物名称
S01-Q07|1 六元稠环连接|1 羰基位置与苯环双键
S01-Q08|1 连接与官能团位置|1 Fischer空间关系及R构型
S01-Q09|2 按题意写俗名糠醛；仅正确系统名时可酌给1分，两者不累计
S01-Q10|2 一套完整、适用的羰基脱氧条件；Zn(Hg)/HCl或肼/强碱加热均可
S01-Q11|1 烯醇结构|1 戊醛结构
S01-Q12|0.5 对甲苯胺|0.5 重氮盐|1 对位偶氮产物
S01-Q13|1 C1/C2双苯腙|1 C3—C5及CH2OH正确保留
S01-Q14|1 PhCH2—N连接|1 N上甲基及一个H
S01-Q15|1 N-Cbz正确连接|1 原侧链和羧酸正确保留
S03-Q01|1 DBE|1 双键与环数|1 二醛复接|1 完整结构
S03-Q02|2 DBE|2 四个甲基的积分|3 取代对称性|2 完整结构|1 谱峰归属
S03-Q03|2 A结构|2 B结构|1 C结构|1 D结构|1 E结构|1 F结构|2 两种裂解的计量回代
S03-Q04|1 DBE|1 CHO与OMe识别|1 对位判断|1 结构与名称|1 逐峰归属
S03-Q05|2 A结构|1 B结构|2 C结构及裂解|1 原子守恒
S04-Q01|1 观察方向|2 六种构象|2 峰谷与周期
S04-Q02|2 二聚结构|2 电子效应与力常数|1 波数关系
S04-Q03|2 四种底物归类|2 结构趋势|1 速率式与量纲
S05-Q01|2 H迁移及中间体|2 Me迁移及产物|2 两步的电子箭头与价态；按原建议分步酌评
S05-Q02|2 三条成桥箭头及桥式中间体|1 Br⁻捕获支路|1 甲醇捕获支路|1 氧正离子的去质子化|1 立体关系
S05-Q03|2 LDA去质子及烯醇盐共振|2 新C—C键及四面体中间体|2 离Cl及产物
S06-Q01|3 第一次炔负离子烷基化及正确C3卤代烷|3 第二次炔负离子烷基化及正确C3卤代烷|2 水合并互变成酮
S06-Q02|2 保护|3 炔盐成键|2 脱保护|1 官能团兼容性说明
S06-Q03|2 C2/C3醇制格氏试剂|2 丙醛和六碳醇|2 氧化为酮|2 末步叔醇
S06-Q04|4 丁酰氯/AlCl3条件及酮|4 Zn(Hg)/HCl条件及正丁苯
S06-Q05|3 转为丙炔|3 羧化为炔酸|2 选择性半氢化''',
'B':'''S01-Q01|1 连接与命名|1 cis及英文完整
S01-Q02|1 三元环及两个Cl|1 两个Me位置
S01-Q03|1 新C—C连接|1 三个乙酯与Me位置完整
S01-Q04|0.5 烯胺|0.5 带电亚胺鎓|1 最终酮
S01-Q05|1 环己烯酰氯母体|1 双键与羰基接位的完整命名
S01-Q06|1 C12链与三甲基季铵的连接|1 N正电及Cl负离子
S01-Q07|1 叔丁基直接C—N连接|1 硝基正确价态
S01-Q08|1 丙醛母体|1 2,2-二甲基定位
S01-Q09|1 磺酸基与噻吩环保留|1 2位取代
S01-Q10|2 可行的过氧酸氧化剂；不限定为本书一种
S01-Q11|1 1,3顺式连接|1 实际画出双平伏优势椅式
S01-Q12|1 萘-2-磺酸主骨架|1 5-Me与8-Et位次均正确
S01-Q13|0.5 苯甲酸|0.5 苯甲酰胺|1 苯胺
S01-Q14|1 α有机锌酯|1 正确脱水烯酯
S01-Q15|1 9/10位成两新键并保留外侧苯环|1 顺式酸酐桥及两个羰基
S03-Q01|1 DBE|1 末端烯及丙酮信息|2 五碳片段|2 完整四烯|2 氢化骨架回代
S03-Q02|2 A结构|2 B结构|2 C结构|2 各组谱峰归属与积分
S03-Q03|2 五碳及无甲酸的碳账|3 两醛端复接邻二醇并成五元环|2 两个保留中心的立体继承|3 说明两个被切中心未定；或给出可成立成员并说明不唯一
S03-Q04|1 烯谱信息|1 tBu信息|1 CH2两H非等价|1 排除炔|1 完整结构
S03-Q05|1 DBE|1 等价12H|1 正确结构|1 分子式核验
S04-Q01|2 角张力|1 扭转及非键因素|1 弯曲键|1 释放张力及条件
S04-Q02|2 氰醇结构|1 酸碱消耗|2 耦合平衡方向
S04-Q03|2 E2几何|2 sp线性与张力|1 二烯结论
S05-Q01|2 (i)五项识别|2 SN2双箭及环铵盐|2 真实去质子化及反应类型
S05-Q02|2 第一轮完整四步|2 第二轮完整四步|2 催化、可逆、平衡与价态
S05-Q03|2 羟醛加成三步|2 E1cb两步|2 目标骨架、碱再生及全部弯箭
S06-Q01|4 正确二聚体|4 一次HCl加成及目标连接
S06-Q02|2 合适的2-戊烯|2 邻二溴物|4 第二次消除条件及2-戊炔
S06-Q03|2 第一条完整组合|2 第二条完整组合|2 第三条完整组合|2 优选与理由
S06-Q04|3 正确丙酮与乙酸乙酯|3 成键及脱EtO|2 产物盐与酸化
S06-Q05|2 明确对位及分离|4 合理苄位转换|2 正确目标与兼容性''',
'C':'''S01-Q01|1 环氧连接|1 trans及外消旋
S01-Q02|1 产物|0.5 亲核性质|0.5 1,4加成位置
S01-Q03|1 正确区域|1 全部官能团及Me数量
S01-Q04|1 双键位置|1 原立体关系保持
S01-Q05|1 主链、烯位及取代基|0.5 2Z|0.5 4R
S01-Q06|1 重排碳架|1 Cl在正确的三级碳
S01-Q07|1 重排主要烯烃连接|1 四个Me与内双键完整
S01-Q08|1 双酰氯及母体|1 烯侧链接位与双键位置
S01-Q09|1 顺式1,2-二醇|1 实际画出同面a/e椅式
S01-Q10|1 母体及取代位|0.5 E|0.5 S
S01-Q11|1 环氧酯|1 2-苯基丙醛
S01-Q12|1 两个桥头及[2.2.1]连接|1 N位置、三键及6C
S01-Q13|1 四取代中心保留Ph/CN/CO2Et|1 新—CH2CH2CN支链
S01-Q14|1 羰基位置及7C骨架|1 新键与末端异丙烯基
S01-Q15|0.5 第一个连续空|0.5 第二个连续空|0.5 第三个连续空|0.5 第四个连续空
S03-Q01|1 DBE|1 谱段|1 连接|1 氢数核对
S03-Q02|2 A结构|1 B结构|1 C结构|2 D反式及外消旋|2 E结构|2 裂解计量
S03-Q03|2 C结构及归属|2 B竞争加成|1 A结构|2 D/E几何|2 F连接|1 原子守恒；不要求未给定的绝对构型
S03-Q04|1 含硝基时的DBE|1 片段|1 连接|2 非等价CH2与多重耦合
S03-Q05|2 C/D结构|2 A/B结构|1 四个Fischer投影|1 对称性及降解回代
S04-Q01|2 桥头与双椅|1 (iii)氯位置|1 (iv)甲基|1 翻椅限制
S04-Q02|2 稠合及两环作用|2 共同零点的能量比较|1 结论与模型边界
S04-Q03|1 间位及sp³碳|3 三个共振式|1 电荷与定位解释
S05-Q01|2 HOBr及溴正离子的完整弯箭|2 两面背面开环|2 区域、anti及对映关系
S05-Q02|2 亲核启动及烯醇盐|2 Br2捕获的全部箭头|2 anti产物镜像与原条件
S05-Q03|2 LDA定向及烯醇盐|2 羟醛成键及质子化|2 E1cb、目标及箭头
S06-Q01|2 唯一β消除|3 端炔制备|3 正确偶联及二炔
S06-Q02|2 内炔前体|3 明确端位异构化|3 氢硼氧化成醛
S06-Q03|2 初次Dieckmann|2 苄基化|3 逆开环及异位再成环|1 最终位置
S06-Q04|3 烯胺及丙酰化|3 正确逆开环|2 选择性酮还原
S06-Q05|1.5 第一条完整路线|1.5 第二条完整路线|1.5 第三条完整路线|1.5 第四条完整路线|2 选择性、原料限制及优劣比较'''
}
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def main():
 source=read(SOURCE)['records'];byid={x['id']:x for x in source};questions=read(SITE/'public/data/questions.json');qmap={q['id']:q for q in questions};answers=read(SITE/'public/data/answers.json');records=[]
 for letter,text in SPECS.items():
  for line in text.strip().splitlines():
   parts=line.split('|');qid=letter+'-'+parts[0];groups=[]
   for i,part in enumerate(parts[1:]):
    weight,label=part.split(' ',1);groups.append({'id':f'P{i+1:02}','label':label,'points':float(Decimal(weight))})
   expected=Decimal(str(byid[qid]['total_score']));actual=sum((Decimal(str(g['points'])) for g in groups),Decimal(0));assert actual==expected,(qid,actual,expected)
   assert Decimal(str(qmap[qid]['score']))==expected
   assert len(answers[qid]['units'])==1
   answers[qid]['units'][0]['markingPoints']=groups
   records.append({'id':qid,'kind':'manual_reference_groups','total_score':float(expected),'groups':groups,'source_suggestions':byid[qid]['suggestions'],'is_official':False,'review':'已逐条对照现有采分建议；未重做化学推导，不新增化学终验。'})
 for q in questions:
  if q['year'] is not None or q['section']!='S02':continue
  labels=q['answerKey'].split(';') if ';' in q['answerKey'] else [q['answerKey']]
  records.append({'id':q['id'],'kind':'objective_existing_key','total_score':q['score'],'parts':len(labels),'part_score':q['score']/len(labels),'is_official':False,'review':'保留现有原选项、单/多选全对及双空分配口径；不修改答案。'})
 assert len(records)==129 and len(set(x['id'] for x in records))==129
 for letter in 'ABC':assert sum(Decimal(str(x['total_score'])) for x in records if x['id'].startswith(letter+'-'))==150
 (SITE/'public/data/answers.json').write_text(json.dumps(answers,ensure_ascii=False,indent=2),encoding='utf-8')
 out={'at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),'records':records,'questions':129,'subjective_with_explicit_groups':93,'objective_existing_keys':36,'points_per_paper':150,'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'scope':'采分建议分组及合计核对；不代表官方评分、学生测试或整卷化学终验。','final_accepted':False}
 (SITE/'audit/MOCK_MARKING_REVIEW.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps({'marking_questions':129,'subjective_groups':93,'objective_keys':36,'all_totals_match':True}))
if __name__=='__main__':main()