"""Tests for the TableRowElement class"""

from unittest.mock import Mock, patch

from src.config import BrowserConfig
from src.elements.table.table_row_element import TableRowElement
from src.html_parser import DOMNode
from src.layout_engine import LayoutEngine
from tests.fixtures.test_utils import TestDataBuilder


class TestTableRowElement:
    """Test the TableRowElement class"""

    def setup_method(self) -> None:
        """Set up test fixtures"""
        self.config = BrowserConfig()
        self.layout_engine = LayoutEngine()

    def create_row_with_cells(
        self, cell_data: list[str], cell_tag: str = "td"
    ) -> DOMNode:
        """Create table row DOM with cells"""
        tr_dom = DOMNode("tr")

        for cell_text in cell_data:
            cell_dom = DOMNode(cell_tag)
            text_dom = DOMNode("text", text=cell_text)
            cell_dom.add_child(text_dom)
            tr_dom.add_child(cell_dom)

        return tr_dom

    def test_table_row_element_creation(self) -> None:
        """Test TableRowElement can be created"""
        tr_dom = DOMNode("tr")
        element = TableRowElement(tr_dom)

        assert element is not None
        assert element.dom_node == tr_dom

    def test_table_row_basic_layout(self) -> None:
        """Test basic table row layout"""
        tr_dom = self.create_row_with_cells(["Cell 1", "Cell 2"])
        element = TableRowElement(tr_dom)

        initial_y = self.layout_engine.current_y
        layout_node = element.layout(self.layout_engine, 10, 800)

        assert layout_node is not None
        assert layout_node.dom_node == tr_dom
        assert layout_node.box.x == 10
        assert layout_node.box.y == initial_y

    def test_table_row_layout_with_table_params(self) -> None:
        """Test table row layout with specific table parameters"""
        tr_dom = self.create_row_with_cells(["Cell A", "Cell B"])
        element = TableRowElement(tr_dom)

        initial_y = self.layout_engine.current_y
        col_width = 150.0
        num_cols = 2

        layout_node = element.layout_with_table_params(
            self.layout_engine, 10, 800, col_width, num_cols
        )

        assert layout_node is not None
        assert layout_node.box.x == 10
        assert layout_node.box.y == initial_y
        assert layout_node.box.width == 800 - 2 * 10  # viewport_width - 2 * x

    def test_table_row_empty_row(self) -> None:
        """Test table row layout with no cells"""
        tr_dom = DOMNode("tr")  # Empty row
        element = TableRowElement(tr_dom)

        layout_node = element.layout_with_table_params(
            self.layout_engine, 10, 800, 100.0, 2
        )

        assert layout_node is not None
        assert len(layout_node.children) == 0
        assert layout_node.box.height == 0  # No cells means no height

    def test_table_row_single_cell(self) -> None:
        """Test table row with single cell"""
        tr_dom = self.create_row_with_cells(["Single cell"])
        element = TableRowElement(tr_dom)

        layout_node = element.layout_with_table_params(
            self.layout_engine, 15, 600, 200.0, 1
        )

        assert layout_node is not None
        assert layout_node.box.x == 15
        assert layout_node.box.width == 600 - 2 * 15

    def test_table_row_multiple_cells(self) -> None:
        """Test table row with multiple cells"""
        tr_dom = self.create_row_with_cells(["Cell 1", "Cell 2", "Cell 3"])
        element = TableRowElement(tr_dom)

        layout_node = element.layout_with_table_params(
            self.layout_engine, 10, 800, 100.0, 3
        )

        assert layout_node is not None
        # Should process cells up to num_cols
        # Note: actual children depend on whether TableCellElement is mocked

    def test_table_row_filters_non_cell_children(self) -> None:
        """Test that table row only processes td and th elements"""
        tr_dom = DOMNode("tr")
        td_dom = DOMNode("td")
        th_dom = DOMNode("th")
        span_dom = DOMNode("span")  # Non-cell element
        div_dom = DOMNode("div")  # Non-cell element

        tr_dom.add_child(td_dom)
        tr_dom.add_child(th_dom)
        tr_dom.add_child(span_dom)
        tr_dom.add_child(div_dom)

        element = TableRowElement(tr_dom)

        # Mock the cell layout to verify only td/th are processed
        mock_cell1 = Mock()
        mock_cell1.box.height = 30
        mock_cell2 = Mock()
        mock_cell2.box.height = 30
        mock_cell_layouts = [mock_cell1, mock_cell2]
        element._layout_table_cell = Mock(side_effect=mock_cell_layouts)

        layout_node = element.layout_with_table_params(
            self.layout_engine, 10, 800, 150.0, 4
        )

        assert layout_node is not None
        # Should only call _layout_table_cell for td and th elements
        assert element._layout_table_cell.call_count == 2

    def test_table_row_respects_column_limit(self) -> None:
        """Test that table row respects num_cols limit"""
        tr_dom = self.create_row_with_cells(["Cell 1", "Cell 2", "Cell 3", "Cell 4"])
        element = TableRowElement(tr_dom)

        # Mock cell layout
        mock_cell = Mock()
        mock_cell.box.height = 30
        element._layout_table_cell = Mock(return_value=mock_cell)

        layout_node = element.layout_with_table_params(
            self.layout_engine, 10, 800, 100.0, 2  # Only 2 columns
        )

        assert layout_node is not None
        # Should only process first 2 cells
        assert element._layout_table_cell.call_count == 2

    def test_table_row_height_calculation(self) -> None:
        """Test table row height calculation from cell heights"""
        tr_dom = self.create_row_with_cells(["Cell 1", "Cell 2"])
        element = TableRowElement(tr_dom)

        # Mock cell layouts with different heights
        mock_cell1 = Mock()
        mock_cell1.box.height = 30
        mock_cell2 = Mock()
        mock_cell2.box.height = 50  # Taller cell

        element._layout_table_cell = Mock(side_effect=[mock_cell1, mock_cell2])

        initial_y = self.layout_engine.current_y
        layout_node = element.layout_with_table_params(
            self.layout_engine, 10, 800, 150.0, 2
        )

        assert layout_node is not None
        # Row height should be max of cell heights
        assert layout_node.box.height == 50
        # current_y should advance by the max height
        assert self.layout_engine.current_y == initial_y + 50

    @patch("src.elements.element_factory.ElementFactory.create_element")
    def test_table_row_layout_cell_method(self, mock_create_element):
        """Test the _layout_table_cell method"""
        from src.elements.table.table_cell_element import TableCellElement

        tr_dom = DOMNode("tr")
        element = TableRowElement(tr_dom)

        td_dom = DOMNode("td")
        mock_cell_element = Mock(spec=TableCellElement)
        mock_layout_result = Mock()
        mock_cell_element.layout_with_width.return_value = mock_layout_result
        mock_create_element.return_value = mock_cell_element

        result = element._layout_table_cell(self.layout_engine, td_dom, 20, 800, 120.0)

        assert result == mock_layout_result
        mock_create_element.assert_called_once_with(td_dom)
        mock_cell_element.layout_with_width.assert_called_once_with(
            self.layout_engine, 20, 800, 120.0
        )

    @patch("src.elements.element_factory.ElementFactory.create_element")
    def test_table_row_layout_cell_method_none_element(self, mock_create_element):
        """Test _layout_table_cell when ElementFactory returns None"""
        tr_dom = DOMNode("tr")
        element = TableRowElement(tr_dom)

        td_dom = DOMNode("td")
        mock_create_element.return_value = None

        result = element._layout_table_cell(self.layout_engine, td_dom, 20, 800, 120.0)

        assert result is None

    @patch("src.elements.element_factory.ElementFactory.create_element")
    def test_table_row_layout_cell_method_wrong_element_type(self, mock_create_element):
        """Test _layout_table_cell when element is not TableCellElement"""
        tr_dom = DOMNode("tr")
        element = TableRowElement(tr_dom)

        td_dom = DOMNode("td")
        mock_element = Mock()  # Not a TableCellElement
        mock_create_element.return_value = mock_element

        result = element._layout_table_cell(self.layout_engine, td_dom, 20, 800, 120.0)

        assert result is None

    def test_table_row_render(self) -> None:
        """Test table row rendering"""
        tr_dom = DOMNode("tr")
        element = TableRowElement(tr_dom)

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

    def test_table_row_render_empty_row(self) -> None:
        """Test table row rendering with no children"""
        tr_dom = DOMNode("tr")
        element = TableRowElement(tr_dom)

        layout_node = TestDataBuilder.create_layout_node(tr_dom)

        mock_renderer = Mock()
        mock_draw = Mock()

        element.render(mock_draw, layout_node, mock_renderer)

        # Should not call renderer for any children
        mock_renderer._render_node.assert_not_called()

    def test_table_row_with_header_cells(self) -> None:
        """Test table row with th (header) cells"""
        tr_dom = self.create_row_with_cells(["Header 1", "Header 2"], cell_tag="th")
        element = TableRowElement(tr_dom)

        # Mock cell layout
        mock_cell = Mock()
        mock_cell.box.height = 30
        element._layout_table_cell = Mock(return_value=mock_cell)

        layout_node = element.layout_with_table_params(
            self.layout_engine, 10, 800, 150.0, 2
        )

        assert layout_node is not None
        # Should process th cells like td cells
        assert element._layout_table_cell.call_count == 2

    def test_table_row_with_mixed_cell_types(self) -> None:
        """Test table row with mixed td and th cells"""
        tr_dom = DOMNode("tr")
        th_dom = DOMNode("th")
        td_dom = DOMNode("td")
        tr_dom.add_child(th_dom)
        tr_dom.add_child(td_dom)

        element = TableRowElement(tr_dom)

        # Mock cell layout
        mock_cell = Mock()
        mock_cell.box.height = 30
        element._layout_table_cell = Mock(return_value=mock_cell)

        layout_node = element.layout_with_table_params(
            self.layout_engine, 10, 800, 150.0, 2
        )

        assert layout_node is not None
        # Should process both th and td cells
        assert element._layout_table_cell.call_count == 2

    def test_table_row_width_calculation(self) -> None:
        """Test table row width calculation"""
        tr_dom = self.create_row_with_cells(["Cell"])
        element = TableRowElement(tr_dom)

        x = 25
        viewport_width = 600
        layout_node = element.layout_with_table_params(
            self.layout_engine, x, viewport_width, 100.0, 1
        )

        assert layout_node is not None
        # Width should be viewport_width - 2 * x
        expected_width = viewport_width - 2 * x
        assert layout_node.box.width == expected_width

    def test_table_row_position_setting(self) -> None:
        """Test table row position is set correctly"""
        tr_dom = DOMNode("tr")
        element = TableRowElement(tr_dom)

        x = 30
        initial_y = self.layout_engine.current_y
        layout_node = element.layout_with_table_params(
            self.layout_engine, x, 800, 100.0, 2
        )

        assert layout_node is not None
        assert layout_node.box.x == x
        assert layout_node.box.y == initial_y

    def test_table_row_cell_positioning(self) -> None:
        """Test that cells are positioned correctly within row"""
        tr_dom = self.create_row_with_cells(["A", "B", "C"])
        element = TableRowElement(tr_dom)

        # Mock cell layouts to capture positions
        captured_positions = []

        def mock_layout_cell(layout_engine, dom_node, x, viewport_width, width):
            captured_positions.append(x)
            mock_cell = Mock()
            mock_cell.box.height = 30
            return mock_cell

        element._layout_table_cell = mock_layout_cell

        x = 20
        col_width = 100.0
        layout_node = element.layout_with_table_params(
            self.layout_engine, x, 800, col_width, 3
        )

        assert layout_node is not None
        # Cells should be positioned at x, x+col_width, x+2*col_width
        expected_positions = [20, 120, 220]
        assert captured_positions == expected_positions

    def test_table_row_no_height_for_empty_row(self) -> None:
        """Test that empty row has no height"""
        tr_dom = DOMNode("tr")  # No cells
        element = TableRowElement(tr_dom)

        initial_y = self.layout_engine.current_y
        layout_node = element.layout_with_table_params(
            self.layout_engine, 10, 800, 100.0, 2
        )

        assert layout_node is not None
        assert layout_node.box.height == 0
        # current_y should not advance
        assert self.layout_engine.current_y == initial_y

    def test_table_row_delegates_to_layout_with_table_params(self) -> None:
        """Test that standard layout method delegates to layout_with_table_params"""
        tr_dom = DOMNode("tr")
        element = TableRowElement(tr_dom)

        # Mock the specific method
        element.layout_with_table_params = Mock(return_value=Mock())

        result = element.layout(self.layout_engine, 10, 800)

        assert result is not None
        # Should have called layout_with_table_params with default parameters
        element.layout_with_table_params.assert_called_once_with(
            self.layout_engine, 10, 800, 0, 0
        )
