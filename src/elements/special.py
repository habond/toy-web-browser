"""
Special element implementations
"""

from typing import Any, Optional

from PIL import ImageDraw

from ..layout_engine import Box, LayoutEngine, LayoutNode
from ..renderer import Renderer
from .base import BaseElement


class BreakElement(BaseElement):
    """Line break element (br)"""

    def layout(
        self, layout_engine: LayoutEngine, x: float, viewport_width: int, **kwargs: Any
    ) -> Optional[LayoutNode]:
        """Layout line break"""
        layout_engine.current_y += layout_engine.DEFAULT_FONT_SIZE * 0.5
        return None

    def render(
        self, draw: ImageDraw.ImageDraw, layout_node: LayoutNode, renderer: Renderer
    ) -> None:
        """Render line break (no visual output)"""
        pass


class HorizontalRuleElement(BaseElement):
    """Horizontal rule element (hr)"""

    def layout(
        self, layout_engine: LayoutEngine, x: float, viewport_width: int, **kwargs: Any
    ) -> LayoutNode:
        """Layout horizontal rule"""
        layout_node = LayoutNode(self.dom_node)
        layout_node.box = Box(x, layout_engine.current_y, viewport_width - 2 * x, 2)
        layout_engine.current_y += 10
        return layout_node

    def render(
        self, draw: ImageDraw.ImageDraw, layout_node: LayoutNode, renderer: Renderer
    ) -> None:
        """Render horizontal rule as a line"""
        draw.rectangle(
            (
                layout_node.box.x,
                layout_node.box.y,
                layout_node.box.x + layout_node.box.width,
                layout_node.box.y + layout_node.box.height,
            ),
            fill="#cccccc",
        )
