# 新仓库与GitHub Pages

公开前先完成三卷所用商业参考书题目转载权限核实。以下仅为工程准备，当前没有发布。

1. 在GitHub Desktop选择File → Add local repository，定位本文件夹。若未初始化，按提示创建独立仓库，名称organic-chemistry-637，不能选择D盘github母版。
2. 检查文件。提交src、public、docs、配置、脚本、说明和审核报告。node_modules与.cache已经忽略；不要添加原卷扫描和整本教材。
3. Commit本次新站。确认公开权限后再由用户Publish repository；不要覆盖物化802仓库。
4. 仓库Settings → Pages → Deploy from a branch，选择main与/docs。
5. 保存后检查网站：仓库子路径首页、#/stage1、#/exam?day=19以及SVG、JSON加载。HashRouter与Vite相对base已经配置。
6. 后续改动执行npm run build，连同docs一起提交。

个人进度仅保存在浏览器organic637.v1中。迁移设备前用错题页的导出/导入备份功能。
