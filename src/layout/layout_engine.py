"""
Layout Engine - Computes positions and sizes of elements
"""

from dataclasses import dataclass
from typing import List, Optional, Tuple

from ..parser.html_parser import DOMNode


@dataclass
class Box:
    """Represents a layout box with position and dimensions"""

    x: float = 0
    y: float = 0
    width: float = 0
    height: float = 0


class LayoutNode:
    """Node in the layout tree with positioning information"""

    def __init__(self, dom_node: DOMNode, box: Optional[Box] = None) -> None:
        self.dom_node: DOMNode = dom_node
        self.box: Box = box or Box()
        self.children: List[LayoutNode] = []
        # Additional attributes that may be set during layout
        self.lines: Optional[List[str]] = None
        self.font_size: Optional[float] = None
        self.marker: Optional[str] = None
        self.marker_pos: Optional[Tuple[float, float]] = None

    def add_child(self, child: "LayoutNode") -> None:
        self.children.append(child)


class LayoutEngine:
    """Computes layout for DOM nodes"""

    DEFAULT_FONT_SIZE: int = 16
    LINE_HEIGHT: float = 1.5
    MARGIN: int = 10
    PADDING: int = 5

    HEADING_SIZES: dict[str, float] = {
        "h1": 2.0,
        "h2": 1.75,
        "h3": 1.5,
        "h4": 1.25,
        "h5": 1.1,
        "h6": 1.0,
    }

    def __init__(self, viewport_width: int = 800) -> None:
        self.viewport_width: int = viewport_width
        self.current_y: float = 0

    def compute_layout(self, dom_root: DOMNode) -> LayoutNode:
        """Compute layout for entire DOM tree"""
        layout_root = LayoutNode(dom_root)
        layout_root.box = Box(0, 0, self.viewport_width, 0)

        for child in dom_root.children:
            if child.tag != "text" or (child.text and child.text.strip()):
                child_layout = self._layout_node(child, layout_root.box.x + self.MARGIN)
                if child_layout:
                    layout_root.add_child(child_layout)

        layout_root.box.height = self.current_y
        return layout_root

    def _layout_node(self, dom_node: DOMNode, x: float) -> Optional[LayoutNode]:
        """Layout a single DOM node"""
        layout_node = LayoutNode(dom_node)

        if dom_node.tag == "text":
            return self._layout_text(dom_node, x)

        elif dom_node.tag in ["p", "div", "blockquote", "pre"]:
            return self._layout_block(dom_node, x)

        elif dom_node.tag in self.HEADING_SIZES:
            return self._layout_heading(dom_node, x)

        elif dom_node.tag in ["ul", "ol"]:
            return self._layout_list(dom_node, x)

        elif dom_node.tag == "li":
            return self._layout_list_item(dom_node, x)

        elif dom_node.tag == "br":
            self.current_y += self.DEFAULT_FONT_SIZE * 0.5
            return None

        elif dom_node.tag == "hr":
            layout_node.box = Box(x, self.current_y, self.viewport_width - 2 * x, 2)
            self.current_y += 10
            return layout_node

        elif dom_node.tag in ["b", "i", "u", "strong", "em", "code", "span", "a"]:
            return self._layout_inline(dom_node, x)

        elif dom_node.tag == "table":
            return self._layout_table(dom_node, x)

        elif dom_node.tag == "tr":
            return self._layout_table_row(dom_node, x)

        elif dom_node.tag in ["td", "th"]:
            return self._layout_table_cell(dom_node, x)

        else:
            # Default block layout
            return self._layout_block(dom_node, x)

    def _layout_text(self, dom_node: DOMNode, x: float) -> LayoutNode:
        """Layout text node"""
        layout_node = LayoutNode(dom_node)
        text = dom_node.text.strip() if dom_node.text else ""

        if text:
            # Simple text wrapping
            words = text.split()
            lines: List[str] = []
            current_line: List[str] = []
            line_width = 0
            max_width = self.viewport_width - 2 * x
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

            height = len(lines) * self.DEFAULT_FONT_SIZE * self.LINE_HEIGHT
            layout_node.box = Box(x, self.current_y, max_width, height)
            layout_node.lines = lines  # Store lines for rendering
            self.current_y += height

        return layout_node

    def _layout_block(self, dom_node: DOMNode, x: float) -> LayoutNode:
        """Layout block-level element"""
        layout_node = LayoutNode(dom_node)
        layout_node.box = Box(x, self.current_y, self.viewport_width - 2 * x, 0)

        start_y = self.current_y
        self.current_y += self.MARGIN

        for child in dom_node.children:
            child_layout = self._layout_node(child, x + self.PADDING)
            if child_layout:
                layout_node.add_child(child_layout)

        self.current_y += self.MARGIN
        layout_node.box.height = self.current_y - start_y

        return layout_node

    def _layout_heading(self, dom_node: DOMNode, x: float) -> LayoutNode:
        """Layout heading element"""
        layout_node = LayoutNode(dom_node)
        size_multiplier = self.HEADING_SIZES.get(dom_node.tag, 1.0)

        layout_node.box = Box(x, self.current_y, self.viewport_width - 2 * x, 0)
        start_y = self.current_y

        self.current_y += self.MARGIN * 1.5

        for child in dom_node.children:
            if child.tag == "text" and child.text:
                text_layout = LayoutNode(child)
                text = child.text.strip()
                if text:
                    height = self.DEFAULT_FONT_SIZE * size_multiplier * self.LINE_HEIGHT
                    text_layout.box = Box(
                        x, self.current_y, self.viewport_width - 2 * x, height
                    )
                    text_layout.font_size = self.DEFAULT_FONT_SIZE * size_multiplier
                    layout_node.add_child(text_layout)
                    self.current_y += height

        self.current_y += self.MARGIN * 1.5
        layout_node.box.height = self.current_y - start_y

        return layout_node

    def _layout_list(self, dom_node: DOMNode, x: float) -> LayoutNode:
        """Layout list element"""
        layout_node = LayoutNode(dom_node)
        layout_node.box = Box(x, self.current_y, self.viewport_width - 2 * x, 0)

        start_y = self.current_y
        self.current_y += self.MARGIN

        for i, child in enumerate(dom_node.children):
            if child.tag == "li":
                child_layout = self._layout_list_item(
                    child, x + 25, i + 1, dom_node.tag == "ol"
                )
                if child_layout:
                    layout_node.add_child(child_layout)

        self.current_y += self.MARGIN
        layout_node.box.height = self.current_y - start_y

        return layout_node

    def _layout_list_item(
        self,
        dom_node: DOMNode,
        x: float,
        index: Optional[int] = None,
        ordered: bool = False,
    ) -> LayoutNode:
        """Layout list item"""
        layout_node = LayoutNode(dom_node)
        layout_node.box = Box(x, self.current_y, self.viewport_width - 2 * x, 0)

        start_y = self.current_y

        # Add bullet or number
        if index is not None:
            marker = f"{index}." if ordered else "•"  # Use traditional bullet point
            layout_node.marker = marker
            # Position marker to the left of text, vertically centered with first line
            layout_node.marker_pos = (
                x - 20,
                self.current_y + self.DEFAULT_FONT_SIZE * 0.2,
            )

        for child in dom_node.children:
            child_layout = self._layout_node(child, x)
            if child_layout:
                layout_node.add_child(child_layout)

        self.current_y += self.MARGIN * 0.5
        layout_node.box.height = self.current_y - start_y

        return layout_node

    def _layout_inline(self, dom_node: DOMNode, x: float) -> LayoutNode:
        """Layout inline element"""
        layout_node = LayoutNode(dom_node)

        for child in dom_node.children:
            child_layout = self._layout_node(child, x)
            if child_layout:
                layout_node.add_child(child_layout)

        return layout_node

    def _layout_table(self, dom_node: DOMNode, x: float) -> LayoutNode:
        """Layout table element"""
        layout_node = LayoutNode(dom_node)
        layout_node.box = Box(x, self.current_y, self.viewport_width - 2 * x, 0)

        start_y = self.current_y
        self.current_y += self.MARGIN

        # First pass: collect all rows to calculate column widths
        rows = [child for child in dom_node.children if child.tag == "tr"]
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
        table_width = self.viewport_width - 2 * x - 2 * self.PADDING
        col_width = table_width / num_cols

        # Layout each row
        for row in rows:
            row_layout = self._layout_table_row_with_width(row, x, col_width, num_cols)
            if row_layout:
                layout_node.add_child(row_layout)

        self.current_y += self.MARGIN
        layout_node.box.height = self.current_y - start_y

        return layout_node

    def _layout_table_row(self, dom_node: DOMNode, x: float) -> LayoutNode:
        """Layout table row element (fallback when not called from table)"""
        return self._layout_table_row_with_width(dom_node, x, 100, 1)

    def _layout_table_row_with_width(
        self, dom_node: DOMNode, x: float, col_width: float, num_cols: int
    ) -> LayoutNode:
        """Layout table row with specified column width"""
        layout_node = LayoutNode(dom_node)
        layout_node.box = Box(x, self.current_y, self.viewport_width - 2 * x, 0)

        start_y = self.current_y
        row_height = 0.0

        # Layout cells horizontally
        current_x = x + self.PADDING
        cell_index = 0

        for child in dom_node.children:
            if child.tag in ["td", "th"] and cell_index < num_cols:
                saved_y = self.current_y
                self.current_y = start_y + self.PADDING

                cell_layout = self._layout_table_cell_with_width(
                    child, current_x, col_width - 2 * self.PADDING
                )
                if cell_layout:
                    layout_node.add_child(cell_layout)
                    # Track the maximum height for this row
                    cell_height = self.current_y - start_y - self.PADDING
                    row_height = max(row_height, cell_height)

                self.current_y = saved_y
                current_x += col_width
                cell_index += 1

        # Set the row height and advance current_y
        min_height = self.DEFAULT_FONT_SIZE * self.LINE_HEIGHT
        row_height = max(row_height, min_height)
        self.current_y = start_y + row_height + 2 * self.PADDING
        layout_node.box.height = row_height + 2 * self.PADDING

        return layout_node

    def _layout_table_cell(self, dom_node: DOMNode, x: float) -> LayoutNode:
        """Layout table cell element (fallback when not called from table)"""
        return self._layout_table_cell_with_width(dom_node, x, 100)

    def _layout_table_cell_with_width(
        self, dom_node: DOMNode, x: float, width: float
    ) -> LayoutNode:
        """Layout table cell with specified width"""
        layout_node = LayoutNode(dom_node)
        layout_node.box = Box(x, self.current_y, width, 0)

        start_y = self.current_y

        # Layout cell contents with constrained width
        for child in dom_node.children:
            child_layout = None
            if child.tag == "text":
                # For text in table cells, use cell-specific width
                child_layout = self._layout_text_with_width(
                    child, x + self.PADDING, width - 2 * self.PADDING
                )
            else:
                child_layout = self._layout_node(child, x + self.PADDING)
            if child_layout:
                layout_node.add_child(child_layout)

        # Ensure minimum height for empty cells
        if self.current_y == start_y:
            min_height = self.DEFAULT_FONT_SIZE * self.LINE_HEIGHT
            self.current_y += min_height

        layout_node.box.height = self.current_y - start_y

        return layout_node

    def _layout_text_with_width(
        self, dom_node: DOMNode, x: float, max_width: float
    ) -> LayoutNode:
        """Layout text node with specific maximum width"""
        layout_node = LayoutNode(dom_node)
        text = dom_node.text.strip() if dom_node.text else ""

        if text:
            # Simple text wrapping with specified max width
            words = text.split()
            lines: List[str] = []
            current_line: List[str] = []
            line_width = 0
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

            height = len(lines) * self.DEFAULT_FONT_SIZE * self.LINE_HEIGHT
            layout_node.box = Box(x, self.current_y, max_width, height)
            layout_node.lines = lines  # Store lines for rendering
            self.current_y += height

        return layout_node
