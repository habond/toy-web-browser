"""
Inline element implementations
"""

from typing import Optional

from PIL import ImageDraw

from ..layout_engine import LayoutEngine, LayoutNode
from ..renderer import Renderer
from .base import BaseElement


class InlineElement(BaseElement):
    """Inline element (b, i, u, strong, em, code, span, a)"""

    def layout(
        self, layout_engine: LayoutEngine, x: float, viewport_width: int, **kwargs
    ) -> Optional[LayoutNode]:
        """Layout inline element"""
        layout_node = LayoutNode(self.dom_node)

        for child in self.dom_node.children:
            child_layout = layout_engine._layout_child(child, x)
            if child_layout:
                layout_node.add_child(child_layout)

        return layout_node if layout_node.children else None

    def render(
        self, draw: ImageDraw.ImageDraw, layout_node: LayoutNode, renderer: Renderer
    ) -> None:
        """Render inline element with appropriate styling"""
        for child in layout_node.children:
            if child.dom_node.tag == "text" and hasattr(child, "lines") and child.lines:
                self._render_styled_text(draw, child, renderer)
            else:
                renderer._render_node(draw, child)

    def _render_styled_text(
        self, draw: ImageDraw.ImageDraw, layout_node: LayoutNode, renderer: Renderer
    ) -> None:
        """Render text with inline styling"""
        tag = self.dom_node.tag

        # Determine styling based on tag
        bold = tag in ["b", "strong"]
        italic = tag in ["i", "em"]
        underline = tag == "u"
        monospace = tag == "code"
        is_link = tag == "a"

        # Get appropriate font
        font = renderer._get_font(bold=bold, italic=italic, monospace=monospace)

        # Choose text color
        color = "#0066cc" if is_link else "black"

        y_offset: float = 0
        line_height: float = renderer.DEFAULT_FONT_SIZE * renderer.LINE_HEIGHT

        for line in layout_node.lines or []:
            if line.strip():
                text_pos = (layout_node.box.x, layout_node.box.y + y_offset)
                draw.text(text_pos, line, fill=color, font=font)

                # Add underline if needed
                if underline or is_link:
                    text_width = draw.textlength(line, font=font)
                    underline_y = text_pos[1] + renderer.DEFAULT_FONT_SIZE
                    draw.line(
                        [
                            text_pos[0],
                            underline_y,
                            text_pos[0] + text_width,
                            underline_y,
                        ],
                        fill=color,
                        width=1,
                    )

                # Add code background if needed
                if monospace:
                    text_width = draw.textlength(line, font=font)
                    padding = 2
                    draw.rectangle(
                        (
                            text_pos[0] - padding,
                            text_pos[1] - padding,
                            text_pos[0] + text_width + padding,
                            text_pos[1] + renderer.DEFAULT_FONT_SIZE + padding,
                        ),
                        outline="#e0e0e0",
                        width=1,
                    )

            y_offset += line_height
