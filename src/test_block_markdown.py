import unittest

from block_markdown import markdown_to_blocks, BlockType, block_to_block_type, markdown_to_html_node, extract_title


class TestMarkdownToBlocks(unittest.TestCase):
    def test_markdown_to_blocks(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )

    def test_markdown_to_blocks_single_block(self):
        md = "This is a single paragraph with no blank lines."
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, ["This is a single paragraph with no blank lines."])

    def test_markdown_to_blocks_multiple_blank_lines(self):
        md = """
First block



Second block
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, ["First block", "Second block"])

    def test_markdown_to_blocks_leading_trailing_whitespace(self):
        md = """
   Leading whitespace

Trailing whitespace   
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, ["Leading whitespace", "Trailing whitespace"])

    def test_markdown_to_blocks_empty_string(self):
        md = ""
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, [])

    def test_markdown_to_blocks_only_whitespace(self):
        md = "   \n\n   \n\n   "
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, [])

    def test_markdown_to_blocks_code_block(self):
        md = """
```python
def hello():
    print("Hello, World!")
```

This is regular text.
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, [
            "```python\ndef hello():\n    print(\"Hello, World!\")\n```",
            "This is regular text."
        ])

    def test_markdown_to_blocks_headings_and_paragraphs(self):
        md = """
# Heading 1

This is a paragraph.

## Heading 2

Another paragraph with **bold** text.
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, [
            "# Heading 1",
            "This is a paragraph.",
            "## Heading 2",
            "Another paragraph with **bold** text."
        ])


class TestBlockToBlockType(unittest.TestCase):
    def test_paragraph(self):
        block = "This is a simple paragraph with some text."
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_heading_h1(self):
        block = "# This is a heading"
        self.assertEqual(block_to_block_type(block), BlockType.HEADING)

    def test_heading_h2(self):
        block = "## This is a heading"
        self.assertEqual(block_to_block_type(block), BlockType.HEADING)

    def test_heading_h6(self):
        block = "###### This is a heading"
        self.assertEqual(block_to_block_type(block), BlockType.HEADING)

    def test_heading_invalid_no_space(self):
        block = "#This is not a heading"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_heading_invalid_too_many_hashes(self):
        block = "####### This is not a heading"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_code_block(self):
        block = "```python\ndef hello():\n    print('Hello')\n```"
        self.assertEqual(block_to_block_type(block), BlockType.CODE)

    def test_code_block_single_line(self):
        block = "```code```"
        self.assertEqual(block_to_block_type(block), BlockType.CODE)

    def test_code_block_no_closing(self):
        block = "```python\nsome code"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_quote(self):
        block = "> This is a quote\n> Another line"
        self.assertEqual(block_to_block_type(block), BlockType.QUOTE)

    def test_quote_single_line(self):
        block = "> This is a quote"
        self.assertEqual(block_to_block_type(block), BlockType.QUOTE)

    def test_quote_invalid_missing_quote(self):
        block = "> This is a quote\nThis is not"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_unordered_list(self):
        block = "- Item 1\n- Item 2\n- Item 3"
        self.assertEqual(block_to_block_type(block), BlockType.UNORDERED_LIST)

    def test_unordered_list_single_item(self):
        block = "- Single item"
        self.assertEqual(block_to_block_type(block), BlockType.UNORDERED_LIST)

    def test_unordered_list_invalid_no_space(self):
        block = "-Item 1\n-Item 2"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_unordered_list_invalid_missing_dash(self):
        block = "- Item 1\nItem 2"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_ordered_list(self):
        block = "1. Item 1\n2. Item 2\n3. Item 3"
        self.assertEqual(block_to_block_type(block), BlockType.ORDERED_LIST)

    def test_ordered_list_single_item(self):
        block = "1. Single item"
        self.assertEqual(block_to_block_type(block), BlockType.ORDERED_LIST)

    def test_ordered_list_invalid_wrong_number(self):
        block = "1. Item 1\n3. Item 2"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_ordered_list_invalid_no_space(self):
        block = "1.Item 1\n2.Item 2"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_ordered_list_invalid_wrong_start(self):
        block = "2. Item 1\n3. Item 2"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)


class TestMarkdownToHTMLNode(unittest.TestCase):
    def test_paragraphs(self):
        md = """
This is **bolded** paragraph
text in a p
tag here

This is another paragraph with _italic_ text and `code` here

"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
        )

    def test_codeblock(self):
        md = """
```
This is text that _should_ remain
the **same** even with inline stuff
```
"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><pre><code>This is text that _should_ remain\nthe **same** even with inline stuff\n</code></pre></div>",
        )

    def test_headings(self):
        md = "# Heading 1\n\n## Heading 2"
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(html, "<div><h1>Heading 1</h1><h2>Heading 2</h2></div>")

    def test_quote(self):
        md = "> This is a quote\n> with multiple lines"
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(html, "<div><blockquote>This is a quote\nwith multiple lines</blockquote></div>")

    def test_unordered_list(self):
        md = "- Item 1\n- Item 2 with **bold**"
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(html, "<div><ul><li>Item 1</li><li>Item 2 with <b>bold</b></li></ul></div>")

    def test_ordered_list(self):
        md = "1. First item\n2. Second item with `code`"
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(html, "<div><ol><li>First item</li><li>Second item with <code>code</code></li></ol></div>")

    def test_mixed_blocks(self):
        md = "# Title\n\nA paragraph with **bold**.\n\n- List item\n- Another item"
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(html, "<div><h1>Title</h1><p>A paragraph with <b>bold</b>.</p><ul><li>List item</li><li>Another item</li></ul></div>")

    def test_empty_markdown(self):
        md = ""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(html, "<div></div>")


class TestExtractTitle(unittest.TestCase):
    def test_extract_title(self):
        md = "# Hello World"
        self.assertEqual(extract_title(md), "Hello World")

    def test_extract_title_with_whitespace(self):
        md = "#   Hello World   "
        self.assertEqual(extract_title(md), "Hello World")

    def test_extract_title_multiline(self):
        md = """
Some text here
# My Title
More content
"""
        self.assertEqual(extract_title(md), "My Title")

    def test_extract_title_no_h1(self):
        md = """
## This is h2
### This is h3
No h1 here
"""
        with self.assertRaises(Exception):
            extract_title(md)

    def test_extract_title_h1_with_other_headers(self):
        md = """
# Main Title
## Subtitle
### Sub-subtitle
"""
        self.assertEqual(extract_title(md), "Main Title")


if __name__ == "__main__":
    unittest.main()