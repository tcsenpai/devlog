import os
from typing import Dict, Any, List
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

def generate_html_index(output_dir: str) -> None:
    """
    Generate and write an HTML index for the HTML files in the output directory.
    """
    html_dir = os.path.join(output_dir, 'html')
    html_files = [f for f in os.listdir(html_dir) if f.endswith('.html') and f != 'index.html']
    
    index_content = "<html><head><title>Weblog Index</title></head><body>"
    index_content += "<h1>Weblog Index</h1><ul>"
    
    for html_file in sorted(html_files, reverse=True):
        file_name = os.path.splitext(html_file)[0]
        parts = file_name.split('_')
        if len(parts) > 1:
            date_range = parts[0]
            title = ' '.join(parts[1:]).title()
        else:
            date_range = "Unknown Date"
            title = file_name.title()
        
        index_content += f'<li><a href="{html_file}">{date_range}: {title}</a></li>'
    
    index_content += "</ul></body></html>"
    
    index_path = os.path.join(html_dir, 'index.html')
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(index_content)

def write_weblog(weblogs: List[Dict[str, Any]], output_dir: str) -> None:
    """
    Write the generated weblogs as markdown and text files in the appropriate folder structure.
    """
    create_folder_structure(output_dir)
    
    for weblog in weblogs:
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
    
    # Generate HTML index after processing all weblogs
    generate_html_index(output_dir)

if __name__ == "__main__":
    # Test the module functionality
    test_weblogs = [
        {
            'date_range': '2023-06-01_to_2023-06-07',
            'title': 'Weekly Development Update',
            'content': '# Weekly Development Update\n\nThis week, we made significant progress on...'
        },
        {
            'date_range': '2023-06-08_to_2023-06-14',
            'title': 'Sprint Review',
            'content': '# Sprint Review\n\nDuring this sprint, we accomplished...'
        }
    ]
    write_weblog(test_weblogs, 'output')
    print("Test weblogs written successfully.")