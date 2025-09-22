"""
Base input renderer for shared functionality
"""

from abc import ABC, abstractmethod
from typing import Tuple, Union

from PIL import ImageDraw, ImageFont
from PIL.ImageFont import FreeTypeFont

from ...config import config
from ...layout_engine import Box
from ...renderer import Renderer


class BaseInputRenderer(ABC):
    """Abstract base class for input type renderers"""

    @abstractmethod
    def get_dimensions(self, display_text: str) -> Tuple[float, float]:
        """Calculate width and height for this input type"""
        pass

    @abstractmethod
    def render(
        self,
        draw: ImageDraw.ImageDraw,
        box: Box,
        display_text: str,
        is_placeholder: bool,
        renderer: Renderer,
    ) -> None:
        """Render this input type"""
        pass


class InputUtilities:
    """Shared utilities for input elements"""

    @staticmethod
    def truncate_text_to_fit(
        text: str, font: Union[FreeTypeFont, ImageFont.ImageFont], max_width: float
    ) -> str:
        """Truncate text to fit within the specified width"""
        if not text:
            return text

        # Check if the text fits without truncation
        try:
            if hasattr(font, "getbbox"):
                text_width = font.getbbox(text)[2]
            else:
                # Fallback to character estimation for older PIL or no getbbox
                text_width = len(text) * config.CHAR_WIDTH_ESTIMATE
        except Exception:
            text_width = len(text) * config.CHAR_WIDTH_ESTIMATE

        if text_width <= max_width:
            return text

        # Binary search for the longest text that fits
        left, right = 0, len(text)
        best_length = 0

        while left <= right:
            mid = (left + right) // 2
            test_text = text[:mid]

            try:
                if hasattr(font, "getbbox"):
                    test_width = font.getbbox(test_text)[2]
                else:
                    test_width = len(test_text) * config.CHAR_WIDTH_ESTIMATE
            except Exception:
                test_width = len(test_text) * config.CHAR_WIDTH_ESTIMATE

            if test_width <= max_width:
                best_length = mid
                left = mid + 1
            else:
                right = mid - 1

        # Return the longest text that fits, with ellipsis if truncated
        truncated = text[:best_length]
        if best_length < len(text) and best_length > 3:
            truncated = truncated[:-3] + "..."

        return truncated

    @staticmethod
    def get_display_text(input_type: str, value: str, placeholder: str) -> str:
        """Get the display text for an input element"""
        if value:
            return value
        elif placeholder:
            return placeholder
        elif input_type in ["submit", "button", "reset"]:
            return input_type.capitalize()
        else:
            return ""
