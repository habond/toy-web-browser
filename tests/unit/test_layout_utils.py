"""Tests for the layout utilities module"""

from unittest.mock import Mock, patch

from PIL import ImageFont

from src.config import BrowserConfig
from src.layout import LayoutMixin, LayoutUtils


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
        text = (
            "This is a very long line of text that should definitely "
            "wrap to multiple lines when rendered with a narrow width"
        )
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

    def test_calculate_content_dimensions_empty_lines(self) -> None:
        """Test calculate_content_dimensions with empty lines list"""
        width, height = LayoutUtils.calculate_content_dimensions([])
        assert width == 0.0
        assert height == 0.0

    def test_calculate_content_dimensions_with_font_size(self) -> None:
        """Test calculate_content_dimensions with custom font size"""
        lines = ["Short line", "Medium length line", "Very long line of text here"]
        font_size = 20.0

        width, height = LayoutUtils.calculate_content_dimensions(lines, font_size)
        assert width > 0
        assert height > 0

        # Height should use the provided font size
        expected_height = LayoutUtils.compute_text_height(lines, font_size)
        assert height == expected_height

    def test_wrap_text_with_font_empty_text(self) -> None:
        """Test wrap_text_with_font with empty text"""
        font = ImageFont.load_default()
        lines = LayoutUtils.wrap_text_with_font("", font, 100)
        assert lines == [""]

    def test_wrap_text_with_font_zero_width(self) -> None:
        """Test wrap_text_with_font with zero or negative width"""
        font = ImageFont.load_default()
        text = "Some text"

        # Zero width
        lines = LayoutUtils.wrap_text_with_font(text, font, 0)
        assert lines == [text]

        # Negative width
        lines = LayoutUtils.wrap_text_with_font(text, font, -10)
        assert lines == [text]

    def test_wrap_text_with_font_empty_paragraphs(self) -> None:
        """Test wrap_text_with_font with empty paragraphs (newlines)"""
        font = ImageFont.load_default()
        text = "Line 1\n\nLine 3\n\n\nLine 6"

        lines = LayoutUtils.wrap_text_with_font(text, font, 500)
        assert "" in lines  # Empty lines should be preserved

    def test_wrap_text_with_font_no_words(self) -> None:
        """Test wrap_text_with_font with text containing only whitespace"""
        font = ImageFont.load_default()
        text = "   \n  \n   "

        lines = LayoutUtils.wrap_text_with_font(text, font, 100)
        # Should handle empty words gracefully
        assert isinstance(lines, list)

    def test_wrap_text_with_font_getbbox_exception(self) -> None:
        """Test wrap_text_with_font when font.getbbox raises exception"""
        mock_font = Mock()
        mock_font.getbbox.side_effect = Exception("Font error")

        text = "Test text that needs wrapping"
        lines = LayoutUtils.wrap_text_with_font(text, mock_font, 50)

        # Should fall back to character estimation
        assert len(lines) > 0
        assert all(isinstance(line, str) for line in lines)

    def test_wrap_text_with_font_getsize_exception(self) -> None:
        """Test wrap_text_with_font when font.getsize raises exception"""
        mock_font = Mock()
        # No getbbox method
        del mock_font.getbbox
        mock_font.getsize.side_effect = Exception("Font error")

        text = "Test text"
        lines = LayoutUtils.wrap_text_with_font(text, mock_font, 50)

        # Should fall back to character estimation
        assert len(lines) > 0

    def test_wrap_text_with_font_no_font_methods(self) -> None:
        """Test wrap_text_with_font when font has no sizing methods"""
        mock_font = Mock(spec=[])  # No methods available

        text = "Test text"
        lines = LayoutUtils.wrap_text_with_font(text, mock_font, 50)

        # Should use character estimation fallback
        assert len(lines) > 0

    def test_calculate_text_dimensions_empty_text(self) -> None:
        """Test calculate_text_dimensions with empty text"""
        font = ImageFont.load_default()
        width, height = LayoutUtils.calculate_text_dimensions("", font)
        assert width == 0
        assert height == 0

    def test_calculate_text_dimensions_getbbox_exception(self) -> None:
        """Test calculate_text_dimensions when font.getbbox raises exception"""
        mock_font = Mock()
        mock_font.getbbox.side_effect = Exception("Font error")

        text = "Test text\nSecond line"
        width, height = LayoutUtils.calculate_text_dimensions(text, mock_font)

        # Should fall back to character estimation
        assert width > 0
        assert height > 0

    def test_calculate_text_dimensions_getsize_exception(self) -> None:
        """Test calculate_text_dimensions when font.getsize raises exception"""
        mock_font = Mock()
        # No getbbox method
        del mock_font.getbbox
        mock_font.getsize.side_effect = Exception("Font error")

        text = "Test text"
        width, height = LayoutUtils.calculate_text_dimensions(text, mock_font)

        # Should fall back to character estimation
        assert width > 0
        assert height > 0

    def test_calculate_text_dimensions_no_font_methods(self) -> None:
        """Test calculate_text_dimensions when font has no sizing methods"""
        mock_font = Mock(spec=[])  # No methods available

        text = "Test text\nSecond line"
        width, height = LayoutUtils.calculate_text_dimensions(text, mock_font)

        # Should use fallback calculations
        assert width > 0
        assert height > 0

    def test_calculate_wrapped_text_height_empty_lines(self) -> None:
        """Test calculate_wrapped_text_height with text that results in empty lines"""
        mock_font = Mock()
        mock_font.getbbox.return_value = (0, 0, 10, 16)  # Mock font metrics

        with patch.object(LayoutUtils, "wrap_text_with_font", return_value=[]):
            height = LayoutUtils.calculate_wrapped_text_height("", mock_font, 100, 1.2)
            assert height == 0

    def test_calculate_wrapped_text_height_getbbox_exception(self) -> None:
        """Test calculate_wrapped_text_height when font.getbbox raises exception"""
        mock_font = Mock()
        mock_font.getbbox.side_effect = Exception("Font error")

        text = "Test text"
        height = LayoutUtils.calculate_wrapped_text_height(text, mock_font, 100, 1.2)

        # Should use default font size fallback
        assert height > 0

    def test_calculate_wrapped_text_height_getsize_exception(self) -> None:
        """Test calculate_wrapped_text_height when font.getsize raises exception"""
        mock_font = Mock()
        # No getbbox method
        del mock_font.getbbox
        mock_font.getsize.side_effect = Exception("Font error")

        text = "Test text"
        height = LayoutUtils.calculate_wrapped_text_height(text, mock_font, 100, 1.2)

        # Should use default font size fallback
        assert height > 0

    def test_calculate_wrapped_text_height_no_font_methods(self) -> None:
        """Test calculate_wrapped_text_height when font has no sizing methods"""
        mock_font = Mock(spec=[])  # No methods available

        text = "Test text"
        height = LayoutUtils.calculate_wrapped_text_height(text, mock_font, 100, 1.2)

        # Should use default font size fallback
        assert height > 0

    def test_layout_mixin_calculate_content_height_no_text_no_children(self) -> None:
        """Test LayoutMixin calculate_content_height with empty node"""
        mixin = LayoutMixin()

        # Mock empty layout node
        mock_layout_node = Mock()
        mock_dom_node = Mock()
        mock_dom_node.text = ""
        mock_dom_node.children = []
        mock_layout_node.dom_node = mock_dom_node

        mock_config = Mock()
        mock_font_manager = Mock()

        height = mixin.calculate_content_height(
            mock_layout_node, 400, mock_config, mock_font_manager
        )

        assert height == 0

    def test_layout_mixin_calculate_content_height_children_with_text(self) -> None:
        """Test LayoutMixin calculate_content_height with children containing text"""
        mixin = LayoutMixin()

        # Mock layout node with children containing text
        mock_layout_node = Mock()
        mock_dom_node = Mock()
        mock_dom_node.text = ""  # No direct text

        # Create mock children with text
        mock_child1 = Mock()
        mock_child1.text = "Child 1 text"
        mock_child2 = Mock()
        mock_child2.text = "Child 2 text"
        mock_dom_node.children = [mock_child1, mock_child2]

        mock_layout_node.dom_node = mock_dom_node

        mock_config = Mock()
        mock_config.LINE_HEIGHT = 1.2

        mock_font_manager = Mock()
        mock_font = Mock()
        mock_font_manager.get_font.return_value = mock_font

        # Mock LayoutUtils.calculate_wrapped_text_height to return a predictable value
        with patch.object(
            LayoutUtils, "calculate_wrapped_text_height", return_value=20
        ):
            height = mixin.calculate_content_height(
                mock_layout_node, 400, mock_config, mock_font_manager
            )

        # Should be sum of heights for both children
        assert height == 40  # 20 + 20
