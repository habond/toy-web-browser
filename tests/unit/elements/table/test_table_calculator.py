"""Tests for the table calculator module"""

from src.config import BrowserConfig
from src.elements.table.table_calculator import TableCalculator
from src.html_parser import DOMNode


class TestTableCalculator:
    """Test the TableCalculator class"""

    def setup_method(self) -> None:
        """Set up test fixtures"""
        self.config = BrowserConfig()

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

    def test_get_table_rows_basic(self) -> None:
        """Test getting table rows from table DOM"""
        table_dom = self.create_table_with_rows(
            [["Cell 1", "Cell 2"], ["Cell 3", "Cell 4"]]
        )

        rows = TableCalculator.get_table_rows(table_dom)

        assert len(rows) == 2
        assert all(row.tag == "tr" for row in rows)

    def test_get_table_rows_empty_table(self) -> None:
        """Test getting rows from empty table"""
        table_dom = DOMNode("table")
        rows = TableCalculator.get_table_rows(table_dom)

        assert len(rows) == 0

    def test_get_table_rows_with_non_row_children(self) -> None:
        """Test getting rows when table has non-row children"""
        table_dom = DOMNode("table")
        caption_dom = DOMNode("caption")
        tr_dom = DOMNode("tr")
        div_dom = DOMNode("div")  # Non-row element

        table_dom.add_child(caption_dom)
        table_dom.add_child(tr_dom)
        table_dom.add_child(div_dom)

        rows = TableCalculator.get_table_rows(table_dom)

        assert len(rows) == 1
        assert rows[0].tag == "tr"

    def test_calculate_column_widths_equal_distribution(self) -> None:
        """Test equal column width distribution"""
        table_dom = self.create_table_with_rows(
            [["Cell 1", "Cell 2"], ["Cell 3", "Cell 4"]]
        )
        rows = TableCalculator.get_table_rows(table_dom)

        viewport_width = 800
        x = 10
        col_width, num_cols = TableCalculator.calculate_column_widths(
            rows, viewport_width, x
        )

        assert num_cols == 2
        # Expected: (viewport_width - 2*x - 2*PADDING) / num_cols
        expected_table_width = viewport_width - 2 * x - 2 * self.config.PADDING
        expected_col_width = expected_table_width / num_cols
        assert col_width == expected_col_width

    def test_calculate_column_widths_single_column(self) -> None:
        """Test calculation with single column table"""
        table_dom = self.create_table_with_rows([["Single cell"], ["Another cell"]])
        rows = TableCalculator.get_table_rows(table_dom)

        viewport_width = 600
        x = 20
        col_width, num_cols = TableCalculator.calculate_column_widths(
            rows, viewport_width, x
        )

        assert num_cols == 1
        expected_table_width = viewport_width - 2 * x - 2 * self.config.PADDING
        assert col_width == expected_table_width

    def test_calculate_column_widths_empty_rows(self) -> None:
        """Test calculation with empty rows list"""
        rows = []

        col_width, num_cols = TableCalculator.calculate_column_widths(rows, 800, 10)

        assert col_width == 0.0
        assert num_cols == 0

    def test_calculate_column_widths_irregular_table(self) -> None:
        """Test calculation with irregular table (different row lengths)"""
        # Create table where first row determines column count
        table_dom = self.create_table_with_rows(
            [
                ["Cell 1", "Cell 2", "Cell 3"],  # 3 columns
                ["Cell 4", "Cell 5"],  # Only 2 cells in this row
                ["Cell 6"],  # Only 1 cell in this row
            ]
        )
        rows = TableCalculator.get_table_rows(table_dom)

        col_width, num_cols = TableCalculator.calculate_column_widths(rows, 900, 15)

        # Should use first row to determine column count
        assert num_cols == 3
        expected_table_width = 900 - 2 * 15 - 2 * self.config.PADDING
        expected_col_width = expected_table_width / 3
        assert col_width == expected_col_width

    def test_calculate_column_widths_with_th_cells(self) -> None:
        """Test calculation with header cells (th)"""
        table_dom = DOMNode("table")
        tr_dom = DOMNode("tr")

        # Mix of th and td cells
        th1_dom = DOMNode("th")
        th1_dom.add_child(DOMNode("text", text="Header 1"))
        th2_dom = DOMNode("th")
        th2_dom.add_child(DOMNode("text", text="Header 2"))

        tr_dom.add_child(th1_dom)
        tr_dom.add_child(th2_dom)
        table_dom.add_child(tr_dom)

        rows = TableCalculator.get_table_rows(table_dom)
        col_width, num_cols = TableCalculator.calculate_column_widths(rows, 800, 10)

        assert num_cols == 2  # th cells should count as columns

    def test_calculate_column_widths_with_mixed_cell_types(self) -> None:
        """Test calculation with mixed td and th cells"""
        table_dom = DOMNode("table")
        tr_dom = DOMNode("tr")

        th_dom = DOMNode("th")
        th_dom.add_child(DOMNode("text", text="Header"))
        td_dom = DOMNode("td")
        td_dom.add_child(DOMNode("text", text="Data"))
        span_dom = DOMNode("span")  # Non-cell element
        span_dom.add_child(DOMNode("text", text="Not a cell"))

        tr_dom.add_child(th_dom)
        tr_dom.add_child(td_dom)
        tr_dom.add_child(span_dom)  # This should be ignored
        table_dom.add_child(tr_dom)

        rows = TableCalculator.get_table_rows(table_dom)
        col_width, num_cols = TableCalculator.calculate_column_widths(rows, 800, 10)

        assert num_cols == 2  # Only th and td should count

    def test_calculate_column_widths_row_with_no_cells(self) -> None:
        """Test calculation when first row has no cells"""
        table_dom = DOMNode("table")
        tr_dom = DOMNode("tr")
        span_dom = DOMNode("span")  # Non-cell element
        tr_dom.add_child(span_dom)
        table_dom.add_child(tr_dom)

        rows = TableCalculator.get_table_rows(table_dom)
        col_width, num_cols = TableCalculator.calculate_column_widths(rows, 800, 10)

        assert num_cols == 0
        assert col_width == 0.0

    def test_calculate_column_widths_with_narrow_viewport(self) -> None:
        """Test calculation with narrow viewport"""
        table_dom = self.create_table_with_rows([["A", "B"]])
        rows = TableCalculator.get_table_rows(table_dom)

        viewport_width = 100
        x = 5
        col_width, num_cols = TableCalculator.calculate_column_widths(
            rows, viewport_width, x
        )

        assert num_cols == 2
        expected_table_width = viewport_width - 2 * x - 2 * self.config.PADDING
        expected_col_width = expected_table_width / 2
        assert col_width == expected_col_width

    def test_calculate_column_widths_with_large_margins(self) -> None:
        """Test calculation when margins consume most of viewport width"""
        table_dom = self.create_table_with_rows([["A"]])
        rows = TableCalculator.get_table_rows(table_dom)

        viewport_width = 100
        x = 40  # Large margin
        col_width, num_cols = TableCalculator.calculate_column_widths(
            rows, viewport_width, x
        )

        assert num_cols == 1
        # Even if result is small or negative, should still calculate
        expected_table_width = viewport_width - 2 * x - 2 * self.config.PADDING
        assert col_width == expected_table_width

    def test_calculate_column_widths_return_type(self) -> None:
        """Test that return type is correct"""
        table_dom = self.create_table_with_rows([["Cell"]])
        rows = TableCalculator.get_table_rows(table_dom)

        result = TableCalculator.calculate_column_widths(rows, 800, 10)

        assert isinstance(result, tuple)
        assert len(result) == 2
        col_width, num_cols = result
        assert isinstance(col_width, float)
        assert isinstance(num_cols, int)

    def test_table_calculator_integration_with_config(self) -> None:
        """Test that TableCalculator uses config properly"""
        table_dom = self.create_table_with_rows([["A", "B"]])
        rows = TableCalculator.get_table_rows(table_dom)

        viewport_width = 800
        x = 10

        # The calculation should use config.PADDING
        col_width, num_cols = TableCalculator.calculate_column_widths(
            rows, viewport_width, x
        )

        # Verify the calculation uses the config padding
        expected_table_width = viewport_width - 2 * x - 2 * self.config.PADDING
        expected_col_width = expected_table_width / num_cols
        assert col_width == expected_col_width
