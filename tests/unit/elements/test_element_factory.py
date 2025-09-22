"""Tests for the element factory module"""

from src.elements.base import BaseElement
from src.elements.block import BlockElement
from src.elements.button import ButtonElement
from src.elements.element_factory import ElementFactory
from src.elements.heading import HeadingElement
from src.elements.inline import InlineElement
from src.elements.input import InputElement
from src.elements.list import ListElement, ListItemElement
from src.elements.pre import PreElement
from src.elements.special import BreakElement, HorizontalRuleElement
from src.elements.table.table_cell_element import TableCellElement
from src.elements.table.table_element import TableElement
from src.elements.table.table_row_element import TableRowElement
from src.elements.text import TextElement


class TestElementFactory:
    """Test the ElementFactory class"""

    def test_create_text_element(self) -> None:
        """Test creating text element"""
        from src.html_parser import DOMNode

        dom_node = DOMNode("text", text="sample text")
        element = ElementFactory.create_element(dom_node)
        assert isinstance(element, TextElement)

    def test_create_heading_elements(self) -> None:
        """Test creating heading elements"""
        from src.html_parser import DOMNode

        for level in range(1, 7):  # h1 through h6
            dom_node = DOMNode(f"h{level}")
            element = ElementFactory.create_element(dom_node)
            assert isinstance(element, HeadingElement)

    def test_create_block_elements(self) -> None:
        """Test creating block elements"""
        from src.html_parser import DOMNode

        block_tags = ["div", "p", "blockquote"]
        for tag in block_tags:
            dom_node = DOMNode(tag)
            element = ElementFactory.create_element(dom_node)
            assert isinstance(element, BlockElement)

    def test_create_pre_element(self) -> None:
        """Test creating pre element"""
        from src.html_parser import DOMNode

        dom_node = DOMNode("pre")
        element = ElementFactory.create_element(dom_node)
        assert isinstance(element, PreElement)

    def test_create_button_element(self) -> None:
        """Test creating button element"""
        from src.html_parser import DOMNode

        dom_node = DOMNode("button")
        element = ElementFactory.create_element(dom_node)
        assert isinstance(element, ButtonElement)

    def test_create_input_element(self) -> None:
        """Test creating input element"""
        from src.html_parser import DOMNode

        dom_node = DOMNode("input")
        element = ElementFactory.create_element(dom_node)
        assert isinstance(element, InputElement)

    def test_create_inline_elements(self) -> None:
        """Test creating inline elements"""
        from src.html_parser import DOMNode

        inline_tags = ["span", "a", "strong", "b", "em", "i", "u", "code"]
        for tag in inline_tags:
            dom_node = DOMNode(tag)
            element = ElementFactory.create_element(dom_node)
            assert isinstance(element, InlineElement)

    def test_create_list_elements(self) -> None:
        """Test creating list elements"""
        from src.html_parser import DOMNode

        list_tags = ["ul", "ol"]
        for tag in list_tags:
            dom_node = DOMNode(tag)
            element = ElementFactory.create_element(dom_node)
            assert isinstance(element, ListElement)

    def test_create_list_item_element(self) -> None:
        """Test creating list item element"""
        from src.html_parser import DOMNode

        dom_node = DOMNode("li")
        element = ElementFactory.create_element(dom_node)
        assert isinstance(element, ListItemElement)

    def test_create_special_elements(self) -> None:
        """Test creating special elements"""
        from src.html_parser import DOMNode

        dom_node = DOMNode("br")
        element = ElementFactory.create_element(dom_node)
        assert isinstance(element, BreakElement)

        dom_node = DOMNode("hr")
        element = ElementFactory.create_element(dom_node)
        assert isinstance(element, HorizontalRuleElement)

    def test_create_table_elements(self) -> None:
        """Test creating table elements"""
        from src.html_parser import DOMNode

        dom_node = DOMNode("table")
        element = ElementFactory.create_element(dom_node)
        assert isinstance(element, TableElement)

        dom_node = DOMNode("tr")
        element = ElementFactory.create_element(dom_node)
        assert isinstance(element, TableRowElement)

        for tag in ["td", "th"]:
            dom_node = DOMNode(tag)
            element = ElementFactory.create_element(dom_node)
            assert isinstance(element, TableCellElement)

    def test_create_unknown_element(self) -> None:
        """Test creating unknown element returns BlockElement"""
        from src.html_parser import DOMNode

        unknown_tags = ["unknown", "custom", "nonexistent"]
        for tag in unknown_tags:
            dom_node = DOMNode(tag)
            element = ElementFactory.create_element(dom_node)
            assert isinstance(element, BlockElement)

    def test_create_element_case_insensitive(self) -> None:
        """Test that element creation is case insensitive"""
        from src.html_parser import DOMNode

        # Most HTML is lowercase, but test uppercase too
        dom_upper = DOMNode("DIV")
        dom_lower = DOMNode("div")
        element_upper = ElementFactory.create_element(dom_upper)
        element_lower = ElementFactory.create_element(dom_lower)

        assert type(element_upper) is type(element_lower)
        assert isinstance(element_upper, BlockElement)

    def test_create_element_with_empty_string(self) -> None:
        """Test creating element with empty string"""
        from src.html_parser import DOMNode

        dom_node = DOMNode("")
        element = ElementFactory.create_element(dom_node)
        assert isinstance(element, BlockElement)  # Default fallback

    def test_create_element_with_whitespace(self) -> None:
        """Test creating element with whitespace"""
        from src.html_parser import DOMNode

        dom_node = DOMNode("  div  ")
        element = ElementFactory.create_element(dom_node)
        assert isinstance(element, BlockElement)

    def test_all_elements_inherit_from_base(self) -> None:
        """Test that all created elements inherit from BaseElement"""
        from src.html_parser import DOMNode

        test_tags = [
            "text",
            "h1",
            "div",
            "span",
            "ul",
            "li",
            "br",
            "hr",
            "table",
            "tr",
            "td",
            "th",
            "unknown",
        ]

        for tag in test_tags:
            dom_node = DOMNode(tag)
            element = ElementFactory.create_element(dom_node)
            assert isinstance(element, BaseElement)

    def test_element_creation_consistency(self) -> None:
        """Test that same tag always creates same element type"""
        from src.html_parser import DOMNode

        dom_node1 = DOMNode("p")
        dom_node2 = DOMNode("p")
        element1 = ElementFactory.create_element(dom_node1)
        element2 = ElementFactory.create_element(dom_node2)

        # Should be same type but different instances
        assert type(element1) is type(element2)
        assert element1 is not element2

    def test_factory_method_signature(self) -> None:
        """Test that factory method has correct signature"""
        # Should accept DOM node and return BaseElement
        import inspect

        sig = inspect.signature(ElementFactory.create_element)
        params = list(sig.parameters.keys())

        assert len(params) == 1
        assert params[0] == "dom_node"

    def test_comprehensive_tag_coverage(self) -> None:
        """Test comprehensive coverage of supported HTML tags"""
        from src.html_parser import DOMNode

        supported_tags = {
            # Text
            "text": TextElement,
            # Headings
            "h1": HeadingElement,
            "h2": HeadingElement,
            "h3": HeadingElement,
            "h4": HeadingElement,
            "h5": HeadingElement,
            "h6": HeadingElement,
            # Block elements
            "div": BlockElement,
            "p": BlockElement,
            "blockquote": BlockElement,
            # Preformatted elements
            "pre": PreElement,
            # Button elements
            "button": ButtonElement,
            # Input elements
            "input": InputElement,
            # Inline elements
            "span": InlineElement,
            "a": InlineElement,
            "strong": InlineElement,
            "b": InlineElement,
            "em": InlineElement,
            "i": InlineElement,
            "u": InlineElement,
            "code": InlineElement,
            # Lists
            "ul": ListElement,
            "ol": ListElement,
            "li": ListItemElement,
            # Special
            "br": BreakElement,
            "hr": HorizontalRuleElement,
            # Table
            "table": TableElement,
            "tr": TableRowElement,
            "td": TableCellElement,
            "th": TableCellElement,
        }

        for tag, expected_type in supported_tags.items():
            dom_node = DOMNode(tag)
            element = ElementFactory.create_element(dom_node)
            assert isinstance(
                element, expected_type
            ), f"Tag '{tag}' should create {expected_type.__name__}"

    def test_factory_is_static(self) -> None:
        """Test that factory method is static"""
        from src.html_parser import DOMNode

        # Should be able to call without instantiating
        dom_node = DOMNode("div")
        element = ElementFactory.create_element(dom_node)
        assert isinstance(element, BlockElement)

        # Method should be a classmethod
        assert hasattr(ElementFactory.create_element, "__func__")

    def test_element_factory_performance(self) -> None:
        """Test factory performance with many elements"""
        import time

        from src.html_parser import DOMNode

        start_time = time.time()
        for _ in range(1000):
            dom_node = DOMNode("div")
            ElementFactory.create_element(dom_node)
        end_time = time.time()

        # Should be fast (less than 1 second for 1000 elements)
        assert (end_time - start_time) < 1.0

    def test_edge_case_tags(self) -> None:
        """Test edge case tag values"""
        from src.html_parser import DOMNode

        # Test with unusual but valid DOM node tags
        edge_cases = [
            DOMNode("unknown"),  # Unknown tag
            DOMNode(""),  # Empty tag
        ]

        for dom_node in edge_cases:
            try:
                # Should either handle gracefully or raise appropriate exception
                element = ElementFactory.create_element(dom_node)
                # If it succeeds, should return a valid element
                assert isinstance(element, BaseElement)
            except (TypeError, AttributeError):
                # Acceptable to raise type errors for invalid input
                pass
