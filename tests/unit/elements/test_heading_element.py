"""Tests for the HeadingElement class"""

from unittest.mock import Mock, patch

import pytest

from src.config import BrowserConfig
from src.elements.heading import HeadingElement
from src.html_parser import DOMNode
from src.layout_engine import LayoutEngine
from tests.fixtures.test_utils import MockFactory, TestDataBuilder


class TestHeadingElement:
    """Test the HeadingElement class"""

    def setup_method(self) -> None:
        """Set up test fixtures"""
        self.config = BrowserConfig()
        self.mock_font_manager = MockFactory.create_font_manager_mock()
        self.layout_engine = LayoutEngine()

    def test_heading_element_creation(self) -> None:
        """Test HeadingElement can be created"""
        dom_node = DOMNode("h1")
        element = HeadingElement(dom_node)

        assert element is not None
        assert element.dom_node == dom_node

    def test_heading_element_h1_layout(self) -> None:
        """Test h1 heading layout"""
        # Create h1 with text child
        h1_dom = DOMNode("h1")
        text_dom = DOMNode("text", text="Main Title")
        h1_dom.add_child(text_dom)

        element = HeadingElement(h1_dom)
        initial_y = self.layout_engine.current_y

        layout_node = element.layout(self.layout_engine, 10, 800)

        assert layout_node is not None
        assert layout_node.dom_node == h1_dom
        assert hasattr(layout_node, "box")
        assert layout_node.box.x == 10
        assert layout_node.box.y == initial_y
        # Should have increased current_y
        assert self.layout_engine.current_y > initial_y

    def test_heading_element_all_heading_levels(self) -> None:
        """Test all heading levels (h1-h6)"""
        heading_tags = ["h1", "h2", "h3", "h4", "h5", "h6"]

        for tag in heading_tags:
            dom_node = DOMNode(tag)
            text_dom = DOMNode("text", text=f"Title {tag}")
            dom_node.add_child(text_dom)

            element = HeadingElement(dom_node)
            layout_node = element.layout(self.layout_engine, 10, 800)

            assert layout_node is not None
            assert layout_node.dom_node.tag == tag

    def test_heading_element_size_multipliers(self) -> None:
        """Test that different heading levels use correct size multipliers"""
        # Test h1 (largest) vs h6 (smallest)
        h1_dom = DOMNode("h1")
        h1_text = DOMNode("text", text="Big Title")
        h1_dom.add_child(h1_text)

        h6_dom = DOMNode("h6")
        h6_text = DOMNode("text", text="Small Title")
        h6_dom.add_child(h6_text)

        h1_element = HeadingElement(h1_dom)
        h6_element = HeadingElement(h6_dom)

        h1_layout = h1_element.layout(self.layout_engine, 10, 800)
        self.layout_engine.current_y = 0  # Reset for fair comparison
        h6_layout = h6_element.layout(self.layout_engine, 10, 800)

        assert h1_layout is not None
        assert h6_layout is not None

        # h1 should be taller than h6 due to larger font size
        assert h1_layout.box.height > h6_layout.box.height

    def test_heading_element_with_empty_text(self) -> None:
        """Test heading element with empty text"""
        h1_dom = DOMNode("h1")
        text_dom = DOMNode("text", text="")
        h1_dom.add_child(text_dom)

        element = HeadingElement(h1_dom)
        layout_node = element.layout(self.layout_engine, 10, 800)

        assert layout_node is not None
        # Should still create layout node even with empty text
        assert layout_node.box.height > 0  # Due to margins

    def test_heading_element_with_no_text_children(self) -> None:
        """Test heading element with no text children"""
        h1_dom = DOMNode("h1")
        # Add non-text child
        span_dom = DOMNode("span")
        h1_dom.add_child(span_dom)

        element = HeadingElement(h1_dom)
        layout_node = element.layout(self.layout_engine, 10, 800)

        assert layout_node is not None
        # Should create layout node with margins
        assert layout_node.box.height > 0

    def test_heading_element_margins(self) -> None:
        """Test that heading elements add appropriate margins"""
        h1_dom = DOMNode("h1")
        text_dom = DOMNode("text", text="Title")
        h1_dom.add_child(text_dom)

        element = HeadingElement(h1_dom)
        initial_y = self.layout_engine.current_y

        layout_node = element.layout(self.layout_engine, 10, 800)

        assert layout_node is not None
        # Should have added margins (1.5 * MARGIN both before and after)
        expected_margin_total = self.config.MARGIN * 3  # 1.5 before + 1.5 after
        assert self.layout_engine.current_y >= initial_y + expected_margin_total

    @patch("src.elements.heading.config")
    def test_heading_element_uses_config_sizes(self, mock_config):
        """Test that heading element uses configuration for sizes"""
        mock_config.HEADING_SIZES = {"h1": 2.5, "h2": 2.0}
        mock_config.DEFAULT_FONT_SIZE = 16
        mock_config.LINE_HEIGHT = 1.5
        mock_config.MARGIN = 10

        h1_dom = DOMNode("h1")
        text_dom = DOMNode("text", text="Title")
        h1_dom.add_child(text_dom)

        element = HeadingElement(h1_dom)

        # Mock the layout engine's _layout_child method
        mock_text_layout = Mock()
        mock_text_layout.box = Mock()
        mock_text_layout.box.y = 0
        self.layout_engine._layout_child = Mock(return_value=mock_text_layout)

        layout_node = element.layout(self.layout_engine, 10, 800)

        assert layout_node is not None
        # Check that font_size was set on the text layout
        assert hasattr(mock_text_layout, "font_size")
        assert (
            mock_text_layout.font_size == 16 * 2.5
        )  # DEFAULT_FONT_SIZE * h1 multiplier

    def test_heading_element_render_basic(self) -> None:
        """Test basic heading element rendering"""
        h1_dom = DOMNode("h1")
        text_dom = DOMNode("text", text="Main Title")
        h1_dom.add_child(text_dom)

        element = HeadingElement(h1_dom)
        layout_node = element.layout(self.layout_engine, 10, 800)

        # Mock a child layout with the necessary attributes
        mock_child = Mock()
        mock_child.font_size = 32
        mock_child.lines = ["Main Title"]
        mock_child.box = Mock()
        mock_child.box.x = 10
        mock_child.box.y = 20
        layout_node.children = [mock_child]

        # Mock renderer and draw
        mock_font = Mock()
        mock_renderer = Mock()
        mock_renderer._get_font.return_value = mock_font
        mock_renderer.LINE_HEIGHT = 1.5

        mock_draw = Mock()

        # Test rendering
        element.render(mock_draw, layout_node, mock_renderer)

        # Should have requested bold font with appropriate size
        mock_renderer._get_font.assert_called_with(size=32, bold=True)

        # Should have drawn text
        mock_draw.text.assert_called()

    def test_heading_element_render_multiple_lines(self) -> None:
        """Test heading element rendering with multiple lines"""
        h1_dom = DOMNode("h1")
        text_dom = DOMNode("text", text="Very Long Heading That Might Wrap")
        h1_dom.add_child(text_dom)

        element = HeadingElement(h1_dom)
        layout_node = element.layout(self.layout_engine, 10, 800)

        # Mock a child layout with multiple lines
        mock_child = Mock()
        mock_child.font_size = 32
        mock_child.lines = ["Very Long Heading", "That Might Wrap"]
        mock_child.box = Mock()
        mock_child.box.x = 10
        mock_child.box.y = 20
        layout_node.children = [mock_child]

        mock_renderer = Mock()
        mock_renderer._get_font.return_value = Mock()
        mock_renderer.LINE_HEIGHT = 1.5

        mock_draw = Mock()

        element.render(mock_draw, layout_node, mock_renderer)

        # Should have drawn text multiple times (once per line)
        assert mock_draw.text.call_count == 2

    def test_heading_element_render_no_font_size(self) -> None:
        """Test heading element rendering when child has no font_size"""
        h1_dom = DOMNode("h1")
        element = HeadingElement(h1_dom)
        layout_node = element.layout(self.layout_engine, 10, 800)

        # Mock a child layout without font_size
        mock_child = Mock()
        del mock_child.font_size  # Remove font_size attribute
        layout_node.children = [mock_child]

        mock_renderer = Mock()
        mock_renderer._render_node = Mock()
        mock_draw = Mock()

        # Should delegate to renderer's _render_node
        element.render(mock_draw, layout_node, mock_renderer)

        mock_renderer._render_node.assert_called_with(mock_draw, mock_child)

    def test_heading_element_render_empty_lines(self) -> None:
        """Test heading element rendering with empty lines"""
        h1_dom = DOMNode("h1")
        element = HeadingElement(h1_dom)
        layout_node = element.layout(self.layout_engine, 10, 800)

        # Mock child with empty lines
        mock_child = Mock()
        mock_child.font_size = 32
        mock_child.lines = ["Title", "", "Subtitle"]
        mock_child.box = Mock()
        mock_child.box.x = 10
        mock_child.box.y = 20
        layout_node.children = [mock_child]

        mock_renderer = Mock()
        mock_renderer._get_font.return_value = Mock()
        mock_renderer.LINE_HEIGHT = 1.5

        mock_draw = Mock()

        element.render(mock_draw, layout_node, mock_renderer)

        # Should skip empty lines (only 2 calls for non-empty lines)
        assert mock_draw.text.call_count == 2

    def test_heading_element_unknown_tag(self) -> None:
        """Test heading element with unknown heading tag"""
        unknown_dom = DOMNode("h7")  # Non-standard heading
        text_dom = DOMNode("text", text="Unknown Heading")
        unknown_dom.add_child(text_dom)

        element = HeadingElement(unknown_dom)
        layout_node = element.layout(self.layout_engine, 10, 800)

        assert layout_node is not None
        # Should use default size multiplier (1.0) for unknown tags

    def test_heading_element_line_height_calculation(self) -> None:
        """Test that heading elements calculate line height correctly"""
        h1_dom = DOMNode("h1")
        text_dom = DOMNode("text", text="Title")
        h1_dom.add_child(text_dom)

        element = HeadingElement(h1_dom)

        # Mock layout child to capture the height calculation
        mock_text_layout = Mock()
        mock_text_layout.box = Mock()
        mock_text_layout.box.y = 0
        self.layout_engine._layout_child = Mock(return_value=mock_text_layout)

        layout_node = element.layout(self.layout_engine, 10, 800)

        assert layout_node is not None
        # Verify height was set based on font size and line height
        expected_height = (
            self.config.DEFAULT_FONT_SIZE
            * self.config.HEADING_SIZES["h1"]
            * self.config.LINE_HEIGHT
        )
        assert mock_text_layout.box.height == expected_height
