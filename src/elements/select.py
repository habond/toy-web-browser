"""
Select and option element implementations
"""

from typing import Any, List, Optional

from PIL import ImageDraw

from ..config import config
from ..html_parser import DOMNode
from ..layout import LayoutMixin
from ..layout_engine import LayoutEngine, LayoutNode
from ..renderer import Renderer
from .base import BaseElement


class OptionElement(BaseElement):
    """Option element for select dropdown items"""

    def layout(
        self, layout_engine: LayoutEngine, x: float, viewport_width: int, **kwargs: Any
    ) -> Optional[LayoutNode]:
        """Option elements are not directly laid out, handled by parent select"""
        return None

    def render(
        self, draw: ImageDraw.ImageDraw, layout_node: LayoutNode, renderer: Renderer
    ) -> None:
        """Option elements are not directly rendered, handled by parent select"""
        pass

    def get_text(self) -> str:
        """Get the text content of the option"""

        def extract_text(node: DOMNode) -> str:
            if node.tag == "text":
                return node.text or ""

            result = ""
            for child in node.children:
                result += extract_text(child)
            return result

        return extract_text(self.dom_node).strip()

    def get_value(self) -> str:
        """Get the value attribute or text if no value"""
        value = self.dom_node.attrs.get("value", "")
        if not value:
            value = self.get_text()
        return value

    def is_selected(self) -> bool:
        """Check if this option is selected"""
        return "selected" in self.dom_node.attrs


class SelectElement(BaseElement, LayoutMixin):
    """Select element that renders as a dropdown box"""

    def layout(
        self, layout_engine: LayoutEngine, x: float, viewport_width: int, **kwargs: Any
    ) -> Optional[LayoutNode]:
        """Layout select element as a dropdown box"""
        # Get selected option text
        selected_text = self._get_selected_text()
        display_text = selected_text if selected_text else "Select..."

        # Calculate dimensions with padding
        padding = config.PADDING * 2
        font_size = layout_engine.DEFAULT_FONT_SIZE
        line_height = font_size * layout_engine.LINE_HEIGHT

        # Estimate text width (approximate)
        estimated_char_width = config.CHAR_WIDTH_ESTIMATE
        text_width = len(display_text) * estimated_char_width

        # Add extra width for dropdown arrow indicator
        arrow_width = 20

        # Select box dimensions
        select_width = max(text_width + 2 * padding + arrow_width, 150)  # Min width
        select_height = line_height + 2 * padding

        # Create layout node
        layout_node = self._create_layout_node(
            x, layout_engine.current_y, select_width, select_height
        )

        # Store select data for rendering
        setattr(layout_node, "selected_text", selected_text)
        setattr(layout_node, "display_text", display_text)
        setattr(layout_node, "options", self._get_options())
        setattr(layout_node, "padding", padding)

        # Move to next line after select (selects are inline-block)
        layout_engine.current_y += select_height + config.MARGIN

        return layout_node

    def render(
        self, draw: ImageDraw.ImageDraw, layout_node: LayoutNode, renderer: Renderer
    ) -> None:
        """Render select element as a dropdown box"""
        if not hasattr(layout_node, "display_text"):
            return

        display_text = getattr(layout_node, "display_text", "")
        padding = getattr(layout_node, "padding", config.PADDING * 2)

        # Select styling
        bg_color = "#ffffff"  # White background
        border_color = "#999999"  # Gray border
        text_color = "#333333"  # Dark gray text
        arrow_color = "#666666"  # Arrow indicator
        border_width = 1

        # Draw select background and border
        select_rect = (
            layout_node.box.x,
            layout_node.box.y,
            layout_node.box.x + layout_node.box.width,
            layout_node.box.y + layout_node.box.height,
        )
        draw.rectangle(
            select_rect, fill=bg_color, outline=border_color, width=border_width
        )

        # Draw the selected text
        font = renderer._get_font()
        text_x = layout_node.box.x + padding
        text_y = layout_node.box.y + padding

        # If no selection, use gray placeholder text
        if not getattr(layout_node, "selected_text", None):
            text_color = "#999999"

        # Cast display_text to ensure it's a string
        draw.text((text_x, text_y), str(display_text), fill=text_color, font=font)

        # Draw dropdown arrow indicator (▼)
        arrow_x = layout_node.box.x + layout_node.box.width - 20
        arrow_y = layout_node.box.y + layout_node.box.height // 2

        # Draw a simple triangle pointing down
        arrow_points = [
            (arrow_x, arrow_y - 3),  # Top left
            (arrow_x + 8, arrow_y - 3),  # Top right
            (arrow_x + 4, arrow_y + 3),  # Bottom center
        ]
        draw.polygon(arrow_points, fill=arrow_color)

    def _get_options(self) -> List[OptionElement]:
        """Get all option elements within this select"""
        options = []
        for child in self.dom_node.children:
            if child.tag == "option":
                option_elem = OptionElement(child)
                options.append(option_elem)
        return options

    def _get_selected_text(self) -> Optional[str]:
        """Get the text of the selected option, or first option if none selected"""
        options = self._get_options()
        if not options:
            return None

        # Look for explicitly selected option
        for option in options:
            if option.is_selected():
                return option.get_text()

        # Default to first option if none selected
        return options[0].get_text()
