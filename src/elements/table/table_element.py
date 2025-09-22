"""
Main table element implementation
"""

from typing import Any, Optional

from PIL import ImageDraw

from ...html_parser import DOMNode
from ...layout_engine import LayoutEngine, LayoutNode
from ...renderer import Renderer
from ..base import BaseElement
from .table_calculator import TableCalculator


class TableElement(BaseElement):
    """Table element"""

    def layout(
        self, layout_engine: LayoutEngine, x: float, viewport_width: int, **kwargs: Any
    ) -> LayoutNode:
        """Layout table element"""
        layout_node = self._create_layout_node(
            x, layout_engine.current_y, viewport_width - 2 * x, 0
        )

        start_y = layout_engine.current_y
        layout_engine.current_y += layout_engine.MARGIN

        # Get all table rows
        rows = TableCalculator.get_table_rows(self.dom_node)
        if not rows:
            return layout_node

        # Calculate column widths
        col_width, num_cols = TableCalculator.calculate_column_widths(
            rows, viewport_width, x
        )

        if num_cols == 0:
            return layout_node

        # Layout each row
        for row in rows:
            row_layout = self._layout_table_row(
                layout_engine, row, x, viewport_width, col_width, num_cols
            )
            if row_layout:
                layout_node.add_child(row_layout)

        layout_engine.current_y += layout_engine.MARGIN
        layout_node.box.height = layout_engine.current_y - start_y

        return layout_node

    def render(
        self, draw: ImageDraw.ImageDraw, layout_node: LayoutNode, renderer: Renderer
    ) -> None:
        """Render table with grid"""
        self._render_table_grid(draw, layout_node, renderer)

        # Render children
        for child in layout_node.children:
            renderer._render_node(draw, child)

    def _render_table_grid(
        self, draw: ImageDraw.ImageDraw, layout_node: LayoutNode, renderer: Renderer
    ) -> None:
        """Draw table grid lines"""
        rows = [child for child in layout_node.children if child.dom_node.tag == "tr"]
        if not rows:
            return

        # Get table bounds
        table_box = layout_node.box

        # Draw horizontal lines (top, between rows, bottom)
        # Start from first row position, not table box top (which includes margin)
        if rows:
            y_positions = [rows[0].box.y]
            for row in rows:
                y_positions.append(row.box.y + row.box.height)

            # Get actual content boundaries
            first_row = rows[0]
            cells = [
                child
                for child in first_row.children
                if child.dom_node.tag in ["td", "th"]
            ]

            if cells:
                # Horizontal lines span from first cell left to last cell right
                left_x = cells[0].box.x
                right_x = cells[-1].box.x + cells[-1].box.width

                for y in y_positions:
                    draw.line(
                        [left_x, y, right_x, y],
                        fill="black",
                        width=1,
                    )

                # Draw vertical lines (left, between columns, right)
                x_positions = [cells[0].box.x]
                for cell in cells:
                    x_positions.append(cell.box.x + cell.box.width)

                # Vertical lines span from first row top to last row bottom
                top_y = rows[0].box.y
                bottom_y = rows[-1].box.y + rows[-1].box.height

                for x_pos in x_positions:
                    draw.line(
                        [x_pos, top_y, x_pos, bottom_y],
                        fill="black",
                        width=1,
                    )
            else:
                # Fallback for rows with no cells - draw using table boundaries
                for y in y_positions:
                    draw.line(
                        [table_box.x, y, table_box.x + table_box.width, y],
                        fill="black",
                        width=1,
                    )

    def _layout_table_row(
        self,
        layout_engine: LayoutEngine,
        dom_node: DOMNode,
        x: float,
        viewport_width: int,
        col_width: float,
        num_cols: int,
    ) -> Optional[LayoutNode]:
        """Layout a table row with proper parameters"""
        # Import here to avoid circular imports
        from ..element_factory import ElementFactory

        element = ElementFactory.create_element(dom_node)
        if element:
            from .table_row_element import TableRowElement

            if isinstance(element, TableRowElement):
                return element.layout_with_table_params(
                    layout_engine, x, viewport_width, col_width, num_cols
                )
        return None
