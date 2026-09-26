# -*- coding: utf-8 -*-
"""
assemble.py —— 把一章的翻译片段按顺序拼入主 .tex 文件（幂等）。

用法:
    python assemble.py <主文件.tex> --mark "_frag_5_1.tex" 片段1.tex 片段2.tex ...

行为:
  1. 若主文件中已存在 MARK（首个片段的注释标记），则判定已拼装过，跳过。
  2. 拼装前自动备份主文件为 <主文件>.bak_<时间戳>。
  3. 每个片段剥去开头连续的 % 注释块与空行（各片段的头部说明不进正文），
     再以 "% >>>>>>>>>> 片段名 <<<<<<<<<<" 分隔注释拼入 \\end{document} 之前。

注意: 拼装前请确认主文件恰好含一个 \\end{document}。
"""
import argparse
import io
import os
import sys
import time


def strip_lead_comments(text: str) -> str:
    """去掉片段开头连续的 % 注释块与空行，保留正文。"""
    lines = text.splitlines(True)
    i = 0
    while i < len(lines) and (lines[i].lstrip().startswith("%") or lines[i].strip() == ""):
        i += 1
    return "".join(lines[i:])


def main() -> None:
    ap = argparse.ArgumentParser(description="拼装翻译片段到主 tex 文件")
    ap.add_argument("main_tex", help="主文件路径（如 test_zh.tex）")
    ap.add_argument("frags", nargs="+", help="片段文件，按出现顺序")
    ap.add_argument("--mark", default=None,
                    help="幂等标记（默认取第一个片段文件名构造）")
    args = ap.parse_args()

    end_doc = chr(92) + "end{document}"
    mark = args.mark or ("% >>>>>>>>>> " + os.path.basename(args.frags[0]) + " <<<<<<<<<<")

    os.chdir(os.path.dirname(os.path.abspath(args.main_tex)) or ".")
    main_name = os.path.basename(args.main_tex)

    s = io.open(main_name, encoding="utf-8").read()
    assert s.count(end_doc) == 1, "end{document} 数量异常"

    if mark in s:
        print("本章内容已拼入，跳过（如需重拼请先从备份恢复主文件）。")
        return

    # 备份
    stamp = time.strftime("%Y%m%d_%H%M%S")
    backup = main_name + f".bak_{stamp}"
    io.open(backup, "w", encoding="utf-8").write(s)
    print(f"已备份主文件 -> {backup}")

    parts = []
    for name in args.frags:
        assert os.path.exists(name), f"缺失片段: {name}"
        body = strip_lead_comments(io.open(name, encoding="utf-8").read())
        parts.append(f"% >>>>>>>>>> {os.path.basename(name)} <<<<<<<<<<\n{body.strip()}\n")

    merged = "\n" + "\n\n".join(parts)
    s = s.replace(end_doc, merged + "\n" + end_doc, 1)
    io.open(main_name, "w", encoding="utf-8").write(s)
    print(f"拼装完成，{main_name} 共 {len(s.splitlines())} 行")
    sys.exit(0)


if __name__ == "__main__":
    main()
