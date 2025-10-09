import os
import glob
import re
import cssutils
from bs4 import BeautifulSoup
import sys
import threading
import time

# Suppress cssutils warnings and errors
cssutils.log.setLevel('CRITICAL')
cssutils.ser.prefs.useMinified()
cssutils.ser.prefs.omitLastSemicolon = False
cssutils.ser.prefs.validOnly = False
cssutils.ser.prefs.resolveVariables = False

# Paths
css_path = 'src/total_bankroll/static/css/_styles.css'
html_dir = 'src/total_bankroll/templates/'
js_dir = 'src/total_bankroll/static/js/'
output_dir = 'css_analysis_output'

# Create output directory if it doesn't exist
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Prompt user for starting line
while True:
    try:
        start_line_input = input("Enter the starting line number in the CSS file (default is 1): ").strip()
        start_line = 1 if not start_line_input else int(start_line_input)
        if start_line < 1:
            print("Starting line must be 1 or greater.")
            continue
        break
    except ValueError:
        print("Please enter a valid number or press Enter for default (1).")

# Preprocess CSS file to start at specified line
try:
    with open(css_path, 'r', encoding='utf-8') as f:
        css_lines = f.readlines()
    if start_line > len(css_lines):
        print(f"Error: Starting line {start_line} is beyond file length ({len(css_lines)} lines).")
        exit(1)
    css_content = ''.join(css_lines[start_line - 1:])
except Exception as e:
    print(f"Error reading CSS file {css_path}: {e}")
    exit(1)

# Parse CSS content
try:
    sheet = cssutils.parseString(css_content)
except Exception as e:
    print(f"Critical error parsing CSS content starting at line {start_line}: {e}")
    exit(1)

# Find HTML and JS files
html_files = glob.glob(os.path.join(html_dir, '**/*.html'), recursive=True)
js_files = glob.glob(os.path.join(js_dir, '**/*.js'), recursive=True)

# Extract dynamic classes from JS files
dynamic_classes = set()
class_add_pattern = re.compile(r'classList\.(?:add|toggle|remove)\(\s*["\']([^"\']+)["\']\s*\)')
for js_file in js_files:
    try:
        with open(js_file, 'r', encoding='utf-8') as f:
            js_content = f.read()
            matches = class_add_pattern.findall(js_content)
            dynamic_classes.update(matches)
    except Exception as e:
        print(f"Error reading JS file {js_file}: {e}")

# Add known Bootstrap and custom dynamic classes
dynamic_classes.update([
    'dark-mode', 'active', 'card-image', 'navbar-shrink', 'show', 'collapsed',
    'fade', 'in', 'open', 'hidden', 'disabled', 'selected', 'focus', 'hover'
])

# Function to get input with timeout
def input_with_timeout(prompt, timeout):
    response = [None]  # List to store response (mutable for thread)
    
    def get_input():
        try:
            response[0] = input(prompt).strip().lower()
        except:
            response[0] = None
    
    # Start input in a separate thread
    thread = threading.Thread(target=get_input)
    thread.daemon = True
    thread.start()
    thread.join(timeout)
    
    return response[0]

# Lists for results
unused_selectors = []
skipped_selectors = []
problematic_rules = []
rule_count = 0
batch_size = 100
auto_continue_rules = 200
batch_number = 1

# Process CSS rules in batches
for rule in sheet:
    if not isinstance(rule, cssutils.css.CSSStyleRule):
        continue

    rule_count += 1
    selector_text = rule.selectorText
    is_used = False

    # Skip problematic selectors
    if not selector_text or '::' in selector_text or selector_text.startswith(':'):
        skipped_selectors.append(selector_text or '<empty selector>')
        continue

    try:
        # Validate selector syntax
        if not all(c.isalnum() or c in '.-_#[ ]>' for c in selector_text):
            skipped_selectors.append(selector_text)
            problematic_rules.append(f"Invalid selector syntax: {selector_text}")
            continue

        # Check HTML files
        for html_file in html_files:
            try:
                with open(html_file, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                soup = BeautifulSoup(html_content, 'html.parser')
                if soup.select(selector_text):
                    is_used = True
                    break
            except Exception as e:
                problematic_rules.append(f"Error processing selector '{selector_text}' in {html_file}: {e}")
                continue

        # Dynamic class check
        if not is_used and any(f'.{dc}' in selector_text for dc in dynamic_classes):
            is_used = True

        if not is_used:
            unused_selectors.append(selector_text)

    except Exception as e:
        skipped_selectors.append(selector_text)
        problematic_rules.append(f"Error processing selector '{selector_text}': {e}")
        continue

    # Pause and output every 100 rules
    if rule_count % batch_size == 0:
        output_file = os.path.join(output_dir, f'css_{rule_count}.txt')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"CSS Analysis Results (Rules {rule_count - batch_size + 1} to {rule_count}, starting from CSS line {start_line})\n")
            f.write("=" * 50 + "\n")
            f.write("Unused CSS selectors (excluding dynamic classes):\n")
            f.write('\n'.join(unused_selectors) + '\n' if unused_selectors else "<none>\n")
            f.write("\nSkipped selectors (pseudo-elements or parsing errors):\n")
            f.write('\n'.join(skipped_selectors) + '\n' if skipped_selectors else "<none>\n")
            f.write("\nProblematic rules (logged for review):\n")
            f.write('\n'.join(problematic_rules) + '\n' if problematic_rules else "<none>\n")
            f.write("\nSummary:\n")
            f.write(f"Total unused selectors: {len(unused_selectors)}\n")
            f.write(f"Total skipped selectors: {len(skipped_selectors)}\n")
            f.write(f"Total problematic rules: {len(problematic_rules)}\n")
            f.write(f"Total HTML files checked: {len(html_files)}\n")
            f.write(f"Total JS files checked: {len(js_files)}\n")
            f.write(f"Detected dynamic classes: {', '.join(sorted(dynamic_classes))}\n")

        print(f"Wrote results to {output_file}")

        # Clear lists for next batch
        unused_selectors = []
        skipped_selectors = []
        problematic_rules = []

        # Prompt with 5-second timeout
        response = input_with_timeout(f"Processed {rule_count} rules. Continue? (y/n): ", 5)
        
        if response == 'n':
            print(f"Stopped after processing {rule_count} rules.")
            break
        elif response is None:
            print(f"No response received within 5 seconds. Continuing for {auto_continue_rules} more rules...")
            batch_size_temp = batch_size + auto_continue_rules
        else:
            batch_size_temp = batch_size

        batch_number += 1
        batch_size = batch_size_temp  # Adjust batch size for auto-continue

# Write final batch if remaining rules
if rule_count % batch_size != 0 or (response is None and rule_count % (batch_size - auto_continue_rules) != 0):
    output_file = os.path.join(output_dir, f'css_{rule_count}.txt')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"CSS Analysis Results (Rules {batch_size * (batch_number - 1) + 1} to {rule_count}, starting from CSS line {start_line})\n")
        f.write("=" * 50 + "\n")
        f.write("Unused CSS selectors (excluding dynamic classes):\n")
        f.write('\n'.join(unused_selectors) + '\n' if unused_selectors else "<none>\n")
        f.write("\nSkipped selectors (pseudo-elements or parsing errors):\n")
        f.write('\n'.join(skipped_selectors) + '\n' if skipped_selectors else "<none>\n")
        f.write("\nProblematic rules (logged for review):\n")
        f.write('\n'.join(problematic_rules) + '\n' if problematic_rules else "<none>\n")
        f.write("\nSummary:\n")
        f.write(f"Total unused selectors: {len(unused_selectors)}\n")
        f.write(f"Total skipped selectors: {len(skipped_selectors)}\n")
        f.write(f"Total problematic rules: {len(problematic_rules)}\n")
        f.write(f"Total HTML files checked: {len(html_files)}\n")
        f.write(f"Total JS files checked: {len(js_files)}\n")
        f.write(f"Detected dynamic classes: {', '.join(sorted(dynamic_classes))}\n")

    print(f"Wrote final results to {output_file}")
    print(f"Completed processing {rule_count} rules starting from CSS line {start_line}.")