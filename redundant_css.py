'''
Install required libraries: pip install cssutils beautifulsoup4
Run from /home/ed/MEGA/total_bankroll/ with python your_script_name.py.
Adjust js_dir if your JS files are in a different location (I assumed static/js/ based on typical structure).
This handles the identified dynamic additions. If more JS files or complex logic (e.g., variable class names) exist, the regex might miss them—manual review is recommended.
For template variables in HTML, this doesn't simulate rendering. If you have sample rendered HTML outputs, you could run the script on those instead of raw templates for better accuracy.
'''

import os
import glob
import re
import cssutils
from bs4 import BeautifulSoup

# Suppress cssutils warnings
cssutils.log.setLevel('ERROR')

# Paths relative to the script run directory (/home/ed/MEGA/total_bankroll/)
css_path = 'src/total_bankroll/static/css/_styles.css'
html_dir = 'src/total_bankroll/templates/'
js_dir = 'src/total_bankroll/static/js/'  # Adjust if JS files are in a different subdir; assuming standard static/js/

# Find all HTML files recursively
html_files = glob.glob(os.path.join(html_dir, '**/*.html'), recursive=True)

# Find all JS files recursively
js_files = glob.glob(os.path.join(js_dir, '**/*.js'), recursive=True)

# Extract dynamic classes from JS files using regex
dynamic_classes = set()
class_add_pattern = re.compile(r'classList\.add\(\s*["\']([^"\']+)["\']\s*\)')
for js_file in js_files:
    with open(js_file, 'r', encoding='utf-8') as f:
        js_content = f.read()
        matches = class_add_pattern.findall(js_content)
        dynamic_classes.update(matches)

# Manually add known dynamic/implied classes from analysis (e.g., 'dark-mode' from contains check, 'active' from Bootstrap)
dynamic_classes.update(['dark-mode', 'active'])

# Parse the CSS file
sheet = cssutils.parseFile(css_path)

# List to hold unused selectors
unused_selectors = []

# Check each style rule
for rule in sheet:
    if not isinstance(rule, cssutils.css.CSSStyleRule):
        continue  # Skip non-style rules like @media, @font-face, etc.

    selector_text = rule.selectorText
    is_used = False

    # Check against each HTML file (static check)
    for html_file in html_files:
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()

        soup = BeautifulSoup(html_content, 'html.parser')

        # If the selector matches any element in the HTML
        if soup.select(selector_text):
            is_used = True
            break

    if not is_used:
        # Dynamic check: if selector contains a dynamic class (e.g., '.navbar-shrink'), consider used
        if any(f'.{dc}' in selector_text for dc in dynamic_classes):
            continue  # Skip adding to unused
        unused_selectors.append(selector_text)

# Output the results
print("Unused CSS selectors (excluding those with dynamic classes):")
for sel in unused_selectors:
    print(sel)

print(f"\nTotal unused selectors: {len(unused_selectors)}")
print(f"Total HTML files checked: {len(html_files)}")
print(f"Total JS files checked: {len(js_files)}")
print(f"Detected dynamic classes: {', '.join(dynamic_classes)}")
