import os
from typing import Dict, Any
import markdown

def create_folder_structure(base_path: str) -> None:
    """
    Create the necessary folder structure if it doesn't exist.
    """
    os.makedirs(base_path, exist_ok=True)
    os.makedirs(os.path.join(base_path, 'markdown'), exist_ok=True)
    os.makedirs(os.path.join(base_path, 'html'), exist_ok=True)

def write_markdown_file(content: str, file_path: str) -> None:
    """
    Write the given content as a markdown file at the specified path.
    """
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def write_text_file(content: str, file_path: str) -> None:
    """
    Write the given content as a text file at the specified path.
    """
    html = markdown.markdown(content)
    text = ''.join(markdown.Markdown().convert(html).split('\n'))
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(text)

def write_weblog(weblog: Dict[str, Any], output_dir: str) -> None:
    """
    Write the generated weblog as markdown and text files in the appropriate folder structure.
    """
    create_folder_structure(output_dir)
    
    date_range = weblog.get('date_range', 'unknown_date')
    title = weblog.get('title', 'Untitled')
    content = weblog.get('content', '')
    
    # Create a filename-friendly version of the title
    filename = f"{date_range}_{title.lower().replace(' ', '_')}"
    
    # Write markdown file
    md_path = os.path.join(output_dir, 'markdown', f"{filename}.md")
    write_markdown_file(content, md_path)
    
    # Write text file
    txt_path = os.path.join(output_dir, 'html', f"{filename}.html")
    write_text_file(content, txt_path)

if __name__ == "__main__":
    # Test the module functionality
    test_weblog = {
        'date_range': '2023-06-01_to_2023-06-07',
        'title': 'Weekly Development Update',
        'content': '# Weekly Development Update\n\nThis week, we made significant progress on...'
    }
    write_weblog(test_weblog, 'output')
    print("Test weblog written successfully.")