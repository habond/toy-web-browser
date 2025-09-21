"""
Font management system for the toy web browser
"""

from pathlib import Path
from typing import Dict, Optional, Tuple, Union

from PIL import ImageFont
from PIL.ImageFont import FreeTypeFont

from .config import config
from .exceptions import FontError


class FontManager:
    """Manages font loading, caching, and retrieval"""

    def __init__(self, fonts_dir: Optional[Path] = None) -> None:
        self.fonts_dir: Path = fonts_dir or self._get_default_fonts_dir()
        self.font_cache: Dict[
            Tuple[int, bool, bool], Union[FreeTypeFont, ImageFont.ImageFont]
        ] = {}
        self.default_font: Optional[Union[FreeTypeFont, ImageFont.ImageFont]] = None
        self.bold_font: Optional[Union[FreeTypeFont, ImageFont.ImageFont]] = None
        self.mono_font: Optional[Union[FreeTypeFont, ImageFont.ImageFont]] = None
        self._load_fonts()

    def _get_default_fonts_dir(self) -> Path:
        """Get the default fonts directory relative to project root"""
        return Path(__file__).parent.parent / "fonts"

    def _load_fonts(self) -> None:
        """Load fonts for rendering"""
        self.default_font = None
        self.bold_font = None
        self.mono_font = None

        # Load regular font (Open Sans)
        regular_font_path = self.fonts_dir / "OpenSans-Regular.ttf"
        if regular_font_path.exists():
            try:
                self.default_font = ImageFont.truetype(
                    str(regular_font_path), config.DEFAULT_FONT_SIZE
                )
                # Use the same font for bold if we don't have a separate bold file
                self.bold_font = ImageFont.truetype(
                    str(regular_font_path), config.DEFAULT_FONT_SIZE
                )
            except Exception as e:
                raise FontError(f"Failed to load regular font: {e}")

        # Load monospace font
        mono_font_path = self.fonts_dir / "SourceCodePro-Regular.ttf"
        if mono_font_path.exists():
            try:
                self.mono_font = ImageFont.truetype(
                    str(mono_font_path), config.DEFAULT_FONT_SIZE
                )
            except (OSError, IOError):
                # Non-critical error, we can fall back to default
                pass

        # Fall back to PIL default font if no TrueType font found
        if not self.default_font:
            self.default_font = ImageFont.load_default()

    def get_font(
        self,
        size: Optional[int] = None,
        bold: bool = False,
        italic: bool = False,
        monospace: bool = False,
    ) -> Union[FreeTypeFont, ImageFont.ImageFont]:
        """Get or create a font with specific size and style"""
        if size is None:
            size = config.DEFAULT_FONT_SIZE

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

    def clear_cache(self) -> None:
        """Clear the font cache"""
        self.font_cache.clear()

    def get_text_size(
        self, text: str, font: Union[FreeTypeFont, ImageFont.ImageFont]
    ) -> Tuple[int, int]:
        """Get the size of text when rendered with the given font"""
        try:
            # Try the newer textbbox method first
            bbox = font.getbbox(text)
            return (bbox[2] - bbox[0], bbox[3] - bbox[1])
        except AttributeError:
            # Fall back to the older textsize method
            return font.getsize(text)
