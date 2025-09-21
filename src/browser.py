#!/usr/bin/env python3
"""
Toy Web Browser - A minimal HTML renderer that outputs to PNG
"""

import argparse
import sys
from pathlib import Path

from .layout import LayoutEngine
from .parser import HTMLParser
from .renderer import Renderer


def render_html(input_file: Path, output_file: Path) -> None:
    """Render an HTML file to a PNG image"""
    if not input_file.exists():
        raise FileNotFoundError(f"Input file '{input_file}' not found")

    # Read HTML content
    with open(input_file, "r", encoding="utf-8") as f:
        html_content: str = f.read()

    # Parse HTML
    parser = HTMLParser()
    dom_tree = parser.parse(html_content)

    # Layout elements
    layout_engine = LayoutEngine()
    layout_tree = layout_engine.compute_layout(dom_tree)

    # Render to image with calculated height
    # Add padding, minimum 600px
    content_height = max(int(layout_tree.box.height) + 20, 600)
    renderer = Renderer(width=800, height=content_height)
    image = renderer.render(layout_tree)

    # Ensure output directory exists
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Save as PNG
    image.save(output_file, "PNG")
    print(f"Rendered HTML to: {output_file}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Toy Web Browser - A minimal HTML renderer that outputs to PNG"
    )
    parser.add_argument("input", type=Path, help="Input HTML file")
    parser.add_argument("output", type=Path, help="Output PNG file")
    parser.add_argument(
        "--output-dir",
        "-o",
        type=Path,
        help="Output directory (overrides output file directory)",
    )

    args = parser.parse_args()

    input_file = args.input
    output_file = args.output

    # Override output directory if specified
    if args.output_dir:
        output_file = args.output_dir / output_file.name

    try:
        render_html(input_file, output_file)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error rendering HTML: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
