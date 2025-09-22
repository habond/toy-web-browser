"""Tests for the browser CLI functionality and main entry point"""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from src.browser import main, render_html


class TestBrowserCLI(unittest.TestCase):
    """Test the browser CLI argument parsing and main function"""

    def setUp(self) -> None:
        """Set up test fixtures"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.examples_dir = Path(__file__).parent.parent.parent / "examples"

        # Create a test HTML file
        self.test_html = self.test_dir / "test.html"
        self.test_html.write_text(
            """<!DOCTYPE html>
<html><body><h1>Test</h1></body></html>""",
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        """Clean up test fixtures"""
        import shutil

        shutil.rmtree(self.test_dir)

    @patch("sys.argv", ["browser.py", "input.html", "output.png"])
    @patch("src.browser.render_html")
    def test_main_basic_arguments(self, mock_render: Mock) -> None:
        """Test main function with basic input and output arguments"""
        main()

        mock_render.assert_called_once_with(Path("input.html"), Path("output.png"))

    @patch(
        "sys.argv",
        ["browser.py", "input.html", "output.png", "--output-dir", "/tmp/custom"],
    )
    @patch("src.browser.render_html")
    def test_main_with_output_dir(self, mock_render: Mock) -> None:
        """Test main function with --output-dir argument"""
        main()

        expected_output = Path("/tmp/custom") / "output.png"
        mock_render.assert_called_once_with(Path("input.html"), expected_output)

    @patch("sys.argv", ["browser.py", "input.html", "output.png", "-o", "/tmp/custom"])
    @patch("src.browser.render_html")
    def test_main_with_output_dir_short_flag(self, mock_render: Mock) -> None:
        """Test main function with -o short flag for output directory"""
        main()

        expected_output = Path("/tmp/custom") / "output.png"
        mock_render.assert_called_once_with(Path("input.html"), expected_output)

    @patch("sys.argv", ["browser.py", "/nonexistent/file.html", "output.png"])
    @patch("builtins.print")
    @patch("sys.exit")
    def test_main_file_not_found_error(self, mock_exit: Mock, mock_print: Mock) -> None:
        """Test main function handles FileNotFoundError properly"""
        main()

        mock_print.assert_called_once()
        error_message = mock_print.call_args[0][0]
        self.assertIn("Error:", error_message)
        self.assertIn("not found", error_message)
        mock_exit.assert_called_once_with(1)

    @patch("sys.argv", ["browser.py", "input.html", "output.png"])
    @patch("src.browser.render_html")
    @patch("builtins.print")
    @patch("sys.exit")
    def test_main_general_exception(
        self, mock_exit: Mock, mock_print: Mock, mock_render: Mock
    ) -> None:
        """Test main function handles general exceptions properly"""
        # Make render_html raise a general exception
        mock_render.side_effect = RuntimeError("Rendering failed")

        main()

        mock_print.assert_called_once()
        error_message = mock_print.call_args[0][0]
        self.assertIn("Error rendering HTML:", error_message)
        self.assertIn("Rendering failed", error_message)
        mock_exit.assert_called_once_with(1)

    @patch("argparse.ArgumentParser.parse_args")
    def test_argument_parser_configuration(self, mock_parse_args: Mock) -> None:
        """Test that argument parser is configured correctly"""
        # Create a mock args object
        mock_args = Mock()
        mock_args.input = Path("input.html")
        mock_args.output = Path("output.png")
        mock_args.output_dir = None
        mock_parse_args.return_value = mock_args

        with patch("src.browser.render_html") as mock_render:
            main()

        # Verify parse_args was called
        mock_parse_args.assert_called_once()

        # Verify render_html was called with correct arguments
        mock_render.assert_called_once_with(Path("input.html"), Path("output.png"))

    def test_render_html_file_not_found(self) -> None:
        """Test render_html raises FileNotFoundError for non-existent files"""
        nonexistent_file = self.test_dir / "nonexistent.html"
        output_file = self.test_dir / "output.png"

        with self.assertRaises(FileNotFoundError) as context:
            render_html(nonexistent_file, output_file)

        self.assertIn("not found", str(context.exception))
        self.assertIn(str(nonexistent_file), str(context.exception))

    @patch("builtins.print")
    def test_render_html_success_message(self, mock_print: Mock) -> None:
        """Test render_html prints success message"""
        output_file = self.test_dir / "output.png"

        with (
            patch("src.browser.HTMLParser"),
            patch("src.browser.LayoutEngine"),
            patch("src.browser.Renderer") as mock_renderer_class,
        ):

            # Mock the renderer and image
            mock_renderer = Mock()
            mock_image = Mock()
            mock_renderer.render.return_value = mock_image
            mock_renderer_class.return_value = mock_renderer

            render_html(self.test_html, output_file)

        # Verify success message was printed
        mock_print.assert_called_once()
        message = mock_print.call_args[0][0]
        self.assertIn("Rendered HTML to:", message)
        self.assertIn(str(output_file), message)

    def test_render_html_creates_output_directory(self) -> None:
        """Test render_html creates output directory structure"""
        nested_output = self.test_dir / "deep" / "nested" / "output.png"

        with (
            patch("src.browser.HTMLParser"),
            patch("src.browser.LayoutEngine"),
            patch("src.browser.Renderer") as mock_renderer_class,
        ):

            # Mock the renderer and image
            mock_renderer = Mock()
            mock_image = Mock()
            mock_renderer.render.return_value = mock_image
            mock_renderer_class.return_value = mock_renderer

            render_html(self.test_html, nested_output)

        # Verify directory was created
        self.assertTrue(nested_output.parent.exists())

    @patch("src.browser.config")
    def test_render_html_uses_config_values(self, mock_config: Mock) -> None:
        """Test render_html uses configuration values correctly"""
        mock_config.MIN_HEIGHT = 800
        mock_config.VIEWPORT_WIDTH = 1024

        output_file = self.test_dir / "output.png"

        with (
            patch("src.browser.HTMLParser"),
            patch("src.browser.LayoutEngine") as mock_layout_class,
            patch("src.browser.Renderer") as mock_renderer_class,
        ):

            # Mock layout engine
            mock_layout_engine = Mock()
            mock_layout_tree = Mock()
            mock_layout_tree.box.height = 500  # Less than MIN_HEIGHT
            mock_layout_engine.compute_layout.return_value = mock_layout_tree
            mock_layout_class.return_value = mock_layout_engine

            # Mock renderer
            mock_renderer = Mock()
            mock_image = Mock()
            mock_renderer.render.return_value = mock_image
            mock_renderer_class.return_value = mock_renderer

            render_html(self.test_html, output_file)

        # Verify renderer was called with config values
        # Height should be MAX(layout_height + 20, MIN_HEIGHT) = MAX(520, 800) = 800
        mock_renderer_class.assert_called_once_with(width=1024, height=800)


if __name__ == "__main__":
    unittest.main()
