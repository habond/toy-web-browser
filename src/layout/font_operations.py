"""
Font-specific layout operations
"""

from typing import List, Tuple, Union

from PIL import ImageFont
from PIL.ImageFont import FreeTypeFont

from ..config import config


class FontOperations:
    """Font-aware layout operations"""

    @staticmethod
    def wrap_text_with_font(
        text: str, font: Union[ImageFont.ImageFont, FreeTypeFont], max_width: int
    ) -> List[str]:
        """Wrap text to fit within the specified width using font metrics"""
        if not text:
            return [""]

        if max_width <= 0:
            return [text]

        lines = []
        for paragraph in text.split("\n"):
            words = paragraph.split()
            if not words:
                lines.append("")
                continue

            current_line: List[str] = []
            for word in words:
                test_line = " ".join(current_line + [word])
                try:
                    # Try to get text width using font metrics
                    if hasattr(font, "getbbox"):
                        width = font.getbbox(test_line)[2]
                    else:
                        # Fallback to character estimation
                        width = len(test_line) * config.CHAR_WIDTH_ESTIMATE
                except Exception:
                    # Fallback to character estimation
                    width = len(test_line) * config.CHAR_WIDTH_ESTIMATE

                if width <= max_width or not current_line:
                    current_line.append(word)
                else:
                    lines.append(" ".join(current_line))
                    current_line = [word]

            if current_line:
                lines.append(" ".join(current_line))

        return lines

    @staticmethod
    def calculate_text_dimensions(
        text: str, font: Union[ImageFont.ImageFont, FreeTypeFont]
    ) -> Tuple[int, int]:
        """Calculate text dimensions using font metrics"""
        if not text:
            return 0, 0

        lines = text.split("\n")
        max_width = 0
        total_height = 0

        try:
            # Get single line height
            if hasattr(font, "getbbox"):
                line_height = font.getbbox("A")[3] - font.getbbox("A")[1]
            else:
                line_height = config.DEFAULT_FONT_SIZE
        except Exception:
            line_height = config.DEFAULT_FONT_SIZE

        # Calculate dimensions for each line
        for line in lines:
            try:
                if hasattr(font, "getbbox"):
                    bbox = font.getbbox(line)
                    width = bbox[2] - bbox[0]
                else:
                    width = len(line) * config.CHAR_WIDTH_ESTIMATE
            except Exception:
                width = len(line) * config.CHAR_WIDTH_ESTIMATE

            max_width = max(max_width, width)
            total_height += line_height

        return int(max_width), int(total_height)

    @staticmethod
    def calculate_wrapped_text_height(
        text: str,
        font: Union[ImageFont.ImageFont, FreeTypeFont],
        max_width: int,
        line_spacing: float,
    ) -> int:
        """Calculate total height needed for wrapped text"""
        # Import here to avoid circular import, and to allow test patching
        from .layout_utils import LayoutUtils

        lines = LayoutUtils.wrap_text_with_font(text, font, max_width)
        if not lines:
            return 0

        try:
            if hasattr(font, "getbbox"):
                line_height = font.getbbox("A")[3] - font.getbbox("A")[1]
            else:
                line_height = config.DEFAULT_FONT_SIZE
        except Exception:
            line_height = config.DEFAULT_FONT_SIZE

        return int(len(lines) * line_height * line_spacing)
