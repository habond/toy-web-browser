"""
Table row element implementation
"""

from typing import Optional

from PIL import ImageDraw

from ...html_parser import DOMNode
from ...layout_engine import LayoutEngine, LayoutNode
from ...renderer import Renderer
from ..base import BaseElement


class TableRowElement(BaseElement):
    """Table row element"""

    def layout(
        self, layout_engine: LayoutEngine, x: float, viewport_width: int, **kwargs
    ) -> LayoutNode:
        """Delegate to layout_with_table_params method"""
        # This shouldn't be called directly for table rows
        # They should use layout_with_table_params instead
        return self.layout_with_table_params(layout_engine, x, viewport_width, 0, 0)

    def layout_with_table_params(
        self,
        layout_engine: LayoutEngine,
        x: float,
        viewport_width: int,
        col_width: float,
        num_cols: int,
    ) -> LayoutNode:
        """Layout table row with specific table parameters"""
        layout_node = self._create_layout_node(
            x, layout_engine.current_y, viewport_width - 2 * x, 0
        )

        start_y = layout_engine.current_y
        current_x = x

        # Layout each cell
        cells = [child for child in self.dom_node.children if child.tag in ["td", "th"]]
        for i, cell in enumerate(cells):
            if i >= num_cols:
                break

            cell_layout = self._layout_table_cell(
                layout_engine, cell, current_x, viewport_width, col_width
            )
            if cell_layout:
                layout_node.add_child(cell_layout)
            current_x += col_width

        # Calculate row height as max of cell heights
        if layout_node.children:
            max_cell_height = max(child.box.height for child in layout_node.children)
            layout_node.box.height = max_cell_height
            layout_engine.current_y = start_y + max_cell_height

        return layout_node

    def render(
        self, draw: ImageDraw.ImageDraw, layout_node: LayoutNode, renderer: Renderer
    ) -> None:
        """Render table row children"""
        for child in layout_node.children:
            renderer._render_node(draw, child)

    def _layout_table_cell(
        self,
        layout_engine: LayoutEngine,
        dom_node: DOMNode,
        x: float,
        viewport_width: int,
        width: float,
    ) -> Optional[LayoutNode]:
        """Layout a table cell with proper parameters"""
        # Import here to avoid circular imports
        from ..element_factory import ElementFactory

        element = ElementFactory.create_element(dom_node)
        if element:
            from .table_cell_element import TableCellElement

            if isinstance(element, TableCellElement):
                return element.layout_with_width(
                    layout_engine, x, viewport_width, width
                )
        return None
