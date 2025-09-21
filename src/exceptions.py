"""
Custom exception hierarchy for the toy web browser
"""


class BrowserError(Exception):
    """Base exception for all browser-related errors"""

    pass


class ParseError(BrowserError):
    """Raised when HTML parsing fails"""

    pass


class LayoutError(BrowserError):
    """Raised when layout computation fails"""

    pass


class RenderError(BrowserError):
    """Raised when rendering to image fails"""

    pass


class FontError(RenderError):
    """Raised when font loading or manipulation fails"""

    pass


class ConfigError(BrowserError):
    """Raised when configuration is invalid"""

    pass
