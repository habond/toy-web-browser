"""
Text element implementation
"""

from typing import Any, Optional

from PIL import ImageDraw

from ..layout_engine import LayoutEngine, LayoutNode
from ..layout_utils import LayoutMixin, LayoutUtils
from ..renderer import Renderer
from .base import BaseElement


class TextElement(BaseElement, LayoutMixin):
    """Text element for rendering text content"""

    def layout(
        self, layout_engine: LayoutEngine, x: float, viewport_width: int, **kwargs: Any
    ) -> Optional[LayoutNode]:
        """Layout text with word wrapping"""
        text = self.dom_node.text.strip() if self.dom_node.text else ""

        if not text:
            return None

        # Use layout utils for text wrapping
        max_width = kwargs.get("max_width", viewport_width - 2 * x)
        lines = LayoutUtils.wrap_text(text, max_width)
        height = LayoutUtils.compute_text_height(lines, layout_engine.DEFAULT_FONT_SIZE)
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
        y_offset: float = 0
        line_height: float = renderer.DEFAULT_FONT_SIZE * renderer.LINE_HEIGHT

        for line in layout_node.lines:
            if line.strip():
                draw.text(
                    (layout_node.box.x, layout_node.box.y + y_offset),
                    line,
                    fill="black",
                    font=font,
                )
            y_offset += line_height
