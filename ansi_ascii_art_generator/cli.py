#!/usr/bin/env python3
import colorama

colorama.init()  # Initialize Colorama to enable ANSI escape sequence handling

import argparse
from .core import AsciiArtGenerator
from .utils import image_to_html, calculate_best_width
from .characters import CharacterSet


def main():
    parser = argparse.ArgumentParser(description="Advanced ASCII Art Generator")
    parser.add_argument("image_path", help="Path to input image")
    parser.add_argument("-o", "--output", help="Output file path")
    parser.add_argument("-w", "--width", type=int, default=100, help="Output width")
    parser.add_argument(
        "-c",
        "--color",
        choices=["grayscale", "ansi", "truecolor", "html", "braille"],
        default="braille",
        help="Color mode (braille produces Unicode Braille art)",
    )
    parser.add_argument("-d", "--dither", action="store_true", help="Enable dithering")
    parser.add_argument(
        "-e", "--edges", action="store_true", help="Enable edge detection"
    )
    parser.add_argument(
        "-p",
        "--preset",
        choices=CharacterSet.get_preset_names(),
        default="classic",
        help="Character set preset",
    )
    parser.add_argument(
        "--no-enhance",
        action="store_false",
        dest="enhance",
        help="Disable auto contrast enhancement",
    )

    args = parser.parse_args()

    best_width = calculate_best_width(args.image_path, args.width)
    generator = AsciiArtGenerator(
        args.image_path,
        output_width=best_width,
        color_mode=args.color,
        dithering=args.dither,
        edge_detect=args.edges,
        preset=args.preset,
        enhance_contrast=args.enhance,
    )

    ascii_art = generator.generate_ascii()

    if args.output:
        if args.color == "html":
            image_to_html(ascii_art, args.image_path, args.output)
        else:
            with open(args.output, "w") as f:
                f.write(ascii_art)
        print(f"Saved to {args.output}")
    else:
        print(ascii_art)


if __name__ == "__main__":
    main()
