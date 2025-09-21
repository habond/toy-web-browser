"""Tests for the configuration module"""

import pytest

from src.config import BrowserConfig


class TestBrowserConfig:
    """Test the BrowserConfig dataclass"""

    def test_config_creation(self) -> None:
        """Test that config can be created with default values"""
        config = BrowserConfig()

        assert config.VIEWPORT_WIDTH == 800
        assert config.MIN_HEIGHT == 600
        assert config.DEFAULT_FONT_SIZE == 16
        assert config.MARGIN == 10
        assert config.PADDING == 5

    def test_font_size_calculations(self) -> None:
        """Test font size multiplier calculations"""
        config = BrowserConfig()

        # Test heading multipliers
        assert config.HEADING_SIZES["h1"] > config.HEADING_SIZES["h2"]
        assert config.HEADING_SIZES["h2"] > config.HEADING_SIZES["h3"]
        assert config.HEADING_SIZES["h3"] > config.HEADING_SIZES["h4"]
        assert config.HEADING_SIZES["h4"] > config.HEADING_SIZES["h5"]
        assert config.HEADING_SIZES["h5"] > config.HEADING_SIZES["h6"]

        # Test that all multipliers are reasonable
        assert all(
            0.5 <= multiplier <= 3.0 for multiplier in config.HEADING_SIZES.values()
        )

    def test_layout_spacing_values(self) -> None:
        """Test that layout spacing values are reasonable"""
        config = BrowserConfig()

        assert config.LINE_HEIGHT > 0
        assert config.CHAR_WIDTH_ESTIMATE > 0

        # Spacing should be non-negative
        assert config.MARGIN >= 0
        assert config.PADDING >= 0

    def test_config_consistency(self) -> None:
        """Test that configuration values are internally consistent"""
        config = BrowserConfig()

        # Font sizes should be positive
        assert config.DEFAULT_FONT_SIZE > 0

        # Dimensions should be positive and reasonable
        assert 100 <= config.VIEWPORT_WIDTH <= 10000
        assert 100 <= config.MIN_HEIGHT <= 10000

        # Line height should be reasonable
        assert 1.0 <= config.LINE_HEIGHT <= 3.0

    def test_heading_sizes_structure(self) -> None:
        """Test that heading sizes dictionary has expected structure"""
        config = BrowserConfig()

        expected_headings = ["h1", "h2", "h3", "h4", "h5", "h6"]
        for heading in expected_headings:
            assert heading in config.HEADING_SIZES
            assert isinstance(config.HEADING_SIZES[heading], float)

    def test_config_attributes_exist(self) -> None:
        """Test that expected configuration attributes exist"""
        config = BrowserConfig()

        # Check that all expected attributes exist
        expected_attrs = [
            "DEFAULT_FONT_SIZE",
            "LINE_HEIGHT",
            "CHAR_WIDTH_ESTIMATE",
            "MARGIN",
            "PADDING",
            "VIEWPORT_WIDTH",
            "MIN_HEIGHT",
            "HEADING_SIZES",
        ]

        for attr in expected_attrs:
            assert hasattr(config, attr), f"Config missing attribute: {attr}"
