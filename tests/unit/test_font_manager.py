"""Tests for the font manager module"""

import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import Mock, patch

from src.exceptions import FontError
from src.font_manager import FontManager


class TestFontManager:
    """Test the FontManager class"""

    def test_font_manager_creation(self) -> None:
        """Test FontManager can be created"""
        font_manager = FontManager()
        assert font_manager is not None
        assert hasattr(font_manager, "default_font")

    def test_get_default_font(self) -> None:
        """Test getting the default font"""
        font_manager = FontManager()
        font = font_manager.get_font()

        assert font is not None
        assert hasattr(font, "getsize") or hasattr(
            font, "getbbox"
        )  # Different PIL versions

    def test_get_font_with_size(self) -> None:
        """Test getting font with specific size"""
        font_manager = FontManager()

        font_16 = font_manager.get_font(size=16)
        font_24 = font_manager.get_font(size=24)

        assert font_16 is not None
        assert font_24 is not None
        assert font_16 != font_24  # Different sizes should be different objects

    def test_get_font_with_styles(self) -> None:
        """Test getting fonts with different styles"""
        font_manager = FontManager()

        regular = font_manager.get_font(bold=False, italic=False)
        bold = font_manager.get_font(bold=True, italic=False)
        italic = font_manager.get_font(bold=False, italic=True)
        bold_italic = font_manager.get_font(bold=True, italic=True)

        assert regular is not None
        assert bold is not None
        assert italic is not None
        assert bold_italic is not None

    def test_font_caching(self) -> None:
        """Test that fonts are cached properly"""
        font_manager = FontManager()

        # Get the same font twice
        font1 = font_manager.get_font(size=16, bold=False)
        font2 = font_manager.get_font(size=16, bold=False)

        # Should be the same object due to caching
        assert font1 is font2

    def test_font_fallback_to_default(self) -> None:
        """Test fallback to default font when specific font fails"""
        font_manager = FontManager()

        # Mock a failed font load
        with patch("PIL.ImageFont.truetype") as mock_truetype:
            mock_truetype.side_effect = OSError("Font not found")

            # Should still return a font (default)
            font = font_manager.get_font(size=16)
            assert font is not None

    def test_get_font_with_zero_size(self) -> None:
        """Test that zero or negative font size is handled gracefully"""
        font_manager = FontManager()

        # Font manager should handle zero/negative sizes gracefully
        # by using default size or minimum size
        font = font_manager.get_font(size=0)
        assert font is not None

        font = font_manager.get_font(size=-5)
        assert font is not None

    def test_get_font_with_large_size(self) -> None:
        """Test getting font with very large size"""
        font_manager = FontManager()

        # Should handle large sizes gracefully
        font = font_manager.get_font(size=200)
        assert font is not None

    @patch("pathlib.Path.exists")
    def test_font_file_discovery(self, mock_exists: Any) -> None:
        """Test font file discovery logic"""
        mock_exists.return_value = True

        font_manager = FontManager()

        # Should attempt to find font files
        font = font_manager.get_font(bold=True)
        assert font is not None

    def test_font_manager_with_missing_fonts_directory(self) -> None:
        """Test behavior when fonts directory doesn't exist"""
        # Create a temporary directory without fonts
        with tempfile.TemporaryDirectory():
            # Should still work with default fonts
            font_manager = FontManager()
            font = font_manager.get_font()
            assert font is not None

    def test_clear_cache(self) -> None:
        """Test clearing the font cache"""
        font_manager = FontManager()

        # Load some fonts to populate cache
        font_manager.get_font(size=16)
        font_manager.get_font(size=18, bold=True)

        # Clear cache
        font_manager.clear_cache()

        # Should be able to get fonts again
        font = font_manager.get_font(size=16)
        assert font is not None

    def test_font_key_generation(self) -> None:
        """Test that font cache keys are generated correctly"""
        font_manager = FontManager()

        # Different parameters should generate different cache entries
        font1 = font_manager.get_font(size=16, bold=False, italic=False)
        font2 = font_manager.get_font(size=16, bold=True, italic=False)
        font3 = font_manager.get_font(size=18, bold=False, italic=False)

        # These should be different objects
        assert font1 is not font2
        assert font1 is not font3
        assert font2 is not font3

    def test_default_font_property(self) -> None:
        """Test the default_font property"""
        font_manager = FontManager()

        default_font = font_manager.default_font
        assert default_font is not None

        # Should be consistent
        assert font_manager.default_font is default_font

    def test_error_handling_for_invalid_font_path(self) -> None:
        """Test error handling when font files are corrupted or invalid"""
        font_manager = FontManager()

        with patch("PIL.ImageFont.truetype") as mock_truetype:
            mock_truetype.side_effect = IOError("Invalid font file")

            # Should fall back gracefully
            font = font_manager.get_font(size=16)
            assert font is not None

    def test_concurrent_font_access(self) -> None:
        """Test that concurrent access to fonts works correctly"""
        import threading
        import time

        font_manager = FontManager()
        results = []
        errors = []

        def get_font_worker() -> None:
            try:
                for i in range(10):
                    font = font_manager.get_font(size=16 + (i % 4))
                    results.append(font)
                    time.sleep(0.001)  # Small delay to encourage race conditions
            except Exception as e:
                errors.append(e)

        # Start multiple threads
        threads = [threading.Thread(target=get_font_worker) for _ in range(3)]
        for thread in threads:
            thread.start()

        # Wait for completion
        for thread in threads:
            thread.join()

        # Should have no errors and some results
        assert len(errors) == 0
        assert len(results) > 0

    def test_font_manager_with_custom_fonts_dir(self) -> None:
        """Test FontManager with custom fonts directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            custom_fonts_dir = Path(temp_dir)
            font_manager = FontManager(fonts_dir=custom_fonts_dir)
            assert font_manager.fonts_dir == custom_fonts_dir

    @patch("pathlib.Path.exists")
    @patch("PIL.ImageFont.truetype")
    def test_regular_font_loading_failure(
        self, mock_truetype: Mock, mock_exists: Mock
    ) -> None:
        """Test FontError when regular font loading fails"""
        mock_exists.return_value = True
        mock_truetype.side_effect = Exception("Font corrupted")

        try:
            FontManager()
            assert False, "Expected FontError to be raised"
        except FontError as e:
            assert "Failed to load regular font" in str(e)
            assert "Font corrupted" in str(e)

    @patch("pathlib.Path.exists")
    @patch("PIL.ImageFont.truetype")
    def test_monospace_font_loading_failure_non_critical(
        self, mock_truetype: Mock, mock_exists: Mock
    ) -> None:
        """Test that monospace font loading failure is handled gracefully"""

        def side_effect(font_path: str, size: int) -> Mock:
            if "SourceCodePro" in font_path:
                raise OSError("Monospace font not found")
            return Mock()

        mock_exists.return_value = True
        mock_truetype.side_effect = side_effect

        # Should not raise exception, just continue without monospace font
        font_manager = FontManager()
        assert font_manager.mono_font is None

    @patch("pathlib.Path.exists")
    @patch("PIL.ImageFont.truetype")
    def test_monospace_font_loading_io_error(
        self, mock_truetype: Mock, mock_exists: Mock
    ) -> None:
        """Test that IOError during monospace font loading is handled"""

        def side_effect(font_path: str, size: int) -> Mock:
            if "SourceCodePro" in font_path:
                raise IOError("I/O error reading monospace font")
            return Mock()

        mock_exists.return_value = True
        mock_truetype.side_effect = side_effect

        # Should not raise exception, just continue without monospace font
        font_manager = FontManager()
        assert font_manager.mono_font is None

    @patch("pathlib.Path.exists")
    @patch("PIL.ImageFont.load_default")
    def test_fallback_to_default_font_when_no_truetype(
        self, mock_load_default: Mock, mock_exists: Mock
    ) -> None:
        """Test fallback to PIL default font when no TrueType fonts available"""
        mock_exists.return_value = False  # No font files exist
        mock_default_font = Mock()
        mock_load_default.return_value = mock_default_font

        font_manager = FontManager()

        assert font_manager.default_font is mock_default_font
        mock_load_default.assert_called_once()

    def test_get_font_with_exception_during_truetype_creation(self) -> None:
        """Test font creation fallback when TrueType font creation fails"""
        font_manager = FontManager()

        # Mock a FreeTypeFont with a path attribute
        mock_base_font = Mock()
        mock_base_font.path = "/fake/font/path.ttf"
        font_manager.default_font = mock_base_font

        with patch("PIL.ImageFont.truetype") as mock_truetype:
            mock_truetype.side_effect = Exception("Cannot create font with size")

            # Should fall back to the base font
            font = font_manager.get_font(size=24)
            assert font is mock_base_font

    def test_get_font_when_no_base_font_available(self) -> None:
        """Test get_font when no base font is available"""
        font_manager = FontManager()

        # Clear all fonts
        font_manager.default_font = None
        font_manager.bold_font = None
        font_manager.mono_font = None

        with patch("PIL.ImageFont.load_default") as mock_load_default:
            mock_default = Mock()
            mock_load_default.return_value = mock_default

            font = font_manager.get_font(size=16)
            assert font is mock_default
            mock_load_default.assert_called_once()

    def test_get_monospace_font_when_available(self) -> None:
        """Test getting monospace font when it's available"""
        font_manager = FontManager()

        mock_mono_font = Mock()
        font_manager.mono_font = mock_mono_font

        font = font_manager.get_font(monospace=True)
        # Since get_font creates a new font with the requested size,
        # we just verify it doesn't crash and returns a font
        assert font is not None

    def test_get_text_size_with_getbbox(self) -> None:
        """Test get_text_size using getbbox method (newer PIL)"""
        font_manager = FontManager()

        mock_font = Mock()
        mock_font.getbbox.return_value = (0, 0, 100, 20)  # x1, y1, x2, y2

        width, height = font_manager.get_text_size("test", mock_font)
        assert width == 100
        assert height == 20

    def test_get_text_size_with_getsize_fallback(self) -> None:
        """Test get_text_size falling back to getsize method"""
        font_manager = FontManager()

        mock_font = Mock()
        # Simulate getbbox not available (raises AttributeError)
        mock_font.getbbox.side_effect = AttributeError("getbbox not available")
        mock_font.getsize.return_value = (80, 16)

        width, height = font_manager.get_text_size("test", mock_font)
        assert width == 80
        assert height == 16

    def test_get_text_size_ultimate_fallback(self) -> None:
        """Test get_text_size ultimate fallback when no size methods available"""
        font_manager = FontManager()

        mock_font = Mock(spec=[])  # Empty spec means no methods available
        # Using delattr and spec=[] to simulate a font object with no getbbox or getsize

        width, height = font_manager.get_text_size("hello", mock_font)
        assert width == 5 * 8  # len("hello") * 8
        assert height == 16

    def test_get_text_size_getsize_method_none(self) -> None:
        """Test get_text_size when getsize method exists but is None"""
        font_manager = FontManager()

        mock_font = Mock()
        mock_font.getbbox.side_effect = AttributeError("getbbox not available")

        # Mock getsize to be None directly on the font object
        mock_font.getsize = None

        width, height = font_manager.get_text_size("test", mock_font)
        assert width == 4 * 8  # len("test") * 8
        assert height == 16
