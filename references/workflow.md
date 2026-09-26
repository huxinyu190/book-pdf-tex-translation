# 书籍 PDF → LaTeX 中文翻译：完整工作流手册

本手册是 `book-pdf-tex-translation` skill 的核心参考。整套流程已在《Density
Functional Theory: An Advanced Course》第 2–5 章翻译中完整跑通（第 4 章 109
页 / 354 条编号公式 / 20 图 13 表；第 5 章 8 页 / 45 条公式）。

---

## 0. 环境与项目结构

### 0.1 环境

| 工具 | 用途 | 获取方式 |
|------|------|----------|
| Python (venv) | 运行所有辅助脚本 | `C:\Users\YU\.workbuddy\binaries\python\envs\default\Scripts\python.exe` |
| pymupdf | PDF 渲染/文字层/裁剪 | `python -m pip install pymupdf`（装入上述 venv） |
| xelatex (TeX Live) | 编译 | `where.exe xelatex` 定位；本项目为 `D:\texlive\2024\bin\windows\xelatex.exe` |

### 0.2 项目结构（铁律：临时文件一律放项目目录，禁止放 C 盘）

```
<项目根>\
├── N章.pdf / N-M章.pdf          # 单章或多章合并的源 PDF（Springer 单章版常见）
├── <书名>_zh\                    # 译文目录
│   ├── test_zh.tex               # 主文件（骨架见 assets/main.tex）
│   ├── book-zh.cls               # 排版类（assets/book-zh.cls）
│   ├── cover.pdf                 # 原书封面（可选）
│   ├── _frag_<章>_<节>.tex       # 各章翻译片段（按节拆分）
│   ├── _assemble_ch<N>.py        # 该章的拼装命令记录（一行参数的脚本或直接命令行）
│   ├── test_zh.pdf               # 编译产物
│   └── test_zh_backup_*.tex      # 每次大拼装前的备份
└── _tmp_ch<N>\                   # 本章临时工作目录（页图、文字层、裁剪图、校验输出）
    ├── pages\p001.png ...
    └── ch_text_*.txt
```

### 0.3 新书项目初始化（模板提取）

1. 复制 `assets/main.tex` → `<书名>_zh\test_zh.tex`，`assets/book-zh.cls` → 同目录。
2. 按目标书实际版式微调 cls（章标题字号/间距、页眉样式、公式编号形式
   `\theequation` 等）。若已有跑通的同类项目，直接从旧项目克隆 cls 与主文件
   头部注释，再改书名。
3. 先翻译第 1 章并编译通过， establishes 基线；此后每章只在 `\end{document}`
   前追加。

---

## 1. 阶段一：章结构分析

对 `N章.pdf`（或 `N-M章.pdf` 中目标章所在的页区间）运行：

```bash
python scripts/pdf_info.py "5-6章.pdf" --eq-tag 5
```

产出判断依据：

- **页码换算**：从版权行 `pp. 219–226` 推出 `原书页 = PDF页 + offset`（上例
  offset = 218）。文字层与图片命名都用它标注。
- **章节边界**：单章 PDF 首页有 `Chapter N` 行；多章合并版注意下一章
  `Chapter N+1` 的起始 PDF 页即本章结束页 +1。
- **公式编号分布**：编号 (N.x) 的范围、总数、缺失、每个编号的首次出现页。
  这是拆分片段和事后校验的唯一权威依据。文字层编号通常无缺失（页眉/脚注
  可能造成个别假阳性，需人工剔除）。
- **图表清单**：`Fig. N.x` / `Table N.x` 及其所在页。跨页表（尤其数据大表）
  要在拆分时特别标注。

## 2. 阶段二：页面渲染与文字层

```bash
python scripts/render_chapter.py "5-6章.pdf" "D:\<项目>\_tmp_ch5" --start 1 --end 8 --book-offset 218
```

- 300dpi PNG 供视觉转写；文字层供散文底本。
- **文字层的公式部分是乱码**（字体子集映射损坏，形如"未0"、"鈭?"），绝不可
  直接采用；散文基本可信但 LaTeX 特殊字符与上下标常丢失。

## 3. 阶段三：拆分策略

- 按节拆片段，每个片段 **不超过约 15 页或 60 条编号公式**（大章节按此上限
  再细分，如 4.4 节拆成前半/后半）。
- 切分点选在**节/小节标题之前**（自然边界）；若必须在段落中间切，先看该页
  有无脚注、跨页公式、跨页表，把边界挪到干净处。
- 每个片段的起止边界要在 brief 里写成"以某式/某句为界"，并明确"上一片段
  已含 X，不要重复翻译"。
- 一章的片段命名：`_frag_<章>_<节>.tex`（同节多片段用 `_p1/_p2` 后缀）。

## 4. 阶段四：工作说明（brief）

写 `_BRIEF_ch<N>.md`（临时目录或译文目录均可），作为所有翻译执行者（子代理
或主会话自身）的统一规则书。**必须包含**（模板见
`references/fragment-brief-template.md`）：

1. 记号宏清单：先 grep 译文 cls 与已完成章节确认可用宏（如
   `\vr \vq \vk \vR \vnabla \dd \ext`），缺的在 cls 里补齐（跟随既有风格：
   `\newcommand{\vq}{\boldsymbol{q}}`）。
2. 术语统一表：grep 已译章节提取既有译法（如 局域/非局域、均匀电子气、
   位力定理、编时响应函数、v-可表示性……），逐条列出新章会用到的。
3. 记号区分约定：如 单位体积能量密度 `e_{\mathrm{xc}}` vs 每粒子能量
   `\varepsilon_{\mathrm{xc}}`；算符 `\hat{T}` 等。
4. 排版规范：编号公式一律 `\begin{equation}\label{eq:N.x}`；交叉引用用
   `\eqref{eq:N.x}`；原书无编号展示式用 `\[...\]` 或 `equation*`；
   多行单编号用 `multline`/`split`；**align 逐行推导若不需编号，每行都必须
   `\nonumber`**（见 §8 陷阱 A）。
5. 插图规范：「待插入插图」模板（`\includegraphics` 注释掉 + 图注全文翻译 +
   `\label{fig:N.x}`），图片文件留待用户自行裁剪放入。
6. 表格规范：数字必须逐格对照图片；跨页表第一部分带 `\caption`+`\label`，
   续页部分用无 caption 的 `table` 浮动体 + 居中文字行
   `\centerline{\textbf{（表~\ref{tab:N.x}，续）}}`（**后面不能跟 `\\`**，
   见 §8 陷阱 B）。
7. 存疑与修正标记：凡不确定处写 `% 【存疑】...`；复核修正处写
   `% 【修正标记】原表述：… → 问题：… → 现表述：…`。

## 5. 阶段五：翻译执行

两种模式，按章的规模和读图可靠性选择：

### 模式 A：主会话亲自翻译（小章节 ≤ 15 页，或子代理读图不可靠时）

1. 逐页 Read 页面 PNG（p001.png…），以**图片为唯一权威**转写每条公式。
2. 散文对照文字层快速成稿，但行内符号仍看图。
3. 看不清的符号立即用 `scripts/crop_zoom.py` 放大 9–10 倍核实（上下标、
   撇号、指数中 π 的幂次、求和下标是单变量还是双变量，都属高危区）。
4. 按节写入片段文件；片段头部写覆盖范围注释。
5. 自查：`\begin{equation}`/`multline` 计数 == 该片段应含编号数；label 唯一；
   无 `\tag`。

### 模式 B：子代理并行（大章节）

1. 用 Agent 工具（后台）并行派出多个翻译子代理，每个代理一个片段。
2. 子代理 prompt 直接引用 brief 文件 + 该片段的边界与范围清单（模板见
   `references/fragment-brief-template.md`）。
3. 子代理报告公式计数后，必须用脚本复核片段文件（统计 `label{eq:` 是否恰好
   覆盖期望区间、有无重复）。
4. **已知风险**：部分子代理无法读图，会退化为按文字层+领域知识重建公式，
   错误率高。对策：
   - 派发后抽查其产出（对照 1–2 页图片验证其读图是否真实生效）；
   - 读图失败的片段改由主会话按模式 A 重做或逐条视觉复核。

## 6. 阶段六：视觉复核（大章节必做）

对子代理产出的每个片段，逐页 Read 图片，将每条公式与图片比对（上下标、
粗体/正体、积分限、括号分组、数字表格逐格核对）。发现的错误用 Edit 直接改，
并加【修正标记】注释。复核时常见错误类型（实测统计）：

- `≈` 误代 `≡`、`χ` 丢 λ 下标、响应函数 χ̃/χ_λ 混用；
- 傅里叶变换末项丢因子（`−1` 应为 `−n_0`）；
- 多行链式等式被压成两行（丢中间的 ∫d³r' 项）；
- 试函数类复杂公式（VWN 型）括号分组错误——必须逐符号重排；
- 表格整列错位/跨页续表缺失；翻译夹生（Average、caution、零-point 等漏译）。

## 7. 阶段七：拼装

```bash
python scripts/assemble.py test_zh.tex --mark "_frag_5_1.tex" _frag_5_1.tex _frag_5_2_3.tex _frag_5_4.tex
```

- 拼装前主文件自动备份；脚本幂等（重复运行跳过）。
- 若需重拼：先 `copy test_zh_backup_xxx.tex test_zh.tex` 恢复，再运行。
- 修改片段文件后**必须恢复备份重拼**（直接改主文件会造成与片段不同步）。

## 8. 阶段八：编译与验证

### 8.1 编译

```bash
xelatex -interaction=nonstopmode -halt-on-error test_zh.tex   # 第 1 遍
xelatex ...                                                    # 第 2 遍（目录/引用）
xelatex ...                                                    # 第 3 遍（收敛）
```

### 8.2 Log 检查清单（逐项过）

| Log 模式 | 含义 | 处置 |
|----------|------|------|
| `! ...` / `Error` | 编译错误 | 按行号回片段修复 |
| `Reference ... undefined`（3 遍后仍在） | label 拼错或引用了未译章节 | 修复或确认前向引用 |
| `Float too large for page by Xpt` | 浮动体（大表）超高 | 拆分续表（见 8.3） |
| `Overfull \hbox > 20pt` | 行/表超宽 | `\small`+`\tabcolsep`、缩短表头 |
| `There's no line here to end` | `\centerline{...}\\` | 去掉 `\\` |

### 8.3 大表超高（Float too large）的标准修法

一个 `table` 浮动体内容高度超过正文区就会整体溢出。修法 = 在自然分组处
（分子、元素、行组）拆成两个浮动体：第一部分带 `\caption`+`\label`（若
caption 尚未出现），后续部分均为无 caption 浮动体 + 续表文字行。

### 8.4 机器校验编号完整性

```bash
python scripts/verify_pdf.py test_zh.pdf --chapter 5 --max-eq 45 --first-section 标度行为 --regress 4:354
```

- `--first-section` 必填的语义：区分目录页（目录里也有章标题词）与正文页。
- 45/45 且无缺失即通过；再目视抽查 1–2 个渲染页（大式子所在页）确认版式。

### 8.5 陷阱清单（实测踩过，必读）

**A. align 漏 \nonumber 导致全章编号偏移**（第 5 章实测）：
多行无编号推导用 `align` 时，漏掉任何一行的 `\nonumber`，该行就会占用一个
公式编号，其后**整章编号 +1**，且正文 `\eqref` 引用显示值随之全部错位。
规则：无编号多行推导要么用 `\[...\]`+`aligned`，要么 align 每行检查
`\nonumber`。

**B. `\centerline{...}\\` 报 "There's no line here to end"**：
续表标题行后不能跟 `\\[2pt]`。

**C. 替换宏时的粘连**：把 `\varepsilon_{\mathrm{x}}` 全局替换为
`e_{\mathrm{x}}` 会把 `\dd\varepsilon` 变成 `\dde`、`\approx\varepsilon`
变成 `\approxe`。替换后必须 grep `dde_|approxe|approx[a-z]` 类粘连模式。

**D. 同一文件并行 Edit 互相覆盖**：两个并行 Edit 调用同时写一个文件时，
后写的会覆盖先写的（工具层不报错）。**对同一文件的所有 Edit 必须严格串行**；
批量符号替换用 replace_all 也要逐个串行执行，做完后 grep 验证。

**E. 目录页干扰章定位**：目录中同样出现「第五章 位力定理」，按章标题词搜
正文起始页会误中目录页。用「章标题词 + 第一节标题关键词 + 无点线 `......`」
三条件定位（verify_pdf.py 已内置）。

**F. 原书印刷错误**：对照图片确认是原书排印问题后，译文**按原书原样保留**，
用 `% 注释`注明"原书如此，疑为印刷错误，正确形式应为…"（如 (4.111) 的
(3π³)^{1/3}/π）。

**G. 单章 PDF 页脚的 Springer 出版说明**（erratum 链接、版权行）不是书内
正文，不译入正文，在片段头部加 `% 注释`记录即可。

**H. 片段头注释会被拼装剥离**：`strip_lead_comments` 去掉片段开头连续注释，
因此片段的覆盖范围/存疑汇总写在头部没问题，但**正文中间的【修正标记】注释
不受影响**，会一并进入主文件（这是期望行为，保留追溯信息）。

## 9. 阶段九：收尾

1. 术语一致性回归：grep 全文检查新旧章节用词统一（如"位力/维里"）。
2. 把本章页码换算、片段清单、公式数、遗留存疑写入工作日志/memory。
3. 向用户报告：覆盖页、公式计数核对结果、修复的错误类型清单、遗留存疑。
