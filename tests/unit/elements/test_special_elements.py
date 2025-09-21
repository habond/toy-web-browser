"""Tests for the SpecialElement classes (BreakElement, HorizontalRuleElement)"""

from unittest.mock import Mock

import pytest

from src.config import BrowserConfig
from src.elements.special import BreakElement, HorizontalRuleElement
from src.html_parser import DOMNode
from src.layout_engine import Box, LayoutEngine
from tests.fixtures.test_utils import MockFactory, TestDataBuilder


class TestBreakElement:
    """Test the BreakElement class"""

    def setup_method(self) -> None:
        """Set up test fixtures"""
        self.config = BrowserConfig()
        self.layout_engine = LayoutEngine()

    def test_break_element_creation(self) -> None:
        """Test BreakElement can be created"""
        dom_node = DOMNode("br")
        element = BreakElement(dom_node)

        assert element is not None
        assert element.dom_node == dom_node

    def test_break_element_layout(self) -> None:
        """Test break element layout"""
        dom_node = DOMNode("br")
        element = BreakElement(dom_node)

        initial_y = self.layout_engine.current_y
        layout_node = element.layout(self.layout_engine, 10, 800)

        # Break element should return None (no visual layout)
        assert layout_node is None

        # Should have increased current_y by half font size
        expected_y_increase = self.layout_engine.DEFAULT_FONT_SIZE * 0.5
        assert self.layout_engine.current_y == initial_y + expected_y_increase

    def test_break_element_multiple_breaks(self) -> None:
        """Test multiple break elements accumulate spacing"""
        dom_node = DOMNode("br")
        element = BreakElement(dom_node)

        initial_y = self.layout_engine.current_y

        # Add multiple breaks
        element.layout(self.layout_engine, 10, 800)
        element.layout(self.layout_engine, 10, 800)
        element.layout(self.layout_engine, 10, 800)

        # Should have increased by 3 * half font size
        expected_y_increase = self.layout_engine.DEFAULT_FONT_SIZE * 0.5 * 3
        assert self.layout_engine.current_y == initial_y + expected_y_increase

    def test_break_element_render(self) -> None:
        """Test break element rendering"""
        dom_node = DOMNode("br")
        element = BreakElement(dom_node)

        # Create mock layout node (though it should be None from layout)
        mock_layout_node = Mock()
        mock_renderer = Mock()
        mock_draw = Mock()

        # Render should do nothing (pass)
        element.render(mock_draw, mock_layout_node, mock_renderer)

        # Should not have called any drawing methods
        assert not mock_draw.called
        assert not mock_renderer.called

    def test_break_element_with_different_positions(self) -> None:
        """Test break element works regardless of position parameters"""
        dom_node = DOMNode("br")
        element = BreakElement(dom_node)

        initial_y = self.layout_engine.current_y

        # Position and viewport width shouldn't matter
        layout_node = element.layout(self.layout_engine, 100, 400)

        assert layout_node is None
        # Should still increase y by half font size
        expected_y_increase = self.layout_engine.DEFAULT_FONT_SIZE * 0.5
        assert self.layout_engine.current_y == initial_y + expected_y_increase

    def test_break_element_with_kwargs(self) -> None:
        """Test break element ignores additional kwargs"""
        dom_node = DOMNode("br")
        element = BreakElement(dom_node)

        initial_y = self.layout_engine.current_y

        # Should work with additional parameters
        layout_node = element.layout(
            self.layout_engine, 10, 800, max_width=200, some_other_param="value"
        )

        assert layout_node is None
        # Should still work normally
        expected_y_increase = self.layout_engine.DEFAULT_FONT_SIZE * 0.5
        assert self.layout_engine.current_y == initial_y + expected_y_increase


class TestHorizontalRuleElement:
    """Test the HorizontalRuleElement class"""

    def setup_method(self) -> None:
        """Set up test fixtures"""
        self.config = BrowserConfig()
        self.layout_engine = LayoutEngine()

    def test_horizontal_rule_element_creation(self) -> None:
        """Test HorizontalRuleElement can be created"""
        dom_node = DOMNode("hr")
        element = HorizontalRuleElement(dom_node)

        assert element is not None
        assert element.dom_node == dom_node

    def test_horizontal_rule_layout(self) -> None:
        """Test horizontal rule layout"""
        dom_node = DOMNode("hr")
        element = HorizontalRuleElement(dom_node)

        initial_y = self.layout_engine.current_y
        layout_node = element.layout(self.layout_engine, 10, 800)

        assert layout_node is not None
        assert layout_node.dom_node == dom_node
        assert hasattr(layout_node, "box")

        # Check box dimensions
        assert layout_node.box.x == 10
        assert layout_node.box.y == initial_y
        assert layout_node.box.width == 800 - 2 * 10  # viewport_width - 2 * x
        assert layout_node.box.height == 2

        # Should have increased current_y by 10
        assert self.layout_engine.current_y == initial_y + 10

    def test_horizontal_rule_layout_different_positions(self) -> None:
        """Test horizontal rule with different positions and viewport widths"""
        dom_node = DOMNode("hr")
        element = HorizontalRuleElement(dom_node)

        initial_y = self.layout_engine.current_y
        x_position = 50
        viewport_width = 1000

        layout_node = element.layout(self.layout_engine, x_position, viewport_width)

        assert layout_node is not None
        assert layout_node.box.x == x_position
        assert layout_node.box.y == initial_y
        assert layout_node.box.width == viewport_width - 2 * x_position
        assert layout_node.box.height == 2

    def test_horizontal_rule_render(self) -> None:
        """Test horizontal rule rendering"""
        dom_node = DOMNode("hr")
        element = HorizontalRuleElement(dom_node)

        layout_node = element.layout(self.layout_engine, 10, 800)
        assert layout_node is not None

        mock_renderer = Mock()
        mock_draw = Mock()

        element.render(mock_draw, layout_node, mock_renderer)

        # Should have drawn a rectangle
        mock_draw.rectangle.assert_called_once()

        # Check rectangle coordinates match the box
        args, kwargs = mock_draw.rectangle.call_args
        coords = args[0]

        expected_coords = (
            layout_node.box.x,
            layout_node.box.y,
            layout_node.box.x + layout_node.box.width,
            layout_node.box.y + layout_node.box.height,
        )
        assert coords == expected_coords
        assert kwargs.get("fill") == "#cccccc"

    def test_horizontal_rule_render_specific_coordinates(self) -> None:
        """Test horizontal rule rendering with specific coordinates"""
        dom_node = DOMNode("hr")
        element = HorizontalRuleElement(dom_node)

        # Create layout node with specific box
        layout_node = TestDataBuilder.create_layout_node(dom_node)
        layout_node.box = Box(25, 50, 300, 2)

        mock_draw = Mock()
        mock_renderer = Mock()

        element.render(mock_draw, layout_node, mock_renderer)

        # Check exact coordinates
        mock_draw.rectangle.assert_called_once()
        args, kwargs = mock_draw.rectangle.call_args
        coords = args[0]

        assert coords == (25, 50, 325, 52)  # (x, y, x+width, y+height)
        assert kwargs.get("fill") == "#cccccc"

    def test_horizontal_rule_multiple_rules(self) -> None:
        """Test multiple horizontal rules create separate layout nodes"""
        dom_node1 = DOMNode("hr")
        dom_node2 = DOMNode("hr")

        element1 = HorizontalRuleElement(dom_node1)
        element2 = HorizontalRuleElement(dom_node2)

        layout_node1 = element1.layout(self.layout_engine, 10, 800)
        layout_node2 = element2.layout(self.layout_engine, 10, 800)

        assert layout_node1 is not None
        assert layout_node2 is not None
        assert layout_node1 != layout_node2

        # Second rule should be positioned after the first
        assert layout_node2.box.y > layout_node1.box.y

    def test_horizontal_rule_with_narrow_viewport(self) -> None:
        """Test horizontal rule with narrow viewport"""
        dom_node = DOMNode("hr")
        element = HorizontalRuleElement(dom_node)

        layout_node = element.layout(self.layout_engine, 5, 100)

        assert layout_node is not None
        assert layout_node.box.x == 5
        assert layout_node.box.width == 100 - 2 * 5  # 90
        assert layout_node.box.height == 2

    def test_horizontal_rule_box_creation(self) -> None:
        """Test that horizontal rule creates Box correctly"""
        dom_node = DOMNode("hr")
        element = HorizontalRuleElement(dom_node)

        layout_node = element.layout(self.layout_engine, 15, 600)

        assert layout_node is not None
        assert isinstance(layout_node.box, Box)
        assert layout_node.box.x == 15
        assert layout_node.box.y >= 0  # Should be current_y at time of layout
        assert layout_node.box.width == 600 - 2 * 15
        assert layout_node.box.height == 2

    def test_horizontal_rule_zero_width_viewport(self) -> None:
        """Test horizontal rule behavior with edge case viewport widths"""
        dom_node = DOMNode("hr")
        element = HorizontalRuleElement(dom_node)

        # Viewport width exactly equal to 2*x
        layout_node = element.layout(self.layout_engine, 50, 100)

        assert layout_node is not None
        assert layout_node.box.width == 0  # 100 - 2*50

    def test_horizontal_rule_render_without_layout(self) -> None:
        """Test horizontal rule rendering with manually created layout node"""
        dom_node = DOMNode("hr")
        element = HorizontalRuleElement(dom_node)

        # Create layout node manually without using layout method
        layout_node = TestDataBuilder.create_layout_node(dom_node)
        layout_node.box = Box(10, 20, 100, 2)

        mock_draw = Mock()
        mock_renderer = Mock()

        element.render(mock_draw, layout_node, mock_renderer)

        # Should still render correctly
        mock_draw.rectangle.assert_called_once()
        args, kwargs = mock_draw.rectangle.call_args
        coords = args[0]
        assert coords == (10, 20, 110, 22)
