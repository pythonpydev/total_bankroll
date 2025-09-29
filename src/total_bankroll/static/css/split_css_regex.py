import re
import os

def split_css_regex(input_file):
    # Read the CSS file
    with open(input_file, 'r', encoding='utf-8') as f:
        css_content = f.read()

    # Initialize output content
    base_css = []
    light_css = []
    dark_css = []

    # Split CSS into individual rules (handles multi-line rules better)
    # Splits on } followed by whitespace and a new selector or @
    rules = re.split(r'(?<=})\s*(?=(?:@|\.|\#|\w|,|\[|\*|::|:root|body|html))', css_content)

    # Base selectors patterns (start of rule)
    base_patterns = [
        r'^\s*:root\s*\{',
        r'^\s*\*\s*\{',
        r'^\s*body\s*(?!\.dark-mode)\s*\{',
        r'^\s*html\s*\{',
        r'^\s*h[1-6]\s*\{',
        r'^\s*p\s*\{',
        r'^\s*ol\s*\{',
        r'^\s*ul\s*\{',
        r'^\s*\.container',
        r'^\s*\.row',
        r'^\s*\.col-',
        r'^\s*\.d-',
        r'^\s*\.flex-',
        r'^\s*\.m-',
        r'^\s*\.p-',
        r'^\s*\.border-',
        r'^\s*\.rounded-'
    ]
    base_regex = re.compile('|'.join(base_patterns))

    # Dark mode pattern
    dark_regex = re.compile(r'^\s*(body\.dark-mode|\.dark-mode)')

    for rule in rules:
        rule = rule.strip()
        if not rule:
            continue
        # Handle at-rules (@media, @charset, etc.)
        if rule.startswith('@'):
            if 'prefers-color-scheme: dark' in rule or 'dark-mode' in rule:
                dark_css.append(rule + '\n')
            else:
                base_css.append(rule + '\n')
        # Handle style rules (if contains { and not @)
        elif '{' in rule:
            if dark_regex.match(rule):
                dark_css.append(rule + '\n')
            elif base_regex.match(rule):
                base_css.append(rule + '\n')
            else:
                light_css.append(rule + '\n')
        else:
            # Fallback for comments or unknown
            light_css.append(rule + '\n')

    # Write to files
    with open('base.css', 'w', encoding='utf-8') as f:
        f.write(''.join(base_css))
    with open('light.css', 'w', encoding='utf-8') as f:
        f.write(''.join(light_css))
    with open('dark.css', 'w', encoding='utf-8') as f:
        f.write(''.join(dark_css))

    print("CSS split complete: base.css, light.css, dark.css created.")

if __name__ == "__main__":
    input_file = '_styles.css'  # Assumes running from same directory
    if os.path.exists(input_file):
        split_css_regex(input_file)
    else:
        print(f"File {input_file} not found.")
