# -*- coding: utf-8 -*-
"""
pdf_info.py —— 分析书籍单章 PDF 的结构，为翻译拆分做准备。

用法:
    python pdf_info.py <章节.pdf> [--eq-tag 5] [--scan-limit 20]

功能:
  1. 页数、页面尺寸
  2. 从版权行探测页码换算（原书页 = PDF 页 + offset）
  3. 章/节/小节标题清单及其所在 PDF 页
  4. 公式编号 (N.x) 分布：编号范围、缺失编号、每个编号的首次出现页
  5. 图 (Fig./Figure N.x) 与表 (Table N.x) 的定位

输出全部为 UTF-8 文本到 stdout，可直接重定向到文件。
依赖: pymupdf（pip install pymupdf）
"""
import argparse
import re
import sys

import pymupdf


def main() -> None:
    ap = argparse.ArgumentParser(description="书籍章节 PDF 结构分析")
    ap.add_argument("pdf", help="章节 PDF 路径（单章版或多章合并版均可）")
    ap.add_argument("--eq-tag", type=int, default=None,
                    help="公式编号的章号 N（匹配 (N.x)）；不指定则自动从章节标题猜")
    ap.add_argument("--scan-limit", type=int, default=0,
                    help="只扫描前 N 页（0 = 全部）")
    args = ap.parse_args()

    # Windows 控制台强制 UTF-8 输出，避免 GBK 乱码
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    doc = pymupdf.open(args.pdf)
    n_pages = doc.page_count
    limit = args.scan_limit if args.scan_limit > 0 else n_pages

    print(f"总页数: {n_pages}")
    print(f"页面尺寸: {doc[0].rect}")

    texts = []  # (pdf_page_1based, text)
    for i in range(limit):
        texts.append((i + 1, doc[i].get_text()))

    # ---- 页码换算：找 "pp. A–B (2011)" 之类的版权行 ----
    print("\n--- 页码换算线索（版权行） ---")
    for p, t in texts:
        m = re.search(r"pp\.\s*(\d+)\s*[-–—]\s*(\d+)", t)
        if m:
            print(f"PDF p{p}: 版权行 pp. {m.group(1)}–{m.group(2)}")
            first_page = int(m.group(1))
            print(f"  => 若本章从该页开始，则 原书页 = PDF页 + {first_page - p}")
            break

    # ---- 章节标题 ----
    print("\n--- 章节标题 ---")
    for p, t in texts:
        lines = [l.strip() for l in t.splitlines()]
        for line in lines:
            # 节标题: "5.1 Scaling ..." / 小节: "5.1.2 Foo bar"
            if re.match(r"^\d+\.\d+(\.\d+)?\s+[A-Z]", line) and len(line) < 90:
                print(f"PDF p{p}: {line}")
            # 章标题: "Chapter 6" 单独行 或 "6 Foo" 大节标题行
            elif re.match(r"^Chapter\s+\d+$", line):
                print(f"PDF p{p}: [章标题行] {line}")

    # ---- 公式编号分布 ----
    tag = args.eq_tag
    if tag is None:
        # 从节标题猜章号
        for p, t in texts:
            m = re.search(r"^(\d+)\.\d+\s+[A-Z]", t, re.MULTILINE)
            if m:
                tag = int(m.group(1))
                break
    if tag is not None:
        print(f"\n--- 公式 ({tag}.x) 编号分布 ---")
        eqs: dict[int, list[int]] = {}
        for p, t in texts:
            for m in re.finditer(rf"\({tag}\.(\d{{1,3}})\)", t):
                eqs.setdefault(int(m.group(1)), []).append(p)
        if eqs:
            lo, hi = min(eqs), max(eqs)
            miss = [n for n in range(lo, hi + 1) if n not in eqs]
            print(f"编号范围: ({tag}.{lo})–({tag}.{hi})，共 {len(eqs)} 个不同编号")
            print(f"缺失编号: {miss if miss else '无'}")
            firsts = {n: min(ps) for n, ps in eqs.items()}
            print("首现页（编号: PDF页）:")
            for n in sorted(firsts):
                print(f"  ({tag}.{n}): p{firsts[n]}")
        else:
            print("未发现公式编号")
    else:
        print("\n[未指定 --eq-tag 且无法自动推断章号，跳过公式分布]")

    # ---- 图表定位 ----
    print("\n--- 图表定位 ---")
    for p, t in texts:
        for m in re.finditer(r"(Fig\.|Figure|Table)\s*(\d+\.\d+)", t):
            print(f"PDF p{p}: {m.group(0)}")


if __name__ == "__main__":
    main()
