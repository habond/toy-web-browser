"""Tests for the BaseElement abstract class"""

from typing import Any, Optional
from unittest.mock import Mock

import pytest
from PIL import ImageDraw

from src.elements.base import BaseElement
from src.html_parser import DOMNode
from src.layout_engine import Box, LayoutEngine, LayoutNode
from src.renderer import Renderer
from tests.fixtures.test_utils import TestDataBuilder


class ConcreteElement(BaseElement):
    """Concrete implementation of BaseElement for testing"""

    def layout(
        self, layout_engine: LayoutEngine, x: float, viewport_width: int, **kwargs: Any
    ) -> Optional[LayoutNode]:
        """Implement concrete layout method"""
        return self._create_layout_node(x, 0, 100, 50)

    def render(
        self, draw: ImageDraw.ImageDraw, layout_node: LayoutNode, renderer: Renderer
    ) -> None:
        """Implement concrete render method"""
        pass


class TestBaseElement:
    """Test the BaseElement abstract base class"""

    def test_base_element_cannot_be_instantiated(self) -> None:
        """Test that BaseElement cannot be instantiated directly"""
        dom_node = DOMNode("div")

        with pytest.raises(TypeError):
            BaseElement(dom_node)  # type: ignore[abstract]

    def test_base_element_concrete_implementation(self) -> None:
        """Test that concrete implementation can be created"""
        dom_node = DOMNode("div")
        element = ConcreteElement(dom_node)

        assert element is not None
        assert element.dom_node == dom_node

    def test_base_element_dom_node_assignment(self) -> None:
        """Test that DOM node is correctly assigned"""
        dom_node = DOMNode("p", text="Test content")
        element = ConcreteElement(dom_node)

        assert element.dom_node is dom_node
        assert element.dom_node.tag == "p"
        assert element.dom_node.text == "Test content"

    def test_base_element_abstract_methods_exist(self) -> None:
        """Test that abstract methods are defined"""
        # Check that the abstract methods exist
        assert hasattr(BaseElement, "layout")
        assert hasattr(BaseElement, "render")

        # Check that they're marked as abstract
        assert getattr(BaseElement.layout, "__isabstractmethod__", False)
        assert getattr(BaseElement.render, "__isabstractmethod__", False)

    def test_create_layout_node_basic(self) -> None:
        """Test _create_layout_node method"""
        dom_node = DOMNode("div")
        element = ConcreteElement(dom_node)

        layout_node = element._create_layout_node(10, 20, 300, 150)

        assert isinstance(layout_node, LayoutNode)
        assert layout_node.dom_node is dom_node
        assert isinstance(layout_node.box, Box)
        assert layout_node.box.x == 10
        assert layout_node.box.y == 20
        assert layout_node.box.width == 300
        assert layout_node.box.height == 150

    def test_create_layout_node_with_zero_dimensions(self) -> None:
        """Test _create_layout_node with zero dimensions"""
        dom_node = DOMNode("span")
        element = ConcreteElement(dom_node)

        layout_node = element._create_layout_node(0, 0, 0, 0)

        assert layout_node is not None
        assert layout_node.box.x == 0
        assert layout_node.box.y == 0
        assert layout_node.box.width == 0
        assert layout_node.box.height == 0

    def test_create_layout_node_with_negative_coordinates(self) -> None:
        """Test _create_layout_node with negative coordinates"""
        dom_node = DOMNode("div")
        element = ConcreteElement(dom_node)

        layout_node = element._create_layout_node(-5, -10, 100, 50)

        assert layout_node is not None
        assert layout_node.box.x == -5
        assert layout_node.box.y == -10
        assert layout_node.box.width == 100
        assert layout_node.box.height == 50

    def test_create_layout_node_with_float_values(self) -> None:
        """Test _create_layout_node with float values"""
        dom_node = DOMNode("p")
        element = ConcreteElement(dom_node)

        layout_node = element._create_layout_node(10.5, 20.7, 150.3, 75.9)

        assert layout_node is not None
        assert layout_node.box.x == 10.5
        assert layout_node.box.y == 20.7
        assert layout_node.box.width == 150.3
        assert layout_node.box.height == 75.9

    def test_create_layout_node_preserves_dom_node_reference(self) -> None:
        """Test that _create_layout_node preserves DOM node reference"""
        dom_node = DOMNode("h1", text="Title")
        element = ConcreteElement(dom_node)

        layout_node = element._create_layout_node(0, 0, 100, 50)

        assert layout_node.dom_node is dom_node
        assert layout_node.dom_node.tag == "h1"
        assert layout_node.dom_node.text == "Title"

    def test_create_layout_node_multiple_calls(self) -> None:
        """Test multiple calls to _create_layout_node create separate objects"""
        dom_node = DOMNode("div")
        element = ConcreteElement(dom_node)

        layout_node1 = element._create_layout_node(0, 0, 100, 50)
        layout_node2 = element._create_layout_node(10, 20, 200, 100)

        assert layout_node1 is not layout_node2
        assert layout_node1.box is not layout_node2.box

        # But both should reference the same DOM node
        assert layout_node1.dom_node is layout_node2.dom_node

    def test_concrete_element_layout_method(self) -> None:
        """Test that concrete implementation's layout method works"""
        dom_node = DOMNode("div")
        element = ConcreteElement(dom_node)
        layout_engine = LayoutEngine()

        layout_node = element.layout(layout_engine, 25, 800)

        assert layout_node is not None
        assert layout_node.box.x == 25
        assert layout_node.box.y == 0
        assert layout_node.box.width == 100
        assert layout_node.box.height == 50

    def test_concrete_element_render_method(self) -> None:
        """Test that concrete implementation's render method can be called"""
        dom_node = DOMNode("div")
        element = ConcreteElement(dom_node)

        layout_node = TestDataBuilder.create_layout_node(dom_node)
        mock_draw = Mock()
        mock_renderer = Mock()

        # Should not raise any exception
        element.render(mock_draw, layout_node, mock_renderer)

    def test_base_element_inheritance(self) -> None:
        """Test inheritance relationship"""
        dom_node = DOMNode("div")
        element = ConcreteElement(dom_node)

        assert isinstance(element, BaseElement)
        assert isinstance(element, ConcreteElement)

    def test_base_element_with_different_dom_node_types(self) -> None:
        """Test BaseElement with different types of DOM nodes"""
        test_cases = [
            DOMNode("div"),
            DOMNode("p", text="Paragraph"),
            DOMNode("text", text="Just text"),
            DOMNode("img", attrs={"src": "image.jpg"}),
            DOMNode("a", attrs={"href": "link.html"}, text="Link text"),
        ]

        for dom_node in test_cases:
            element = ConcreteElement(dom_node)
            assert element.dom_node is dom_node

            # Should be able to create layout nodes
            layout_node = element._create_layout_node(0, 0, 100, 50)
            assert layout_node.dom_node is dom_node

    def test_create_layout_node_box_properties(self) -> None:
        """Test that created layout node has correct Box properties"""
        dom_node = DOMNode("div")
        element = ConcreteElement(dom_node)

        x, y, width, height = 15, 25, 200, 100
        layout_node = element._create_layout_node(x, y, width, height)

        box = layout_node.box
        assert hasattr(box, "x")
        assert hasattr(box, "y")
        assert hasattr(box, "width")
        assert hasattr(box, "height")

        assert box.x == x
        assert box.y == y
        assert box.width == width
        assert box.height == height

    def test_create_layout_node_with_large_values(self) -> None:
        """Test _create_layout_node with large values"""
        dom_node = DOMNode("div")
        element = ConcreteElement(dom_node)

        # Test with large values
        layout_node = element._create_layout_node(1000, 2000, 5000, 3000)

        assert layout_node is not None
        assert layout_node.box.x == 1000
        assert layout_node.box.y == 2000
        assert layout_node.box.width == 5000
        assert layout_node.box.height == 3000

    def test_base_element_method_signatures(self) -> None:
        """Test that abstract method signatures are as expected"""
        import inspect

        # Check layout method signature
        layout_sig = inspect.signature(BaseElement.layout)
        layout_params = list(layout_sig.parameters.keys())
        expected_layout_params = [
            "self",
            "layout_engine",
            "x",
            "viewport_width",
            "kwargs",
        ]
        assert layout_params == expected_layout_params

        # Check render method signature
        render_sig = inspect.signature(BaseElement.render)
        render_params = list(render_sig.parameters.keys())
        expected_render_params = ["self", "draw", "layout_node", "renderer"]
        assert render_params == expected_render_params
