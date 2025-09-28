import os
import re
from filtercss import filter_css
from bs4 import BeautifulSoup

def find_unused_css():
    """
    Finds unused CSS selectors in the project's stylesheets.
    Protects dark mode CSS and uses relative paths.
    Processes multiple CSS files.
    """
    # Use relative paths from the script execution directory
    templates_dir = "src/total_bankroll/templates/"
    static_dir = "src/total_bankroll/static/"
    css_output_dir = "src/total_bankroll/static/css/cleaned/"

    # Check if directories exist
    if not os.path.exists(templates_dir):
        print(f"Error: Templates directory not found at {templates_dir}")
        return
    
    if not os.path.exists(static_dir):
        print(f"Error: Static directory not found at {static_dir}")
        return

    # Find all CSS files in the static directory
    css_files = []
    for root, _, files in os.walk(static_dir):
        for file in files:
            if file.endswith(".css"):
                css_file_path = os.path.join(root, file)
                css_files.append(css_file_path)

    if not css_files:
        print("No CSS files found in the static directory")
        return
    
    print(f"Found {len(css_files)} CSS files:")
    for css_file in css_files:
        print(f"  - {css_file}")

    # Read all CSS files
    all_css = ""
    css_file_contents = {}
    
    for css_file_path in css_files:
        try:
            with open(css_file_path, "r", encoding="utf-8") as f:
                css_content = f.read()
                css_file_contents[css_file_path] = css_content
                all_css += f"\n/* From {css_file_path} */\n" + css_content
        except Exception as e:
            print(f"Error reading CSS file {css_file_path}: {e}")
            return

    # Collect all HTML content
    html = ""
    html_files_processed = 0
    
    for root, _, files in os.walk(templates_dir):
        for file in files:
            if file.endswith(".html"):
                file_path = os.path.join(root, file)
                print(f"Parsing {file_path}...")
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        html_content = f.read()
                        # Clean up the HTML content to avoid parsing issues
                        html_content = clean_html_for_parsing(html_content)
                        # Test parsing with html.parser (more robust than lxml)
                        BeautifulSoup(html_content, "html.parser")
                        html += html_content + "\n"
                        html_files_processed += 1
                except Exception as e:
                    print(f"Warning: Error parsing {file_path}: {e}")
                    # Continue with other files instead of returning

    # Also scan JavaScript files for dynamic class usage
    js_content = ""
    js_files_processed = 0
    
    for root, _, files in os.walk(static_dir):
        for file in files:
            if file.endswith(".js"):
                file_path = os.path.join(root, file)
                print(f"Scanning JavaScript file: {file_path}...")
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        js_file_content = f.read()
                        js_content += js_file_content
                        js_files_processed += 1
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")

    print(f"Processed {html_files_processed} HTML files and {js_files_processed} JS files")

    # Extract dynamic classes and IDs from JavaScript
    dynamic_selectors = extract_dynamic_selectors(js_content, html)
    
    # Create protected selectors set
    protected_selectors = get_protected_selectors(dynamic_selectors)
    
    print(f"Found {len(protected_selectors)} protected selectors (including dark mode)")
    
    # Create output directory
    os.makedirs(css_output_dir, exist_ok=True)
    
    # Process each CSS file individually
    for css_file_path, css_content in css_file_contents.items():
        # Get relative path for output file naming
        rel_path = os.path.relpath(css_file_path, static_dir)
        output_file_path = os.path.join(css_output_dir, rel_path)
        
        # Create subdirectories if needed
        os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
        
        print(f"Processing {css_file_path}...")
        
        # Filter CSS but preserve protected selectors
        cleaned_css = filter_css_with_protection(css_content, html + js_content, protected_selectors)
        
        # Write cleaned CSS
        try:
            with open(output_file_path, "w", encoding="utf-8") as f:
                f.write(cleaned_css)
            print(f"  -> Cleaned CSS written to {output_file_path}")
        except Exception as e:
            print(f"  -> Error writing cleaned CSS: {e}")
    
    # Also create a combined cleaned CSS file
    combined_output_path = os.path.join(css_output_dir, "combined.css")
    combined_cleaned_css = filter_css_with_protection(all_css, html + js_content, protected_selectors)
    
    try:
        with open(combined_output_path, "w", encoding="utf-8") as f:
            f.write(combined_cleaned_css)
        print(f"Combined cleaned CSS written to {combined_output_path}")
    except Exception as e:
        print(f"Error writing combined cleaned CSS: {e}")

    print(f"\nSummary:")
    print(f"- Processed {len(css_files)} CSS files")
    print(f"- Processed {html_files_processed} HTML files and {js_files_processed} JS files")
    print(f"- Protected {len(protected_selectors)} dynamic/dark mode selectors")
    print(f"- Output directory: {css_output_dir}")

def extract_dynamic_selectors(js_content, html_content):
    """
    Extract CSS selectors that are dynamically used in JavaScript.
    """
    dynamic_selectors = set()
    
    # Common patterns for dynamic class/ID usage in JavaScript
    patterns = [
        r'classList\.(?:add|remove|toggle|contains)\(["\']([^"\']+)["\']\)',  # classList operations
        r'className\s*[=+]\s*["\']([^"\']+)["\']',  # className assignments
        r'\.setAttribute\(["\']class["\']\s*,\s*["\']([^"\']+)["\']\)',  # setAttribute for class
        r'\.getAttribute\(["\']class["\']\)',  # getAttribute for class
        r'querySelector\(["\']\.([^"\']+)["\']\)',  # querySelector with class
        r'querySelectorAll\(["\']\.([^"\']+)["\']\)',  # querySelectorAll with class
        r'getElementById\(["\']([^"\']+)["\']\)',  # getElementById
        r'getElementsByClassName\(["\']([^"\']+)["\']\)',  # getElementsByClassName
        r'["\']([a-zA-Z][\w-]*(?:\s+[a-zA-Z][\w-]*)*)["\']',  # Generic quoted strings that might be classes
    ]
    
    for pattern in patterns:
        matches = re.finditer(pattern, js_content, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            selector = match.group(1).strip()
            if selector:
                # Split multiple classes
                classes = selector.split()
                for cls in classes:
                    if cls and re.match(r'^[a-zA-Z][\w-]*$', cls):  # Valid CSS class name
                        dynamic_selectors.add(f'.{cls}')
                        dynamic_selectors.add(cls)  # Also add without dot for ID matching

    # Also look for data attributes and other dynamic selectors in HTML/JS
    data_attr_pattern = r'data-[\w-]+'
    data_matches = re.finditer(data_attr_pattern, html_content + js_content, re.IGNORECASE)
    for match in data_matches:
        attr = match.group(0)
        dynamic_selectors.add(f'[{attr}]')
    
    return dynamic_selectors

def get_protected_selectors(dynamic_selectors):
    """
    Get selectors that should be protected from removal.
    """
    protected = set(dynamic_selectors)
    
    # Common dark mode patterns
    dark_mode_patterns = [
        r'\.dark\b',
        r'\[data-theme["\']?=["\']?dark["\']?\]',
        r'\.theme-dark\b',
        r'\.dark-mode\b',
        r'\.night\b',
        r'\.night-mode\b',
        r'body\.dark',
        r'html\.dark',
        r':root\.dark',
        r'\.dark\s+',  # Dark mode with descendant selectors
        r'\.dark\.',   # Dark mode with chained classes
        r'\.dark:',    # Dark mode with pseudo-classes
    ]
    
    # Add common dark mode selector patterns
    for pattern in dark_mode_patterns:
        protected.add(pattern)
    
    # Add common utility classes that might be used dynamically
    utility_classes = [
        '.hidden', '.show', '.hide', '.visible', '.invisible',
        '.active', '.inactive', '.disabled', '.enabled',
        '.selected', '.unselected', '.current',
        '.loading', '.loaded', '.error', '.success',
        '.open', '.closed', '.expanded', '.collapsed',
        '.fade-in', '.fade-out', '.slide-in', '.slide-out',
    ]
    
    protected.update(utility_classes)
    
    return protected

def clean_html_for_parsing(html_content):
    """
    Clean HTML content to avoid parsing issues with BeautifulSoup.
    """
    # Remove problematic XML namespaces that might cause lxml issues
    html_content = re.sub(r'xmlns[^=]*="[^"]*"', '', html_content)
    
    # Remove or fix malformed tags that might cause issues
    html_content = re.sub(r'<\?[^>]*\?>', '', html_content)  # Remove processing instructions
    html_content = re.sub(r'<!DOCTYPE[^>]*>', '', html_content, flags=re.IGNORECASE)  # Remove DOCTYPE
    
    # Fix common template syntax that might confuse parsers
    html_content = re.sub(r'\{\{[^}]*\}\}', '<!-- template -->', html_content)  # Jinja2 templates
    html_content = re.sub(r'\{%[^%]*%\}', '<!-- template -->', html_content)   # Jinja2 blocks
    
    return html_content

def filter_css_with_protection(css, html_js_content, protected_selectors):
    """
    Filter CSS while protecting specified selectors.
    Uses safer HTML parsing methods.
    """
    try:
        # Clean the HTML content before passing to filter_css
        cleaned_html = clean_html_for_parsing(html_js_content)
        
        # Try with html.parser first (more forgiving than lxml)
        try:
            filtered_css = filter_css(css, cleaned_html)
        except Exception as e:
            print(f"Warning: filtercss failed with cleaned HTML: {e}")
            # Try with a minimal HTML wrapper
            minimal_html = f"<html><body>{cleaned_html}</body></html>"
            try:
                filtered_css = filter_css(css, minimal_html)
            except Exception as e2:
                print(f"Warning: filtercss failed with minimal HTML: {e2}")
                # Extract just the class and ID names for a basic approach
                return filter_css_basic(css, html_js_content, protected_selectors)
        
        # Parse the original CSS to find protected rules
        css_rules = parse_css_rules(css)
        filtered_rules = parse_css_rules(filtered_css)
        
        # Find rules that were removed but should be protected
        protected_rules = []
        for rule in css_rules:
            selector = rule['selector'].strip()
            
            # Check if this rule should be protected
            should_protect = False
            for protected in protected_selectors:
                if (protected in selector or 
                    re.search(protected.replace('.', r'\.').replace('[', r'\[').replace(']', r'\]'), selector)):
                    should_protect = True
                    break
            
            # If it should be protected and wasn't included in filtered CSS, add it back
            if should_protect and not any(r['selector'] == rule['selector'] for r in filtered_rules):
                protected_rules.append(rule)
        
        # Combine filtered CSS with protected rules
        result_css = filtered_css
        if protected_rules:
            result_css += "\n\n/* Protected selectors (dynamic/dark mode) */\n"
            for rule in protected_rules:
                result_css += f"{rule['selector']} {{\n{rule['content']}\n}}\n\n"
        
        return result_css
        
    except Exception as e:
        print(f"Error in filter_css_with_protection: {e}")
        print("Falling back to basic CSS filtering")
        return filter_css_basic(css, html_js_content, protected_selectors)

def filter_css_basic(css, html_js_content, protected_selectors):
    """
    Basic CSS filtering when filtercss library fails.
    Extracts classes and IDs from HTML/JS and keeps only matching CSS rules.
    """
    print("Using basic CSS filtering method...")
    
    # Extract all class names and IDs from HTML and JS content
    used_classes = set()
    used_ids = set()
    
    # Find class names
    class_matches = re.findall(r'class\s*=\s*["\']([^"\']*)["\']', html_js_content, re.IGNORECASE)
    for match in class_matches:
        classes = match.split()
        used_classes.update(classes)
    
    # Find IDs
    id_matches = re.findall(r'id\s*=\s*["\']([^"\']*)["\']', html_js_content, re.IGNORECASE)
    used_ids.update(id_matches)
    
    # Find JavaScript class manipulations
    js_class_matches = re.findall(r'["\']([a-zA-Z][\w-]*)["\']', html_js_content)
    for match in js_class_matches:
        if re.match(r'^[a-zA-Z][\w-]*', match):
            used_classes.add(match)
        if re.match(r'^[a-zA-Z][\w-]*$', match):
            used_ids.add(match)

def parse_css_rules(css_content):
    """
    Simple CSS parser to extract rules.
    """
    rules = []
    
    # Remove comments
    css_content = re.sub(r'/\*.*?\*/', '', css_content, flags=re.DOTALL)
    
    # Find CSS rules
    rule_pattern = r'([^{}]+)\s*\{([^{}]*)\}'
    matches = re.finditer(rule_pattern, css_content, re.MULTILINE | re.DOTALL)
    
    for match in matches:
        selector = match.group(1).strip()
        content = match.group(2).strip()
        
        if selector and content:
            rules.append({
                'selector': selector,
                'content': content
            })
    
    return rules

if __name__ == "__main__":
    find_unused_css()
    