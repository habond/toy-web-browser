"""
Main input element implementation using specialized renderers
"""

from typing import Any, Dict, Optional

from PIL import ImageDraw

from ...config import config
from ...layout_engine import LayoutEngine, LayoutNode
from ...renderer import Renderer
from ..base import BaseElement
from .base_input import BaseInputRenderer, InputUtilities
from .button_input import ButtonInputRenderer
from .control_input import CheckboxInputRenderer, RadioInputRenderer
from .fallback_input import FallbackInputRenderer
from .text_input import TextInputRenderer


class InputElement(BaseElement):
    """Input element for form controls using strategy pattern"""

    def __init__(self, dom_node: Any) -> None:
        super().__init__(dom_node)
        # Initialize renderer registry
        self._renderers: Dict[str, BaseInputRenderer] = {
            "text": TextInputRenderer(),
            "email": TextInputRenderer(),
            "password": TextInputRenderer(),
            "url": TextInputRenderer(),
            "search": TextInputRenderer(),
            "submit": ButtonInputRenderer(),
            "button": ButtonInputRenderer(),
            "reset": ButtonInputRenderer(),
            "checkbox": CheckboxInputRenderer(),
            "radio": RadioInputRenderer(),
        }
        self._fallback_renderer = FallbackInputRenderer()

    def layout(
        self, layout_engine: LayoutEngine, x: float, viewport_width: int, **kwargs: Any
    ) -> Optional[LayoutNode]:
        """Layout input element"""
        # Get input type and attributes
        input_type = self.dom_node.attrs.get("type", "text")
        value = self.dom_node.attrs.get("value", "")
        placeholder = self.dom_node.attrs.get("placeholder", "")

        # Get display text
        display_text = InputUtilities.get_display_text(input_type, value, placeholder)

        # Get appropriate renderer
        renderer = self._get_renderer(input_type)

        # Calculate dimensions
        width, height = renderer.get_dimensions(display_text)

        # Ensure minimum height for larger inputs
        if input_type not in ["checkbox", "radio"]:
            height = max(height, config.DEFAULT_FONT_SIZE + 2 * config.PADDING)

        # Create layout node
        y_pos = layout_engine.current_y
        layout_node = self._create_layout_node(x, y_pos, width, height)

        # Store rendering data
        layout_node.display_text = display_text
        layout_node.input_type = input_type
        layout_node.is_placeholder = not bool(value)
        # Store checked state for checkbox/radio inputs
        setattr(layout_node, "is_checked", "checked" in self.dom_node.attrs)

        # Update current_y position for next element
        layout_engine.current_y += height + config.MARGIN

        return layout_node

    def render(
        self, draw: ImageDraw.ImageDraw, layout_node: LayoutNode, renderer: Renderer
    ) -> None:
        """Render input element using appropriate renderer"""
        box = layout_node.box
        input_type = getattr(layout_node, "input_type", "text")
        display_text = getattr(layout_node, "display_text", "")
        is_placeholder = getattr(layout_node, "is_placeholder", False)
        is_checked = getattr(layout_node, "is_checked", False)

        # Get appropriate renderer and render
        input_renderer = self._get_renderer(input_type)
        if input_type in ["checkbox", "radio"]:
            # For checkbox/radio, pass checked state to renderer
            input_renderer.render(draw, box, display_text, is_checked, renderer)
        else:
            input_renderer.render(draw, box, display_text, is_placeholder, renderer)

    def _get_renderer(self, input_type: str) -> BaseInputRenderer:
        """Get the appropriate renderer for the input type"""
        # Use fallback renderer for unknown types to maintain original behavior
        return self._renderers.get(input_type, self._fallback_renderer)
