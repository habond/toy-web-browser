"""Test utilities and helper functions"""

from typing import Any, Optional
from unittest.mock import Mock

from PIL import Image, ImageDraw, ImageFont

from src.config import BrowserConfig
from src.html_parser import DOMNode
from src.layout_engine import Box, LayoutNode


class TestDataBuilder:
    """Builder class for creating test data"""

    @staticmethod
    def create_dom_node(
        tag: str = "div",
        text: Optional[str] = None,
        attrs: Optional[dict[str, str]] = None,
        children: Optional[list[DOMNode]] = None,
    ) -> DOMNode:
        """Create a DOM node with optional properties"""
        node = DOMNode(tag=tag, text=text, attrs=attrs or {})
        if children:
            for child in children:
                node.add_child(child)
        return node

    @staticmethod
    def create_layout_node(
        dom_node: Optional[DOMNode] = None,
        box: Optional[Box] = None,
        children: Optional[list[LayoutNode]] = None,
        **kwargs: Any,
    ) -> LayoutNode:
        """Create a layout node with optional properties"""
        if dom_node is None:
            dom_node = TestDataBuilder.create_dom_node()

        layout_node = LayoutNode(dom_node)

        if box is not None:
            layout_node.box = box

        if children is not None:
            layout_node.children = children

        # Set any additional attributes
        for key, value in kwargs.items():
            setattr(layout_node, key, value)

        return layout_node

    @staticmethod
    def create_test_image(
        width: int = 800,
        height: int = 600,
        background: str = "white",
        content: Optional[str] = None,
    ) -> Image.Image:
        """Create a test image with optional content"""
        img = Image.new("RGB", (width, height), background)

        if content:
            draw = ImageDraw.Draw(img)
            font = ImageFont.load_default()
            draw.text((10, 10), content, fill="black", font=font)

        return img


class MockFactory:
    """Factory for creating mock objects"""

    @staticmethod
    def create_font_manager_mock() -> Mock:
        """Create a mocked FontManager"""
        mock = Mock()
        mock.get_font.return_value = ImageFont.load_default()
        mock.default_font = ImageFont.load_default()
        return mock

    @staticmethod
    def create_config_mock(**overrides: Any) -> Mock:
        """Create a mocked BrowserConfig with optional overrides"""
        config = BrowserConfig()
        mock = Mock(spec=config)

        # Set default values
        for attr in dir(config):
            if not attr.startswith("_"):
                setattr(mock, attr, getattr(config, attr))

        # Apply overrides
        for key, value in overrides.items():
            setattr(mock, key, value)

        return mock


class CustomAssertions:
    """Custom assertion methods for testing"""

    @staticmethod
    def assert_box_equals(
        actual: Box,
        expected: Box,
        msg: Optional[str] = None,
    ) -> None:
        """Assert that two Box objects are equal"""
        if actual != expected:
            error_msg = (
                f"Boxes are not equal:\n"
                f"  Expected: Box(x={expected.x}, y={expected.y}, "
                f"width={expected.width}, height={expected.height})\n"
                f"  Actual:   Box(x={actual.x}, y={actual.y}, "
                f"width={actual.width}, height={actual.height})"
            )
            if msg:
                error_msg = f"{msg}\n{error_msg}"
            raise AssertionError(error_msg)

    @staticmethod
    def assert_dom_structure(
        node: DOMNode,
        expected_tag: str,
        expected_children_count: Optional[int] = None,
        expected_text: Optional[str] = None,
        expected_attrs: Optional[dict[str, str]] = None,
    ) -> None:
        """Assert DOM node structure matches expectations"""
        assert node.tag == expected_tag, f"Expected tag {expected_tag}, got {node.tag}"

        if expected_children_count is not None:
            assert (
                len(node.children) == expected_children_count
            ), f"Expected {expected_children_count} children, got {len(node.children)}"

        if expected_text is not None:
            assert (
                node.text == expected_text
            ), f"Expected text '{expected_text}', got '{node.text}'"

        if expected_attrs is not None:
            for key, value in expected_attrs.items():
                assert key in node.attrs, f"Expected attribute '{key}' not found"
                assert (
                    node.attrs[key] == value
                ), f"Expected attribute {key}='{value}', got '{node.attrs[key]}'"

    @staticmethod
    def assert_image_valid(
        image: Image.Image,
        expected_format: str = "RGB",
        min_width: int = 1,
        min_height: int = 1,
    ) -> None:
        """Assert that an image is valid and meets basic requirements"""
        assert (
            image.mode == expected_format
        ), f"Expected image format {expected_format}, got {image.mode}"
        assert (
            image.width >= min_width
        ), f"Expected minimum width {min_width}, got {image.width}"
        assert (
            image.height >= min_height
        ), f"Expected minimum height {min_height}, got {image.height}"


# Convenience functions for common test scenarios
def create_simple_dom_tree() -> DOMNode:
    """Create a simple DOM tree for testing"""
    root = TestDataBuilder.create_dom_node("root")
    p = TestDataBuilder.create_dom_node("p")
    text = TestDataBuilder.create_dom_node("text", text="Hello World")
    p.children.append(text)
    root.children.append(p)
    return root


def create_table_dom_tree() -> DOMNode:
    """Create a table DOM tree for testing"""
    root = TestDataBuilder.create_dom_node("root")
    table = TestDataBuilder.create_dom_node("table")
    tr = TestDataBuilder.create_dom_node("tr")
    td = TestDataBuilder.create_dom_node("td")
    text = TestDataBuilder.create_dom_node("text", text="Cell content")

    td.children.append(text)
    tr.children.append(td)
    table.children.append(tr)
    root.children.append(table)

    return root
