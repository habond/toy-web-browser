"""Tests for the TableCellElement class"""

from unittest.mock import Mock

from src.config import BrowserConfig
from src.elements.table.table_cell_element import TableCellElement
from src.html_parser import DOMNode
from src.layout_engine import LayoutEngine
from tests.fixtures.test_utils import TestDataBuilder


class TestTableCellElement:
    """Test the TableCellElement class"""

    def setup_method(self) -> None:
        """Set up test fixtures"""
        self.config = BrowserConfig()
        self.layout_engine = LayoutEngine()

    def create_cell_with_text(self, text: str, tag: str = "td") -> DOMNode:
        """Create table cell DOM with text"""
        cell_dom = DOMNode(tag)
        text_dom = DOMNode("text", text=text)
        cell_dom.add_child(text_dom)
        return cell_dom

    def test_table_cell_element_creation(self) -> None:
        """Test TableCellElement can be created"""
        td_dom = DOMNode("td")
        element = TableCellElement(td_dom)

        assert element is not None
        assert element.dom_node == td_dom

    def test_table_cell_basic_layout(self) -> None:
        """Test basic table cell layout"""
        td_dom = self.create_cell_with_text("Cell content")
        element = TableCellElement(td_dom)

        initial_y = self.layout_engine.current_y
        layout_node = element.layout(self.layout_engine, 10, 800)

        assert layout_node is not None
        assert layout_node.dom_node == td_dom
        assert layout_node.box.x == 10
        assert layout_node.box.y == initial_y

    def test_table_cell_layout_with_width(self) -> None:
        """Test table cell layout with specific width"""
        td_dom = self.create_cell_with_text("Cell content")
        element = TableCellElement(td_dom)

        initial_y = self.layout_engine.current_y
        width = 150.0

        layout_node = element.layout_with_width(self.layout_engine, 20, 800, width)

        assert layout_node is not None
        assert layout_node.box.x == 20
        assert layout_node.box.y == initial_y
        assert layout_node.box.width == width

        # Table cells should NOT advance current_y (that's the table row's job)
        assert self.layout_engine.current_y == initial_y

    def test_table_cell_td_element(self) -> None:
        """Test table cell with td tag"""
        td_dom = self.create_cell_with_text("Regular cell", "td")
        element = TableCellElement(td_dom)

        layout_node = element.layout_with_width(self.layout_engine, 10, 800, 100.0)

        assert layout_node is not None
        assert element.dom_node.tag == "td"

    def test_table_cell_th_element(self) -> None:
        """Test table cell with th tag"""
        th_dom = self.create_cell_with_text("Header cell", "th")
        element = TableCellElement(th_dom)

        layout_node = element.layout_with_width(self.layout_engine, 10, 800, 100.0)

        assert layout_node is not None
        assert element.dom_node.tag == "th"

    def test_table_cell_empty_cell(self) -> None:
        """Test table cell with no content"""
        td_dom = DOMNode("td")  # No children
        element = TableCellElement(td_dom)

        initial_y = self.layout_engine.current_y
        layout_node = element.layout_with_width(self.layout_engine, 10, 800, 100.0)

        assert layout_node is not None
        # Should still have height from padding
        expected_height = 2 * self.config.PADDING
        assert layout_node.box.height == expected_height
        assert self.layout_engine.current_y == initial_y

    def test_table_cell_with_empty_text(self) -> None:
        """Test table cell with empty text content"""
        td_dom = DOMNode("td")
        empty_text_dom = DOMNode("text", text="")
        td_dom.add_child(empty_text_dom)

        element = TableCellElement(td_dom)

        layout_node = element.layout_with_width(self.layout_engine, 10, 800, 100.0)

        assert layout_node is not None
        # Empty text should be skipped, so no children
        assert len(layout_node.children) == 0

    def test_table_cell_with_whitespace_only_text(self) -> None:
        """Test table cell with whitespace-only text content"""
        td_dom = DOMNode("td")
        whitespace_text_dom = DOMNode("text", text="   \n  \t  ")
        td_dom.add_child(whitespace_text_dom)

        element = TableCellElement(td_dom)

        layout_node = element.layout_with_width(self.layout_engine, 10, 800, 100.0)

        assert layout_node is not None
        # Whitespace-only text should be skipped
        assert len(layout_node.children) == 0

    def test_table_cell_with_valid_text(self) -> None:
        """Test table cell with valid text content"""
        td_dom = self.create_cell_with_text("Valid content")
        element = TableCellElement(td_dom)

        # Mock the layout engine method
        mock_child_layout = Mock()
        self.layout_engine._layout_child_with_width = Mock(
            return_value=mock_child_layout
        )

        layout_node = element.layout_with_width(self.layout_engine, 10, 800, 120.0)

        assert layout_node is not None
        assert len(layout_node.children) == 1
        assert layout_node.children[0] == mock_child_layout

        # Should have called layout with correct parameters
        self.layout_engine._layout_child_with_width.assert_called_once()
        call_args = self.layout_engine._layout_child_with_width.call_args
        assert call_args[0][1] == 10 + self.config.PADDING  # x + padding
        assert call_args[0][2] == 120.0 - 2 * self.config.PADDING  # content_width

    def test_table_cell_multiple_children(self) -> None:
        """Test table cell with multiple child elements"""
        td_dom = DOMNode("td")
        text1_dom = DOMNode("text", text="First part")
        text2_dom = DOMNode("text", text="Second part")
        td_dom.add_child(text1_dom)
        td_dom.add_child(text2_dom)

        element = TableCellElement(td_dom)

        # Mock the layout engine method
        mock_child1 = Mock()
        mock_child2 = Mock()
        self.layout_engine._layout_child_with_width = Mock(
            side_effect=[mock_child1, mock_child2]
        )

        layout_node = element.layout_with_width(self.layout_engine, 10, 800, 100.0)

        assert layout_node is not None
        assert len(layout_node.children) == 2
        # Should have called layout for each child
        assert self.layout_engine._layout_child_with_width.call_count == 2

    def test_table_cell_mixed_children(self) -> None:
        """Test table cell with mixed child types"""
        td_dom = DOMNode("td")
        text_dom = DOMNode("text", text="Text content")
        span_dom = DOMNode("span")  # Non-text element
        empty_text_dom = DOMNode("text", text="")  # Empty text
        td_dom.add_child(text_dom)
        td_dom.add_child(span_dom)
        td_dom.add_child(empty_text_dom)

        element = TableCellElement(td_dom)

        # Mock the layout engine method
        mock_text_layout = Mock()
        mock_span_layout = Mock()
        self.layout_engine._layout_child_with_width = Mock(
            side_effect=[mock_text_layout, mock_span_layout]
        )

        layout_node = element.layout_with_width(self.layout_engine, 10, 800, 100.0)

        assert layout_node is not None
        # Should layout text and span, but skip empty text
        assert len(layout_node.children) == 2
        assert self.layout_engine._layout_child_with_width.call_count == 2

    def test_table_cell_height_calculation(self) -> None:
        """Test table cell height calculation"""
        td_dom = self.create_cell_with_text("Content")
        element = TableCellElement(td_dom)

        layout_node = element.layout_with_width(self.layout_engine, 10, 800, 100.0)

        assert layout_node is not None
        # Height should be content height plus padding
        # Text content (font_size * line_height) + 2 * padding
        expected_height = 16 * 1.5 + 2 * self.config.PADDING  # 24 + 10 = 34
        assert layout_node.box.height == expected_height

    def test_table_cell_content_width_calculation(self) -> None:
        """Test table cell content width calculation"""
        td_dom = self.create_cell_with_text("Content")
        element = TableCellElement(td_dom)

        # Mock to capture content width
        self.layout_engine._layout_child_with_width = Mock(return_value=Mock())

        cell_width = 120.0
        layout_node = element.layout_with_width(self.layout_engine, 10, 800, cell_width)

        assert layout_node is not None
        # Content width should be cell width minus 2 * padding
        expected_content_width = cell_width - 2 * self.config.PADDING
        call_args = self.layout_engine._layout_child_with_width.call_args
        assert call_args[0][2] == expected_content_width

    def test_table_cell_position_calculation(self) -> None:
        """Test table cell position calculation"""
        td_dom = self.create_cell_with_text("Content")
        element = TableCellElement(td_dom)

        x = 30
        initial_y = self.layout_engine.current_y
        layout_node = element.layout_with_width(self.layout_engine, x, 800, 100.0)

        assert layout_node is not None
        assert layout_node.box.x == x
        assert layout_node.box.y == initial_y

    def test_table_cell_render_td(self) -> None:
        """Test rendering of td cell"""
        td_dom = DOMNode("td")
        element = TableCellElement(td_dom)

        layout_node = TestDataBuilder.create_layout_node(td_dom)

        # Add mock children
        mock_child1 = Mock()
        mock_child2 = Mock()
        layout_node.children = [mock_child1, mock_child2]

        mock_renderer = Mock()
        mock_draw = Mock()

        element.render(mock_draw, layout_node, mock_renderer)

        # Should not draw background for td
        mock_draw.rectangle.assert_not_called()

        # Should have rendered each child
        assert mock_renderer._render_node.call_count == 2
        mock_renderer._render_node.assert_any_call(mock_draw, mock_child1)
        mock_renderer._render_node.assert_any_call(mock_draw, mock_child2)

    def test_table_cell_render_th(self) -> None:
        """Test rendering of th cell"""
        th_dom = DOMNode("th")
        element = TableCellElement(th_dom)

        layout_node = TestDataBuilder.create_layout_node(th_dom)
        layout_node.box.x = 10
        layout_node.box.y = 20
        layout_node.box.width = 80
        layout_node.box.height = 30

        # Add mock child
        mock_child = Mock()
        layout_node.children = [mock_child]

        mock_renderer = Mock()
        mock_draw = Mock()

        element.render(mock_draw, layout_node, mock_renderer)

        # Should draw background for th (adjusted for 1px grid line spacing)
        mock_draw.rectangle.assert_called_once()
        call_args = mock_draw.rectangle.call_args
        assert call_args[0][0] == (11, 21, 89, 49)  # x+1, y+1, x+w-1, y+h-1
        assert call_args[1]["fill"] == "#f0f0f0"

        # Should have rendered child
        mock_renderer._render_node.assert_called_once_with(mock_draw, mock_child)

    def test_table_cell_render_empty_cell(self) -> None:
        """Test rendering of empty cell"""
        td_dom = DOMNode("td")
        element = TableCellElement(td_dom)

        layout_node = TestDataBuilder.create_layout_node(td_dom)

        mock_renderer = Mock()
        mock_draw = Mock()

        element.render(mock_draw, layout_node, mock_renderer)

        # Should not render any children
        mock_renderer._render_node.assert_not_called()

    def test_table_cell_delegates_to_layout_with_width(self) -> None:
        """Test that standard layout method delegates to layout_with_width"""
        td_dom = DOMNode("td")
        element = TableCellElement(td_dom)

        # Mock the specific method
        element.layout_with_width = Mock(return_value=Mock())

        result = element.layout(self.layout_engine, 10, 800)

        assert result is not None
        # Should have called layout_with_width with default width
        element.layout_with_width.assert_called_once_with(
            self.layout_engine, 10, 800, 0
        )

    def test_table_cell_padding_application(self) -> None:
        """Test that cell applies padding correctly"""
        td_dom = self.create_cell_with_text("Content")
        element = TableCellElement(td_dom)

        initial_y = self.layout_engine.current_y
        layout_node = element.layout_with_width(self.layout_engine, 10, 800, 100.0)

        assert layout_node is not None
        # current_y should NOT advance (that's the table row's responsibility)
        assert self.layout_engine.current_y == initial_y
        # But cell height should include padding
        assert layout_node.box.height >= 2 * self.config.PADDING

    def test_table_cell_layout_child_none_result(self) -> None:
        """Test table cell when layout_child_with_width returns None"""
        td_dom = self.create_cell_with_text("Content")
        element = TableCellElement(td_dom)

        # Mock to return None (child layout failed)
        self.layout_engine._layout_child_with_width = Mock(return_value=None)

        layout_node = element.layout_with_width(self.layout_engine, 10, 800, 100.0)

        assert layout_node is not None
        # Should not add None children
        assert len(layout_node.children) == 0

    def test_table_cell_width_zero(self) -> None:
        """Test table cell with zero width"""
        td_dom = self.create_cell_with_text("Content")
        element = TableCellElement(td_dom)

        layout_node = element.layout_with_width(self.layout_engine, 10, 800, 0.0)

        assert layout_node is not None
        assert layout_node.box.width == 0.0

    def test_table_cell_negative_content_width(self) -> None:
        """Test table cell when padding exceeds width"""
        td_dom = self.create_cell_with_text("Content")
        element = TableCellElement(td_dom)

        # Mock to capture content width
        self.layout_engine._layout_child_with_width = Mock(return_value=Mock())

        # Small width that's less than 2 * padding
        small_width = self.config.PADDING * 1.5
        layout_node = element.layout_with_width(
            self.layout_engine, 10, 800, small_width
        )

        assert layout_node is not None
        # Content width should be negative but handled gracefully
        call_args = self.layout_engine._layout_child_with_width.call_args
        content_width = call_args[0][2]
        assert content_width < 0  # Should be negative

    def test_table_cell_different_positions(self) -> None:
        """Test table cell at different positions"""
        positions = [(0, 100.0), (25, 75.0), (50, 150.0)]

        for x, width in positions:
            td_dom = self.create_cell_with_text(f"Content at {x}")
            element = TableCellElement(td_dom)

            layout_node = element.layout_with_width(self.layout_engine, x, 800, width)

            assert layout_node is not None
            assert layout_node.box.x == x
            assert layout_node.box.width == width
