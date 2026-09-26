# -*- coding: utf-8 -*-
"""
crop_zoom.py —— 从章节 PDF 裁剪局部区域并放大，用于核实疑难公式/符号。

用法:
    python crop_zoom.py <章节.pdf> <输出.png> <页码1基> <y0比例> <y1比例> [倍数] [x0比例] [x1比例]

示例:
    python crop_zoom.py 5-6章.pdf crop_eq532.png 5 0.60 0.73 10
      -> 第 5 页，纵向 60%~73% 区域，10 倍放大

说明:
  - y0/y1 是相对页面高度的比例（0~1）；x0/x1 默认整页宽。
  - 当整页 300dpi 图上仍有符号看不清（上下标、撇号、指数中的 π 幂次等），
    用本脚本放大到 9~10 倍再目视确认。
依赖: pymupdf
"""
import sys

import pymupdf


def main() -> None:
    if len(sys.argv) < 6:
        print(__doc__)
        sys.exit(1)
    pdf, out = sys.argv[1], sys.argv[2]
    page_no = int(sys.argv[3])          # 1 基
    y0, y1 = float(sys.argv[4]), float(sys.argv[5])
    zoom = float(sys.argv[6]) if len(sys.argv) > 6 else 9.0
    x0 = float(sys.argv[7]) if len(sys.argv) > 7 else 0.0
    x1 = float(sys.argv[8]) if len(sys.argv) > 8 else 1.0

    doc = pymupdf.open(pdf)
    page = doc[page_no - 1]
    r = page.rect
    clip = pymupdf.Rect(r.width * x0, r.height * y0, r.width * x1, r.height * y1)
    pix = page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), clip=clip)
    pix.save(out)
    print(f"saved {out}  ({pix.width}x{pix.height})")


if __name__ == "__main__":
    main()
