from textnode import TextNode, TextType
from markdown_extract import extract_markdown_images, extract_markdown_links

def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes = []
    for node in old_nodes:
        if node.text_type not in [TextType.TEXT]:
            # Don't process delimiters in LINK, IMAGE, or other special nodes
            new_nodes.append(node)
            continue
        
        # Split the text by delimiter
        parts = node.text.split(delimiter)
        
        # Check for unmatched delimiters
        if len(parts) % 2 == 0:
            # Unmatched delimiters - treat as regular text
            new_nodes.append(node)
            continue
        
        # Process each part
        for i, part in enumerate(parts):
            if i % 2 == 0:
                # Even index: regular text
                if part:  # Only add if not empty
                    new_nodes.append(TextNode(part, TextType.TEXT))
            else:
                # Odd index: delimited text
                new_nodes.append(TextNode(part, text_type))
    
    return new_nodes


def split_nodes_image(old_nodes):
    new_nodes = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue
        
        # Extract images from the text
        images = extract_markdown_images(node.text)
        
        if not images:
            # No images found, keep the original node
            new_nodes.append(node)
            continue
        
        # Split the text around each image
        remaining_text = node.text
        for alt_text, url in images:
            # Find the markdown pattern
            markdown_pattern = f"![{alt_text}]({url})"
            
            # Split the remaining text by this pattern (only once)
            parts = remaining_text.split(markdown_pattern, 1)
            
            # Add the text before the image (if not empty)
            if parts[0]:
                new_nodes.append(TextNode(parts[0], TextType.TEXT))
            
            # Add the image node
            new_nodes.append(TextNode(alt_text, TextType.IMAGE, url))
            
            # Update remaining text for next iteration
            remaining_text = parts[1] if len(parts) > 1 else ""
        
        # Add any remaining text after the last image
        if remaining_text:
            new_nodes.append(TextNode(remaining_text, TextType.TEXT))
    
    return new_nodes


def split_nodes_link(old_nodes):
    new_nodes = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue
        
        # Extract links from the text
        links = extract_markdown_links(node.text)
        
        if not links:
            # No links found, keep the original node
            new_nodes.append(node)
            continue
        
        # Split the text around each link
        remaining_text = node.text
        for anchor_text, url in links:
            # Find the markdown pattern
            markdown_pattern = f"[{anchor_text}]({url})"
            
            # Split the remaining text by this pattern (only once)
            parts = remaining_text.split(markdown_pattern, 1)
            
            # Add the text before the link (if not empty)
            if parts[0]:
                new_nodes.append(TextNode(parts[0], TextType.TEXT))
            
            # Add the link node
            new_nodes.append(TextNode(anchor_text, TextType.LINK, url))
            
            # Update remaining text for next iteration
            remaining_text = parts[1] if len(parts) > 1 else ""
        
        # Add any remaining text after the last link
        if remaining_text:
            new_nodes.append(TextNode(remaining_text, TextType.TEXT))
    
    return new_nodes


def text_to_textnodes(text):
    # Start with a single TEXT node containing the entire text
    nodes = [TextNode(text, TextType.TEXT)]
    
    # Apply splitting functions in order
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    
    return nodes