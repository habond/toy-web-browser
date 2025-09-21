"""
Renderer - Renders the layout tree to a PNG image
"""

from pathlib import Path
from typing import Dict, Optional, Tuple, Union

from PIL import Image, ImageDraw, ImageFont
from PIL.ImageFont import FreeTypeFont

from .layout_engine import LayoutNode


class Renderer:
    """Renders layout tree to image"""

    DEFAULT_FONT_SIZE: int = 16
    LINE_HEIGHT: float = 1.5

    def __init__(
        self, width: int = 800, height: int = 600, bg_color: str = "white"
    ) -> None:
        self.width: int = width
        self.height: int = height
        self.bg_color: str = bg_color

        # Try to use a nice font, fall back to default
        self.font_cache: Dict[
            Tuple[int, bool, bool], Union[FreeTypeFont, ImageFont.ImageFont]
        ] = {}
        self.default_font: Optional[Union[FreeTypeFont, ImageFont.ImageFont]] = None
        self.bold_font: Optional[Union[FreeTypeFont, ImageFont.ImageFont]] = None
        self.mono_font: Optional[Union[FreeTypeFont, ImageFont.ImageFont]] = None
        self._load_fonts()

    def _load_fonts(self) -> None:
        """Load fonts for rendering"""
        # Get path to project fonts directory
        project_root = Path(__file__).parent.parent
        fonts_dir = project_root / "fonts"

        self.default_font = None
        self.bold_font = None
        self.mono_font = None

        # Load regular font (Open Sans)
        regular_font_path = fonts_dir / "OpenSans-Regular.ttf"
        if regular_font_path.exists():
            try:
                self.default_font = ImageFont.truetype(str(regular_font_path), 16)
                # Use the same font for bold if we don't have a separate bold file
                self.bold_font = ImageFont.truetype(str(regular_font_path), 16)
            except Exception:
                pass

        # Load monospace font
        mono_font_path = fonts_dir / "SourceCodePro-Regular.ttf"
        if mono_font_path.exists():
            try:
                self.mono_font = ImageFont.truetype(str(mono_font_path), 16)
            except Exception:
                pass

        # Fall back to PIL default font if no TrueType font found
        if not self.default_font:
            self.default_font = ImageFont.load_default()

    def _get_font(
        self,
        size: int = 16,
        bold: bool = False,
        italic: bool = False,
        monospace: bool = False,
    ) -> Union[FreeTypeFont, ImageFont.ImageFont]:
        """Get or create a font with specific size and style"""
        key: Tuple[int, bool, bool] = (size, bold, italic)
        if key in self.font_cache:
            return self.font_cache[key]

        font: Union[FreeTypeFont, ImageFont.ImageFont]

        # Choose base font based on style
        base_font: Optional[Union[FreeTypeFont, ImageFont.ImageFont]]
        if monospace and self.mono_font:
            base_font = self.mono_font
        elif bold and self.bold_font:
            base_font = self.bold_font
        else:
            base_font = self.default_font

        # Try to create font with requested size
        if base_font and isinstance(base_font, FreeTypeFont):
            try:
                font = ImageFont.truetype(str(base_font.path), int(size))
            except Exception:
                font = base_font
        elif base_font:
            font = base_font
        else:
            font = ImageFont.load_default()

        self.font_cache[key] = font
        return font

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
