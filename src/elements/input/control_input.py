"""
Control input element renderers (checkbox, radio)
"""

from typing import Tuple

from PIL import ImageDraw

from ...layout_engine import Box
from ...renderer import Renderer
from .base_input import BaseInputRenderer


class CheckboxInputRenderer(BaseInputRenderer):
    """Renderer for checkbox inputs"""

    def get_dimensions(self, display_text: str) -> Tuple[float, float]:
        """Calculate dimensions for checkbox"""
        # display_text is not used for checkboxes, but required by interface
        return 16.0, 16.0

    def render(
        self,
        draw: ImageDraw.ImageDraw,
        box: Box,
        display_text: str,
        is_placeholder: bool,
        renderer: Renderer,
    ) -> None:
        """Render checkbox"""
        # display_text not used for checkboxes, but required by interface
        # is_placeholder parameter is actually used as is_checked for control inputs
        _ = display_text, renderer
        is_checked = is_placeholder  # Reuse parameter for checked state

        # Draw checkbox border
        draw.rectangle(
            (box.x, box.y, box.x + box.width, box.y + box.height),
            outline="black",
            fill="white",
            width=1,
        )

        # Draw checkmark if checked
        if is_checked:
            draw.line(
                [box.x + 3, box.y + 8, box.x + 6, box.y + 11], fill="black", width=2
            )
            draw.line(
                [box.x + 6, box.y + 11, box.x + 13, box.y + 4], fill="black", width=2
            )


class RadioInputRenderer(BaseInputRenderer):
    """Renderer for radio button inputs"""

    def get_dimensions(self, display_text: str) -> Tuple[float, float]:
        """Calculate dimensions for radio button"""
        # display_text is not used for radio buttons, but required by interface
        return 16.0, 16.0

    def render(
        self,
        draw: ImageDraw.ImageDraw,
        box: Box,
        display_text: str,
        is_placeholder: bool,
        renderer: Renderer,
    ) -> None:
        """Render radio button"""
        # display_text not used for radio buttons, but required by interface
        # is_placeholder parameter is actually used as is_checked for control inputs
        _ = display_text, renderer
        is_checked = is_placeholder  # Reuse parameter for checked state

        # Calculate center and radius
        center_x = box.x + box.width / 2
        center_y = box.y + box.height / 2
        radius = min(box.width, box.height) / 2 - 1

        # Draw radio button circle
        draw.ellipse(
            (
                center_x - radius,
                center_y - radius,
                center_x + radius,
                center_y + radius,
            ),
            outline="black",
            fill="white",
            width=1,
        )

        # Draw filled center if checked
        if is_checked:
            inner_radius = radius * 0.5
            draw.ellipse(
                (
                    center_x - inner_radius,
                    center_y - inner_radius,
                    center_x + inner_radius,
                    center_y + inner_radius,
                ),
                fill="black",
            )
