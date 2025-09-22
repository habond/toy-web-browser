"""
Table cell element implementation
"""

from typing import Any

from PIL import ImageDraw

from ...config import config
from ...layout_engine import LayoutEngine, LayoutNode
from ...renderer import Renderer
from ..base import BaseElement


class TableCellElement(BaseElement):
    """Table cell element (td, th)"""

    def layout(
        self, layout_engine: LayoutEngine, x: float, viewport_width: int, **kwargs: Any
    ) -> LayoutNode:
        """Delegate to layout_with_width method"""
        # This shouldn't be called directly for table cells
        # They should use layout_with_width instead
        return self.layout_with_width(layout_engine, x, viewport_width, 0)

    def layout_with_width(
        self,
        layout_engine: LayoutEngine,
        x: float,
        viewport_width: int,
        width: float,
    ) -> LayoutNode:
        """Layout table cell with specific width"""
        layout_node = self._create_layout_node(x, layout_engine.current_y, width, 0)

        start_y = layout_engine.current_y
        cell_content_y = start_y + config.PADDING

        # Save the current Y position to restore later (for table row consistency)
        saved_y = layout_engine.current_y
        layout_engine.current_y = cell_content_y

        # Layout cell content with restricted width
        content_width = width - 2 * config.PADDING
        for child in self.dom_node.children:
            if child.tag != "text" or (child.text and child.text.strip()):
                child_layout = layout_engine._layout_child_with_width(
                    child, x + config.PADDING, content_width
                )
                if child_layout:
                    layout_node.add_child(child_layout)

        # Calculate cell height based on content
        content_height = layout_engine.current_y - cell_content_y
        layout_node.box.height = content_height + 2 * config.PADDING

        # Restore the Y position so other cells in the same row start at the same Y
        layout_engine.current_y = saved_y

        return layout_node

    def render(
        self, draw: ImageDraw.ImageDraw, layout_node: LayoutNode, renderer: Renderer
    ) -> None:
        """Render table cell with background for headers"""
        # Draw background for header cells
        if self.dom_node.tag == "th":
            # Adjust rectangle to not cover grid lines (1px border)
            draw.rectangle(
                (
                    layout_node.box.x + 1,
                    layout_node.box.y + 1,
                    layout_node.box.x + layout_node.box.width - 1,
                    layout_node.box.y + layout_node.box.height - 1,
                ),
                fill="#f0f0f0",
            )

        # Render children
        for child in layout_node.children:
            renderer._render_node(draw, child)
