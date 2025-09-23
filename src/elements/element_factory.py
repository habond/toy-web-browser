"""
Element factory for creating appropriate element instances
"""

from typing import Dict, Optional, Type

from ..html_parser import DOMNode
from .base import BaseElement
from .block import BlockElement
from .button import ButtonElement
from .heading import HeadingElement
from .inline import InlineElement
from .input import InputElement
from .list import ListElement, ListItemElement
from .pre import PreElement
from .select import OptionElement, SelectElement
from .special import BreakElement, HorizontalRuleElement
from .table import TableCellElement, TableElement, TableRowElement
from .text import TextElement


class ElementFactory:
    """Factory for creating element instances based on DOM node tags"""

    # Heading tags
    HEADING_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6"}

    # Block-level tags
    BLOCK_TAGS = {"p", "div", "blockquote"}

    # Preformatted tags
    PRE_TAGS = {"pre"}

    # Button tags
    BUTTON_TAGS = {"button"}

    # Input tags
    INPUT_TAGS = {"input"}

    # Select tags
    SELECT_TAGS = {"select"}
    OPTION_TAGS = {"option"}

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

    # Tag to element class mapping
    TAG_TO_ELEMENT: Dict[str, Type[BaseElement]] = {
        # Text element
        "text": TextElement,
        # Heading elements
        **{tag: HeadingElement for tag in HEADING_TAGS},
        # Block elements
        **{tag: BlockElement for tag in BLOCK_TAGS},
        # Preformatted elements
        **{tag: PreElement for tag in PRE_TAGS},
        # Button elements
        **{tag: ButtonElement for tag in BUTTON_TAGS},
        # Input elements
        **{tag: InputElement for tag in INPUT_TAGS},
        # Select elements
        **{tag: SelectElement for tag in SELECT_TAGS},
        **{tag: OptionElement for tag in OPTION_TAGS},
        # List elements
        **{tag: ListElement for tag in LIST_TAGS},
        "li": ListItemElement,  # Special case for list items
        # Inline elements
        **{tag: InlineElement for tag in INLINE_TAGS},
        # Table elements
        **{tag: TableElement for tag in TABLE_TAGS},
        **{tag: TableRowElement for tag in TABLE_ROW_TAGS},
        **{tag: TableCellElement for tag in TABLE_CELL_TAGS},
        # Special elements
        **{tag: BreakElement for tag in BREAK_TAGS},
        **{tag: HorizontalRuleElement for tag in HR_TAGS},
    }

    @classmethod
    def create_element(cls, dom_node: DOMNode) -> Optional[BaseElement]:
        """Create appropriate element instance for the given DOM node"""
        tag = dom_node.tag

        # Look up element class in mapping, default to BlockElement for unknown tags
        element_class = cls.TAG_TO_ELEMENT.get(tag, BlockElement)
        return element_class(dom_node)
