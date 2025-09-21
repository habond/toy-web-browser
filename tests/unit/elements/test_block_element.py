"""Tests for the BlockElement class"""

from unittest.mock import Mock

from src.config import BrowserConfig
from src.elements.block import BlockElement
from src.html_parser import DOMNode
from src.layout_engine import Box, LayoutEngine
from tests.fixtures.test_utils import MockFactory


class TestBlockElement:
    """Test the BlockElement class"""

    def setup_method(self) -> None:
        """Set up test fixtures"""
        self.config = BrowserConfig()
        self.mock_font_manager = MockFactory.create_font_manager_mock()
        self.layout_engine = LayoutEngine()

    def test_block_element_creation(self) -> None:
        """Test BlockElement can be created"""
        dom_node = DOMNode("div")
        element = BlockElement(dom_node)

        assert element is not None
        assert element.dom_node == dom_node

    def test_block_element_supported_tags(self) -> None:
        """Test BlockElement works with all supported block tags"""
        block_tags = ["p", "div", "blockquote", "pre"]

        for tag in block_tags:
            dom_node = DOMNode(tag)
            element = BlockElement(dom_node)

            assert element is not None
            assert element.dom_node.tag == tag

    def test_block_element_basic_layout(self) -> None:
        """Test basic block element layout"""
        div_dom = DOMNode("div")
        element = BlockElement(div_dom)

        initial_y = self.layout_engine.current_y
        layout_node = element.layout(self.layout_engine, 10, 800)

        assert layout_node is not None
        assert layout_node.dom_node == div_dom
        assert hasattr(layout_node, "box")
        assert layout_node.box.x == 10
        assert layout_node.box.y == initial_y
        assert layout_node.box.width == 800 - 2 * 10  # viewport_width - 2 * x

        # Should have added margins
        assert self.layout_engine.current_y > initial_y

    def test_block_element_with_children(self) -> None:
        """Test block element layout with children"""
        div_dom = DOMNode("div")
        text_dom = DOMNode("text", text="Child content")
        div_dom.add_child(text_dom)

        element = BlockElement(div_dom)

        # Mock the layout child call
        mock_child_layout = Mock()
        self.layout_engine._layout_child = Mock(return_value=mock_child_layout)

        layout_node = element.layout(self.layout_engine, 10, 800)

        assert layout_node is not None
        assert len(layout_node.children) == 1
        assert layout_node.children[0] == mock_child_layout

        # Should have called _layout_child with padding offset
        expected_x = 10 + self.layout_engine.PADDING
        self.layout_engine._layout_child.assert_called_with(text_dom, expected_x)

    def test_block_element_multiple_children(self) -> None:
        """Test block element with multiple children"""
        div_dom = DOMNode("div")
        text1_dom = DOMNode("text", text="First child")
        text2_dom = DOMNode("text", text="Second child")
        div_dom.add_child(text1_dom)
        div_dom.add_child(text2_dom)

        element = BlockElement(div_dom)

        mock_child1 = Mock()
        mock_child2 = Mock()
        self.layout_engine._layout_child = Mock(side_effect=[mock_child1, mock_child2])

        layout_node = element.layout(self.layout_engine, 10, 800)

        assert layout_node is not None
        assert len(layout_node.children) == 2
        assert layout_node.children[0] == mock_child1
        assert layout_node.children[1] == mock_child2

        # Should have called _layout_child for each child
        assert self.layout_engine._layout_child.call_count == 2

    def test_block_element_child_returns_none(self) -> None:
        """Test block element when child layout returns None"""
        div_dom = DOMNode("div")
        text_dom = DOMNode("text", text="")  # Empty text might return None
        div_dom.add_child(text_dom)

        element = BlockElement(div_dom)

        # Mock child layout returning None
        self.layout_engine._layout_child = Mock(return_value=None)

        layout_node = element.layout(self.layout_engine, 10, 800)

        assert layout_node is not None
        assert len(layout_node.children) == 0  # None children should not be added

    def test_block_element_margins(self) -> None:
        """Test that block element adds correct margins"""
        div_dom = DOMNode("div")
        element = BlockElement(div_dom)

        initial_y = self.layout_engine.current_y
        layout_node = element.layout(self.layout_engine, 10, 800)

        assert layout_node is not None
        # Should have added margin before and after
        expected_margin_total = self.layout_engine.MARGIN * 2
        assert self.layout_engine.current_y >= initial_y + expected_margin_total

    def test_block_element_height_calculation(self) -> None:
        """Test that block element calculates height correctly"""
        div_dom = DOMNode("div")
        element = BlockElement(div_dom)

        initial_y = self.layout_engine.current_y
        layout_node = element.layout(self.layout_engine, 10, 800)

        assert layout_node is not None
        # Height should be the difference between final and initial y
        expected_height = self.layout_engine.current_y - initial_y
        assert layout_node.box.height == expected_height

    def test_block_element_render_basic(self) -> None:
        """Test basic block element rendering"""
        div_dom = DOMNode("div")
        element = BlockElement(div_dom)

        layout_node = element.layout(self.layout_engine, 10, 800)

        # Add mock children
        mock_child1 = Mock()
        mock_child2 = Mock()
        layout_node.children = [mock_child1, mock_child2]

        # Mock renderer
        mock_renderer = Mock()
        mock_draw = Mock()

        element.render(mock_draw, layout_node, mock_renderer)

        # Should have rendered each child
        assert mock_renderer._render_node.call_count == 2
        mock_renderer._render_node.assert_any_call(mock_draw, mock_child1)
        mock_renderer._render_node.assert_any_call(mock_draw, mock_child2)

    def test_block_element_render_no_children(self) -> None:
        """Test block element rendering with no children"""
        div_dom = DOMNode("div")
        element = BlockElement(div_dom)

        layout_node = element.layout(self.layout_engine, 10, 800)
        layout_node.children = []

        mock_renderer = Mock()
        mock_draw = Mock()

        # Should not crash with no children
        element.render(mock_draw, layout_node, mock_renderer)

        # Should not have called _render_node
        mock_renderer._render_node.assert_not_called()

    def test_blockquote_element_render_with_border(self) -> None:
        """Test blockquote element renders with left border"""
        blockquote_dom = DOMNode("blockquote")
        element = BlockElement(blockquote_dom)

        layout_node = element.layout(self.layout_engine, 10, 800)

        mock_renderer = Mock()
        mock_draw = Mock()

        element.render(mock_draw, layout_node, mock_renderer)

        # Should have drawn rectangle for blockquote border
        mock_draw.rectangle.assert_called_once()

        # Check that rectangle coordinates are for left border
        args, kwargs = mock_draw.rectangle.call_args
        coords = args[0]
        assert coords[0] == layout_node.box.x - 5  # x - 5
        assert coords[2] == layout_node.box.x - 3  # x - 3 (2px wide border)

    def test_non_blockquote_element_no_border(self) -> None:
        """Test non-blockquote elements don't render border"""
        div_dom = DOMNode("div")
        element = BlockElement(div_dom)

        layout_node = element.layout(self.layout_engine, 10, 800)

        mock_renderer = Mock()
        mock_draw = Mock()

        element.render(mock_draw, layout_node, mock_renderer)

        # Should not have drawn rectangle for non-blockquote
        mock_draw.rectangle.assert_not_called()

    def test_blockquote_border_coordinates(self) -> None:
        """Test blockquote border coordinates are calculated correctly"""
        blockquote_dom = DOMNode("blockquote")
        element = BlockElement(blockquote_dom)

        layout_node = element.layout(self.layout_engine, 10, 800)
        layout_node.box = Box(50, 100, 400, 200)  # Set specific coordinates

        mock_draw = Mock()

        element._render_blockquote_border(mock_draw, layout_node.box)

        # Check border coordinates
        mock_draw.rectangle.assert_called_once()
        args, kwargs = mock_draw.rectangle.call_args
        coords = args[0]

        assert coords == (45, 100, 47, 300)  # (x-5, y, x-3, y+height)
        assert kwargs.get("fill") == "#cccccc"

    def test_block_element_padding_offset(self) -> None:
        """Test that children are positioned with padding offset"""
        div_dom = DOMNode("div")
        text_dom = DOMNode("text", text="Child")
        div_dom.add_child(text_dom)

        element = BlockElement(div_dom)

        # Capture the x coordinate passed to _layout_child
        def mock_layout_child(child, x):
            mock_layout_child.called_with_x = x
            return Mock()

        self.layout_engine._layout_child = mock_layout_child

        layout_node = element.layout(self.layout_engine, 10, 800)

        assert layout_node is not None
        # Child should have been positioned with padding offset
        expected_x = 10 + self.layout_engine.PADDING
        assert mock_layout_child.called_with_x == expected_x

    def test_block_element_viewport_width_calculation(self) -> None:
        """Test viewport width calculation for block elements"""
        div_dom = DOMNode("div")
        element = BlockElement(div_dom)

        layout_node = element.layout(self.layout_engine, 20, 1000)

        assert layout_node is not None
        # Width should account for left and right margins
        expected_width = 1000 - 2 * 20  # viewport_width - 2 * x
        assert layout_node.box.width == expected_width

    def test_block_element_preserves_layout_engine_state(self) -> None:
        """Test that block element properly manages layout engine state"""
        div_dom = DOMNode("div")
        element = BlockElement(div_dom)

        # Record initial state
        initial_y = self.layout_engine.current_y
        initial_margin = self.layout_engine.MARGIN

        layout_node = element.layout(self.layout_engine, 10, 800)

        assert layout_node is not None
        # Layout engine state should be preserved (except current_y)
        assert self.layout_engine.MARGIN == initial_margin
        # current_y should have increased
        assert self.layout_engine.current_y > initial_y
