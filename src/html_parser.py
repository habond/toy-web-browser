"""
HTML Parser - Parses HTML into a simple DOM tree
"""

from html.parser import HTMLParser as BaseHTMLParser
from typing import Dict, List, Optional, Tuple


class DOMNode:
    """Represents a node in the DOM tree"""

    def __init__(
        self,
        tag: str,
        attrs: Optional[Dict[str, str]] = None,
        text: Optional[str] = None,
    ) -> None:
        self.tag: str = tag
        self.attrs: Dict[str, str] = attrs or {}
        self.text: Optional[str] = text
        self.children: List[DOMNode] = []
        self.parent: Optional[DOMNode] = None

    def add_child(self, child: "DOMNode") -> None:
        child.parent = self
        self.children.append(child)

    def __repr__(self) -> str:
        if self.tag == "text":
            if self.text and len(self.text) > 20:
                return f"Text('{self.text[:20]}...')"
            return f"Text('{self.text}')"
        return f"<{self.tag}>"


class HTMLParser(BaseHTMLParser):
    """Parses HTML and builds a DOM tree"""

    BLOCK_TAGS: set[str] = {
        "html",
        "body",
        "div",
        "p",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "ul",
        "ol",
        "li",
        "br",
        "hr",
        "blockquote",
        "pre",
    }
    INLINE_TAGS: set[str] = {"a", "span", "b", "i", "u", "strong", "em", "code"}
    VOID_TAGS: set[str] = {"br", "hr", "img"}

    def __init__(self) -> None:
        super().__init__()
        self.root: DOMNode = DOMNode("root")
        self.current: DOMNode = self.root
        self.stack: List[DOMNode] = []

    def parse(self, html_content: str) -> DOMNode:
        """Parse HTML content and return root node"""
        self.root = DOMNode("root")
        self.current = self.root
        self.stack = [self.root]

        self.feed(html_content)

        return self.root

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        """Handle opening tags"""
        # Convert attrs to dict, handling None values
        attr_dict = {k: v if v is not None else "" for k, v in attrs}

        if tag in self.VOID_TAGS:
            node = DOMNode(tag, attr_dict)
            self.current.add_child(node)
        else:
            node = DOMNode(tag, attr_dict)
            self.current.add_child(node)
            self.stack.append(node)
            self.current = node

    def handle_endtag(self, tag: str) -> None:
        """Handle closing tags"""
        if tag in self.VOID_TAGS:
            return

        # Find matching opening tag in stack
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i].tag == tag:
                # Close all tags up to this one
                self.stack = self.stack[:i]
                self.current = self.stack[-1] if self.stack else self.root
                break

    def handle_data(self, data: str) -> None:
        """Handle text content"""
        text = data.strip()
        if text:
            text_node = DOMNode("text", text=text)
            self.current.add_child(text_node)
