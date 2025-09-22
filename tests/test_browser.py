"""Tests for the toy web browser rendering functionality"""

import shutil
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from src.browser import render_html


class TestBrowser(unittest.TestCase):
    """Test the main browser functionality"""

    def setUp(self) -> None:
        """Set up test fixtures"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.examples_dir = Path(__file__).parent.parent / "examples"
        self.output_dir = self.test_dir / "output"
        self.output_dir.mkdir(exist_ok=True)

    def tearDown(self) -> None:
        """Clean up test fixtures"""
        shutil.rmtree(self.test_dir)

    def test_render_basic_structure_html(self) -> None:
        """Test rendering the basic structure example HTML file"""
        input_file = self.examples_dir / "01_basic_structure.html"
        output_file = self.output_dir / "basic_structure_output.png"

        # Render the HTML
        render_html(input_file, output_file)

        # Check that output file was created
        self.assertTrue(output_file.exists(), "Output PNG file should be created")

        # Check that it's a valid PNG image
        with Image.open(output_file) as img:
            self.assertEqual(img.format, "PNG", "Output should be a PNG image")
            self.assertEqual(img.size[0], 800, "Image width should be 800px")
            self.assertGreaterEqual(
                img.size[1], 600, "Image height should be at least 600px"
            )

    def test_render_text_formatting_html(self) -> None:
        """Test rendering the text formatting example HTML file"""
        input_file = self.examples_dir / "02_text_formatting.html"
        output_file = self.output_dir / "text_formatting_output.png"

        # Render the HTML
        render_html(input_file, output_file)

        # Check that output file was created
        self.assertTrue(output_file.exists(), "Output PNG file should be created")

        # Check that it's a valid PNG image
        with Image.open(output_file) as img:
            self.assertEqual(img.format, "PNG", "Output should be a PNG image")
            self.assertEqual(img.size[0], 800, "Image width should be 800px")
            self.assertGreaterEqual(
                img.size[1], 600, "Image height should be at least 600px"
            )

    def test_render_complex_nesting_html(self) -> None:
        """Test rendering the complex nesting example HTML file"""
        input_file = self.examples_dir / "06_complex_nesting.html"
        output_file = self.output_dir / "complex_nesting_output.png"

        # Render the HTML
        render_html(input_file, output_file)

        # Check that output file was created
        self.assertTrue(output_file.exists(), "Output PNG file should be created")

        # Check that it's a valid PNG image
        with Image.open(output_file) as img:
            self.assertEqual(img.format, "PNG", "Output should be a PNG image")
            self.assertEqual(img.size[0], 800, "Image width should be 800px")
            self.assertGreaterEqual(
                img.size[1], 600, "Image height should be at least 600px"
            )

    def test_render_nonexistent_file(self) -> None:
        """Test that rendering a non-existent file raises FileNotFoundError"""
        input_file = self.examples_dir / "nonexistent.html"
        output_file = self.output_dir / "nonexistent_output.png"

        with self.assertRaises(FileNotFoundError):
            render_html(input_file, output_file)

    def test_output_directory_creation(self) -> None:
        """Test that output directories are created automatically"""
        input_file = self.examples_dir / "01_basic_structure.html"
        output_file = self.test_dir / "nested" / "deep" / "directories" / "output.png"

        # Render the HTML
        render_html(input_file, output_file)

        # Check that output file was created and directories exist
        self.assertTrue(output_file.exists(), "Output PNG file should be created")
        self.assertTrue(
            output_file.parent.exists(), "Output directory should be created"
        )

    def test_simple_html_content(self) -> None:
        """Test rendering simple HTML content"""
        # Create a simple HTML file
        simple_html = """<!DOCTYPE html>
<html>
<body>
    <h1>Test Title</h1>
    <p>This is a simple test.</p>
</body>
</html>"""

        input_file = self.test_dir / "simple.html"
        output_file = self.output_dir / "simple_output.png"

        # Write the HTML content
        with open(input_file, "w", encoding="utf-8") as f:
            f.write(simple_html)

        # Render the HTML
        render_html(input_file, output_file)

        # Check that output file was created
        self.assertTrue(output_file.exists(), "Output PNG file should be created")

        # Check that it's a valid PNG image
        with Image.open(output_file) as img:
            self.assertEqual(img.format, "PNG", "Output should be a PNG image")


if __name__ == "__main__":
    unittest.main()
