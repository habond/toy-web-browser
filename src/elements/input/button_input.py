"""
Button input element renderer
"""

from typing import Tuple

from PIL import ImageDraw

from ...config import config
from ...layout_engine import Box
from ...renderer import Renderer
from .base_input import BaseInputRenderer


class ButtonInputRenderer(BaseInputRenderer):
    """Renderer for button inputs (submit, button, reset)"""

    def get_dimensions(self, display_text: str) -> Tuple[float, float]:
        """Calculate dimensions for button input"""
        # Use character width estimation for layout calculations
        text_width = len(display_text) * config.CHAR_WIDTH_ESTIMATE
        width = text_width + 2 * config.PADDING + 20  # Extra padding for button
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
        """Render button input"""
        # Draw button background
        draw.rectangle(
            (box.x, box.y, box.x + box.width, box.y + box.height),
            outline="black",
            fill="#f0f0f0",
            width=1,
        )

        # Draw button text
        if display_text:
            font = renderer.font_manager.get_font(size=config.DEFAULT_FONT_SIZE)

            # Center text in button
            try:
                if hasattr(font, "getbbox"):
                    bbox = font.getbbox(display_text)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                elif hasattr(font, "getsize"):
                    text_width, text_height = font.getsize(display_text)
                else:
                    text_width = len(display_text) * config.CHAR_WIDTH_ESTIMATE
                    text_height = config.DEFAULT_FONT_SIZE
            except Exception:
                text_width = len(display_text) * config.CHAR_WIDTH_ESTIMATE
                text_height = config.DEFAULT_FONT_SIZE

            text_x = box.x + (box.width - text_width) / 2
            text_y = box.y + (box.height - text_height) / 2

            draw.text((text_x, text_y), display_text, fill="black", font=font)
