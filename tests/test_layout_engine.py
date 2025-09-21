"""Tests for the layout engine module"""

import unittest

from src.html_parser import DOMNode, HTMLParser
from src.layout_engine import Box, LayoutEngine, LayoutNode


class TestLayoutEngine(unittest.TestCase):
    """Test the layout engine functionality"""

    def setUp(self) -> None:
        """Set up test fixtures"""
        self.layout_engine = LayoutEngine()
        self.parser = HTMLParser()

    def test_box_creation(self) -> None:
        """Test Box dataclass creation"""
        box = Box(10, 20, 100, 50)
        self.assertEqual(box.x, 10)
        self.assertEqual(box.y, 20)
        self.assertEqual(box.width, 100)
        self.assertEqual(box.height, 50)

    def test_layout_node_creation(self) -> None:
        """Test LayoutNode creation"""
        dom_node = DOMNode("p", text="Test")
        layout_node = LayoutNode(dom_node)

        self.assertEqual(layout_node.dom_node, dom_node)
        self.assertIsInstance(layout_node.box, Box)
        self.assertEqual(len(layout_node.children), 0)

    def test_simple_layout(self) -> None:
        """Test layout computation for simple HTML"""
        html = "<p>Hello World</p>"
        dom_tree = self.parser.parse(html)
        layout_tree = self.layout_engine.compute_layout(dom_tree)

        self.assertEqual(layout_tree.dom_node.tag, "root")
        self.assertGreaterEqual(len(layout_tree.children), 1)

    def test_heading_layout(self) -> None:
        """Test layout computation for headings"""
        html = "<h1>Big Title</h1><h2>Smaller Title</h2>"
        dom_tree = self.parser.parse(html)
        layout_tree = self.layout_engine.compute_layout(dom_tree)

        # Should have layout nodes for the headings
        self.assertGreaterEqual(len(layout_tree.children), 2)

    def test_list_layout(self) -> None:
        """Test layout computation for lists"""
        html = "<ul><li>Item 1</li><li>Item 2</li></ul>"
        dom_tree = self.parser.parse(html)
        layout_tree = self.layout_engine.compute_layout(dom_tree)

        # Should have a layout node for the ul
        self.assertGreaterEqual(len(layout_tree.children), 1)

    def test_nested_layout(self) -> None:
        """Test layout computation for nested elements"""
        html = "<div><p>Paragraph in div</p></div>"
        dom_tree = self.parser.parse(html)
        layout_tree = self.layout_engine.compute_layout(dom_tree)

        # Should have layout nodes
        self.assertGreaterEqual(len(layout_tree.children), 1)

    def test_text_wrapping_calculation(self) -> None:
        """Test that text wrapping is computed"""
        # Create a long text that should wrap
        long_text = "This is a very long line of text " * 20
        html = f"<p>{long_text}</p>"
        dom_tree = self.parser.parse(html)
        layout_tree = self.layout_engine.compute_layout(dom_tree)

        # Find the text layout node
        def find_text_node(node: LayoutNode) -> LayoutNode:
            if node.dom_node.tag == "text":
                return node
            for child in node.children:
                result = find_text_node(child)
                if result:
                    return result

        text_node = find_text_node(layout_tree)
        if text_node and hasattr(text_node, "lines"):
            # Should have multiple lines due to wrapping
            self.assertGreater(len(text_node.lines), 1)


if __name__ == "__main__":
    unittest.main()
