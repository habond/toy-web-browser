"""
Button element implementation
"""

from typing import Any, Optional

from PIL import ImageDraw

from ..config import config
from ..html_parser import DOMNode
from ..layout_engine import LayoutEngine, LayoutNode
from ..layout_utils import LayoutMixin
from ..renderer import Renderer
from .base import BaseElement


class ButtonElement(BaseElement, LayoutMixin):
    """Button element that renders as a clickable button with background and border"""

    def layout(
        self, layout_engine: LayoutEngine, x: float, viewport_width: int, **kwargs: Any
    ) -> Optional[LayoutNode]:
        """Layout button element with padding and content"""
        # Get button text content
        text = self._get_button_text()

        if not text:
            return None

        # Calculate button dimensions with padding
        button_padding = config.PADDING * 2  # Extra padding for buttons
        font_size = layout_engine.DEFAULT_FONT_SIZE
        line_height = font_size * layout_engine.LINE_HEIGHT

        # Estimate text width (approximate since we don't have the actual font here)
        # We'll refine this in the render method
        estimated_char_width = config.CHAR_WIDTH_ESTIMATE
        text_width = len(text) * estimated_char_width

        # Button dimensions
        button_width = text_width + 2 * button_padding
        button_height = line_height + 2 * button_padding

        # Create layout node
        layout_node = self._create_layout_node(
            x, layout_engine.current_y, button_width, button_height
        )
        layout_node.button_text = text  # Store text for rendering
        layout_node.button_padding = button_padding  # Store padding for rendering

        # Move to next line after button (buttons are inline-block)
        layout_engine.current_y += button_height + config.MARGIN

        return layout_node

    def render(
        self, draw: ImageDraw.ImageDraw, layout_node: LayoutNode, renderer: Renderer
    ) -> None:
        """Render button with background, border, and text"""
        if not hasattr(layout_node, "button_text") or not layout_node.button_text:
            return

        button_text = layout_node.button_text

        # Button styling
        bg_color = "#f0f0f0"  # Light gray background
        border_color = "#999999"  # Gray border
        text_color = "#333333"  # Dark gray text
        border_width = 1

        # Draw button background
        button_rect = (
            layout_node.box.x,
            layout_node.box.y,
            layout_node.box.x + layout_node.box.width,
            layout_node.box.y + layout_node.box.height,
        )
        draw.rectangle(
            button_rect, fill=bg_color, outline=border_color, width=border_width
        )

        # Draw button text
        font = renderer._get_font()

        # Calculate text position to center it in the button
        text_bbox = draw.textbbox((0, 0), button_text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        text_x = layout_node.box.x + (layout_node.box.width - text_width) / 2
        text_y = layout_node.box.y + (layout_node.box.height - text_height) / 2

        draw.text((text_x, text_y), button_text, fill=text_color, font=font)

    def _get_button_text(self) -> str:
        """Extract text content from button element"""

        def extract_text(node: DOMNode) -> str:
            if node.tag == "text":
                return node.text or ""

            result: str = ""
            for child in node.children:
                result += extract_text(child)
            return result

        return extract_text(self.dom_node).strip()
