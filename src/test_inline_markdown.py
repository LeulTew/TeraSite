import unittest

from textnode import TextNode, TextType
from inline_markdown import split_nodes_delimiter, split_nodes_image, split_nodes_link, text_to_textnodes


class TestSplitNodesDelimiter(unittest.TestCase):
    def test_split_code_block(self):
        node = TextNode("This is text with a `code block` word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        expected = [
            TextNode("This is text with a ", TextType.TEXT),
            TextNode("code block", TextType.CODE),
            TextNode(" word", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)

    def test_split_bold_text(self):
        node = TextNode("This is **bold** text", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode(" text", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)

    def test_split_italic_text(self):
        node = TextNode("This is _italic_ text", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "_", TextType.ITALIC)
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" text", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)

    def test_no_delimiter(self):
        node = TextNode("This is plain text", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        expected = [TextNode("This is plain text", TextType.TEXT)]
        self.assertEqual(new_nodes, expected)

    def test_multiple_delimiters(self):
        node = TextNode("This `code` and `more code` here", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        expected = [
            TextNode("This ", TextType.TEXT),
            TextNode("code", TextType.CODE),
            TextNode(" and ", TextType.TEXT),
            TextNode("more code", TextType.CODE),
            TextNode(" here", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)

    def test_non_text_node_passthrough(self):
        node1 = TextNode("plain", TextType.TEXT)
        node2 = TextNode("bold", TextType.BOLD)
        node3 = TextNode("more plain", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node1, node2, node3], "`", TextType.CODE)
        expected = [
            TextNode("plain", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode("more plain", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)

    def test_unmatched_delimiter(self):
        node = TextNode("This has an unmatched `delimiter", TextType.TEXT)
        with self.assertRaises(ValueError):
            split_nodes_delimiter([node], "`", TextType.CODE)

    def test_empty_string_between_delimiters(self):
        node = TextNode("Empty `` delimiters", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        expected = [
            TextNode("Empty ", TextType.TEXT),
            TextNode("", TextType.CODE),
            TextNode(" delimiters", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)

    def test_delimiter_at_start(self):
        node = TextNode("`code` at start", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        expected = [
            TextNode("code", TextType.CODE),
            TextNode(" at start", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)

    def test_delimiter_at_end(self):
        node = TextNode("End with `code`", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        expected = [
            TextNode("End with ", TextType.TEXT),
            TextNode("code", TextType.CODE),
        ]
        self.assertEqual(new_nodes, expected)


class TestSplitNodesImage(unittest.TestCase):
    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
        )

    def test_no_images(self):
        node = TextNode("This is text with no images", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        expected = [TextNode("This is text with no images", TextType.TEXT)]
        self.assertEqual(new_nodes, expected)

    def test_image_at_start(self):
        node = TextNode("![start image](https://example.com/start.png) then text", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        expected = [
            TextNode("start image", TextType.IMAGE, "https://example.com/start.png"),
            TextNode(" then text", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)

    def test_image_at_end(self):
        node = TextNode("Text before ![end image](https://example.com/end.png)", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        expected = [
            TextNode("Text before ", TextType.TEXT),
            TextNode("end image", TextType.IMAGE, "https://example.com/end.png"),
        ]
        self.assertEqual(new_nodes, expected)

    def test_single_image(self):
        node = TextNode("Just ![one image](https://example.com/one.png)", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        expected = [
            TextNode("Just ", TextType.TEXT),
            TextNode("one image", TextType.IMAGE, "https://example.com/one.png"),
        ]
        self.assertEqual(new_nodes, expected)

    def test_non_text_node_passthrough_image(self):
        node1 = TextNode("plain text", TextType.TEXT)
        node2 = TextNode("bold text", TextType.BOLD)
        new_nodes = split_nodes_image([node1, node2])
        expected = [
            TextNode("plain text", TextType.TEXT),
            TextNode("bold text", TextType.BOLD),
        ]
        self.assertEqual(new_nodes, expected)


class TestSplitNodesLink(unittest.TestCase):
    def test_split_links(self):
        node = TextNode(
            "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("This is text with a link ", TextType.TEXT),
            TextNode("to boot dev", TextType.LINK, "https://www.boot.dev"),
            TextNode(" and ", TextType.TEXT),
            TextNode(
                "to youtube", TextType.LINK, "https://www.youtube.com/@bootdotdev"
            ),
        ]
        self.assertEqual(new_nodes, expected)

    def test_no_links(self):
        node = TextNode("This is text with no links", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        expected = [TextNode("This is text with no links", TextType.TEXT)]
        self.assertEqual(new_nodes, expected)

    def test_link_at_start(self):
        node = TextNode("[start link](https://example.com/start) then text", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("start link", TextType.LINK, "https://example.com/start"),
            TextNode(" then text", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)

    def test_link_at_end(self):
        node = TextNode("Text before [end link](https://example.com/end)", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("Text before ", TextType.TEXT),
            TextNode("end link", TextType.LINK, "https://example.com/end"),
        ]
        self.assertEqual(new_nodes, expected)

    def test_single_link(self):
        node = TextNode("Just [one link](https://example.com/one)", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("Just ", TextType.TEXT),
            TextNode("one link", TextType.LINK, "https://example.com/one"),
        ]
        self.assertEqual(new_nodes, expected)

    def test_non_text_node_passthrough_link(self):
        node1 = TextNode("plain text", TextType.TEXT)
        node2 = TextNode("bold text", TextType.BOLD)
        new_nodes = split_nodes_link([node1, node2])
        expected = [
            TextNode("plain text", TextType.TEXT),
            TextNode("bold text", TextType.BOLD),
        ]
        self.assertEqual(new_nodes, expected)

    def test_mixed_links_and_images(self):
        # This tests that links are extracted correctly even with images present
        node = TextNode(
            "Text [link](https://example.com) and ![image](https://img.com/pic.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("Text ", TextType.TEXT),
            TextNode("link", TextType.LINK, "https://example.com"),
            TextNode(" and ![image](https://img.com/pic.png)", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)


class TestTextToTextNodes(unittest.TestCase):
    def test_text_to_textnodes(self):
        text = "This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("text", TextType.BOLD),
            TextNode(" with an ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" word and a ", TextType.TEXT),
            TextNode("code block", TextType.CODE),
            TextNode(" and an ", TextType.TEXT),
            TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
            TextNode(" and a ", TextType.TEXT),
            TextNode("link", TextType.LINK, "https://boot.dev"),
        ]
        self.assertEqual(nodes, expected)

    def test_text_to_textnodes_plain_text(self):
        text = "This is just plain text"
        nodes = text_to_textnodes(text)
        expected = [TextNode("This is just plain text", TextType.TEXT)]
        self.assertEqual(nodes, expected)

    def test_text_to_textnodes_only_bold(self):
        text = "**Just bold text**"
        nodes = text_to_textnodes(text)
        expected = [TextNode("Just bold text", TextType.BOLD)]
        self.assertEqual(nodes, expected)

    def test_text_to_textnodes_only_italic(self):
        text = "_Just italic text_"
        nodes = text_to_textnodes(text)
        expected = [TextNode("Just italic text", TextType.ITALIC)]
        self.assertEqual(nodes, expected)

    def test_text_to_textnodes_only_code(self):
        text = "`Just code text`"
        nodes = text_to_textnodes(text)
        expected = [TextNode("Just code text", TextType.CODE)]
        self.assertEqual(nodes, expected)

    def test_text_to_textnodes_only_image(self):
        text = "![alt text](https://example.com/image.png)"
        nodes = text_to_textnodes(text)
        expected = [TextNode("alt text", TextType.IMAGE, "https://example.com/image.png")]
        self.assertEqual(nodes, expected)

    def test_text_to_textnodes_only_link(self):
        text = "[link text](https://example.com)"
        nodes = text_to_textnodes(text)
        expected = [TextNode("link text", TextType.LINK, "https://example.com")]
        self.assertEqual(nodes, expected)

    def test_text_to_textnodes_mixed_delimiters(self):
        text = "**Bold** and _italic_ and `code`"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("Bold", TextType.BOLD),
            TextNode(" and ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" and ", TextType.TEXT),
            TextNode("code", TextType.CODE),
        ]
        self.assertEqual(nodes, expected)


if __name__ == "__main__":
    unittest.main()