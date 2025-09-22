"""
Layout mixin providing common functionality to elements
"""

from typing import Any, List, Optional, Tuple

from ..config import config
from .text_operations import TextOperations


class LayoutMixin:
    """Mixin class providing common layout functionality to elements"""

    def _wrap_and_layout_text(
        self, text: str, max_width: float, font_size: Optional[float] = None
    ) -> Tuple[List[str], float]:
        """Wrap text and calculate layout dimensions"""
        if font_size is None:
            font_size = config.DEFAULT_FONT_SIZE

        lines = TextOperations.wrap_text(text, max_width)
        height = TextOperations.compute_text_height(lines, font_size)
        return lines, height

    def _calculate_element_height(
        self, content_height: float, include_margins: bool = True
    ) -> float:
        """Calculate total element height including margins/padding"""
        if include_margins:
            return content_height + config.MARGIN
        return content_height

    def _get_content_width(self, viewport_width: int, x: float) -> float:
        """Calculate available content width"""
        return viewport_width - 2 * x

    def calculate_content_height(
        self, layout_node: Any, width: int, config_obj: Any, font_manager: Any
    ) -> int:
        """Calculate content height for layout node"""
        dom_node = layout_node.dom_node

        if not dom_node.text and not dom_node.children:
            return 0

        total_height = 0

        # Handle text content
        if dom_node.text:
            font = font_manager.get_font()
            # Import here to avoid circular import and allow test patching
            from .layout_utils import LayoutUtils

            height = LayoutUtils.calculate_wrapped_text_height(
                dom_node.text, font, width, config_obj.LINE_HEIGHT
            )
            total_height += height

        # Handle children content
        for child in dom_node.children:
            if child.text:
                font = font_manager.get_font()
                # Import here to avoid circular import and allow test patching
                from .layout_utils import LayoutUtils

                height = LayoutUtils.calculate_wrapped_text_height(
                    child.text, font, width, config_obj.LINE_HEIGHT
                )
                total_height += height

        return total_height
