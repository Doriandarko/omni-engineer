import json
import argparse
import os

def parse_args():
    parser = argparse.ArgumentParser(description='Reformat JSON chat log to markdown')
    parser.add_argument('input_file', type=str, help='Path to JSON input file')
    return parser.parse_args()

def json_to_markdown(json_data):
    """
    Convert JSON data containing messages into a human-readable markdown format
    """
    markdown = []
    
    for item in json_data:
        role = item.get('role', '').title()
        content = item.get('content', '')
        
        if role == "System":
            markdown.append(f"## {role} Message")
        else:
            markdown.append(f"### {role}")
        
        # Process content for markdown formatting
        lines = content.split('\n')
        for line in lines:
            # Handle code blocks
            if line.startswith('```'):
                markdown.append('```')
            elif line.strip().startswith('#'):
                # Handle headers
                header_level = line.strip().find('#') + 1
                markdown.append(f"{'#' * header_level} {line.strip()[header_level:]}")
            elif line.strip() == '':
                markdown.append('')  # Add empty line for spacing
            else:
                markdown.append(line)
        
        markdown.append('---')  # Add horizontal line between sections
    
    return '\n\n'.join(markdown)

if __name__ == "__main__":
    args = parse_args()
    
    # Load JSON data from file
    with open(args.input_file, 'r') as f:
        json_data = json.load(f)
        
    # Convert to markdown
    markdown_content = json_to_markdown(json_data)
    
    # Get output filename
    base, ext = os.path.splitext(args.input_file)
    output_file = f"{base}_reformatted.md"
    
    # Save to file
    with open(output_file, 'w') as f:
        f.write(markdown_content)