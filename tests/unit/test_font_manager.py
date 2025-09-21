"""Tests for the font manager module"""

import tempfile
from typing import Any
from unittest.mock import patch

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
