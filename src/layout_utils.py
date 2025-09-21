"""
Layout utility functions and mixins for the toy web browser
"""

from typing import Any, List, Optional, Tuple, Union

from PIL import ImageFont

from .config import config


class LayoutUtils:
    """Utility class for common layout operations"""

    @staticmethod
    def compute_text_height(lines: List[str], font_size: float) -> float:
        """Compute the total height needed for a list of text lines"""
        return len(lines) * font_size * config.LINE_HEIGHT

    @staticmethod
    def wrap_text(
        text: str, max_width: float, char_width: Optional[float] = None
    ) -> List[str]:
        """Wrap text to fit within the specified width"""
        if char_width is None:
            char_width = config.CHAR_WIDTH_ESTIMATE

        words = text.split()
        lines: List[str] = []
        current_line: List[str] = []
        line_width: float = 0

        for word in words:
            word_width: float = len(word) * char_width
            if line_width + word_width > max_width and current_line:
                lines.append(" ".join(current_line))
                current_line = [word]
                line_width = word_width
            else:
                current_line.append(word)
                line_width += word_width + char_width

        if current_line:
            lines.append(" ".join(current_line))

        return lines

    @staticmethod
    def calculate_content_dimensions(
        lines: List[str], font_size: Optional[float] = None
    ) -> Tuple[float, float]:
        """Calculate width and height for text content"""
        if font_size is None:
            font_size = config.DEFAULT_FONT_SIZE

        if not lines:
            return 0.0, 0.0

        # Approximate width based on longest line
        max_line_width = max(len(line) for line in lines) * config.CHAR_WIDTH_ESTIMATE
        height = LayoutUtils.compute_text_height(lines, font_size)

        return float(max_line_width), height

    @staticmethod
    def add_margins_and_padding(
        width: float,
        height: float,
        margin: Optional[float] = None,
        padding: Optional[float] = None,
    ) -> Tuple[float, float]:
        """Add margins and padding to content dimensions"""
        if margin is None:
            margin = config.MARGIN
        if padding is None:
            padding = config.PADDING

        return width + 2 * (margin + padding), height + 2 * (margin + padding)

    @staticmethod
    def wrap_text_with_font(
        text: str, font: Union[ImageFont.ImageFont, Any], max_width: int
    ) -> List[str]:
        """Wrap text to fit within the specified width using font metrics"""
        if not text:
            return [""]

        if max_width <= 0:
            return [text]

        lines = []
        for paragraph in text.split("\n"):
            words = paragraph.split()
            if not words:
                lines.append("")
                continue

            current_line: List[str] = []
            for word in words:
                test_line = " ".join(current_line + [word])
                try:
                    # Try to get text width using font metrics
                    if hasattr(font, "getbbox"):
                        width = font.getbbox(test_line)[2]
                    elif hasattr(font, "getsize"):
                        width = font.getsize(test_line)[0]
                    else:
                        # Fallback to character estimation
                        width = len(test_line) * config.CHAR_WIDTH_ESTIMATE
                except Exception:
                    # Fallback to character estimation
                    width = len(test_line) * config.CHAR_WIDTH_ESTIMATE

                if width <= max_width or not current_line:
                    current_line.append(word)
                else:
                    lines.append(" ".join(current_line))
                    current_line = [word]

            if current_line:
                lines.append(" ".join(current_line))

        return lines

    @staticmethod
    def calculate_text_dimensions(
        text: str, font: Union[ImageFont.ImageFont, Any]
    ) -> Tuple[int, int]:
        """Calculate text dimensions using font metrics"""
        if not text:
            return 0, 0

        lines = text.split("\n")
        max_width = 0
        total_height = 0

        try:
            # Get single line height
            if hasattr(font, "getbbox"):
                line_height = font.getbbox("A")[3] - font.getbbox("A")[1]
            elif hasattr(font, "getsize"):
                line_height = font.getsize("A")[1]
            else:
                line_height = config.DEFAULT_FONT_SIZE
        except Exception:
            line_height = config.DEFAULT_FONT_SIZE

        # Calculate dimensions for each line
        for line in lines:
            try:
                if hasattr(font, "getbbox"):
                    bbox = font.getbbox(line)
                    width = bbox[2] - bbox[0]
                elif hasattr(font, "getsize"):
                    width = font.getsize(line)[0]
                else:
                    width = len(line) * config.CHAR_WIDTH_ESTIMATE
            except Exception:
                width = len(line) * config.CHAR_WIDTH_ESTIMATE

            max_width = max(max_width, width)
            total_height += line_height

        return int(max_width), int(total_height)

    @staticmethod
    def calculate_wrapped_text_height(
        text: str,
        font: Union[ImageFont.ImageFont, Any],
        max_width: int,
        line_spacing: float,
    ) -> int:
        """Calculate total height needed for wrapped text"""
        lines = LayoutUtils.wrap_text_with_font(text, font, max_width)
        if not lines:
            return 0

        try:
            if hasattr(font, "getbbox"):
                line_height = font.getbbox("A")[3] - font.getbbox("A")[1]
            elif hasattr(font, "getsize"):
                line_height = font.getsize("A")[1]
            else:
                line_height = config.DEFAULT_FONT_SIZE
        except Exception:
            line_height = config.DEFAULT_FONT_SIZE

        return int(len(lines) * line_height * line_spacing)


class LayoutMixin:
    """Mixin class providing common layout functionality to elements"""

    def _wrap_and_layout_text(
        self, text: str, max_width: float, font_size: Optional[float] = None
    ) -> Tuple[List[str], float]:
        """Wrap text and calculate layout dimensions"""
        if font_size is None:
            font_size = config.DEFAULT_FONT_SIZE

        lines = LayoutUtils.wrap_text(text, max_width)
        height = LayoutUtils.compute_text_height(lines, font_size)
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
        self, layout_node: Any, width: int, config: Any, font_manager: Any
    ) -> int:
        """Calculate content height for layout node"""
        dom_node = layout_node.dom_node

        if not dom_node.text and not dom_node.children:
            return 0

        total_height = 0

        # Handle text content
        if dom_node.text:
            font = font_manager.get_font()
            height = LayoutUtils.calculate_wrapped_text_height(
                dom_node.text, font, width, config.LINE_HEIGHT
            )
            total_height += height

        # Handle children content
        for child in dom_node.children:
            if child.text:
                font = font_manager.get_font()
                height = LayoutUtils.calculate_wrapped_text_height(
                    child.text, font, width, config.LINE_HEIGHT
                )
                total_height += height

        return total_height
