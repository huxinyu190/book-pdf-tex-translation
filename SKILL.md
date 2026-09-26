---
name: book-pdf-tex-translation
description: 把学术书籍的单章 PDF（Springer 单章版等）OCR 级翻译并转写为 LaTeX 中文版，拼入主 .tex 并编译验证。当用户要求"翻译第 N 章"、"继续下一章翻译"、"把 N章.pdf 转成 LaTeX/中文"、"拼装/编译 test_zh"、"核对公式编号"时使用。涵盖章节结构分析、300dpi 页面渲染、公式视觉转写、片段拆分与子代理派发、幂等拼装、xelatex 编译排错、编号完整性机器校验的全流程。临时文件一律放项目目录、不放 C 盘。
agent_created: true
---

# 书籍 PDF → LaTeX 中文翻译

把一本英文书籍按章翻译为 LaTeX 中文版：分析章节结构 → 渲染页面 → 逐条视觉转写公式 → 按节产出片段 → 幂等拼装 → 编译排错 → 编号完整性校验。已完整跑通《Density Functional Theory: An Advanced Course》第 2–5 章（含 109 页 / 354 条编号公式 / 20 图 13 表的单章）。

## 使用前必读

1. 先读完整工作流手册：`references/workflow.md`（环境、九阶段流程、陷阱清单）。
2. 派发片段任务时使用模板：`references/fragment-brief-template.md`。
3. 新书项目初始化用 `assets/main.tex` + `assets/book-zh.cls`；已有项目则从
   其主文件与 cls 中提取既有约定（宏、术语、版式），保持全篇一致。

## 快速流程

### 阶段 1：结构分析
```bash
python <skill>/scripts/pdf_info.py "N章.pdf" --eq-tag N
```
得到：页码换算（版权行 pp. A–B → 原书页 = PDF 页 + offset）、节标题清单、
公式 (N.x) 总数与首现页、图表定位。**公式分布是拆分与校验的唯一权威依据。**

### 阶段 2：渲染
```bash
python <skill>/scripts/render_chapter.py "N章.pdf" "D:\<项目>\_tmp_chN" --start 1 --end 109 --book-offset 108
```
产物：`pages\pNNN.png`（300dpi）+ 文字层 txt。**文字层散文可信、公式是乱码，
公式一律以图片为准。**

### 阶段 3–5：拆分、brief、翻译
- 按节拆片段（每片 ≤ 约 15 页或 60 条编号公式），切分点选在节标题前。
- 写 `_BRIEF_chN.md`：记号宏（先 grep cls 与旧章确认）、术语统一表、
  e/ε 记号区分、图表与续表规范、存疑/修正标记规范。
- 翻译执行两模式：小章节主会话逐页读图亲自转写；大章节派子代理并行
  （prompt 按模板），**必须抽查子代理是否真的在读图**（部分子代理无法读图
  会按乱码文字层+领域知识重建公式，错误率高），失败片段改主会话重做。
- 看不清的符号立即裁剪放大：`scripts/crop_zoom.py <pdf> <out.png> <页> <y0> <y1> 10`。

### 阶段 6：视觉复核（大章节必做）
逐页对照图片复核每条公式与表格数字。高频错误：关系符 ≈/≡、χ 丢 λ 下标、
傅里叶末项丢因子、链式等式被压缩、试函数括号分组错、表格整列错位、
漏译夹生（Average、零-point 等）。

### 阶段 7：拼装
```bash
python <skill>/scripts/assemble.py test_zh.tex --mark "_frag_N_1.tex" _frag_N_1.tex _frag_N_2.tex ...
```
自动备份、幂等。改了片段文件后必须恢复备份重拼，保持主文件与片段同步。

### 阶段 8：编译与验证
```bash
xelatex -interaction=nonstopmode -halt-on-error test_zh.tex   # 连跑 3 遍
python <skill>/scripts/verify_pdf.py test_zh.pdf --chapter 5 --max-eq 45 --first-section <首节关键词> --regress 4:354
```
log 检查：`! Error`、3 遍后仍 `undefined` 的引用、`Float too large`（超高
大表 → 按自然分组拆续表）、`Overfull \hbox > 20pt`（超宽 → `\small` +
`\tabcolsep` + 缩表头）。最后目视抽查大式子所在渲染页。

## 高危陷阱（实测踩过，详见 workflow.md §8.5）

- **A. `align` 无编号推导漏 `\nonumber`** → 该行静默占用编号，其后整章编号
  +1，所有 `\eqref` 显示值错位。每行检查。
- **B. `\centerline{...}\\`** → "There's no line here to end"。续表标题行后不加 `\\`。
- **C. 全局符号替换产生粘连**（`\dd\varepsilon` → `\dde`、`\approx\varepsilon`
  → `\approxe`）。替换后 grep `dde_|approxe` 类模式。
- **D. 同一文件并行 Edit 互相覆盖**（后写覆盖先写，无报错）。对同一文件的
  所有 Edit/replace_all 严格串行，做完 grep 验证。
- **E. 目录页干扰章定位**：目录也含章标题词。用「章标题词 + 首节标题关键词 +
  无点线」三条件定位正文（verify_pdf.py 已内置）。
- **F. 原书印刷错误**：确认后按原书原样保留，`% 注释` 说明疑似正确形式。
- **G. 单章 PDF 页脚的 Springer 出版说明不是正文**，不译，`% 注释`记录。
- **临时文件一律放项目目录**（如 `_tmp_chN\`），禁止放 C 盘——用户明确要求。

## 收尾

术语一致性 grep 回归（新旧章节统一）；把页码换算、片段清单、公式计数、遗留
存疑写入工作日志；向用户报告覆盖页、计数核对、修复清单与存疑。
