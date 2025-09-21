"""
Renderer - Renders the layout tree to a PNG image
"""

from pathlib import Path
from typing import Dict, Optional, Tuple, Union

from PIL import Image, ImageDraw, ImageFont
from PIL.ImageFont import FreeTypeFont

from .layout_engine import LayoutNode


class Renderer:
    """Renders layout tree to image"""

    def __init__(
        self, width: int = 800, height: int = 600, bg_color: str = "white"
    ) -> None:
        self.width: int = width
        self.height: int = height
        self.bg_color: str = bg_color

        # Try to use a nice font, fall back to default
        self.font_cache: Dict[
            Tuple[int, bool, bool], Union[FreeTypeFont, ImageFont.ImageFont]
        ] = {}
        self.default_font: Optional[Union[FreeTypeFont, ImageFont.ImageFont]] = None
        self.bold_font: Optional[Union[FreeTypeFont, ImageFont.ImageFont]] = None
        self.mono_font: Optional[Union[FreeTypeFont, ImageFont.ImageFont]] = None
        self._load_fonts()

    def _load_fonts(self) -> None:
        """Load fonts for rendering"""
        # Get path to project fonts directory
        project_root = Path(__file__).parent.parent
        fonts_dir = project_root / "fonts"

        self.default_font = None
        self.bold_font = None
        self.mono_font = None

        # Load regular font (Open Sans)
        regular_font_path = fonts_dir / "OpenSans-Regular.ttf"
        if regular_font_path.exists():
            try:
                self.default_font = ImageFont.truetype(str(regular_font_path), 16)
                # Use the same font for bold if we don't have a separate bold file
                self.bold_font = ImageFont.truetype(str(regular_font_path), 16)
            except Exception:
                pass

        # Load monospace font
        mono_font_path = fonts_dir / "SourceCodePro-Regular.ttf"
        if mono_font_path.exists():
            try:
                self.mono_font = ImageFont.truetype(str(mono_font_path), 16)
            except Exception:
                pass

        # Fall back to PIL default font if no TrueType font found
        if not self.default_font:
            self.default_font = ImageFont.load_default()

    def _get_font(
        self,
        size: int = 16,
        bold: bool = False,
        italic: bool = False,
        monospace: bool = False,
    ) -> Union[FreeTypeFont, ImageFont.ImageFont]:
        """Get or create a font with specific size and style"""
        key: Tuple[int, bool, bool] = (size, bold, italic)
        if key in self.font_cache:
            return self.font_cache[key]

        font: Union[FreeTypeFont, ImageFont.ImageFont]

        # Choose base font based on style
        base_font: Optional[Union[FreeTypeFont, ImageFont.ImageFont]]
        if monospace and self.mono_font:
            base_font = self.mono_font
        elif bold and self.bold_font:
            base_font = self.bold_font
        else:
            base_font = self.default_font

        # Try to create font with requested size
        if base_font and isinstance(base_font, FreeTypeFont):
            try:
                font = ImageFont.truetype(base_font.path, int(size))  # type: ignore
            except Exception:
                font = base_font
        elif base_font:
            font = base_font
        else:
            font = ImageFont.load_default()

        self.font_cache[key] = font
        return font

    def render(self, layout_root: LayoutNode) -> Image.Image:
        """Render layout tree to image"""
        # Create image with white background
        image = Image.new("RGB", (self.width, self.height), self.bg_color)
        draw = ImageDraw.Draw(image)

        # Render the tree
        self._render_node(draw, layout_root)

        return image

    def _render_node(self, draw: ImageDraw.ImageDraw, layout_node: LayoutNode) -> None:
        """Recursively render a layout node"""
        dom_node = layout_node.dom_node
        box = layout_node.box

        # Handle different node types
        if dom_node.tag == "text":
            self._render_text(draw, layout_node)

        elif dom_node.tag == "hr":
            # Draw horizontal rule
            draw.line(
                [(box.x, box.y), (box.x + box.width, box.y)], fill="gray", width=2
            )

        elif dom_node.tag in ["h1", "h2", "h3", "h4", "h5", "h6"]:
            # Render headings with appropriate font size
            for child in layout_node.children:
                if child.dom_node.tag == "text" and child.dom_node.text:
                    font_size = getattr(child, "font_size", 16)
                    font = self._get_font(int(font_size), bold=True)
                    text = child.dom_node.text.strip()
                    if text:
                        draw.text(
                            (child.box.x, child.box.y), text, fill="black", font=font
                        )

        elif dom_node.tag == "li":
            # Draw list marker
            if hasattr(layout_node, "marker") and layout_node.marker:
                marker_pos = getattr(layout_node, "marker_pos", (box.x - 20, box.y))
                # Use a slightly smaller font for markers to improve alignment
                marker_font = self._get_font(14, bold=True)
                draw.text(
                    marker_pos, layout_node.marker, fill="black", font=marker_font
                )

        elif dom_node.tag in ["b", "strong"]:
            # Bold text
            for child in layout_node.children:
                if child.dom_node.tag == "text":
                    self._render_text(draw, child, bold=True)
                else:
                    self._render_node(draw, child)
            return

        elif dom_node.tag in ["i", "em"]:
            # Italic text (simulated with normal text for simplicity)
            for child in layout_node.children:
                if child.dom_node.tag == "text":
                    self._render_text(draw, child, italic=True)
                else:
                    self._render_node(draw, child)
            return

        elif dom_node.tag == "u":
            # Underlined text
            for child in layout_node.children:
                if child.dom_node.tag == "text":
                    self._render_text(draw, child, underline=True)
                else:
                    self._render_node(draw, child)
            return

        elif dom_node.tag == "code":
            # Code with background
            if box.width > 0 and box.height > 0:
                # Draw light gray background
                draw.rectangle(
                    (box.x, box.y, box.x + box.width, box.y + box.height),
                    fill="#f0f0f0",
                )
            for child in layout_node.children:
                if child.dom_node.tag == "text":
                    self._render_text(draw, child, monospace=True)
                else:
                    self._render_node(draw, child)
            return

        elif dom_node.tag == "a":
            # Links (rendered in blue)
            for child in layout_node.children:
                if child.dom_node.tag == "text":
                    self._render_text(draw, child, color="blue", underline=True)
                else:
                    self._render_node(draw, child)
            return

        elif dom_node.tag == "blockquote":
            # Draw left border for blockquote
            if box.height > 0:
                draw.line(
                    [(box.x, box.y), (box.x, box.y + box.height)], fill="gray", width=3
                )

        # Render children
        for child in layout_node.children:
            self._render_node(draw, child)

    def _render_text(
        self,
        draw: ImageDraw.ImageDraw,
        layout_node: LayoutNode,
        bold: bool = False,
        italic: bool = False,
        underline: bool = False,
        monospace: bool = False,
        color: str = "black",
    ) -> None:
        """Render text content"""
        if not layout_node.dom_node.text:
            return
        text = layout_node.dom_node.text.strip()
        if not text:
            return

        font_size = getattr(layout_node, "font_size", None) or 16
        font = self._get_font(
            int(font_size), bold=bold, italic=italic, monospace=monospace
        )

        # Handle multi-line text
        if hasattr(layout_node, "lines") and layout_node.lines:
            y = layout_node.box.y
            for line in layout_node.lines:
                draw.text((layout_node.box.x, y), line, fill=color, font=font)
                if underline:
                    text_bbox = draw.textbbox((layout_node.box.x, y), line, font=font)
                    draw.line(
                        [(text_bbox[0], text_bbox[3]), (text_bbox[2], text_bbox[3])],
                        fill=color,
                        width=1,
                    )
                y += font_size * 1.5
        else:
            # Single line text
            draw.text(
                (layout_node.box.x, layout_node.box.y), text, fill=color, font=font
            )
            if underline:
                text_bbox = draw.textbbox(
                    (layout_node.box.x, layout_node.box.y), text, font=font
                )
                draw.line(
                    [(text_bbox[0], text_bbox[3]), (text_bbox[2], text_bbox[3])],
                    fill=color,
                    width=1,
                )
