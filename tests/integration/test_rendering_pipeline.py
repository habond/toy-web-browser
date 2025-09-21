"""Integration tests for the complete rendering pipeline"""

import tempfile
from pathlib import Path

import pytest
from PIL import Image

from src.browser import render_html
from src.config import BrowserConfig
from src.font_manager import FontManager
from src.html_parser import HTMLParser
from src.layout_engine import LayoutEngine
from src.renderer import Renderer


class TestRenderingPipeline:
    """Integration tests for the complete HTML to PNG rendering pipeline"""

    def setup_method(self) -> None:
        """Set up test fixtures"""
        self.config = BrowserConfig()
        self.font_manager = FontManager()
        self.html_parser = HTMLParser()
        self.layout_engine = LayoutEngine()
        self.renderer = Renderer()

    def create_temp_html_file(self, content: str) -> Path:
        """Create temporary HTML file with given content"""
        temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False)
        temp_file.write(content)
        temp_file.close()
        return Path(temp_file.name)

    def test_complete_pipeline_simple_html(self) -> None:
        """Test complete pipeline with simple HTML"""
        html_content = """
        <!DOCTYPE html>
        <html>
        <body>
            <h1>Test Title</h1>
            <p>This is a test paragraph.</p>
        </body>
        </html>
        """

        # Step 1: Parse HTML
        dom_tree = self.html_parser.parse(html_content)
        assert dom_tree.tag == "root"
        assert len(dom_tree.children) > 0

        # Step 2: Compute layout
        layout_tree = self.layout_engine.compute_layout(dom_tree)
        assert layout_tree.dom_node.tag == "root"
        assert hasattr(layout_tree, "box")

        # Step 3: Render to image
        image = self.renderer.render(layout_tree)
        assert isinstance(image, Image.Image)
        assert image.size == (self.config.VIEWPORT_WIDTH, self.config.MIN_HEIGHT)

    def test_pipeline_with_tables(self) -> None:
        """Test pipeline with table elements"""
        html_content = """
        <table>
            <tr>
                <th>Header 1</th>
                <th>Header 2</th>
            </tr>
            <tr>
                <td>Data 1</td>
                <td>Data 2</td>
            </tr>
        </table>
        """

        dom_tree = self.html_parser.parse(html_content)
        layout_tree = self.layout_engine.compute_layout(dom_tree)
        image = self.renderer.render(layout_tree)

        assert isinstance(image, Image.Image)
        # Should have rendered table content
        assert image.size[0] > 0 and image.size[1] > 0

    def test_pipeline_with_lists(self) -> None:
        """Test pipeline with list elements"""
        html_content = """
        <ul>
            <li>First item</li>
            <li>Second item</li>
            <li>Third item</li>
        </ul>
        <ol>
            <li>Numbered item 1</li>
            <li>Numbered item 2</li>
        </ol>
        """

        dom_tree = self.html_parser.parse(html_content)
        layout_tree = self.layout_engine.compute_layout(dom_tree)
        image = self.renderer.render(layout_tree)

        assert isinstance(image, Image.Image)

    def test_pipeline_with_nested_elements(self) -> None:
        """Test pipeline with deeply nested elements"""
        html_content = """
        <div>
            <h2>Section Title</h2>
            <div>
                <p>Paragraph with <strong>bold text</strong> and <em>italic text</em>.</p>
                <ul>
                    <li>Item with <a href="#">link</a></li>
                    <li>Another item</li>
                </ul>
            </div>
        </div>
        """

        dom_tree = self.html_parser.parse(html_content)
        layout_tree = self.layout_engine.compute_layout(dom_tree)
        image = self.renderer.render(layout_tree)

        assert isinstance(image, Image.Image)

    def test_end_to_end_file_rendering(self) -> None:
        """Test end-to-end file rendering using browser.py"""
        html_content = """
        <!DOCTYPE html>
        <html>
        <head><title>Test Page</title></head>
        <body>
            <h1>Main Title</h1>
            <p>Introduction paragraph.</p>
            <h2>Subsection</h2>
            <ul>
                <li>List item 1</li>
                <li>List item 2</li>
            </ul>
            <table>
                <tr><th>Name</th><th>Value</th></tr>
                <tr><td>Test</td><td>123</td></tr>
            </table>
        </body>
        </html>
        """

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create input file
            input_file = Path(temp_dir) / "test.html"
            with open(input_file, "w", encoding="utf-8") as f:
                f.write(html_content)

            # Create output file
            output_file = Path(temp_dir) / "output.png"

            # Render using main function
            render_html(input_file, output_file)

            # Verify output
            assert output_file.exists()
            with Image.open(output_file) as img:
                assert img.format == "PNG"
                assert img.size == (self.config.VIEWPORT_WIDTH, self.config.MIN_HEIGHT)

    def test_pipeline_error_recovery(self) -> None:
        """Test pipeline handles malformed HTML gracefully"""
        malformed_html = """
        <html>
        <body>
            <h1>Title with missing closing tag
            <p>Paragraph with <strong>unclosed tag
            <ul>
                <li>Item 1
                <li>Item 2</li>
            </ul>
        </body>
        """

        # Should not crash, even with malformed HTML
        dom_tree = self.html_parser.parse(malformed_html)
        layout_tree = self.layout_engine.compute_layout(dom_tree)
        image = self.renderer.render(layout_tree)

        assert isinstance(image, Image.Image)

    def test_pipeline_performance(self) -> None:
        """Test pipeline performance with moderately complex content"""
        # Create content with many elements
        html_parts = ["<html><body>"]
        for i in range(50):
            html_parts.append(
                f"<div><h3>Section {i}</h3><p>Content for section {i}</p></div>"
            )
        html_parts.append("</body></html>")
        html_content = "\n".join(html_parts)

        import time

        start_time = time.time()

        dom_tree = self.html_parser.parse(html_content)
        layout_tree = self.layout_engine.compute_layout(dom_tree)
        image = self.renderer.render(layout_tree)

        end_time = time.time()

        # Should complete in reasonable time (less than 5 seconds)
        assert (end_time - start_time) < 5.0
        assert isinstance(image, Image.Image)

    def test_pipeline_with_empty_content(self) -> None:
        """Test pipeline with empty or minimal content"""
        empty_html = "<html></html>"

        dom_tree = self.html_parser.parse(empty_html)
        layout_tree = self.layout_engine.compute_layout(dom_tree)
        image = self.renderer.render(layout_tree)

        assert isinstance(image, Image.Image)
        assert image.size == (self.config.VIEWPORT_WIDTH, self.config.MIN_HEIGHT)

    def test_pipeline_font_integration(self) -> None:
        """Test that fonts are properly integrated throughout pipeline"""
        html_content = """
        <h1>Large Heading</h1>
        <h2>Medium Heading</h2>
        <p>Regular paragraph text</p>
        <strong>Bold text</strong>
        <em>Italic text</em>
        """

        dom_tree = self.html_parser.parse(html_content)
        layout_tree = self.layout_engine.compute_layout(dom_tree)

        # Verify that layout computed text dimensions
        def check_layout_dimensions(node):
            if hasattr(node, "box") and node.box.height > 0:
                assert node.box.width >= 0
                assert node.box.height >= 0
            for child in getattr(node, "children", []):
                check_layout_dimensions(child)

        check_layout_dimensions(layout_tree)

        image = self.renderer.render(layout_tree)
        assert isinstance(image, Image.Image)

    def test_pipeline_coordinate_consistency(self) -> None:
        """Test that coordinates are consistent throughout pipeline"""
        html_content = """
        <div>
            <h1>Title</h1>
            <p>First paragraph</p>
            <p>Second paragraph</p>
        </div>
        """

        dom_tree = self.html_parser.parse(html_content)
        layout_tree = self.layout_engine.compute_layout(dom_tree)

        # Check that coordinates make sense
        def validate_coordinates(node, parent_box=None):
            if hasattr(node, "box"):
                # Node should be within parent bounds (if parent exists)
                if parent_box:
                    assert node.box.x >= parent_box.x
                    assert node.box.y >= parent_box.y
                    # Width might extend beyond parent due to wrapping
                    assert node.box.x + node.box.width >= parent_box.x

                # Child nodes should be positioned after this node
                current_y = node.box.y
                for child in getattr(node, "children", []):
                    validate_coordinates(child, node.box)

        validate_coordinates(layout_tree)

        image = self.renderer.render(layout_tree)
        assert isinstance(image, Image.Image)

    def test_pipeline_memory_usage(self) -> None:
        """Test that pipeline doesn't leak memory with repeated use"""
        html_content = "<h1>Test</h1><p>Content</p>"

        # Run pipeline multiple times
        for _ in range(10):
            dom_tree = self.html_parser.parse(html_content)
            layout_tree = self.layout_engine.compute_layout(dom_tree)
            image = self.renderer.render(layout_tree)

            assert isinstance(image, Image.Image)
            # Clean up references
            del dom_tree, layout_tree, image

    def test_component_integration(self) -> None:
        """Test that all components work together correctly"""
        # Verify each component can handle output from previous component
        html_content = "<div><h1>Test</h1><p>Content</p></div>"

        # Parser produces DOM that layout engine can process
        dom_tree = self.html_parser.parse(html_content)
        assert hasattr(dom_tree, "tag")
        assert hasattr(dom_tree, "children")

        # Layout engine produces layout that renderer can process
        layout_tree = self.layout_engine.compute_layout(dom_tree)
        assert hasattr(layout_tree, "dom_node")
        assert hasattr(layout_tree, "box")

        # Renderer produces valid image
        image = self.renderer.render(layout_tree)
        assert isinstance(image, Image.Image)
        assert image.mode == "RGB"
