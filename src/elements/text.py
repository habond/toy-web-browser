"""
Text element implementation
"""

from typing import List, Optional

from PIL import ImageDraw

from ..layout_engine import LayoutEngine, LayoutNode
from ..renderer import Renderer
from .base import BaseElement


class TextElement(BaseElement):
    """Text element for rendering text content"""

    def layout(
        self, layout_engine: LayoutEngine, x: float, viewport_width: int, **kwargs
    ) -> Optional[LayoutNode]:
        """Layout text with word wrapping"""
        text = self.dom_node.text.strip() if self.dom_node.text else ""

        if not text:
            return None

        # Simple text wrapping
        words = text.split()
        lines: List[str] = []
        current_line: List[str] = []
        line_width = 0
        max_width = kwargs.get("max_width", viewport_width - 2 * x)
        char_width = 8  # Approximate character width

        for word in words:
            word_width = len(word) * char_width
            if line_width + word_width > max_width and current_line:
                lines.append(" ".join(current_line))
                current_line = [word]
                line_width = word_width
            else:
                current_line.append(word)
                line_width += word_width + char_width

        if current_line:
            lines.append(" ".join(current_line))

        height = (
            len(lines) * layout_engine.DEFAULT_FONT_SIZE * layout_engine.LINE_HEIGHT
        )
        layout_node = self._create_layout_node(
            x, layout_engine.current_y, max_width, height
        )
        layout_node.lines = lines  # Store lines for rendering
        layout_engine.current_y += height

        return layout_node

    def render(
        self, draw: ImageDraw.ImageDraw, layout_node: LayoutNode, renderer: Renderer
    ) -> None:
        """Render text to the image"""
        if not hasattr(layout_node, "lines") or not layout_node.lines:
            return

        font = renderer._get_font()
        y_offset = 0
        line_height = renderer.DEFAULT_FONT_SIZE * renderer.LINE_HEIGHT

        for line in layout_node.lines:
            if line.strip():
                draw.text(
                    (layout_node.box.x, layout_node.box.y + y_offset),
                    line,
                    fill="black",
                    font=font,
                )
            y_offset += line_height
