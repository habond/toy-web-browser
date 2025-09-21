"""Tests for the HTML parser module"""

import unittest

from src.html_parser import DOMNode, HTMLParser


class TestHTMLParser(unittest.TestCase):
    """Test the HTML parser functionality"""

    def setUp(self) -> None:
        """Set up test fixtures"""
        self.parser = HTMLParser()

    def test_parse_simple_html(self) -> None:
        """Test parsing simple HTML"""
        html = "<html><body><h1>Hello</h1></body></html>"
        root = self.parser.parse(html)

        self.assertEqual(root.tag, "root")
        self.assertEqual(len(root.children), 1)
        self.assertEqual(root.children[0].tag, "html")

    def test_parse_text_content(self) -> None:
        """Test parsing text content"""
        html = "<p>Hello World</p>"
        root = self.parser.parse(html)

        p_element = root.children[0]
        self.assertEqual(p_element.tag, "p")
        self.assertEqual(len(p_element.children), 1)
        self.assertEqual(p_element.children[0].tag, "text")
        self.assertEqual(p_element.children[0].text, "Hello World")

    def test_parse_nested_elements(self) -> None:
        """Test parsing nested elements"""
        html = "<div><p>Paragraph</p></div>"
        root = self.parser.parse(html)

        div_element = root.children[0]
        self.assertEqual(div_element.tag, "div")
        self.assertEqual(len(div_element.children), 1)

        p_element = div_element.children[0]
        self.assertEqual(p_element.tag, "p")
        self.assertEqual(len(p_element.children), 1)
        self.assertEqual(p_element.children[0].text, "Paragraph")

    def test_parse_attributes(self) -> None:
        """Test parsing element attributes"""
        html = '<a href="https://example.com" class="link">Link</a>'
        root = self.parser.parse(html)

        a_element = root.children[0]
        self.assertEqual(a_element.tag, "a")
        self.assertEqual(a_element.attrs["href"], "https://example.com")
        self.assertEqual(a_element.attrs["class"], "link")

    def test_parse_void_elements(self) -> None:
        """Test parsing void elements (br, hr)"""
        html = "<p>Line 1<br>Line 2</p><hr>"
        root = self.parser.parse(html)

        self.assertEqual(len(root.children), 2)

        p_element = root.children[0]
        self.assertEqual(p_element.tag, "p")
        self.assertEqual(len(p_element.children), 3)  # text, br, text
        self.assertEqual(p_element.children[1].tag, "br")

        hr_element = root.children[1]
        self.assertEqual(hr_element.tag, "hr")

    def test_parse_lists(self) -> None:
        """Test parsing list elements"""
        html = "<ul><li>Item 1</li><li>Item 2</li></ul>"
        root = self.parser.parse(html)

        ul_element = root.children[0]
        self.assertEqual(ul_element.tag, "ul")
        self.assertEqual(len(ul_element.children), 2)

        li1 = ul_element.children[0]
        self.assertEqual(li1.tag, "li")
        self.assertEqual(li1.children[0].text, "Item 1")

        li2 = ul_element.children[1]
        self.assertEqual(li2.tag, "li")
        self.assertEqual(li2.children[0].text, "Item 2")

    def test_dom_node_representation(self) -> None:
        """Test DOMNode string representation"""
        text_node = DOMNode("text", text="Hello World")
        self.assertEqual(str(text_node), "Text('Hello World')")

        long_text_node = DOMNode(
            "text", text="This is a very long text that should be truncated"
        )
        self.assertEqual(str(long_text_node), "Text('This is a very long ...')")

        element_node = DOMNode("div")
        self.assertEqual(str(element_node), "<div>")


if __name__ == "__main__":
    unittest.main()
