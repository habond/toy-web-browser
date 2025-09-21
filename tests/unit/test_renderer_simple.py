"""Simple working tests for renderer module"""

from src.renderer import Renderer


class TestRendererSimple:
    """Simple tests for Renderer that match the actual API"""

    def test_renderer_creation(self) -> None:
        """Test Renderer can be created with default parameters"""
        renderer = Renderer()
        assert renderer is not None
        assert hasattr(renderer, "width")
        assert hasattr(renderer, "height")
        assert hasattr(renderer, "bg_color")

    def test_renderer_with_parameters(self) -> None:
        """Test Renderer can be created with custom parameters"""
        renderer = Renderer(width=400, height=300, bg_color="blue")
        assert renderer.width == 400
        assert renderer.height == 300
        assert renderer.bg_color == "blue"

    def test_renderer_has_font_manager(self) -> None:
        """Test that renderer has font manager"""
        renderer = Renderer()
        assert hasattr(renderer, "font_manager")
        assert renderer.font_manager is not None

    def test_renderer_properties(self) -> None:
        """Test renderer properties"""
        renderer = Renderer()

        # Test that properties exist and return reasonable values
        assert hasattr(renderer, "DEFAULT_FONT_SIZE")
        assert hasattr(renderer, "LINE_HEIGHT")

        font_size = renderer.DEFAULT_FONT_SIZE
        line_height = renderer.LINE_HEIGHT

        assert isinstance(font_size, int)
        assert isinstance(line_height, float)
        assert font_size > 0
        assert line_height > 0

    def test_get_font_method(self) -> None:
        """Test the _get_font method"""
        renderer = Renderer()

        # Test that _get_font method exists and works
        font = renderer._get_font()
        assert font is not None

        # Test with parameters
        font_bold = renderer._get_font(size=20, bold=True)
        assert font_bold is not None
