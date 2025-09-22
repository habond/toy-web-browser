"""
Main layout utilities combining text and font operations
"""

from typing import Optional, Tuple

from ..config import config
from .font_operations import FontOperations
from .text_operations import TextOperations


class LayoutUtils:
    """Unified layout utility class for backward compatibility"""

    # Re-export text operations
    compute_text_height = TextOperations.compute_text_height
    wrap_text = TextOperations.wrap_text
    calculate_content_dimensions = TextOperations.calculate_content_dimensions

    # Re-export font operations
    wrap_text_with_font = FontOperations.wrap_text_with_font
    calculate_text_dimensions = FontOperations.calculate_text_dimensions
    calculate_wrapped_text_height = FontOperations.calculate_wrapped_text_height

    @staticmethod
    def add_margins_and_padding(
        width: float,
        height: float,
        margin: Optional[float] = None,
        padding: Optional[float] = None,
    ) -> Tuple[float, float]:
        """Add margins and padding to content dimensions"""
        if margin is None:
            margin = config.MARGIN
        if padding is None:
            padding = config.PADDING

        return width + 2 * (margin + padding), height + 2 * (margin + padding)
