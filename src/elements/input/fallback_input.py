"""
Fallback input renderer for unknown input types
"""

from typing import Tuple

from PIL import ImageDraw

from ...config import config
from ...layout_engine import Box
from ...renderer import Renderer
from .base_input import BaseInputRenderer, InputUtilities


class FallbackInputRenderer(BaseInputRenderer):
    """Fallback renderer for unknown input types"""

    def get_dimensions(self, display_text: str) -> Tuple[float, float]:
        """Calculate dimensions for fallback input"""
        width = 100.0
        height = config.DEFAULT_FONT_SIZE + 2 * config.PADDING
        return width, height

    def render(
        self,
        draw: ImageDraw.ImageDraw,
        box: Box,
        display_text: str,
        is_placeholder: bool,
        renderer: Renderer,
    ) -> None:
        """Render fallback input as text input"""
        # Draw border
        draw.rectangle(
            (box.x, box.y, box.x + box.width, box.y + box.height),
            outline="black",
            fill="white",
            width=1,
        )

        # Draw text if present
        if display_text:
            font = renderer.font_manager.get_font(size=config.DEFAULT_FONT_SIZE)
            text_color = "#888888" if is_placeholder else "black"

            # Position text with padding
            text_x = box.x + config.PADDING
            text_y = box.y + config.PADDING

            # Calculate available width for text (subtract padding from both sides)
            available_width = box.width - 2 * config.PADDING

            # Truncate text if it's too long to fit
            truncated_text = InputUtilities.truncate_text_to_fit(
                display_text, font, available_width
            )

            draw.text((text_x, text_y), truncated_text, fill=text_color, font=font)
