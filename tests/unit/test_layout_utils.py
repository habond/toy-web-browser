"""Tests for the layout utilities module"""

from unittest.mock import Mock

import pytest
from PIL import ImageFont

from src.config import BrowserConfig
from src.layout_utils import LayoutMixin, LayoutUtils


class TestLayoutUtils:
    """Test the LayoutUtils static methods"""

    def test_wrap_text_short_text(self) -> None:
        """Test text wrapping with text that fits on one line"""
        font = ImageFont.load_default()
        text = "Short text"
        max_width = 500

        lines = LayoutUtils.wrap_text_with_font(text, font, max_width)

        assert len(lines) == 1
        assert lines[0] == text

    def test_wrap_text_long_text(self) -> None:
        """Test text wrapping with text that needs multiple lines"""
        font = ImageFont.load_default()
        text = "This is a very long line of text that should definitely wrap to multiple lines when rendered with a narrow width constraint"
        max_width = 100

        lines = LayoutUtils.wrap_text_with_font(text, font, max_width)

        assert len(lines) > 1
        # All lines should be non-empty
        assert all(line.strip() for line in lines)
        # Joined lines should equal original text (minus extra spaces)
        assert " ".join(lines).replace("  ", " ").strip() == text.strip()

    def test_wrap_text_with_newlines(self) -> None:
        """Test text wrapping preserves explicit newlines"""
        font = ImageFont.load_default()
        text = "Line 1\nLine 2\nLine 3"
        max_width = 500

        lines = LayoutUtils.wrap_text_with_font(text, font, max_width)

        assert len(lines) >= 3  # At least one line per explicit newline

    def test_wrap_text_empty_string(self) -> None:
        """Test text wrapping with empty string"""
        font = ImageFont.load_default()
        text = ""
        max_width = 100

        lines = LayoutUtils.wrap_text_with_font(text, font, max_width)

        assert len(lines) == 1
        assert lines[0] == ""

    def test_wrap_text_single_word_too_long(self) -> None:
        """Test text wrapping when single word is longer than max width"""
        font = ImageFont.load_default()
        text = "supercalifragilisticexpialidocious"
        max_width = 10  # Very narrow

        lines = LayoutUtils.wrap_text_with_font(text, font, max_width)

        # Should still wrap the word, even if it exceeds max width
        assert len(lines) >= 1
        assert lines[0] == text  # Single word should not be broken

    def test_calculate_text_dimensions(self) -> None:
        """Test calculating text dimensions"""
        font = ImageFont.load_default()
        text = "Sample text"

        width, height = LayoutUtils.calculate_text_dimensions(text, font)

        assert width > 0
        assert height > 0
        assert isinstance(width, int)
        assert isinstance(height, int)

    def test_calculate_text_dimensions_empty_text(self) -> None:
        """Test calculating dimensions for empty text"""
        font = ImageFont.load_default()
        text = ""

        width, height = LayoutUtils.calculate_text_dimensions(text, font)

        assert width == 0
        assert height >= 0  # Height might be font height even for empty text

    def test_calculate_text_dimensions_multiline(self) -> None:
        """Test calculating dimensions for multiline text"""
        font = ImageFont.load_default()
        text = "Line 1\nLine 2\nLine 3"

        width, height = LayoutUtils.calculate_text_dimensions(text, font)

        assert width > 0
        assert height > 0

        # Should be taller than single line
        single_line_width, single_line_height = LayoutUtils.calculate_text_dimensions(
            "Line 1", font
        )
        assert height > single_line_height

    def test_wrap_text_with_zero_width(self) -> None:
        """Test text wrapping with zero or negative width"""
        font = ImageFont.load_default()
        text = "Sample text"

        # Should handle gracefully
        lines = LayoutUtils.wrap_text_with_font(text, font, 0)
        assert len(lines) >= 1

        lines = LayoutUtils.wrap_text_with_font(text, font, -10)
        assert len(lines) >= 1

    def test_calculate_wrapped_text_height(self) -> None:
        """Test calculating total height for wrapped text"""
        font = ImageFont.load_default()
        config = BrowserConfig()
        text = "This is a long text that will wrap to multiple lines"
        max_width = 100

        height = LayoutUtils.calculate_wrapped_text_height(
            text, font, max_width, config.LINE_HEIGHT
        )

        assert height > 0
        # Should be greater than single line height
        single_height = LayoutUtils.calculate_text_dimensions(text, font)[1]
        assert height >= single_height


class TestLayoutMixin:
    """Test the LayoutMixin class"""

    def test_layout_mixin_creation(self) -> None:
        """Test that LayoutMixin can be instantiated"""
        mixin = LayoutMixin()
        assert mixin is not None

    def test_layout_mixin_calculate_content_height(self) -> None:
        """Test the calculate_content_height method"""
        mixin = LayoutMixin()
        config = BrowserConfig()

        # Mock DOM node with text content
        mock_dom_node = Mock()
        mock_dom_node.tag = "p"
        mock_dom_node.text = "Sample text content"
        mock_dom_node.children = []

        # Mock font manager
        mock_font_manager = Mock()
        mock_font_manager.get_font.return_value = ImageFont.load_default()

        # Mock layout node
        mock_layout_node = Mock()
        mock_layout_node.dom_node = mock_dom_node

        width = 200
        height = mixin.calculate_content_height(
            mock_layout_node, width, config, mock_font_manager
        )

        assert height >= 0
        mock_font_manager.get_font.assert_called()

    def test_layout_mixin_with_children(self) -> None:
        """Test LayoutMixin with DOM node that has children"""
        mixin = LayoutMixin()
        config = BrowserConfig()

        # Create mock parent with child
        mock_child = Mock()
        mock_child.tag = "text"
        mock_child.text = "Child text"
        mock_child.children = []

        mock_parent = Mock()
        mock_parent.tag = "div"
        mock_parent.text = None
        mock_parent.children = [mock_child]

        mock_font_manager = Mock()
        mock_font_manager.get_font.return_value = ImageFont.load_default()

        mock_layout_node = Mock()
        mock_layout_node.dom_node = mock_parent

        width = 200
        height = mixin.calculate_content_height(
            mock_layout_node, width, config, mock_font_manager
        )

        assert height >= 0

    def test_layout_mixin_empty_content(self) -> None:
        """Test LayoutMixin with empty content"""
        mixin = LayoutMixin()
        config = BrowserConfig()

        mock_dom_node = Mock()
        mock_dom_node.tag = "div"
        mock_dom_node.text = None
        mock_dom_node.children = []

        mock_font_manager = Mock()
        mock_font_manager.get_font.return_value = ImageFont.load_default()

        mock_layout_node = Mock()
        mock_layout_node.dom_node = mock_dom_node

        width = 200
        height = mixin.calculate_content_height(
            mock_layout_node, width, config, mock_font_manager
        )

        assert height >= 0

    def test_layout_mixin_text_wrapping_integration(self) -> None:
        """Test that LayoutMixin properly integrates with text wrapping"""
        mixin = LayoutMixin()
        config = BrowserConfig()

        # Create a long text that should wrap
        long_text = "This is a very long text that should wrap to multiple lines " * 5

        mock_dom_node = Mock()
        mock_dom_node.tag = "p"
        mock_dom_node.text = long_text
        mock_dom_node.children = []

        mock_font_manager = Mock()
        mock_font_manager.get_font.return_value = ImageFont.load_default()

        mock_layout_node = Mock()
        mock_layout_node.dom_node = mock_dom_node

        # Test with narrow width to force wrapping
        narrow_width = 100
        narrow_height = mixin.calculate_content_height(
            mock_layout_node, narrow_width, config, mock_font_manager
        )

        # Test with wide width
        wide_width = 800
        wide_height = mixin.calculate_content_height(
            mock_layout_node, wide_width, config, mock_font_manager
        )

        # Narrow width should result in greater height due to wrapping
        assert narrow_height >= wide_height
