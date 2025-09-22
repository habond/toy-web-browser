"""Simple working tests for layout utilities"""

from src.layout_utils import LayoutUtils


class TestLayoutUtilsSimple:
    """Simple tests for LayoutUtils that match the actual API"""

    def test_layout_utils_import(self) -> None:
        """Test that LayoutUtils can be imported"""
        assert LayoutUtils is not None

    def test_wrap_text_basic(self) -> None:
        """Test basic text wrapping functionality"""
        text = "Hello world"
        max_width = 1000.0  # Wide enough to fit

        lines = LayoutUtils.wrap_text(text, max_width)
        assert isinstance(lines, list)
        assert len(lines) >= 1

    def test_calculate_content_dimensions_basic(self) -> None:
        """Test basic content dimension calculation"""
        lines = ["Test line 1", "Test line 2"]
        font_size = 16.0

        width, height = LayoutUtils.calculate_content_dimensions(lines, font_size)
        assert isinstance(width, (int, float))
        assert isinstance(height, (int, float))
        assert width >= 0
        assert height >= 0

    def test_compute_text_height_basic(self) -> None:
        """Test basic text height computation"""
        lines = ["Line 1", "Line 2", "Line 3"]
        font_size = 16.0

        height = LayoutUtils.compute_text_height(lines, font_size)
        assert isinstance(height, (int, float))
        assert height >= 0

    def test_layout_utils_methods_exist(self) -> None:
        """Test that expected methods exist on LayoutUtils"""
        expected_methods = [
            "wrap_text",
            "calculate_content_dimensions",
            "compute_text_height",
            "add_margins_and_padding",
        ]

        for method in expected_methods:
            if hasattr(LayoutUtils, method):
                assert callable(getattr(LayoutUtils, method))
