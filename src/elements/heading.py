"""
Heading element implementation
"""

from typing import Any

from PIL import ImageDraw

from ..config import config
from ..layout_engine import LayoutEngine, LayoutNode
from ..renderer import Renderer
from .base import BaseElement


class HeadingElement(BaseElement):
    """Heading element (h1-h6)"""

    def layout(
        self, layout_engine: LayoutEngine, x: float, viewport_width: int, **kwargs: Any
    ) -> LayoutNode:
        """Layout heading element"""
        size_multiplier = config.HEADING_SIZES.get(self.dom_node.tag, 1.0)
        layout_node = self._create_layout_node(
            x, layout_engine.current_y, viewport_width - 2 * x, 0
        )
        start_y = layout_engine.current_y

        layout_engine.current_y += config.MARGIN * 1.5

        for child in self.dom_node.children:
            if child.tag == "text" and child.text:
                text = child.text.strip()
                if text:
                    text_layout = layout_engine._layout_child(child, x)
                    if text_layout:
                        # Override height and font size for heading
                        height = (
                            config.DEFAULT_FONT_SIZE
                            * size_multiplier
                            * config.LINE_HEIGHT
                        )
                        text_layout.box.height = height
                        text_layout.font_size = (
                            config.DEFAULT_FONT_SIZE * size_multiplier
                        )
                        layout_node.add_child(text_layout)
                        layout_engine.current_y = text_layout.box.y + height

        layout_engine.current_y += config.MARGIN * 1.5
        layout_node.box.height = layout_engine.current_y - start_y

        return layout_node

    def render(
        self, draw: ImageDraw.ImageDraw, layout_node: LayoutNode, renderer: Renderer
    ) -> None:
        """Render heading element"""
        for child in layout_node.children:
            if hasattr(child, "font_size") and hasattr(child, "lines") and child.lines:
                font = renderer._get_font(size=int(child.font_size or 16), bold=True)
                y_offset: float = 0
                line_height: float = (child.font_size or 16) * renderer.LINE_HEIGHT

                for line in child.lines:
                    if line.strip():
                        draw.text(
                            (child.box.x, child.box.y + y_offset),
                            line,
                            fill="black",
                            font=font,
                        )
                    y_offset += line_height
            else:
                renderer._render_node(draw, child)
