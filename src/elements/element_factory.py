"""
Element factory for creating appropriate element instances
"""

from typing import Optional

from ..html_parser import DOMNode
from .base import BaseElement
from .block import BlockElement
from .heading import HeadingElement
from .inline import InlineElement
from .list import ListElement, ListItemElement
from .special import BreakElement, HorizontalRuleElement
from .table import TableCellElement, TableElement, TableRowElement
from .text import TextElement


class ElementFactory:
    """Factory for creating element instances based on DOM node tags"""

    # Heading tags
    HEADING_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6"}

    # Block-level tags
    BLOCK_TAGS = {"p", "div", "blockquote", "pre"}

    # List tags
    LIST_TAGS = {"ul", "ol"}

    # Inline formatting tags
    INLINE_TAGS = {"b", "i", "u", "strong", "em", "code", "span", "a"}

    # Table tags
    TABLE_TAGS = {"table"}
    TABLE_ROW_TAGS = {"tr"}
    TABLE_CELL_TAGS = {"td", "th"}

    # Special tags
    BREAK_TAGS = {"br"}
    HR_TAGS = {"hr"}

    @classmethod
    def create_element(cls, dom_node: DOMNode) -> Optional[BaseElement]:
        """Create appropriate element instance for the given DOM node"""
        tag = dom_node.tag

        if tag == "text":
            return TextElement(dom_node)
        elif tag in cls.HEADING_TAGS:
            return HeadingElement(dom_node)
        elif tag in cls.BLOCK_TAGS:
            return BlockElement(dom_node)
        elif tag in cls.LIST_TAGS:
            return ListElement(dom_node)
        elif tag == "li":
            return ListItemElement(dom_node)
        elif tag in cls.INLINE_TAGS:
            return InlineElement(dom_node)
        elif tag in cls.TABLE_TAGS:
            return TableElement(dom_node)
        elif tag in cls.TABLE_ROW_TAGS:
            return TableRowElement(dom_node)
        elif tag in cls.TABLE_CELL_TAGS:
            return TableCellElement(dom_node)
        elif tag in cls.BREAK_TAGS:
            return BreakElement(dom_node)
        elif tag in cls.HR_TAGS:
            return HorizontalRuleElement(dom_node)
        else:
            # Default to block element for unknown tags
            return BlockElement(dom_node)
