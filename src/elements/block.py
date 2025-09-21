"""
Block element implementations
"""

from PIL import ImageDraw

from ..layout_engine import LayoutEngine, LayoutNode
from ..renderer import Renderer
from .base import BaseElement


class BlockElement(BaseElement):
    """Block-level element (p, div, blockquote, pre)"""

    def layout(
        self, layout_engine: LayoutEngine, x: float, viewport_width: int, **kwargs
    ) -> LayoutNode:
        """Layout block-level element"""
        layout_node = self._create_layout_node(
            x, layout_engine.current_y, viewport_width - 2 * x, 0
        )

        start_y = layout_engine.current_y
        layout_engine.current_y += layout_engine.MARGIN

        for child in self.dom_node.children:
            child_layout = layout_engine._layout_child(child, x + layout_engine.PADDING)
            if child_layout:
                layout_node.add_child(child_layout)

        layout_engine.current_y += layout_engine.MARGIN
        layout_node.box.height = layout_engine.current_y - start_y

        return layout_node

    def render(
        self, draw: ImageDraw.ImageDraw, layout_node: LayoutNode, renderer: Renderer
    ) -> None:
        """Render block element"""
        # For blockquote, draw a left border
        if self.dom_node.tag == "blockquote":
            self._render_blockquote_border(draw, layout_node.box)

        # Render children
        for child in layout_node.children:
            renderer._render_node(draw, child)

    def _render_blockquote_border(self, draw: ImageDraw.ImageDraw, box) -> None:
        """Draw left border for blockquote"""
        draw.rectangle(
            (box.x - 5, box.y, box.x - 3, box.y + box.height), fill="#cccccc"
        )
