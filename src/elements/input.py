"""
Input element implementation
"""

from typing import Any, Optional, Union

from PIL import ImageDraw, ImageFont
from PIL.ImageFont import FreeTypeFont

from ..config import config
from ..layout_engine import Box, LayoutEngine, LayoutNode
from ..renderer import Renderer
from .base import BaseElement


class InputElement(BaseElement):
    """Input element for form controls"""

    def layout(
        self, layout_engine: LayoutEngine, x: float, viewport_width: int, **kwargs: Any
    ) -> Optional[LayoutNode]:
        """Layout input element"""
        # Get input type and value
        input_type = self.dom_node.attrs.get("type", "text")
        value = self.dom_node.attrs.get("value", "")
        placeholder = self.dom_node.attrs.get("placeholder", "")

        # Display text (value, placeholder, or default for buttons)
        if value:
            display_text = value
        elif placeholder:
            display_text = placeholder
        elif input_type in ["submit", "button", "reset"]:
            display_text = input_type.capitalize()
        else:
            display_text = ""

        # Calculate dimensions based on input type
        width: float
        height: float

        if input_type in ["text", "email", "password", "url", "search"]:
            # Text input - fixed width with padding
            width = 200.0
            height = config.DEFAULT_FONT_SIZE + 2 * config.PADDING
        elif input_type in ["submit", "button", "reset"]:
            # Button input - width based on text content
            button_text = value if value else input_type.capitalize()
            # Use character width estimation for layout calculations
            text_width = len(button_text) * config.CHAR_WIDTH_ESTIMATE
            width = text_width + 2 * config.PADDING + 20  # Extra padding for button
            height = config.DEFAULT_FONT_SIZE + 2 * config.PADDING
        elif input_type == "checkbox":
            # Checkbox - small square
            width = height = 16.0
        elif input_type == "radio":
            # Radio button - small circle
            width = height = 16.0
        else:
            # Default for other types
            width = 100.0
            height = config.DEFAULT_FONT_SIZE + 2 * config.PADDING

        # Ensure minimum height (except for small controls like checkbox/radio)
        if input_type not in ["checkbox", "radio"]:
            height = max(height, config.DEFAULT_FONT_SIZE + 2 * config.PADDING)

        # Create layout node
        y_pos = layout_engine.current_y
        layout_node = self._create_layout_node(x, y_pos, width, height)

        # Store display text and input type for rendering as additional attributes
        # (similar to how other elements store additional layout data)
        layout_node.display_text = display_text  # type: ignore
        layout_node.input_type = input_type  # type: ignore
        layout_node.is_placeholder = not bool(value)  # type: ignore

        # Update current_y position for next element
        layout_engine.current_y += height + config.MARGIN

        return layout_node

    def render(
        self, draw: ImageDraw.ImageDraw, layout_node: LayoutNode, renderer: Renderer
    ) -> None:
        """Render input element"""
        box = layout_node.box
        input_type = getattr(layout_node, "input_type", "text")
        display_text = getattr(layout_node, "display_text", "")
        is_placeholder = getattr(layout_node, "is_placeholder", False)

        if input_type in ["text", "email", "password", "url", "search"]:
            self._render_text_input(draw, box, display_text, is_placeholder, renderer)
        elif input_type in ["submit", "button", "reset"]:
            self._render_button_input(draw, box, display_text, renderer)
        elif input_type == "checkbox":
            self._render_checkbox(draw, box, renderer)
        elif input_type == "radio":
            self._render_radio(draw, box, renderer)
        else:
            # Default to text input for unknown types
            self._render_text_input(draw, box, display_text, is_placeholder, renderer)

    def _render_text_input(
        self,
        draw: ImageDraw.ImageDraw,
        box: Box,
        display_text: str,
        is_placeholder: bool,
        renderer: Renderer,
    ) -> None:
        """Render text input field"""
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
            truncated_text = self._truncate_text_to_fit(
                display_text, font, available_width, draw
            )

            draw.text((text_x, text_y), truncated_text, fill=text_color, font=font)

    def _render_button_input(
        self, draw: ImageDraw.ImageDraw, box: Box, display_text: str, renderer: Renderer
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
            text_width = draw.textlength(display_text, font=font)
            text_x = box.x + (box.width - text_width) / 2
            text_y = box.y + config.PADDING

            draw.text((text_x, text_y), display_text, fill="black", font=font)

    def _render_checkbox(
        self, draw: ImageDraw.ImageDraw, box: Box, renderer: Renderer
    ) -> None:
        """Render checkbox input"""
        # Draw checkbox square
        draw.rectangle(
            (box.x, box.y, box.x + box.width, box.y + box.height),
            outline="black",
            fill="white",
            width=1,
        )

        # Check if checked attribute is present
        if "checked" in self.dom_node.attrs:
            # Draw checkmark
            padding = 3
            draw.line(
                [
                    box.x + padding,
                    box.y + box.height / 2,
                    box.x + box.width / 2,
                    box.y + box.height - padding,
                ],
                fill="black",
                width=2,
            )
            draw.line(
                [
                    box.x + box.width / 2,
                    box.y + box.height - padding,
                    box.x + box.width - padding,
                    box.y + padding,
                ],
                fill="black",
                width=2,
            )

    def _render_radio(
        self, draw: ImageDraw.ImageDraw, box: Box, renderer: Renderer
    ) -> None:
        """Render radio button input"""
        # Draw radio circle
        radius = box.width / 2
        center_x = box.x + radius
        center_y = box.y + radius

        draw.ellipse(
            (box.x, box.y, box.x + box.width, box.y + box.height),
            outline="black",
            fill="white",
            width=1,
        )

        # Check if checked attribute is present
        if "checked" in self.dom_node.attrs:
            # Draw filled center
            inner_radius = radius * 0.6
            draw.ellipse(
                (
                    center_x - inner_radius,
                    center_y - inner_radius,
                    center_x + inner_radius,
                    center_y + inner_radius,
                ),
                fill="black",
            )

    def _truncate_text_to_fit(
        self,
        text: str,
        font: Union[FreeTypeFont, ImageFont.ImageFont],
        available_width: float,
        draw: ImageDraw.ImageDraw,
    ) -> str:
        """Show the rightmost portion of text that fits, like real input fields"""
        if not text:
            return text

        # Check if the full text fits
        full_width = draw.textlength(text, font=font)
        if full_width <= available_width:
            return text

        # If text is too long, show the rightmost portion (tail end)
        # Binary search to find the longest suffix that fits
        left, right = 0, len(text)
        best_start = len(text)

        while left <= right:
            mid = (left + right) // 2
            test_text = text[mid:]
            test_width = draw.textlength(test_text, font=font)

            if test_width <= available_width:
                best_start = mid
                right = mid - 1
            else:
                left = mid + 1

        return text[best_start:]
