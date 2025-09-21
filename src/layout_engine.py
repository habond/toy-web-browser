"""
Layout Engine - Computes positions and sizes of elements
"""

from dataclasses import dataclass
from typing import List, Optional, Tuple

from .html_parser import DOMNode


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
                child_layout = self._layout_child(
                    child, layout_root.box.x + self.MARGIN
                )
                if child_layout:
                    layout_root.add_child(child_layout)

        layout_root.box.height = self.current_y
        return layout_root

    def _layout_child(self, dom_node: DOMNode, x: float) -> Optional[LayoutNode]:
        """Layout a child DOM node by creating appropriate element"""
        # Import here to avoid circular imports
        from .elements.element_factory import ElementFactory

        element = ElementFactory.create_element(dom_node)
        if element:
            return element.layout(self, x, self.viewport_width)
        return None

    def _layout_child_with_width(
        self, dom_node: DOMNode, x: float, max_width: float
    ) -> Optional[LayoutNode]:
        """Layout a child DOM node with specific max width (for text in table cells)"""
        # Import here to avoid circular imports
        from .elements.element_factory import ElementFactory

        element = ElementFactory.create_element(dom_node)
        if element:
            return element.layout(self, x, self.viewport_width, max_width=max_width)
        return None
