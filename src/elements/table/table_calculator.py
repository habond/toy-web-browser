"""
Table width calculation utilities
"""

from typing import List

from ...config import config
from ...html_parser import DOMNode


class TableCalculator:
    """Handles table layout calculations"""

    @staticmethod
    def calculate_column_widths(
        rows: List[DOMNode], viewport_width: int, x: float
    ) -> tuple[float, int]:
        """Calculate column widths and count for table"""
        if not rows:
            return 0.0, 0

        # Calculate number of columns from the first row
        first_row = rows[0]
        num_cols = len(
            [cell for cell in first_row.children if cell.tag in ["td", "th"]]
        )

        if num_cols == 0:
            return 0.0, 0

        # Simple equal column width distribution
        table_width = viewport_width - 2 * x - 2 * config.PADDING
        col_width = table_width / num_cols

        return col_width, num_cols

    @staticmethod
    def get_table_rows(dom_node: DOMNode) -> List[DOMNode]:
        """Extract table rows from table node"""
        return [child for child in dom_node.children if child.tag == "tr"]
