"""Tests for the TableElement class"""

from unittest.mock import Mock, patch

from src.config import BrowserConfig
from src.elements.table.table_element import TableElement
from src.html_parser import DOMNode
from src.layout_engine import LayoutEngine
from tests.fixtures.test_utils import TestDataBuilder


class TestTableElement:
    """Test the TableElement class"""

    def setup_method(self) -> None:
        """Set up test fixtures"""
        self.config = BrowserConfig()
        self.layout_engine = LayoutEngine()

    def create_table_with_rows(self, cell_data: list[list[str]]) -> DOMNode:
        """Create table DOM with rows"""
        table_dom = DOMNode("table")

        for row_data in cell_data:
            tr_dom = DOMNode("tr")
            for cell_text in row_data:
                td_dom = DOMNode("td")
                text_dom = DOMNode("text", text=cell_text)
                td_dom.add_child(text_dom)
                tr_dom.add_child(td_dom)
            table_dom.add_child(tr_dom)

        return table_dom

    def test_table_element_creation(self) -> None:
        """Test TableElement can be created"""
        table_dom = DOMNode("table")
        element = TableElement(table_dom)

        assert element is not None
        assert element.dom_node == table_dom

    def test_table_element_basic_layout(self) -> None:
        """Test basic table layout"""
        table_dom = self.create_table_with_rows(
            [["Cell 1", "Cell 2"], ["Cell 3", "Cell 4"]]
        )

        element = TableElement(table_dom)
        initial_y = self.layout_engine.current_y

        layout_node = element.layout(self.layout_engine, 10, 800)

        assert layout_node is not None
        assert layout_node.dom_node == table_dom
        assert hasattr(layout_node, "box")
        assert layout_node.box.x == 10
        assert layout_node.box.y == initial_y

        # Should have increased current_y (margins + content)
        assert self.layout_engine.current_y > initial_y

    def test_table_element_empty_table(self) -> None:
        """Test table layout with empty table"""
        table_dom = DOMNode("table")  # No rows
        element = TableElement(table_dom)

        layout_node = element.layout(self.layout_engine, 10, 800)

        assert layout_node is not None
        assert len(layout_node.children) == 0
        # Should still have some height from margins
        assert layout_node.box.height >= 0

    def test_table_element_single_cell(self) -> None:
        """Test table with single cell"""
        table_dom = self.create_table_with_rows([["Single cell"]])
        element = TableElement(table_dom)

        layout_node = element.layout(self.layout_engine, 15, 600)

        assert layout_node is not None
        assert layout_node.box.x == 15
        assert layout_node.box.width == 600 - 2 * 15  # viewport_width - 2 * x

    @patch("src.elements.table.table_calculator.TableCalculator.get_table_rows")
    @patch(
        "src.elements.table.table_calculator.TableCalculator.calculate_column_widths"
    )
    def test_table_uses_calculator(self, mock_calc_widths, mock_get_rows):
        """Test that table layout uses TableCalculator"""
        # Mock the calculator responses
        mock_rows = [Mock(), Mock()]
        mock_get_rows.return_value = mock_rows
        mock_calc_widths.return_value = (100.0, 2)

        table_dom = self.create_table_with_rows([["A", "B"]])
        element = TableElement(table_dom)

        layout_node = element.layout(self.layout_engine, 10, 800)

        assert layout_node is not None
        # Should have called the calculator methods
        mock_get_rows.assert_called_once_with(table_dom)
        mock_calc_widths.assert_called_once_with(mock_rows, 800, 10)

    @patch("src.elements.table.table_calculator.TableCalculator.get_table_rows")
    @patch(
        "src.elements.table.table_calculator.TableCalculator.calculate_column_widths"
    )
    def test_table_with_no_columns(self, mock_calc_widths, mock_get_rows):
        """Test table when calculator returns no columns"""
        mock_get_rows.return_value = [Mock()]
        mock_calc_widths.return_value = (0.0, 0)  # No columns

        table_dom = self.create_table_with_rows([["A"]])
        element = TableElement(table_dom)

        layout_node = element.layout(self.layout_engine, 10, 800)

        assert layout_node is not None
        assert len(layout_node.children) == 0  # No rows should be added

    @patch("src.elements.element_factory.ElementFactory.create_element")
    def test_table_layout_row_method(self, mock_create_element):
        """Test the _layout_table_row method"""
        from src.elements.table.table_row_element import TableRowElement

        table_dom = DOMNode("table")
        element = TableElement(table_dom)

        tr_dom = DOMNode("tr")
        mock_row_element = Mock(spec=TableRowElement)
        mock_layout_result = Mock()
        mock_row_element.layout_with_table_params.return_value = mock_layout_result
        mock_create_element.return_value = mock_row_element

        result = element._layout_table_row(
            self.layout_engine, tr_dom, 10, 800, 150.0, 2
        )

        assert result == mock_layout_result
        mock_create_element.assert_called_once_with(tr_dom)
        mock_row_element.layout_with_table_params.assert_called_once_with(
            self.layout_engine, 10, 800, 150.0, 2
        )

    @patch("src.elements.element_factory.ElementFactory.create_element")
    def test_table_layout_row_method_none_element(self, mock_create_element):
        """Test _layout_table_row when ElementFactory returns None"""
        table_dom = DOMNode("table")
        element = TableElement(table_dom)

        tr_dom = DOMNode("tr")
        mock_create_element.return_value = None

        result = element._layout_table_row(
            self.layout_engine, tr_dom, 10, 800, 150.0, 2
        )

        assert result is None

    @patch("src.elements.element_factory.ElementFactory.create_element")
    def test_table_layout_row_method_wrong_element_type(self, mock_create_element):
        """Test _layout_table_row when element is not TableRowElement"""
        table_dom = DOMNode("table")
        element = TableElement(table_dom)

        tr_dom = DOMNode("tr")
        mock_element = Mock()  # Not a TableRowElement
        mock_create_element.return_value = mock_element

        result = element._layout_table_row(
            self.layout_engine, tr_dom, 10, 800, 150.0, 2
        )

        assert result is None

    def test_table_element_render(self) -> None:
        """Test table element rendering"""
        table_dom = DOMNode("table")
        element = TableElement(table_dom)

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

    def test_table_render_grid_basic(self) -> None:
        """Test table grid rendering"""
        table_dom = DOMNode("table")
        element = TableElement(table_dom)

        layout_node = TestDataBuilder.create_layout_node(table_dom)
        layout_node.box.x = 10
        layout_node.box.y = 20
        layout_node.box.width = 200
        layout_node.box.height = 100

        # Create mock row with cells
        row_dom = DOMNode("tr")
        row_layout = TestDataBuilder.create_layout_node(row_dom)
        row_layout.box.x = 10
        row_layout.box.y = 20
        row_layout.box.width = 200
        row_layout.box.height = 50

        cell1_dom = DOMNode("td")
        cell1_layout = TestDataBuilder.create_layout_node(cell1_dom)
        cell1_layout.box.x = 10
        cell1_layout.box.y = 20
        cell1_layout.box.width = 100
        cell1_layout.box.height = 50

        cell2_dom = DOMNode("td")
        cell2_layout = TestDataBuilder.create_layout_node(cell2_dom)
        cell2_layout.box.x = 110
        cell2_layout.box.y = 20
        cell2_layout.box.width = 100
        cell2_layout.box.height = 50

        row_layout.add_child(cell1_layout)
        row_layout.add_child(cell2_layout)
        layout_node.add_child(row_layout)

        mock_draw = Mock()
        mock_renderer = Mock()

        element.render(mock_draw, layout_node, mock_renderer)

        # Should have drawn lines for the grid
        assert mock_draw.line.call_count > 0

    def test_table_render_grid_no_rows(self) -> None:
        """Test table grid rendering with no rows"""
        table_dom = DOMNode("table")
        element = TableElement(table_dom)

        layout_node = TestDataBuilder.create_layout_node(table_dom)

        mock_draw = Mock()
        mock_renderer = Mock()

        element._render_table_grid(mock_draw, layout_node, mock_renderer)

        # Should not draw any lines
        mock_draw.line.assert_not_called()

    def test_table_render_grid_empty_row(self) -> None:
        """Test table grid rendering with empty row"""
        table_dom = DOMNode("table")
        element = TableElement(table_dom)

        layout_node = TestDataBuilder.create_layout_node(table_dom)
        layout_node.box.x = 10
        layout_node.box.y = 20
        layout_node.box.width = 200
        layout_node.box.height = 100

        # Create row with no cells
        row_dom = DOMNode("tr")
        row_layout = TestDataBuilder.create_layout_node(row_dom)
        layout_node.add_child(row_layout)

        mock_draw = Mock()
        mock_renderer = Mock()

        element._render_table_grid(mock_draw, layout_node, mock_renderer)

        # Should draw horizontal lines but no vertical lines
        assert mock_draw.line.call_count > 0

    def test_table_margin_handling(self) -> None:
        """Test that table adds appropriate margins"""
        table_dom = self.create_table_with_rows(
            [["Cell 1"]]
        )  # Add content so margins are applied
        element = TableElement(table_dom)

        initial_y = self.layout_engine.current_y
        layout_node = element.layout(self.layout_engine, 10, 800)

        assert layout_node is not None
        # Should have added margins before and after
        expected_margin_total = self.layout_engine.MARGIN * 2
        assert self.layout_engine.current_y >= initial_y + expected_margin_total

    def test_table_width_calculation(self) -> None:
        """Test table width calculation"""
        table_dom = self.create_table_with_rows([["A", "B"]])
        element = TableElement(table_dom)

        x = 25
        viewport_width = 600
        layout_node = element.layout(self.layout_engine, x, viewport_width)

        assert layout_node is not None
        # Width should be viewport_width - 2 * x
        expected_width = viewport_width - 2 * x
        assert layout_node.box.width == expected_width

    def test_table_height_calculation(self) -> None:
        """Test table height calculation"""
        table_dom = self.create_table_with_rows([["Row 1"], ["Row 2"]])
        element = TableElement(table_dom)

        initial_y = self.layout_engine.current_y
        layout_node = element.layout(self.layout_engine, 10, 800)

        assert layout_node is not None
        # Height should be the difference in current_y
        expected_height = self.layout_engine.current_y - initial_y
        assert layout_node.box.height == expected_height

    def test_table_position_setting(self) -> None:
        """Test table position is set correctly"""
        table_dom = DOMNode("table")
        element = TableElement(table_dom)

        x = 30
        initial_y = self.layout_engine.current_y
        layout_node = element.layout(self.layout_engine, x, 800)

        assert layout_node is not None
        assert layout_node.box.x == x
        assert layout_node.box.y == initial_y

    @patch("src.elements.table.table_calculator.TableCalculator.get_table_rows")
    def test_table_with_mixed_row_children(self, mock_get_rows):
        """Test table with non-row children mixed in"""
        # TableCalculator.get_table_rows should filter out non-row children
        mock_get_rows.return_value = []  # No valid rows found

        table_dom = DOMNode("table")
        caption_dom = DOMNode("caption")
        div_dom = DOMNode("div")
        table_dom.add_child(caption_dom)
        table_dom.add_child(div_dom)

        element = TableElement(table_dom)
        layout_node = element.layout(self.layout_engine, 10, 800)

        assert layout_node is not None
        mock_get_rows.assert_called_once_with(table_dom)
        # Should have no children since no valid rows
        assert len(layout_node.children) == 0
