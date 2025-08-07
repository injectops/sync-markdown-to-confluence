import os
import yaml
import markdown
import re

def _convert_img_to_confluence_macro(html):
    """Converts standard HTML img tags to Confluence-specific macros."""
    def replacer(match):
        alt = match.group(1) or ''
        src = match.group(2)
        return f'<ac:image ac:align="center" ac:layout="center" ac:alt="{alt}"><ri:attachment ri:filename="{src}" /></ac:image>'
    
    return re.sub(r'<img alt="([^"]*)" src="([^"]+)"\s*/?>', replacer, html)

def _normalize_image_paths(md_text, base_path):
    """Normalizes relative image paths to be just the filename."""
    def replacer(match):
        alt_text = match.group(1)
        img_path = match.group(2)

        # If the path is already a URL, skip it
        if img_path.startswith(('http://', 'https://')):
            return f"![{alt_text}]({img_path})"

        filename = os.path.basename(img_path)
        return f"![{alt_text}]({filename})"

    return re.sub(r"!\[(.*?)\]\((.*?)\)", replacer, md_text)


def read_markdown_and_metadata(folder_path):
    """
    Reads a README.md file, extracts YAML frontmatter, and converts the
    Markdown content to Confluence-compatible HTML.
    """
    md_path = os.path.join(folder_path, 'README.md')
    yaml_path = os.path.join(folder_path, 'labels.yaml')

    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # Parse embedded frontmatter
    match = re.match(r"(?s)^---\n(.*?)\n---\n(.*)$", md_content)
    if match:
        frontmatter_yaml, md_body = match.groups()
        frontmatter = yaml.safe_load(frontmatter_yaml) or {}
    else:
        frontmatter = {}
        md_body = md_content

    # Load and merge labels from labels.yaml
    if os.path.exists(yaml_path):
        with open(yaml_path, 'r', encoding='utf-8') as f:
            labels_data = yaml.safe_load(f)
            if labels_data and 'labels' in labels_data:
                frontmatter.setdefault('labels', []).extend(labels_data['labels'])

    # Process markdown content
    md_body = _normalize_image_paths(md_body, folder_path)
    html_content = markdown.markdown(md_body, extensions=['tables', 'fenced_code'])
    html_content = _convert_img_to_confluence_macro(html_content)

    return frontmatter, html_content
