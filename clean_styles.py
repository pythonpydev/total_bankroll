import os
from cssutils.css import CSSStyleSheet  # Updated import
import cssutils

# Paths relative to the script run directory (/home/ed/MEGA/total_bankroll/)
report_path = 'full_css_report.txt'
css_path = 'src/total_bankroll/static/css/_styles.css'
output_css_path = 'src/total_bankroll/static/css/_styles_cleaned.css'

# Step 1: Parse the report to extract unused selectors
unused_selectors = set()
with open(report_path, 'r', encoding='utf-8') as f:
    report_content = f.read()

# Split the report into sections (each batch starts with "CSS Analysis Results")
sections = report_content.split('==================================================\n')
for section in sections:
    if 'Unused CSS selectors (excluding dynamic classes):' in section:
        # Extract the unused selectors part
        unused_part = section.split('Unused CSS selectors (excluding dynamic classes):\n')[1].split('\n\n')[0]
        selectors = [sel.strip() for sel in unused_part.split('\n') if sel.strip() and sel.strip() != '<none>']
        unused_selectors.update(selectors)

print(f"Found {len(unused_selectors)} unique unused selectors to remove.")

# Step 2: Parse the original CSS file
cssutils.log.setLevel('CRITICAL')  # Suppress warnings
try:
    sheet = cssutils.parseFile(css_path)
except Exception as e:
    print(f"Error parsing CSS file {css_path}: {e}")
    exit(1)

# Step 3: Remove rules with unused selectors
rules_to_keep = []
for rule in sheet:
    if isinstance(rule, cssutils.css.CSSStyleRule):
        if rule.selectorText not in unused_selectors:
            rules_to_keep.append(rule)
    else:
        # Keep non-style rules like @media, @font-face, etc.
        rules_to_keep.append(rule)

# Create a new stylesheet with kept rules
new_sheet = CSSStyleSheet()
for rule in rules_to_keep:
    new_sheet.add(rule)

# Step 4: Write the cleaned CSS to a new file
with open(output_css_path, 'w', encoding='utf-8') as f:
    f.write(new_sheet.cssText.decode('utf-8'))

print(f"Cleaned CSS written to {output_css_path}. Removed rules for {len(unused_selectors)} selectors.")