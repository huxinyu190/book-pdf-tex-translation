# book-pdf-tex-translation

把学术书籍的单章 PDF（Springer 单章版等）**OCR 级翻译并转写为 LaTeX 中文版**，拼入主 `.tex` 并编译验证的完整工作流（WorkBuddy Skill）。

> 本 skill 从《Density Functional Theory: An Advanced Course》(Dreizler & Gross)  
> 第 2–5 章的完整翻译实战中提炼：含 109 页 / 354 条编号公式 / 20 图 13 表的单章  
> 端到端翻译经验。

## 功能一览

- 章节结构分析：页码换算、节标题清单、公式编号分布、图表定位
- 页面渲染：300dpi PNG（公式视觉转写用）+ 文字层（散文底本）
- 疑难符号放大核实：局部裁剪 9–10 倍
- 片段拼装：幂等、自动备份
- 编译验证：公式编号完整性机器校验 + 旧章回归

## 目录结构

```
book-pdf-tex-translation/
├── SKILL.md                            # skill 主文件（流程概览 + 陷阱精选）
├── scripts/
│   ├── pdf_info.py                     # 结构分析（页码换算/公式分布/图表定位）
│   ├── render_chapter.py               # 渲染 300dpi PNG + 文字层
│   ├── crop_zoom.py                    # 局部裁剪放大
│   ├── assemble.py                     # 片段拼装（幂等 + 备份）
│   └── verify_pdf.py                   # 编译产物编号校验 + 回归
├── references/
│   ├── workflow.md                     # 九阶段完整流程 + 实测陷阱 A–H
│   └── fragment-brief-template.md      # 片段派发 / 视觉复核任务模板
└── assets/
    ├── main.tex                        # 译著主文件骨架
    └── book-zh.cls                     # 中译排版类（xelatex，复刻 Springer 版式）
```

## 环境要求

- Python 3.10+，`pip install pymupdf`
- TeX Live（xelatex；cls 基于 ctexbook，需中文环境）

## 快速上手

```bash
# 1. 结构分析（页码换算 / 公式分布 / 图表定位）
python scripts/pdf_info.py "5-6章.pdf" --eq-tag 5

# 2. 渲染页面 + 文字层（临时目录放项目下，勿放系统盘）
python scripts/render_chapter.py "5-6章.pdf" ./_tmp_ch5 --start 1 --end 8 --book-offset 218

# 3. 疑难公式放大核实
python scripts/crop_zoom.py "5-6章.pdf" crop.png 5 0.60 0.73 10

# 4. 翻译完成后拼入主文件（幂等，自动备份）
python scripts/assemble.py test_zh.tex --mark "_frag_5_1.tex" _frag_5_1.tex _frag_5_2_3.tex _frag_5_4.tex

# 5. 编译 3 遍后机器校验编号完整性 + 旧章回归
xelatex -interaction=nonstopmode -halt-on-error test_zh.tex   # ×3
python scripts/verify_pdf.py test_zh.pdf --chapter 5 --max-eq 45 \
    --first-section 标度行为 --regress 4:354
```

完整流程、拆分策略、子代理派发模板与实测陷阱清单见  
[`references/workflow.md`](references/workflow.md)。

## 实测陷阱（节选，详见 workflow.md §8.5）

- `align` 无编号多行推导漏 `\nonumber` → 该行静默占用编号，其后**整章编号 +1**，  
  所有 `\eqref` 显示值错位
- 跨页大表超高（`Float too large`）→ 按自然分组拆续表
- 全局符号替换产生粘连（`\dd\varepsilon` → `\dde`）
- 文字层公式是乱码（字体子集映射损坏），公式一律以页面图片为准

## 免责声明

本仓库仅包含翻译工作流工具与排版模板，**不含任何原书内容**（原书 PDF、  
扫描页图、封面等均不得提交）。使用本工具翻译受版权保护的书籍时，译文仅供  
个人学习交流，版权归原作者与出版社所有。

## License

[MIT](LICENSE)（仅覆盖本仓库自有的脚本、模板与文档）
