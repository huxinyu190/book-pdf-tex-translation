# -*- coding: utf-8 -*-
"""
render_chapter.py —— 把一章 PDF 的指定页渲染为 300dpi PNG 并提取文字层。

用法:
    python render_chapter.py <章节.pdf> <输出目录> --start 1 --end 8 --book-offset 218

产物:
    <输出目录>/pages/p001.png ... pNNN.png   (300dpi，用于视觉转写公式)
    <输出目录>/chN_text.txt                   (文字层，带页分隔标记)

说明:
  - 文字层中散文可信、公式是乱码（字体子集映射损坏），公式一律以 PNG 图片为准。
  - 文字层页分隔标记格式: ===== PDF_PAGE n (book m) =====
依赖: pymupdf
"""
import argparse
import os

import pymupdf


def main() -> None:
    ap = argparse.ArgumentParser(description="渲染章节页面并提取文字层")
    ap.add_argument("pdf", help="章节 PDF 路径")
    ap.add_argument("outdir", help="输出目录（建议放在项目下 _tmp_chN，勿放系统盘）")
    ap.add_argument("--start", type=int, required=True, help="起始 PDF 页（1 基）")
    ap.add_argument("--end", type=int, required=True, help="结束 PDF 页（1 基，含）")
    ap.add_argument("--book-offset", type=int, required=True,
                    help="页码换算偏移: 原书页 = PDF 页 + offset")
    ap.add_argument("--dpi", type=int, default=300, help="渲染分辨率（默认 300）")
    args = ap.parse_args()

    pages_dir = os.path.join(args.outdir, "pages")
    os.makedirs(pages_dir, exist_ok=True)

    doc = pymupdf.open(args.pdf)
    zoom = args.dpi / 72.0
    txt_parts = []

    for i in range(args.start - 1, args.end):
        page = doc[i]
        pix = page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom))
        png = os.path.join(pages_dir, f"p{i+1:03d}.png")
        pix.save(png)
        book_page = i + 1 + args.book_offset
        txt_parts.append(
            f"===== PDF_PAGE {i+1} (book {book_page}) =====\n{page.get_text()}")

    txt_path = os.path.join(args.outdir, f"ch_text_p{args.start:03d}_p{args.end:03d}.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(txt_parts))

    rendered = sorted(os.listdir(pages_dir))
    print(f"已渲染 {len(rendered)} 页到 {pages_dir}")
    print(f"文字层已写入 {txt_path}")


if __name__ == "__main__":
    main()
