import unittest

from markdown_extract import extract_markdown_images, extract_markdown_links


class TestMarkdownExtract(unittest.TestCase):
    def test_extract_markdown_images(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)

    def test_extract_markdown_images_multiple(self):
        text = "This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)"
        matches = extract_markdown_images(text)
        expected = [("rick roll", "https://i.imgur.com/aKaOqIh.gif"), ("obi wan", "https://i.imgur.com/fJRm4Vk.jpeg")]
        self.assertListEqual(expected, matches)

    def test_extract_markdown_images_no_images(self):
        matches = extract_markdown_images("This is text with no images")
        self.assertListEqual([], matches)

    def test_extract_markdown_links(self):
        text = "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)"
        matches = extract_markdown_links(text)
        expected = [("to boot dev", "https://www.boot.dev"), ("to youtube", "https://www.youtube.com/@bootdotdev")]
        self.assertListEqual(expected, matches)

    def test_extract_markdown_links_no_links(self):
        matches = extract_markdown_links("This is text with no links")
        self.assertListEqual([], matches)

    def test_extract_markdown_links_with_images(self):
        text = "This is text with a link [to boot dev](https://www.boot.dev) and an ![image](https://i.imgur.com/zjjcJKZ.png)"
        matches = extract_markdown_links(text)
        expected = [("to boot dev", "https://www.boot.dev")]
        self.assertListEqual(expected, matches)

    def test_extract_markdown_images_with_links(self):
        text = "This is text with a link [to boot dev](https://www.boot.dev) and an ![image](https://i.imgur.com/zjjcJKZ.png)"
        matches = extract_markdown_images(text)
        expected = [("image", "https://i.imgur.com/zjjcJKZ.png")]
        self.assertListEqual(expected, matches)

    def test_extract_markdown_empty_alt_text(self):
        matches = extract_markdown_images("This is text with an ![](/path/to/image.png)")
        self.assertListEqual([("", "/path/to/image.png")], matches)

    def test_extract_markdown_empty_link_text(self):
        matches = extract_markdown_links("This is text with a [](https://www.example.com)")
        self.assertListEqual([("", "https://www.example.com")], matches)

    def test_extract_markdown_complex_urls(self):
        text = "Check out [this link](https://www.example.com/path?query=value&other=123)"
        matches = extract_markdown_links(text)
        expected = [("this link", "https://www.example.com/path?query=value&other=123")]
        self.assertListEqual(expected, matches)

    def test_extract_markdown_multiple_spaces(self):
        text = "This is [link with spaces](https://example.com) and ![image with spaces](https://img.com/pic.jpg)"
        link_matches = extract_markdown_links(text)
        image_matches = extract_markdown_images(text)
        self.assertListEqual([("link with spaces", "https://example.com")], link_matches)
        self.assertListEqual([("image with spaces", "https://img.com/pic.jpg")], image_matches)


if __name__ == "__main__":
    unittest.main()