"""
Preformatted text element implementation
"""

from typing import Any, Optional

from PIL import ImageDraw

from ..config import config
from ..html_parser import DOMNode
from ..layout import LayoutMixin
from ..layout_engine import LayoutEngine, LayoutNode
from ..renderer import Renderer
from .base import BaseElement


class PreElement(BaseElement, LayoutMixin):
    """Preformatted text element that preserves whitespace and uses monospace font"""

    def layout(
        self, layout_engine: LayoutEngine, x: float, viewport_width: int, **kwargs: Any
    ) -> Optional[LayoutNode]:
        """Layout preformatted text without wrapping"""
        # Get all text content from children, preserving whitespace
        text = self._get_preformatted_text()

        if not text:
            return None

        # Split into lines, preserving empty lines
        lines = text.split("\n")

        # Calculate dimensions using monospace font
        font_size = layout_engine.DEFAULT_FONT_SIZE
        line_height = font_size * layout_engine.LINE_HEIGHT

        # For pre elements, we don't wrap text but may need to handle overflow
        max_width = viewport_width - 2 * x

        # Calculate content height (lines + margins + padding)
        content_height = len(lines) * line_height
        total_height = content_height + 2 * layout_engine.MARGIN

        # Create layout node
        layout_node = self._create_layout_node(
            x, layout_engine.current_y, max_width, total_height
        )
        layout_node.lines = lines  # Store lines for rendering
        layout_node.font_type = "monospace"  # Mark as monospace

        layout_engine.current_y += total_height

        return layout_node

    def render(
        self, draw: ImageDraw.ImageDraw, layout_node: LayoutNode, renderer: Renderer
    ) -> None:
        """Render preformatted text with monospace font"""
        if not hasattr(layout_node, "lines") or not layout_node.lines:
            return

        # Get monospace font
        font = renderer._get_font(monospace=True)
        line_height = renderer.DEFAULT_FONT_SIZE * renderer.LINE_HEIGHT

        # Add background for better visibility (light gray)
        padding = config.PADDING
        bg_box = (
            layout_node.box.x - padding,
            layout_node.box.y,
            layout_node.box.x + layout_node.box.width,
            layout_node.box.y + layout_node.box.height,
        )
        draw.rectangle(bg_box, fill="#f8f8f8", outline="#e0e0e0")

        # Render each line
        y_offset: float = float(config.MARGIN)
        for line in layout_node.lines:
            # Preserve all whitespace including leading/trailing spaces
            draw.text(
                (layout_node.box.x + padding, layout_node.box.y + y_offset),
                line,
                fill="black",
                font=font,
            )
            y_offset += line_height

    def _get_preformatted_text(self) -> str:
        """Extract all text content while preserving whitespace"""

        def extract_text(node: DOMNode) -> str:
            if node.tag == "text":
                return node.text or ""

            result: str = ""
            for child in node.children:
                result += extract_text(child)
            return result

        return extract_text(self.dom_node)
