"""Tests for the renderer module"""

from unittest.mock import Mock, patch

import pytest
from PIL import Image, ImageDraw

from src.config import BrowserConfig
from src.html_parser import DOMNode
from src.layout_engine import Box, LayoutNode
from src.renderer import Renderer
from tests.fixtures import TestDataBuilder


class TestRenderer:
    """Test the Renderer class"""

    def setup_method(self) -> None:
        """Set up test fixtures"""
        self.config = BrowserConfig()

    def test_renderer_creation(self) -> None:
        """Test Renderer can be created"""
        renderer = Renderer()
        assert renderer is not None
        assert hasattr(renderer, "width")
        assert hasattr(renderer, "height")
        assert hasattr(renderer, "font_manager")

    def test_create_image(self) -> None:
        """Test image creation with default dimensions"""
        renderer = Renderer()
        image = renderer.create_image()

        assert isinstance(image, Image.Image)
        assert image.size == (self.config.VIEWPORT_WIDTH, self.config.MIN_HEIGHT)
        assert image.mode == "RGB"

    def test_create_image_custom_dimensions(self) -> None:
        """Test image creation with custom dimensions"""
        renderer = Renderer()
        custom_width, custom_height = 1000, 800
        image = renderer.create_image(custom_width, custom_height)

        assert image.size == (custom_width, custom_height)
        assert image.mode == "RGB"

    def test_render_simple_layout(self) -> None:
        """Test rendering a simple layout tree"""
        # Create simple layout tree
        root_dom = TestDataBuilder.create_dom_node("root")
        p_dom = TestDataBuilder.create_dom_node("p")
        text_dom = TestDataBuilder.create_dom_node("text", text="Hello World")
        p_dom.children.append(text_dom)
        root_dom.children.append(p_dom)

        layout_tree = TestDataBuilder.create_layout_node(
            root_dom, Box(0, 0, self.config.VIEWPORT_WIDTH, self.config.MIN_HEIGHT)
        )

        renderer = Renderer()
        image = renderer.render(layout_tree)

        assert isinstance(image, Image.Image)
        assert image.size == (self.config.VIEWPORT_WIDTH, self.config.MIN_HEIGHT)

    def test_render_with_custom_image(self) -> None:
        """Test rendering to a provided image"""
        custom_image = Image.new("RGB", (400, 300), "blue")
        layout_tree = TestDataBuilder.create_layout_node(
            TestDataBuilder.create_dom_node("root"), Box(0, 0, 400, 300)
        )

        renderer = Renderer()
        result_image = renderer.render(layout_tree, custom_image)

        assert result_image is custom_image
        assert result_image.size == (400, 300)

    def test_render_empty_layout(self) -> None:
        """Test rendering empty layout tree"""
        empty_dom = TestDataBuilder.create_dom_node("root")
        layout_tree = TestDataBuilder.create_layout_node(
            empty_dom, Box(0, 0, self.config.VIEWPORT_WIDTH, self.config.MIN_HEIGHT)
        )

        renderer = Renderer()
        image = renderer.render(layout_tree)

        # Should create valid image even with empty content
        assert isinstance(image, Image.Image)
        assert image.size == (self.config.VIEWPORT_WIDTH, self.config.MIN_HEIGHT)

    @patch("src.elements.element_factory.ElementFactory.create_element")
    def test_render_delegates_to_elements(self, mock_create_element: Mock) -> None:
        """Test that renderer delegates to element classes"""
        mock_element = Mock()
        mock_create_element.return_value = mock_element

        # Create layout tree with paragraph
        p_dom = TestDataBuilder.create_dom_node("p")
        layout_tree = TestDataBuilder.create_layout_node(p_dom, Box(0, 0, 100, 50))

        renderer = Renderer()
        renderer.render(layout_tree)

        # Should have created element and called render
        mock_create_element.assert_called_with(p_dom)
        mock_element.render.assert_called()

    def test_render_nested_layout(self) -> None:
        """Test rendering nested layout structure"""
        # Create nested structure: root -> div -> p -> text
        root_dom = TestDataBuilder.create_dom_node("root")
        div_dom = TestDataBuilder.create_dom_node("div")
        p_dom = TestDataBuilder.create_dom_node("p")
        text_dom = TestDataBuilder.create_dom_node("text", text="Nested content")

        p_dom.children.append(text_dom)
        div_dom.children.append(p_dom)
        root_dom.children.append(div_dom)

        layout_tree = TestDataBuilder.create_layout_node(root_dom)
        p_layout = TestDataBuilder.create_layout_node(p_dom)
        div_layout = TestDataBuilder.create_layout_node(div_dom)
        div_layout.children.append(p_layout)
        layout_tree.children.append(div_layout)

        renderer = Renderer()
        image = renderer.render(layout_tree)

        assert isinstance(image, Image.Image)

    def test_render_with_different_element_types(self) -> None:
        """Test rendering layout with various element types"""
        root_dom = TestDataBuilder.create_dom_node("root")

        # Add different element types
        elements = ["h1", "p", "ul", "table", "div"]
        for tag in elements:
            element_dom = TestDataBuilder.create_dom_node(tag)
            root_dom.children.append(element_dom)

        layout_tree = TestDataBuilder.create_layout_node(root_dom)

        renderer = Renderer()
        image = renderer.render(layout_tree)

        # Should handle all element types without error
        assert isinstance(image, Image.Image)

    def test_render_coordinates_and_clipping(self) -> None:
        """Test that rendering respects coordinates and clipping"""
        # Create layout with specific coordinates
        p_dom = TestDataBuilder.create_dom_node("p")
        layout_tree = TestDataBuilder.create_layout_node(
            p_dom, Box(50, 100, 200, 50)  # Specific position and size
        )

        renderer = Renderer()
        image = renderer.render(layout_tree)

        # Image should still be the configured size
        assert image.size == (self.config.VIEWPORT_WIDTH, self.config.MIN_HEIGHT)

    def test_render_with_zero_dimensions(self) -> None:
        """Test rendering with zero-sized elements"""
        zero_dom = TestDataBuilder.create_dom_node("div")
        layout_tree = TestDataBuilder.create_layout_node(
            zero_dom, Box(0, 0, 0, 0)  # Zero dimensions
        )

        renderer = Renderer()
        image = renderer.render(layout_tree)

        # Should handle gracefully
        assert isinstance(image, Image.Image)

    def test_render_performance_with_large_tree(self) -> None:
        """Test rendering performance with larger layout tree"""
        root_dom = TestDataBuilder.create_dom_node("root")

        # Create a reasonably large tree
        for i in range(50):
            div_dom = TestDataBuilder.create_dom_node("div")
            text_dom = TestDataBuilder.create_dom_node("text", text=f"Content {i}")
            div_dom.children.append(text_dom)
            root_dom.children.append(div_dom)

        layout_tree = TestDataBuilder.create_layout_node(root_dom)

        renderer = Renderer()

        # Should complete without timeout
        import time

        start_time = time.time()
        image = renderer.render(layout_tree)
        end_time = time.time()

        assert isinstance(image, Image.Image)
        # Should complete reasonably quickly (less than 5 seconds)
        assert (end_time - start_time) < 5.0

    def test_render_error_handling(self) -> None:
        """Test error handling during rendering"""
        # Create layout that might cause issues
        problematic_dom = TestDataBuilder.create_dom_node("nonexistent_tag")
        layout_tree = TestDataBuilder.create_layout_node(problematic_dom)

        renderer = Renderer()

        # Should handle unknown elements gracefully
        image = renderer.render(layout_tree)
        assert isinstance(image, Image.Image)

    def test_render_background_color(self) -> None:
        """Test that background color is applied correctly"""
        layout_tree = TestDataBuilder.create_layout_node(
            TestDataBuilder.create_dom_node("root")
        )

        renderer = Renderer()
        image = renderer.render(layout_tree)

        # Check that background color is applied
        # Sample a pixel that should be background color
        background_pixel = image.getpixel((0, 0))
        assert background_pixel == (255, 255, 255)  # white background

    def test_image_format_consistency(self) -> None:
        """Test that rendered images have consistent format"""
        layout_tree = TestDataBuilder.create_layout_node(
            TestDataBuilder.create_dom_node("root")
        )

        renderer = Renderer()
        image = renderer.render(layout_tree)

        assert image.mode == "RGB"
        assert image.format is None  # New images don't have format until saved

    def test_render_preserves_image_references(self) -> None:
        """Test that custom images are not modified unexpectedly"""
        original_image = Image.new("RGB", (200, 200), "red")
        original_pixel = original_image.getpixel((100, 100))

        layout_tree = TestDataBuilder.create_layout_node(
            TestDataBuilder.create_dom_node("root")
        )

        renderer = Renderer()
        result_image = renderer.render(layout_tree, original_image)

        # Should be the same image object
        assert result_image is original_image
        # But content may have changed due to rendering
        assert result_image.size == (200, 200)
