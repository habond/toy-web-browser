"""
Centralized configuration for the toy web browser
"""

from dataclasses import dataclass


@dataclass
class BrowserConfig:
    """Configuration settings for the toy web browser"""

    # Font settings
    DEFAULT_FONT_SIZE: int = 16
    LINE_HEIGHT: float = 1.5
    CHAR_WIDTH_ESTIMATE: int = 8

    # Layout settings
    MARGIN: int = 10
    PADDING: int = 5
    VIEWPORT_WIDTH: int = 800
    MIN_HEIGHT: int = 600

    # Heading size multipliers
    HEADING_SIZES: dict[str, float] = None

    def __post_init__(self) -> None:
        """Initialize computed values after dataclass creation"""
        if self.HEADING_SIZES is None:
            self.HEADING_SIZES = {
                "h1": 2.0,
                "h2": 1.75,
                "h3": 1.5,
                "h4": 1.25,
                "h5": 1.1,
                "h6": 1.0,
            }


# Global configuration instance
config = BrowserConfig()
