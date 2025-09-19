from enum import Enum
import os

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


def extract_title(markdown):
    """Extract the h1 header from markdown content"""
    lines = markdown.split('\n')
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('# ') and not stripped.startswith('##'):
            # Found h1 header, extract title
            return stripped[2:].strip()
    
    # No h1 header found
    raise Exception("No h1 header found in markdown")


def generate_page(from_path, template_path, dest_path, basepath="/"):
    """Generate an HTML page from markdown using a template"""
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")
    
    # Read markdown file
    with open(from_path, 'r') as f:
        markdown_content = f.read()
    
    # Read template file
    with open(template_path, 'r') as f:
        template_content = f.read()
    
    # Convert markdown to HTML
    html_node = markdown_to_html_node(markdown_content)
    html_content = html_node.to_html()
    
    # Extract title
    title = extract_title(markdown_content)
    
    # Replace placeholders in template
    final_html = template_content.replace("{{ Title }}", title).replace("{{ Content }}", html_content)
    
    # Replace href="/" and src="/" with basepath (for absolute paths)
    final_html = final_html.replace('href="/', f'href="{basepath}')
    final_html = final_html.replace('src="/', f'src="{basepath}')
    
    # Replace specific relative paths that need basepath
    final_html = final_html.replace('href="index.css"', f'href="{basepath}index.css"')
    final_html = final_html.replace('href="/"', f'href="{basepath}"')
    
    # Create destination directory if it doesn't exist
    dest_dir = os.path.dirname(dest_path)
    os.makedirs(dest_dir, exist_ok=True)
    
    # Write the final HTML to destination
    with open(dest_path, 'w') as f:
        f.write(final_html)


def generate_pages_recursive(dir_path_content, template_path, dest_dir_path, basepath="/"):
    """Recursively generate HTML pages for all markdown files in content directory"""
    for item in os.listdir(dir_path_content):
        item_path = os.path.join(dir_path_content, item)
        
        if os.path.isfile(item_path) and item.endswith('.md'):
            # This is a markdown file, generate HTML
            # Remove .md extension and add .html
            html_filename = item.replace('.md', '.html')
            
            # Build destination path maintaining directory structure
            # Get relative path from content directory
            rel_path = os.path.relpath(item_path, dir_path_content)
            # Replace .md with .html
            rel_html_path = rel_path.replace('.md', '.html')
            # Build full destination path
            dest_path = os.path.join(dest_dir_path, rel_html_path)
            
            # Generate the page
            generate_page(item_path, template_path, dest_path, basepath)
            
        elif os.path.isdir(item_path):
            # This is a directory, recurse into it
            # Create corresponding directory in destination
            dest_subdir = os.path.join(dest_dir_path, item)
            os.makedirs(dest_subdir, exist_ok=True)
            
            # Recurse
            generate_pages_recursive(item_path, template_path, dest_subdir, basepath)