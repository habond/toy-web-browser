"""Tests for the ListElement and ListItemElement classes"""

from unittest.mock import Mock, patch

import pytest

from src.config import BrowserConfig
from src.elements.element_factory import ElementFactory
from src.elements.list import ListElement, ListItemElement
from src.html_parser import DOMNode
from src.layout_engine import LayoutEngine
from tests.fixtures.test_utils import MockFactory, TestDataBuilder


class TestListElement:
    """Test the ListElement class"""

    def setup_method(self) -> None:
        """Set up test fixtures"""
        self.config = BrowserConfig()
        self.layout_engine = LayoutEngine()

    def test_list_element_creation(self) -> None:
        """Test ListElement can be created"""
        dom_node = DOMNode("ul")
        element = ListElement(dom_node)

        assert element is not None
        assert element.dom_node == dom_node

    def test_list_element_supported_tags(self) -> None:
        """Test ListElement works with ul and ol tags"""
        for tag in ["ul", "ol"]:
            dom_node = DOMNode(tag)
            element = ListElement(dom_node)

            assert element is not None
            assert element.dom_node.tag == tag

    def test_unordered_list_basic_layout(self) -> None:
        """Test basic unordered list layout"""
        ul_dom = DOMNode("ul")
        li_dom = DOMNode("li")
        text_dom = DOMNode("text", text="List item")
        li_dom.add_child(text_dom)
        ul_dom.add_child(li_dom)

        element = ListElement(ul_dom)
        initial_y = self.layout_engine.current_y

        layout_node = element.layout(self.layout_engine, 10, 800)

        assert layout_node is not None
        assert layout_node.dom_node == ul_dom
        assert hasattr(layout_node, "box")
        assert layout_node.box.x == 10
        assert layout_node.box.y == initial_y

        # Should have increased current_y (margins + content)
        assert self.layout_engine.current_y > initial_y

    def test_ordered_list_basic_layout(self) -> None:
        """Test basic ordered list layout"""
        ol_dom = DOMNode("ol")
        li_dom = DOMNode("li")
        text_dom = DOMNode("text", text="Numbered item")
        li_dom.add_child(text_dom)
        ol_dom.add_child(li_dom)

        element = ListElement(ol_dom)
        layout_node = element.layout(self.layout_engine, 10, 800)

        assert layout_node is not None
        assert layout_node.dom_node == ol_dom

    def test_list_with_multiple_items(self) -> None:
        """Test list with multiple list items"""
        ul_dom = DOMNode("ul")

        # Add multiple list items
        for i in range(3):
            li_dom = DOMNode("li")
            text_dom = DOMNode("text", text=f"Item {i+1}")
            li_dom.add_child(text_dom)
            ul_dom.add_child(li_dom)

        element = ListElement(ul_dom)

        # Mock the list item layout
        mock_layouts = [Mock() for _ in range(3)]
        element._layout_list_item = Mock(side_effect=mock_layouts)

        layout_node = element.layout(self.layout_engine, 10, 800)

        assert layout_node is not None
        assert len(layout_node.children) == 3

        # Should have called _layout_list_item for each item
        assert element._layout_list_item.call_count == 3

    def test_list_with_non_li_children(self) -> None:
        """Test list that contains non-li children (should be skipped)"""
        ul_dom = DOMNode("ul")
        li_dom = DOMNode("li")
        text_dom = DOMNode("text", text="Valid item")
        span_dom = DOMNode("span")  # Non-li child

        li_dom.add_child(text_dom)
        ul_dom.add_child(li_dom)
        ul_dom.add_child(span_dom)  # This should be skipped

        element = ListElement(ul_dom)
        mock_layout = Mock()
        element._layout_list_item = Mock(return_value=mock_layout)

        layout_node = element.layout(self.layout_engine, 10, 800)

        assert layout_node is not None
        assert len(layout_node.children) == 1  # Only the li should be processed

        # Should only call _layout_list_item once (for the li)
        element._layout_list_item.assert_called_once()

    def test_list_margins(self) -> None:
        """Test that list elements add appropriate margins"""
        ul_dom = DOMNode("ul")
        element = ListElement(ul_dom)

        initial_y = self.layout_engine.current_y
        layout_node = element.layout(self.layout_engine, 10, 800)

        assert layout_node is not None
        # Should have added margins before and after
        expected_margin_total = self.layout_engine.MARGIN * 2
        assert self.layout_engine.current_y >= initial_y + expected_margin_total

    def test_list_item_indentation(self) -> None:
        """Test that list items are indented correctly"""
        ul_dom = DOMNode("ul")
        li_dom = DOMNode("li")
        ul_dom.add_child(li_dom)

        element = ListElement(ul_dom)

        # Mock _layout_list_item to capture the x coordinate
        def mock_layout_list_item(
            layout_engine, dom_node, x, viewport_width, index, ordered
        ):
            mock_layout_list_item.captured_x = x
            return Mock()

        element._layout_list_item = mock_layout_list_item

        layout_node = element.layout(self.layout_engine, 10, 800)

        assert layout_node is not None
        # List items should be indented by 25 pixels
        expected_x = 10 + 25
        assert mock_layout_list_item.captured_x == expected_x

    @patch("src.elements.element_factory.ElementFactory.create_element")
    def test_layout_list_item_method(self, mock_create_element):
        """Test the _layout_list_item method"""
        ul_dom = DOMNode("ul")
        element = ListElement(ul_dom)

        li_dom = DOMNode("li")
        mock_list_item_element = Mock(spec=ListItemElement)
        mock_layout_result = Mock()
        mock_list_item_element.layout.return_value = mock_layout_result
        mock_create_element.return_value = mock_list_item_element

        result = element._layout_list_item(
            self.layout_engine, li_dom, 35, 800, 2, False
        )

        assert result == mock_layout_result

        # Should have created element and called layout with correct parameters
        mock_create_element.assert_called_once_with(li_dom)
        mock_list_item_element.layout.assert_called_once_with(
            self.layout_engine, 35, 800, index=2, ordered=False
        )

    @patch("src.elements.element_factory.ElementFactory.create_element")
    def test_layout_list_item_ordered_vs_unordered(self, mock_create_element):
        """Test that ordered parameter is passed correctly"""
        # Test unordered list
        ul_dom = DOMNode("ul")
        ul_element = ListElement(ul_dom)
        li_dom = DOMNode("li")

        mock_list_item = Mock(spec=ListItemElement)
        mock_create_element.return_value = mock_list_item

        ul_element._layout_list_item(self.layout_engine, li_dom, 35, 800, 1, False)

        # Check that ordered=False was passed
        call_args = mock_list_item.layout.call_args
        assert call_args[1]["ordered"] == False

        # Test ordered list
        ol_dom = DOMNode("ol")
        ol_element = ListElement(ol_dom)

        mock_list_item.reset_mock()
        ol_element._layout_list_item(self.layout_engine, li_dom, 35, 800, 1, True)

        # Check that ordered=True was passed
        call_args = mock_list_item.layout.call_args
        assert call_args[1]["ordered"] == True

    def test_list_element_render(self) -> None:
        """Test list element rendering"""
        ul_dom = DOMNode("ul")
        element = ListElement(ul_dom)

        layout_node = element.layout(self.layout_engine, 10, 800)

        # Add mock children
        mock_child1 = Mock()
        mock_child2 = Mock()
        layout_node.children = [mock_child1, mock_child2]

        mock_renderer = Mock()
        mock_draw = Mock()

        element.render(mock_draw, layout_node, mock_renderer)

        # Should have rendered each child
        assert mock_renderer._render_node.call_count == 2
        mock_renderer._render_node.assert_any_call(mock_draw, mock_child1)
        mock_renderer._render_node.assert_any_call(mock_draw, mock_child2)

    def test_list_index_numbering(self) -> None:
        """Test that list items receive correct index numbers"""
        ol_dom = DOMNode("ol")

        # Add 3 list items
        for i in range(3):
            li_dom = DOMNode("li")
            ol_dom.add_child(li_dom)

        element = ListElement(ol_dom)

        # Mock _layout_list_item to capture indices
        captured_indices = []

        def mock_layout_list_item(
            layout_engine, dom_node, x, viewport_width, index, ordered
        ):
            captured_indices.append(index)
            return Mock()

        element._layout_list_item = mock_layout_list_item

        layout_node = element.layout(self.layout_engine, 10, 800)

        assert layout_node is not None
        # Indices should be 1, 2, 3
        assert captured_indices == [1, 2, 3]


class TestListItemElement:
    """Test the ListItemElement class"""

    def setup_method(self) -> None:
        """Set up test fixtures"""
        self.config = BrowserConfig()
        self.layout_engine = LayoutEngine()

    def test_list_item_element_creation(self) -> None:
        """Test ListItemElement can be created"""
        dom_node = DOMNode("li")
        element = ListItemElement(dom_node)

        assert element is not None
        assert element.dom_node == dom_node

    def test_list_item_basic_layout(self) -> None:
        """Test basic list item layout"""
        li_dom = DOMNode("li")
        text_dom = DOMNode("text", text="Item content")
        li_dom.add_child(text_dom)

        element = ListItemElement(li_dom)
        initial_y = self.layout_engine.current_y

        layout_node = element.layout(
            self.layout_engine, 35, 800, index=1, ordered=False
        )

        assert layout_node is not None
        assert layout_node.dom_node == li_dom
        assert layout_node.box.x == 35
        assert layout_node.box.y == initial_y

        # Should have marker for unordered list
        assert hasattr(layout_node, "marker")
        assert layout_node.marker == "•"

    def test_list_item_ordered_layout(self) -> None:
        """Test ordered list item layout"""
        li_dom = DOMNode("li")
        element = ListItemElement(li_dom)

        layout_node = element.layout(self.layout_engine, 35, 800, index=3, ordered=True)

        assert layout_node is not None
        assert hasattr(layout_node, "marker")
        assert layout_node.marker == "3."

    def test_list_item_without_index(self) -> None:
        """Test list item layout without index (no marker)"""
        li_dom = DOMNode("li")
        element = ListItemElement(li_dom)

        layout_node = element.layout(self.layout_engine, 35, 800)

        assert layout_node is not None
        # Should not have marker when index is None
        assert not hasattr(layout_node, "marker") or layout_node.marker is None

    def test_list_item_marker_position(self) -> None:
        """Test list item marker positioning"""
        li_dom = DOMNode("li")
        element = ListItemElement(li_dom)

        initial_y = self.layout_engine.current_y
        layout_node = element.layout(
            self.layout_engine, 35, 800, index=1, ordered=False
        )

        assert layout_node is not None
        assert hasattr(layout_node, "marker_pos")

        # Marker should be positioned to the left and slightly down from start
        expected_x = 35 - 20  # x - 20
        expected_y = initial_y + self.layout_engine.DEFAULT_FONT_SIZE * 0.2
        assert layout_node.marker_pos == (expected_x, expected_y)

    def test_list_item_with_children(self) -> None:
        """Test list item with child content"""
        li_dom = DOMNode("li")
        text_dom = DOMNode("text", text="Child content")
        li_dom.add_child(text_dom)

        element = ListItemElement(li_dom)

        # Mock child layout
        mock_child_layout = Mock()
        self.layout_engine._layout_child = Mock(return_value=mock_child_layout)

        layout_node = element.layout(
            self.layout_engine, 35, 800, index=1, ordered=False
        )

        assert layout_node is not None
        assert len(layout_node.children) == 1
        assert layout_node.children[0] == mock_child_layout

        # Should have called _layout_child with correct x position
        self.layout_engine._layout_child.assert_called_with(text_dom, 35)

    def test_list_item_margin_after(self) -> None:
        """Test that list item adds margin after content"""
        li_dom = DOMNode("li")
        element = ListItemElement(li_dom)

        initial_y = self.layout_engine.current_y
        layout_node = element.layout(
            self.layout_engine, 35, 800, index=1, ordered=False
        )

        assert layout_node is not None
        # Should have added half margin after content
        expected_margin = self.layout_engine.MARGIN * 0.5
        assert self.layout_engine.current_y >= initial_y + expected_margin

    def test_list_item_render_with_marker(self) -> None:
        """Test list item rendering with marker"""
        li_dom = DOMNode("li")
        element = ListItemElement(li_dom)

        layout_node = element.layout(self.layout_engine, 35, 800, index=2, ordered=True)
        assert layout_node is not None

        # Add mock child
        mock_child = Mock()
        layout_node.children = [mock_child]

        mock_font = Mock()
        mock_renderer = Mock()
        mock_renderer._get_font.return_value = mock_font
        mock_draw = Mock()

        element.render(mock_draw, layout_node, mock_renderer)

        # Should have drawn marker text
        mock_draw.text.assert_called()
        marker_call = mock_draw.text.call_args
        assert marker_call[0][0] == layout_node.marker_pos  # Position
        assert marker_call[0][1] == "2."  # Marker text
        assert marker_call[1]["font"] == mock_font

        # Should have rendered child
        mock_renderer._render_node.assert_called_with(mock_draw, mock_child)

    def test_list_item_render_without_marker(self) -> None:
        """Test list item rendering without marker"""
        li_dom = DOMNode("li")
        element = ListItemElement(li_dom)

        layout_node = element.layout(self.layout_engine, 35, 800)  # No index
        assert layout_node is not None

        mock_child = Mock()
        layout_node.children = [mock_child]

        mock_renderer = Mock()
        mock_draw = Mock()

        element.render(mock_draw, layout_node, mock_renderer)

        # Should not have drawn marker text
        mock_draw.text.assert_not_called()

        # Should still render child
        mock_renderer._render_node.assert_called_with(mock_draw, mock_child)

    def test_list_item_render_missing_marker_attributes(self) -> None:
        """Test list item rendering when marker attributes are missing"""
        li_dom = DOMNode("li")
        element = ListItemElement(li_dom)

        # Create layout node without marker attributes
        layout_node = TestDataBuilder.create_layout_node(li_dom)

        mock_renderer = Mock()
        mock_draw = Mock()

        # Should not crash
        element.render(mock_draw, layout_node, mock_renderer)

        # Should not draw marker
        mock_draw.text.assert_not_called()

    def test_list_item_multiple_children(self) -> None:
        """Test list item with multiple children"""
        li_dom = DOMNode("li")
        text1_dom = DOMNode("text", text="First")
        text2_dom = DOMNode("text", text="Second")
        li_dom.add_child(text1_dom)
        li_dom.add_child(text2_dom)

        element = ListItemElement(li_dom)

        mock_child1 = Mock()
        mock_child2 = Mock()
        self.layout_engine._layout_child = Mock(side_effect=[mock_child1, mock_child2])

        layout_node = element.layout(
            self.layout_engine, 35, 800, index=1, ordered=False
        )

        assert layout_node is not None
        assert len(layout_node.children) == 2

        # Should have called _layout_child for each
        assert self.layout_engine._layout_child.call_count == 2

    def test_list_item_height_calculation(self) -> None:
        """Test list item height calculation"""
        li_dom = DOMNode("li")
        element = ListItemElement(li_dom)

        initial_y = self.layout_engine.current_y
        layout_node = element.layout(
            self.layout_engine, 35, 800, index=1, ordered=False
        )

        assert layout_node is not None
        # Height should include all content plus margin
        expected_height = self.layout_engine.current_y - initial_y
        assert layout_node.box.height == expected_height
