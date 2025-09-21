"""
Base element class for HTML elements
"""

from abc import ABC, abstractmethod
from typing import Any, Optional

from PIL import ImageDraw

from ..html_parser import DOMNode
from ..layout_engine import Box, LayoutEngine, LayoutNode
from ..renderer import Renderer


class BaseElement(ABC):
    """Base class for all HTML elements"""

    def __init__(self, dom_node: DOMNode) -> None:
        self.dom_node = dom_node

    @abstractmethod
    def layout(
        self, layout_engine: LayoutEngine, x: float, viewport_width: int, **kwargs: Any
    ) -> Optional[LayoutNode]:
        """Compute layout for this element"""
        pass

    @abstractmethod
    def render(
        self, draw: ImageDraw.ImageDraw, layout_node: LayoutNode, renderer: Renderer
    ) -> None:
        """Render this element to the image"""
        pass

    def _create_layout_node(
        self, x: float, y: float, width: float, height: float
    ) -> LayoutNode:
        """Create a layout node with the given dimensions"""
        layout_node = LayoutNode(self.dom_node)
        layout_node.box = Box(x, y, width, height)
        return layout_node
