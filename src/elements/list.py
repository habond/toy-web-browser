"""
List element implementations
"""

from typing import Any, Optional

from PIL import ImageDraw

from ..html_parser import DOMNode
from ..layout_engine import LayoutEngine, LayoutNode
from ..renderer import Renderer
from .base import BaseElement


class ListElement(BaseElement):
    """List element (ul, ol)"""

    def layout(
        self, layout_engine: LayoutEngine, x: float, viewport_width: int, **kwargs: Any
    ) -> LayoutNode:
        """Layout list element"""
        layout_node = self._create_layout_node(
            x, layout_engine.current_y, viewport_width - 2 * x, 0
        )

        start_y = layout_engine.current_y
        layout_engine.current_y += layout_engine.MARGIN

        for i, child in enumerate(self.dom_node.children):
            if child.tag == "li":
                # Handle list items specially to pass index and ordered parameters
                child_layout = self._layout_list_item(
                    layout_engine,
                    child,
                    x + 25,
                    viewport_width,
                    i + 1,
                    self.dom_node.tag == "ol",
                )
                if child_layout:
                    layout_node.add_child(child_layout)

        layout_engine.current_y += layout_engine.MARGIN
        layout_node.box.height = layout_engine.current_y - start_y

        return layout_node

    def render(
        self, draw: ImageDraw.ImageDraw, layout_node: LayoutNode, renderer: Renderer
    ) -> None:
        """Render list element"""
        for child in layout_node.children:
            renderer._render_node(draw, child)

    def _layout_list_item(
        self,
        layout_engine: LayoutEngine,
        dom_node: DOMNode,
        x: float,
        viewport_width: int,
        index: int,
        ordered: bool,
    ) -> Optional[LayoutNode]:
        """Layout a list item with proper parameters"""
        # Import here to avoid circular imports
        from .element_factory import ElementFactory

        element = ElementFactory.create_element(dom_node)
        if element and isinstance(element, ListItemElement):
            return element.layout(
                layout_engine,
                x,
                viewport_width,
                index=index,
                ordered=ordered,
            )
        return None


class ListItemElement(BaseElement):
    """List item element (li)"""

    def layout(
        self,
        layout_engine: LayoutEngine,
        x: float,
        viewport_width: int,
        index: Optional[int] = None,
        ordered: bool = False,
        **kwargs: Any,
    ) -> LayoutNode:
        """Layout list item"""
        layout_node = self._create_layout_node(
            x, layout_engine.current_y, viewport_width - 2 * x, 0
        )

        start_y = layout_engine.current_y

        # Add bullet or number
        if index is not None:
            marker = f"{index}." if ordered else "•"
            layout_node.marker = marker
            # Position marker to the left of text, vertically centered with first line
            layout_node.marker_pos = (
                x - 20,
                layout_engine.current_y + layout_engine.DEFAULT_FONT_SIZE * 0.2,
            )

        for child in self.dom_node.children:
            child_layout = layout_engine._layout_child(child, x)
            if child_layout:
                layout_node.add_child(child_layout)

        layout_engine.current_y += layout_engine.MARGIN * 0.5
        layout_node.box.height = layout_engine.current_y - start_y

        return layout_node

    def render(
        self, draw: ImageDraw.ImageDraw, layout_node: LayoutNode, renderer: Renderer
    ) -> None:
        """Render list item"""
        # Render marker if present
        if (
            hasattr(layout_node, "marker")
            and hasattr(layout_node, "marker_pos")
            and layout_node.marker_pos
        ):
            font = renderer._get_font()
            draw.text(
                layout_node.marker_pos,
                layout_node.marker or "",
                fill="black",
                font=font,
            )

        # Render children
        for child in layout_node.children:
            renderer._render_node(draw, child)
