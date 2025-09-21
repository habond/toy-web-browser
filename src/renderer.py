"""
Renderer - Renders the layout tree to a PNG image
"""

from typing import Optional, Union

from PIL import Image, ImageDraw, ImageFont
from PIL.ImageFont import FreeTypeFont

from .config import config
from .font_manager import FontManager
from .layout_engine import LayoutNode


class Renderer:
    """Renders layout tree to image"""

    def __init__(
        self, width: int = 800, height: int = 600, bg_color: str = "white"
    ) -> None:
        self.width: int = width
        self.height: int = height
        self.bg_color: str = bg_color
        self.font_manager: FontManager = FontManager()

    @property
    def DEFAULT_FONT_SIZE(self) -> int:
        """Get default font size from config"""
        return config.DEFAULT_FONT_SIZE

    @property
    def LINE_HEIGHT(self) -> float:
        """Get line height from config"""
        return config.LINE_HEIGHT

    def _get_font(
        self,
        size: Optional[int] = None,
        bold: bool = False,
        italic: bool = False,
        monospace: bool = False,
    ) -> Union[FreeTypeFont, ImageFont.ImageFont]:
        """Get a font with specific size and style"""
        return self.font_manager.get_font(size, bold, italic, monospace)

    def render(self, layout_root: LayoutNode) -> Image.Image:
        """Render layout tree to image"""
        # Create image with white background
        image = Image.new("RGB", (self.width, self.height), self.bg_color)
        draw = ImageDraw.Draw(image)

        # Render the tree
        self._render_node(draw, layout_root)

        return image

    def _render_node(self, draw: ImageDraw.ImageDraw, layout_node: LayoutNode) -> None:
        """Recursively render a layout node using element classes"""
        # Import here to avoid circular imports
        from .elements.element_factory import ElementFactory

        element = ElementFactory.create_element(layout_node.dom_node)
        if element:
            element.render(draw, layout_node, self)
        else:
            # Fallback: render children directly
            for child in layout_node.children:
                self._render_node(draw, child)
