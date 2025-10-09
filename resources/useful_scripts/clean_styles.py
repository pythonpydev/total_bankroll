import os
import tinycss2

# Paths relative to the script run directory (/home/ed/MEGA/total_bankroll/)
report_path = 'full_css_report.txt'
css_path = 'src/total_bankroll/static/css/_styles.css'
output_css_path = 'src/total_bankroll/static/css/_styles_cleaned.css'

# Step 1: Parse the report to extract unused selectors
unused_selectors = set()
with open(report_path, 'r', encoding='utf-8') as f:
    report_content = f.read()

# Split the report into sections
sections = report_content.split('==================================================\n')
for section in sections:
    if 'Unused CSS selectors (excluding dynamic classes):' in section:
        # Extract the unused selectors part
        unused_part = section.split('Unused CSS selectors (excluding dynamic classes):\n')[1].split('\n\n')[0]
        selectors = [sel.strip() for sel in unused_part.split('\n') if sel.strip() and sel.strip() != '<none>']
        for sel in selectors:
            # Split combined selectors (e.g., 'h1, .h1' -> ['h1', '.h1'])
            split_sels = [s.strip() for s in sel.split(',')]
            unused_selectors.update(split_sels)

print(f"Found {len(unused_selectors)} unique unused selectors (after splitting combined) to consider for removal.")

# Step 2: Parse the original CSS file using tinycss2
with open(css_path, 'r', encoding='utf-8') as f:
    css_content = f.read()
rules = tinycss2.parse_stylesheet(css_content, skip_comments=True, skip_whitespace=True)

# Step 3: Remove rules with unused selectors
rules_to_keep = []
removed_rules_count = 0
for rule in rules:
    if rule.type == 'qualified-rule':
        # Get the selector text
        selector_tokens = rule.prelude
        selector_text = ''.join(token.serialize() for token in selector_tokens).strip()
        
        # Split combined selectors
        split_sels = [s.strip() for s in selector_text.split(',')]
        
        # Check if all parts of the selector are unused
        if all(s in unused_selectors for s in split_sels):
            removed_rules_count += 1
            continue  # Remove the entire rule if all selectors are unused
        
    # Keep the rule (or non-style rules like @media, @font-face)
    rules_to_keep.append(rule)

# Step 4: Write the cleaned CSS to a new file
cleaned_css = ''.join(rule.serialize() for rule in rules_to_keep)
with open(output_css_path, 'w', encoding='utf-8') as f:
    f.write(cleaned_css)

print(f"Cleaned CSS written to {output_css_path}. Removed {removed_rules_count} rules matching unused selectors.")
