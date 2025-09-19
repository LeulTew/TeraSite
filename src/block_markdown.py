from enum import Enum

from htmlnode import HTMLNode, LeafNode, ParentNode, text_node_to_html_node
from inline_markdown import text_to_textnodes
from markdown_extract import extract_markdown_images, extract_markdown_links


def markdown_to_blocks(markdown):
    # Split by double newlines
    blocks = markdown.split('\n\n')
    
    # Strip whitespace and filter out empty blocks
    cleaned_blocks = []
    for block in blocks:
        stripped = block.strip()
        if stripped:  # Only add non-empty blocks
            cleaned_blocks.append(stripped)
    
    return cleaned_blocks


class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"


def block_to_block_type(block):
    lines = block.split('\n')
    
    # Check for heading (1-6 # followed by space)
    if lines[0].startswith('#'):
        parts = lines[0].split(' ', 1)
        if len(parts) == 2 and parts[0].count('#') <= 6 and parts[0].count('#') >= 1 and all(c == '#' for c in parts[0]):
            return BlockType.HEADING
    
    # Check for code block (starts and ends with ```)
    if block.startswith('```') and block.endswith('```'):
        return BlockType.CODE
    
    # Check for quote (every line starts with >)
    if all(line.startswith('>') for line in lines):
        return BlockType.QUOTE
    
    # Check for unordered list (every line starts with - followed by space)
    if all(line.startswith('- ') for line in lines):
        return BlockType.UNORDERED_LIST
    
    # Check for ordered list (every line starts with number. space, incrementing from 1)
    if len(lines) > 0:
        expected_num = 1
        is_ordered_list = True
        for line in lines:
            if not line.startswith(f"{expected_num}. "):
                is_ordered_list = False
                break
            expected_num += 1
        if is_ordered_list:
            return BlockType.ORDERED_LIST
    
    # Default to paragraph
    return BlockType.PARAGRAPH


def text_to_children(text):
    """Convert text with inline markdown to list of HTMLNodes"""
    text_nodes = text_to_textnodes(text)
    html_nodes = []
    for text_node in text_nodes:
        html_nodes.append(text_node_to_html_node(text_node))
    return html_nodes


def markdown_to_html_node(markdown):
    """Convert full markdown document to single parent HTMLNode"""
    blocks = markdown_to_blocks(markdown)
    parent = ParentNode("div", [])
    
    for block in blocks:
        block_type = block_to_block_type(block)
        
        if block_type == BlockType.HEADING:
            # Extract heading level and text
            lines = block.split('\n', 1)
            heading_line = lines[0]
            hash_count = heading_line.count('#')
            heading_text = heading_line.lstrip('#').strip()
            
            # Create heading node with inline children
            children = text_to_children(heading_text)
            heading_node = ParentNode(f"h{hash_count}", children)
            parent.children.append(heading_node)
            
        elif block_type == BlockType.CODE:
            # Extract code content (remove ``` markers)
            lines = block.split('\n')
            if len(lines) >= 3:
                code_content = '\n'.join(lines[1:-1])
            else:
                # Single line code block
                code_content = block.strip('`')
            
            # Add trailing newline for code blocks
            if not code_content.endswith('\n'):
                code_content += '\n'
            
            # Code blocks don't parse inline markdown
            code_node = ParentNode("pre", [LeafNode("code", code_content)])
            parent.children.append(code_node)
            
        elif block_type == BlockType.QUOTE:
            # Remove > from each line
            quote_lines = []
            for line in block.split('\n'):
                if line.startswith('>'):
                    quote_lines.append(line[1:].lstrip())
                else:
                    quote_lines.append(line)
            quote_text = '\n'.join(quote_lines)
            
            # Create blockquote with inline children
            children = text_to_children(quote_text)
            quote_node = ParentNode("blockquote", children)
            parent.children.append(quote_node)
            
        elif block_type == BlockType.UNORDERED_LIST:
            list_items = []
            for line in block.split('\n'):
                if line.startswith('- '):
                    item_text = line[2:]  # Remove "- "
                    children = text_to_children(item_text)
                    list_items.append(ParentNode("li", children))
            
            ul_node = ParentNode("ul", list_items)
            parent.children.append(ul_node)
            
        elif block_type == BlockType.ORDERED_LIST:
            list_items = []
            for line in block.split('\n'):
                # Extract text after "X. "
                parts = line.split('. ', 1)
                if len(parts) == 2:
                    item_text = parts[1]
                    children = text_to_children(item_text)
                    list_items.append(ParentNode("li", children))
            
            ol_node = ParentNode("ol", list_items)
            parent.children.append(ol_node)
            
        elif block_type == BlockType.PARAGRAPH:
            # Convert newlines to spaces for paragraphs
            paragraph_text = block.replace('\n', ' ')
            # Create paragraph with inline children
            children = text_to_children(paragraph_text)
            para_node = ParentNode("p", children)
            parent.children.append(para_node)
    
    return parent