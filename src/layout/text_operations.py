"""
Text wrapping and dimension calculation utilities
"""

from typing import List, Optional, Tuple

from ..config import config


class TextOperations:
    """Text-specific layout operations"""

    @staticmethod
    def compute_text_height(lines: List[str], font_size: float) -> float:
        """Compute the total height needed for a list of text lines"""
        return len(lines) * font_size * config.LINE_HEIGHT

    @staticmethod
    def wrap_text(
        text: str, max_width: float, char_width: Optional[float] = None
    ) -> List[str]:
        """Wrap text to fit within the specified width"""
        if char_width is None:
            char_width = config.CHAR_WIDTH_ESTIMATE

        words = text.split()
        lines: List[str] = []
        current_line: List[str] = []
        line_width: float = 0

        for word in words:
            word_width: float = len(word) * char_width
            if line_width + word_width > max_width and current_line:
                lines.append(" ".join(current_line))
                current_line = [word]
                line_width = word_width
            else:
                current_line.append(word)
                line_width += word_width + char_width

        if current_line:
            lines.append(" ".join(current_line))

        return lines

    @staticmethod
    def calculate_content_dimensions(
        lines: List[str], font_size: Optional[float] = None
    ) -> Tuple[float, float]:
        """Calculate width and height for text content"""
        if font_size is None:
            font_size = config.DEFAULT_FONT_SIZE

        if not lines:
            return 0.0, 0.0

        # Approximate width based on longest line
        max_line_width = max(len(line) for line in lines) * config.CHAR_WIDTH_ESTIMATE
        height = TextOperations.compute_text_height(lines, font_size)

        return float(max_line_width), height
