# 📖 book-pdf-tex-translation

> 一个把**学术书籍章节 PDF** 翻译成**可编译 LaTeX 中文版**的 WorkBuddy Agent Skill。  
> 从《Density Functional Theory: An Advanced Course》(Dreizler & Gross, Springer)  
> 第 2–5 章的完整翻译实战中提炼——含 109 页 / 354 条编号公式 / 20 图 13 表的单章  
> 端到端经验。

**解决的问题**：PDF 文字层的公式是字体子集乱码、无法直接复制；长章节手工翻译  
容易漏公式、错编号、编号对不上交叉引用。本 skill 把整件事变成一条可校验的流水线：

```
章节结构分析 → 300dpi 页面渲染 → 公式逐条视觉转写 → 按节产出片段
→ 幂等拼装 → xelatex 编译 → 公式编号完整性机器校验
```

## 安装

把整个 `book-pdf-tex-translation/` 文件夹放入：

```
Windows:  C:\Users\<你>\.workbuddy\skills\
macOS:    ~/.workbuddy/skills/
```

或在 WorkBuddy 对话中通过技能市场 / 本地导入安装。

## 使用

在 WorkBuddy 对话中直接说：

- 「把 `4章.pdf` 翻译成 LaTeX 放进 `test_zh.tex`」
- 「继续翻译第 6 章」
- 「拼装编译 test_zh 并核对公式编号」

## 九阶段工作流

| 阶段      | 内容                            | 工具                  |
| ------- | ----------------------------- | ------------------- |
| 1 结构分析  | 页码换算、节标题、公式编号分布、图表定位          | `pdf_info.py`       |
| 2 页面渲染  | 300dpi PNG（转写用）+ 文字层（散文底本）    | `render_chapter.py` |
| 3 拆分    | 按节拆片段（≤15 页 / 60 条公式），切点选节标题前 | —                   |
| 4 Brief | 记号宏、术语表、图表规范、修正标记规范           | 见 references        |
| 5 翻译    | 逐页读图转写公式；长章派子代理并行             | `crop_zoom.py`      |
| 6 视觉复核  | 逐条对照图片修正（大章节必做）               | 见 references        |
| 7 拼装    | 幂等、自动备份                       | `assemble.py`       |
| 8 编译验证  | xelatex ×3 + log 排错 + 编号机器校验  | `verify_pdf.py`     |
| 9 收尾    | 术语回归、进度记录                     | —                   |

## 目录结构

```
book-pdf-tex-translation/
├── SKILL.md                    # skill 入口（WorkBuddy 自动加载）
├── scripts/
│   ├── pdf_info.py             # 章节结构 / 公式编号分布 / 图表定位
│   ├── render_chapter.py       # 300dpi 渲染 + 文字层提取
│   ├── crop_zoom.py            # 疑难公式局部放大（9–10×）
│   ├── assemble.py             # 片段拼装（幂等 + 自动备份）
│   └── verify_pdf.py           # 编号完整性校验 + 旧章回归
├── references/
│   ├── workflow.md             # 九阶段完整手册 + 实测陷阱 A–H
│   └── fragment-brief-template.md  # 片段派发 / 视觉复核任务模板
└── assets/
    ├── main.tex                # 译著主文件骨架
    └── book-zh.cls             # 中译排版类（复刻 Springer 版式）
```

## 实测陷阱（节选）

- 🔴 `align` 无编号推导漏一行 `\nonumber` → 该行静默占用编号，**其后整章编号  
  +1**，所有 `\eqref` 显示值错位
- 🟠 跨页大表超高（`Float too large`）→ 按自然分组拆续表
- 🟠 全局符号替换产生粘连（`\dd\varepsilon` → `\dde`）
- 🟡 同一文件并行 Edit 互相覆盖（后写覆盖先写，无报错）
- 🟡 目录页也含章标题词 → 用「章标题 + 首节标题 + 无点线」三条件定位正文

完整清单见 [`references/workflow.md`](references/workflow.md) §8.5。

## 环境要求

- WorkBuddy（Agent 模式，支持图片读取的模型）
- Python 3.10+，`pip install pymupdf`
- TeX Live（XeLaTeX + ctex 中文环境）

## 免责声明

本 skill 仅包含翻译工作流工具与排版模板，**不含任何书籍内容**。用它翻译受  
版权保护的书籍时，译文仅供个人学习交流，版权归原作者与出版社所有。

## License

[MIT](LICENSE)
