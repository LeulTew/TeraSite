import os
import shutil
import sys
from textnode import TextNode, TextType
from block_markdown import generate_page, generate_pages_recursive

def copy_static_to_public(src_dir, dest_dir):
    """
    Recursively copy all contents from source directory to destination directory.
    First deletes all contents of destination directory to ensure clean copy.
    """
    # Delete destination directory contents if it exists
    if os.path.exists(dest_dir):
        print(f"Deleting contents of {dest_dir}")
        shutil.rmtree(dest_dir)
    
    # Create destination directory
    os.makedirs(dest_dir, exist_ok=True)
    print(f"Created directory {dest_dir}")
    
    # Copy all files and directories recursively
    _copy_directory_contents(src_dir, dest_dir)

def _copy_directory_contents(src_dir, dest_dir):
    """Helper function to recursively copy directory contents"""
    for item in os.listdir(src_dir):
        src_path = os.path.join(src_dir, item)
        dest_path = os.path.join(dest_dir, item)
        
        if os.path.isfile(src_path):
            # Copy file
            shutil.copy(src_path, dest_path)
            print(f"Copied file: {src_path} -> {dest_path}")
        elif os.path.isdir(src_path):
            # Create directory and recurse
            os.makedirs(dest_path, exist_ok=True)
            print(f"Created directory: {dest_path}")
            _copy_directory_contents(src_path, dest_path)

def main():
    # Get the project root directory (parent of src/)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Get basepath from command line argument, default to "/"
    basepath = sys.argv[1] if len(sys.argv) > 1 else "/"
    
    # Copy static files to docs directory
    static_dir = os.path.join(project_root, "static")
    docs_dir = os.path.join(project_root, "docs")
    
    print("Starting static site generation...")
    copy_static_to_public(static_dir, docs_dir)
    
    # Generate all pages recursively
    content_dir = os.path.join(project_root, "content")
    template_path = os.path.join(project_root, "template.html")
    
    generate_pages_recursive(content_dir, template_path, docs_dir, basepath)
    
    print("Static site generation complete!")
    
    # Original demo code
    node = TextNode("This is some anchor text", TextType.LINK, "https://www.boot.dev")
    print(node)

if __name__ == "__main__":
    main()