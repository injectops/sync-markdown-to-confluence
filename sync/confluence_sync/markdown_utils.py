import os
import yaml
import markdown
import re

def convert_img_to_confluence_macro(html):
    def replacer(match):
        src = match.group(2)
        alt = match.group(1) or ''
        # <ac:image ac:align="left" ac:layout="align-start" ac:alt="Logo" ac:src="github-square-icon-size_256.png"><ri:url ri:value="github-square-icon-size_256.png" /></ac:image>
        return f'<ac:image ac:align="center" ac:layout="center" ac:alt="{alt}" ac:src="{src}"><ri:attachment ri:filename="{src}" /></ac:image>'
    
    
    return re.sub(r'<img alt="([^"]*)" src="([^"]+)"\s*/?>', replacer, html)

def normalize_image_paths(md_text):
    return re.sub(r'!\[([^\]]*)\]\(attachments/([^)]+)\)', r'![\1](\2)', md_text)

def read_markdown_and_metadata(folder_path):
    md_path = os.path.join(folder_path, 'README.md')
    yaml_path = os.path.join(folder_path, 'labels.yaml')

    # Load markdown
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # Parse embedded frontmatter if present
    match = re.match(r"(?s)^---\n(.*?)\n---\n(.*)$", md_content)
    if match:
        frontmatter_yaml, md_body = match.groups()
        frontmatter = yaml.safe_load(frontmatter_yaml)
    else:
        frontmatter = {}
        md_body = md_content

    # Load YAML labels file
    if os.path.exists(yaml_path):
        with open(yaml_path, 'r', encoding='utf-8') as f:
            external_yaml = yaml.safe_load(f)
        frontmatter.update(external_yaml or {})

    md_body = normalize_image_paths(md_body)
    html_content = markdown.markdown(md_body)
    html_content = convert_img_to_confluence_macro(html_content)

    return frontmatter, html_content

