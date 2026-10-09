#!/usr/bin/env python3
"""Scale a PNG logo to a target physical circle diameter and add a metric ruler.

CLI QUICK HELP
--------------
Usage:
  python flatball-logo-scale-with-ruler.py [options]

Core inputs:
  --input PATH
      Input PNG path.
      Default: flatball-logo.png

  --output PATH
      Output PNG path.
      Default: flatball-logo-135mm-with-ruler.png

  --dpi INT
      Output DPI written into PNG metadata and used for all mm->px conversions.
      Default: 600

Source image geometry (pixels in the original/input image):
  --image-center-x-px FLOAT
      X coordinate of the circle/badge center in the source image.
      Default: 765.0  (midpoint of 355..1175)

  --image-center-y-px FLOAT
      Y coordinate of the circle/badge center in the source image.
      Default: 485.0

    --image-diameter-px FLOAT
      Pixel diameter of the circle/badge in the source image.
      Default: 820.0  (1175 - 355)

Physical target:
  --target-image-diameter-mm FLOAT
      Desired printed/physical circle diameter in millimeters.
      Default: 135.0

  --ruler-margins-mm FLOAT
      Margin used for ruler placement from LEFT edge (x) and TOP edge (y), in mm.
      Ruler starts at that point and reads 0 mm there.
      Default: 75.0

Paper / page:
  --paper-size {none,ansi-a,letter,a4}
      Fix canvas to a standard paper size. Logo is centered on the page.
        ansi-a / letter : 8.5 x 11 in  (215.9 x 279.4 mm)
        a4              : 210 x 297 mm
        none            : size canvas to content (see margins below)
      Default: ansi-a

  --orientation {landscape,portrait}
      Page orientation. For ANSI A landscape the short edge is 215.9 mm,
      so the ruler spans [0..215.9] mm top-to-bottom.
      Default: landscape

Canvas margins — only used when --paper-size none (millimeters):
  --left-margin-mm FLOAT   Padding left of logo.   Default: 12.0
  --right-margin-mm FLOAT  Padding right of logo.  Default: 10.0
  --top-margin-mm FLOAT    Padding above logo.     Default: 6.0
  --bottom-margin-mm FLOAT Padding below logo.     Default: 6.0

Styling:
  --ruler-color COLOR
      Pillow color for ruler/ticks/labels (for example: black, #222222).
      Default: black

  --background COLOR
      Pillow color for output background.
      Default: white

Example:
  python flatball-logo-scale-with-ruler.py \
      --input flatball-logo.png \
      --output flatball-logo-135mm-with-ruler.png \
      --target-image-diameter-mm 135 \
      --dpi 600

Note:
  Run with --help for auto-generated argparse help (includes defaults).
"""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def pick_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    # Try common Windows fonts first, then fall back to PIL default.
    font_candidates = [
        "arial.ttf",
        "segoeui.ttf",
        "tahoma.ttf",
    ]
    for name in font_candidates:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


# (width_mm, height_mm) defined in portrait orientation; swap for landscape.
PAPER_SIZES: dict[str, tuple[float, float] | None] = {
    "none":   None,
    "ansi-a": (215.9, 279.4),  # 8.5 x 11 in
    "letter": (215.9, 279.4),  # alias for ansi-a
    "a4":     (210.0, 297.0),
}


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Scale a logo to a physical circle diameter and add a left-side metric ruler.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("--input", default="flatball-logo.png", help="Input PNG path")
    p.add_argument(
        "--output",
        default="flatball-logo-135mm-with-ruler.png",
        help="Output PNG path",
    )
    p.add_argument(
        "--dpi",
        type=int,
        default=600,
        help="Output DPI used for mm->px conversion and saved into PNG metadata",
    )

    p.add_argument(
        "--image-center-x-px",
        type=float,
        default=765.0,
        help="X coordinate of circle/badge center in source image pixels",
    )
    p.add_argument(
        "--image-center-y-px",
        type=float,
        default=485.0,
        help="Y coordinate of circle/badge center in source image pixels",
    )
    p.add_argument(
        "--image-diameter-px",
        type=float,
        default=820.0,
        help="Pixel diameter of the circle/badge in the source image",
    )

    p.add_argument(
        "--target-image-diameter-mm",
        type=float,
        default=135.0,
        help="Desired printed/physical circle diameter in millimeters",
    )
    p.add_argument(
        "--ruler-margins-mm",
        type=float,
        default=75.0,
        help="Ruler offset from left and top page edges in millimeters",
    )

    p.add_argument(
        "--left-margin-mm",
        type=float,
        default=12.0,
        help="Canvas margin to the left of the ruler labels",
    )
    p.add_argument(
        "--right-margin-mm",
        type=float,
        default=10.0,
        help="Canvas right margin in millimeters",
    )
    p.add_argument(
        "--top-margin-mm",
        type=float,
        default=6.0,
        help="Canvas top margin in millimeters",
    )
    p.add_argument(
        "--bottom-margin-mm",
        type=float,
        default=6.0,
        help="Canvas bottom margin in millimeters",
    )

    p.add_argument(
        "--paper-size",
        default="ansi-a",
        choices=list(PAPER_SIZES.keys()),
        help="Fix canvas to a standard paper size; 'none' sizes canvas to content",
    )
    p.add_argument(
        "--orientation",
        default="landscape",
        choices=["landscape", "portrait"],
        help="Page orientation applied to paper-size (or content canvas when paper-size is none)",
    )
    p.add_argument(
        "--ruler-color",
        default="black",
        help="Ruler/tick/label color accepted by Pillow",
    )
    p.add_argument(
        "--background",
        default="white",
        help="Output background color accepted by Pillow",
    )
    return p


def main() -> None:
    args = build_parser().parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        raise FileNotFoundError(f"Input image not found: {input_path}")
    if args.image_diameter_px <= 0:
        raise ValueError("--image-diameter-px must be > 0")

    src = Image.open(input_path).convert("RGBA")

    # --- Scale factor ---
    px_per_mm = args.dpi / 25.4
    target_diam_px = args.target_image_diameter_mm * px_per_mm
    scale = target_diam_px / args.image_diameter_px

    scaled_w = max(1, int(round(src.width * scale)))
    scaled_h = max(1, int(round(src.height * scale)))
    logo = src.resize((scaled_w, scaled_h), Image.Resampling.LANCZOS)

    # --- Canvas (paper) size ---
    paper_dim = PAPER_SIZES.get(args.paper_size)
    if paper_dim is not None:
        pw_mm, ph_mm = paper_dim
        if args.orientation == "landscape":
            pw_mm, ph_mm = max(pw_mm, ph_mm), min(pw_mm, ph_mm)
        else:
            pw_mm, ph_mm = min(pw_mm, ph_mm), max(pw_mm, ph_mm)
        canvas_w = int(round(pw_mm * px_per_mm))
        canvas_h = int(round(ph_mm * px_per_mm))
        if scaled_w > canvas_w or scaled_h > canvas_h:
            print(
                f"Warning: scaled logo ({scaled_w}x{scaled_h}px) exceeds "
                f"paper ({canvas_w}x{canvas_h}px) — logo will be clipped."
            )
    else:
        # Size canvas to logo with margins, then enforce orientation.
        top_px    = int(round(args.top_margin_mm    * px_per_mm))
        bottom_px = int(round(args.bottom_margin_mm * px_per_mm))
        left_px   = int(round(args.left_margin_mm   * px_per_mm))
        right_px  = int(round(args.right_margin_mm  * px_per_mm))
        canvas_w  = scaled_w + left_px + right_px
        canvas_h  = scaled_h + top_px  + bottom_px
        if args.orientation == "landscape" and canvas_w <= canvas_h:
            canvas_w = canvas_h + int(round(10.0 * px_per_mm))
        elif args.orientation == "portrait" and canvas_h <= canvas_w:
            canvas_h = canvas_w + int(round(10.0 * px_per_mm))

    # --- Logo placement: center of circle/badge on center of canvas ---
    scaled_cx = args.image_center_x_px * scale
    scaled_cy = args.image_center_y_px * scale
    logo_x = int(round(canvas_w / 2.0 - scaled_cx))
    logo_y = int(round(canvas_h / 2.0 - scaled_cy))

    # --- Ruler: start at (margin, margin), then run down to bottom page edge ---
    ruler_margin_px = int(round(args.ruler_margins_mm * px_per_mm))
    ruler_x   = ruler_margin_px
    ruler_y0  = ruler_margin_px
    ruler_y1  = max(ruler_y0, canvas_h - ruler_margin_px)

    # --- Render ---
    out = Image.new("RGBA", (canvas_w, canvas_h), color=args.background)
    out.alpha_composite(logo, dest=(max(0, logo_x), max(0, logo_y)))

    draw = ImageDraw.Draw(out)

    draw.line([(ruler_x, ruler_y0), (ruler_x, ruler_y1)], fill=args.ruler_color, width=3)

    ruler_span_px = max(0, ruler_y1 - ruler_y0)
    ruler_total_mm = int(round(ruler_span_px / px_per_mm))
    major_len = int(round(6.0 * px_per_mm))
    minor_len = int(round(3.0 * px_per_mm))
    font = pick_font(max(12, int(round(3.2 * px_per_mm))))

    for mm_i in range(0, ruler_total_mm + 1):
        y = int(round(ruler_y0 + mm_i * px_per_mm))
        if y > ruler_y1:
            break
        is_major = (mm_i % 10) == 0
        tick_len = major_len if is_major else minor_len
        draw.line([(ruler_x, y), (ruler_x + tick_len, y)], fill=args.ruler_color, width=2)
        if is_major:
            label = str(mm_i // 10)
            bbox  = draw.textbbox((0, 0), label, font=font)
            tw    = bbox[2] - bbox[0]
            th    = bbox[3] - bbox[1]
            draw.text(
                (ruler_x - tw - int(round(1.2 * px_per_mm)), y - th // 2),
                label,
                fill=args.ruler_color,
                font=font,
            )

    unit_bbox = draw.textbbox((0, 0), "cm", font=font)
    draw.text(
        (ruler_x - (unit_bbox[2] - unit_bbox[0]) - int(round(1.2 * px_per_mm)),
         ruler_y0 + int(round(2.0 * px_per_mm))),
        "cm",
        fill=args.ruler_color,
        font=font,
    )

    out.save(output_path, dpi=(args.dpi, args.dpi))

    page_desc = (
        f"{args.paper_size.upper()} {args.orientation}"
        if args.paper_size != "none"
        else f"content-sized {args.orientation}"
    )
    print(f"Saved:          {output_path}")
    print(f"Paper:          {page_desc}")
    print(f"Scale factor:   {scale:.6f}")
    print(f"Circle diam:    {args.target_image_diameter_mm:.1f} mm  ({target_diam_px:.1f}px)")
    print(f"Output size:    {canvas_w}x{canvas_h}px @ {args.dpi} DPI  "
          f"({canvas_w/px_per_mm:.1f} x {canvas_h/px_per_mm:.1f} mm)")
    print(f"Ruler:          0..{ruler_total_mm} mm  (0..{ruler_total_mm/10:.1f} cm)  "
            f"at x={ruler_x}px, y0={ruler_y0}px ({args.ruler_margins_mm:.1f} mm from left/top edges)")


if __name__ == "__main__":
    main()
