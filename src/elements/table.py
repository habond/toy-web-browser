"""
Table element implementations
"""

from typing import Optional

from PIL import ImageDraw

from ..html_parser import DOMNode
from ..layout_engine import LayoutEngine, LayoutNode
from ..renderer import Renderer
from .base import BaseElement


class TableElement(BaseElement):
    """Table element"""

    def layout(
        self, layout_engine: LayoutEngine, x: float, viewport_width: int, **kwargs
    ) -> LayoutNode:
        """Layout table element"""
        layout_node = self._create_layout_node(
            x, layout_engine.current_y, viewport_width - 2 * x, 0
        )

        start_y = layout_engine.current_y
        layout_engine.current_y += layout_engine.MARGIN

        # First pass: collect all rows to calculate column widths
        rows = [child for child in self.dom_node.children if child.tag == "tr"]
        if not rows:
            return layout_node

        # Calculate number of columns from the first row
        first_row = rows[0]
        num_cols = len(
            [cell for cell in first_row.children if cell.tag in ["td", "th"]]
        )

        if num_cols == 0:
            return layout_node

        # Simple equal column width distribution
        table_width = viewport_width - 2 * x - 2 * layout_engine.PADDING
        col_width = table_width / num_cols

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
        y_positions = [table_box.y]
        for row in rows:
            y_positions.append(row.box.y + row.box.height)

        for y in y_positions:
            draw.line(
                [table_box.x, y, table_box.x + table_box.width, y],
                fill="black",
                width=1,
            )

        # Draw vertical lines (left, between columns, right)
        if rows:
            first_row = rows[0]
            cells = [
                child
                for child in first_row.children
                if child.dom_node.tag in ["td", "th"]
            ]

            x_positions = [table_box.x]
            for cell in cells:
                x_positions.append(cell.box.x + cell.box.width)

            for x in x_positions:
                draw.line(
                    [x, table_box.y, x, table_box.y + table_box.height],
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
        """Helper to layout a table row with proper parameters"""
        # Import here to avoid circular imports
        from .element_factory import ElementFactory

        element = ElementFactory.create_element(dom_node)
        if element and isinstance(element, TableRowElement):
            return element.layout(
                layout_engine,
                x,
                viewport_width,
                col_width=col_width,
                num_cols=num_cols,
            )
        return None


class TableRowElement(BaseElement):
    """Table row element"""

    def layout(
        self,
        layout_engine: LayoutEngine,
        x: float,
        viewport_width: int,
        col_width: float = 100,
        num_cols: int = 1,
        **kwargs,
    ) -> LayoutNode:
        """Layout table row with specified column width"""
        layout_node = self._create_layout_node(
            x, layout_engine.current_y, viewport_width - 2 * x, 0
        )

        start_y = layout_engine.current_y
        row_height = 0.0

        # Layout cells horizontally
        current_x = x + layout_engine.PADDING
        cell_index = 0

        for child in self.dom_node.children:
            if child.tag in ["td", "th"] and cell_index < num_cols:
                saved_y = layout_engine.current_y
                layout_engine.current_y = start_y + layout_engine.PADDING

                cell_layout = self._layout_table_cell(
                    layout_engine,
                    child,
                    current_x,
                    viewport_width,
                    col_width - 2 * layout_engine.PADDING,
                )
                if cell_layout:
                    layout_node.add_child(cell_layout)
                    # Track the maximum height for this row
                    cell_height = (
                        layout_engine.current_y - start_y - layout_engine.PADDING
                    )
                    row_height = max(row_height, cell_height)

                layout_engine.current_y = saved_y
                current_x += col_width
                cell_index += 1

        # Set the row height and advance current_y
        min_height = layout_engine.DEFAULT_FONT_SIZE * layout_engine.LINE_HEIGHT
        row_height = max(row_height, min_height)
        layout_engine.current_y = start_y + row_height + 2 * layout_engine.PADDING
        layout_node.box.height = row_height + 2 * layout_engine.PADDING

        return layout_node

    def render(
        self, draw: ImageDraw.ImageDraw, layout_node: LayoutNode, renderer: Renderer
    ) -> None:
        """Render table row"""
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
        """Helper to layout a table cell with proper parameters"""
        # Import here to avoid circular imports
        from .element_factory import ElementFactory

        element = ElementFactory.create_element(dom_node)
        if element and isinstance(element, TableCellElement):
            return element.layout(
                layout_engine,
                x,
                viewport_width,
                width=width,
            )
        return None


class TableCellElement(BaseElement):
    """Table cell element (td, th)"""

    def layout(
        self,
        layout_engine: LayoutEngine,
        x: float,
        viewport_width: int,
        width: float = 100,
        **kwargs,
    ) -> LayoutNode:
        """Layout table cell with specified width"""
        layout_node = self._create_layout_node(x, layout_engine.current_y, width, 0)

        start_y = layout_engine.current_y

        # Layout cell contents with constrained width
        for child in self.dom_node.children:
            if child.tag == "text":
                # For text in table cells, use cell-specific width
                child_layout = layout_engine._layout_child_with_width(
                    child, x + layout_engine.PADDING, width - 2 * layout_engine.PADDING
                )
            else:
                child_layout = layout_engine._layout_child(
                    child, x + layout_engine.PADDING
                )
            if child_layout:
                layout_node.add_child(child_layout)

        # Ensure minimum height for empty cells
        if layout_engine.current_y == start_y:
            min_height = layout_engine.DEFAULT_FONT_SIZE * layout_engine.LINE_HEIGHT
            layout_engine.current_y += min_height

        layout_node.box.height = layout_engine.current_y - start_y

        return layout_node

    def render(
        self, draw: ImageDraw.ImageDraw, layout_node: LayoutNode, renderer: Renderer
    ) -> None:
        """Render table cell"""
        # For header cells (th), draw a light gray background
        if self.dom_node.tag == "th":
            draw.rectangle(
                (
                    layout_node.box.x,
                    layout_node.box.y,
                    layout_node.box.x + layout_node.box.width,
                    layout_node.box.y + layout_node.box.height,
                ),
                fill="#f0f0f0",
            )

        # Render children
        for child in layout_node.children:
            renderer._render_node(draw, child)
