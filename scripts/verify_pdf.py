# -*- coding: utf-8 -*-
"""
verify_pdf.py —— 机器校验编译产物：公式编号完整性与旧章回归。

用法:
    python verify_pdf.py <编译产物.pdf> --chapter 5 --max-eq 45 [--chapter-word 第五章] [--regress 4:354 3:229]

行为:
  1. 定位目标章的正文起始页（要求同时含章标题词与首个节标题，且不含目录点线，
     以跳过目录页）。
  2. 提取该章范围内所有 (N.x) 公式编号，报告缺失与最大编号。
  3. 若给出 --regress 旧章号:旧章最大编号，则同时回归校验旧章编号完整性
     （防止新章拼装破坏旧章）。

注意: 中文数字章标题（如 第五章）由 --chapter-word 指定；正则同时匹配 (5.x)
     形式的编号。若某编号从未在正文中出现，多半是对应 equation 环境漏写
     \\label 或编号公式总数不符，需回到片段排查。
依赖: pymupdf
"""
import argparse
import re
import sys

import pymupdf


def collect_nums(doc, start_page, stop_pred, tag, max_eq):
    nums = set()
    for i in range(start_page, doc.page_count):
        t = doc[i].get_text()
        for m in re.finditer(rf"\({tag}\.(\d{{1,3}})\)", t):
            n = int(m.group(1))
            if 1 <= n <= max_eq:
                nums.add(n)
        if stop_pred(t):
            break
    return nums


def main() -> None:
    ap = argparse.ArgumentParser(description="校验编译 PDF 中的公式编号完整性")
    ap.add_argument("pdf", help="编译产物 PDF")
    ap.add_argument("--chapter", type=int, required=True, help="目标章号 N")
    ap.add_argument("--max-eq", type=int, required=True, help="该章编号公式总数")
    ap.add_argument("--chapter-word", default=None,
                    help="中文数字章标题词（如 第五章）；不指定则自动生成")
    ap.add_argument("--first-section", default=None,
                    help="该章第一个节标题关键词（用于区分目录与正文，如 标度行为）")
    ap.add_argument("--regress", nargs="*", default=[],
                    help="回归校验: 章号:最大编号（如 4:354），可多个")
    ap.add_argument("--next-chapter-word", default=None,
                    help="下一章的中文数字章标题词（用于界定扫描结束，如 第六章）")
    args = ap.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    cn_num = {1: "一", 2: "二", 3: "三", 4: "四", 5: "五", 6: "六",
              7: "七", 8: "八", 9: "九", 10: "十"}
    word = args.chapter_word or f"第{cn_num.get(args.chapter, args.chapter)}章"

    doc = pymupdf.open(args.pdf)

    # ---- 定位正文起始页：含章标题词 + 首个节标题关键词 + 无目录点线 ----
    start = None
    for i in range(2, doc.page_count):
        t = doc[i].get_text()
        if word not in t or "......" in t:
            continue
        if args.first_section and args.first_section not in t:
            continue
        start = i
        break
    if start is None:
        print(f"[错误] 未找到 {word} 的正文起始页；"
              f"请用 --first-section 提供该章第一节标题的关键词重试。")
        raise SystemExit(1)
    print(f"{word} 正文起始页(0基): {start}  总页数: {doc.page_count}")

    # ---- 编号收集，直到下一章标题出现 ----
    next_word = args.next_chapter_word
    if next_word is None:
        next_word = f"第{cn_num.get(args.chapter + 1, '?')}章"

    def stop(t: str) -> bool:
        return next_word in t

    nums = collect_nums(doc, start, stop, args.chapter, args.max_eq)
    missing = [n for n in range(1, args.max_eq + 1) if n not in nums]
    print(f"第 {args.chapter} 章: 出现编号 {len(nums)}/{args.max_eq}，"
          f"最大编号 {max(nums) if nums else None}")
    print(f"缺失编号: {missing if missing else '无'}")

    # ---- 回归校验 ----
    for spec in args.regress:
        tag_s, max_s = spec.split(":")
        tag, max_eq = int(tag_s), int(max_s)
        rw = f"第{cn_num.get(tag, tag)}章"
        # 回归章从文档头扫到目标章正文开始即可
        nums_r = set()
        for i in range(0, start + 1):
            t = doc[i].get_text()
            for m in re.finditer(rf"\({tag}\.(\d{{1,3}})\)", t):
                n = int(m.group(1))
                if 1 <= n <= max_eq:
                    nums_r.add(n)
            if rw in t and i > 2:
                pass  # 继续扫完当前页即可，简单起见不中断
        miss_r = [n for n in range(1, max_eq + 1) if n not in nums_r]
        print(f"回归 第 {tag} 章: {len(nums_r)}/{max_eq}，"
              f"缺失: {miss_r if miss_r else '无'}")

    if missing:
        raise SystemExit(2)
    print("校验通过。")


if __name__ == "__main__":
    main()
