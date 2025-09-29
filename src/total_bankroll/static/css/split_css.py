import cssutils
import os

def split_css(input_file):
    # Parse the CSS file
    sheet = cssutils.parseFile(input_file)

    # Initialize strings for each output file
    base_css = []
    light_css = []
    dark_css = []

    # Helper to check if a rule is dark-mode specific
    def is_dark_mode_rule(rule):
        if hasattr(rule, 'selectorText'):
            selector = rule.selectorText.lower()
            return selector.startswith('body.dark-mode') or selector.startswith('.dark-mode')
        return False

    # Iterate through all rules in the stylesheet
    for rule in sheet:
        if isinstance(rule, cssutils.css.CSSComment):
            # Preserve comments in light.css by default (or distribute based on context if needed)
            light_css.append(rule.cssText + '\n')
        elif isinstance(rule, cssutils.css.CSSCharsetRule) or isinstance(rule, cssutils.css.CSSImportRule):
            # At-rules like @charset, @import go to base
            base_css.append(rule.cssText + '\n')
        elif isinstance(rule, cssutils.css.CSSNamespaceRule):
            # Namespaces to base
            base_css.append(rule.cssText + '\n')
        elif isinstance(rule, cssutils.css.CSSFontFaceRule):
            # Font faces to base
            base_css.append(rule.cssText + '\n')
        elif isinstance(rule, cssutils.css.CSSPageRule):
            # Page rules to base
            base_css.append(rule.cssText + '\n')
        elif isinstance(rule, cssutils.css.CSSMediaRule):
            # Media queries: Recurse and categorize nested rules
            media_text = '@media ' + rule.media.mediaText + ' {\n'
            has_dark = False
            media_base = []
            media_light = []
            media_dark = []
            for nested_rule in rule:
                if isinstance(nested_rule, cssutils.css.CSSStyleRule):
                    if is_dark_mode_rule(nested_rule):
                        media_dark.append('  ' + nested_rule.cssText + '\n')
                        has_dark = True
                    else:
                        # Check if structural/base or light
                        if is_base_rule(nested_rule):
                            media_base.append('  ' + nested_rule.cssText + '\n')
                        else:
                            media_light.append('  ' + nested_rule.cssText + '\n')
            media_text += ''.join(media_base + media_light + media_dark) + '}\n'
            if has_dark:
                dark_css.append(media_text)
            elif media_base:
                base_css.append(media_text)
            else:
                light_css.append(media_text)
        elif isinstance(rule, cssutils.css.CSSStyleRule):
            # Regular style rules
            if is_dark_mode_rule(rule):
                dark_css.append(rule.cssText + '\n')
            else:
                # Distinguish base vs light
                if is_base_rule(rule):
                    base_css.append(rule.cssText + '\n')
                else:
                    light_css.append(rule.cssText + '\n')
        else:
            # Fallback: Unknown rules to light
            light_css.append(rule.cssText + '\n')

    # Helper to check if a rule is 'base' (structural, resets, non-color/layout only)
    def is_base_rule(rule):
        selector = rule.selectorText.lower()
        base_selectors = [
            ':root', '*', 'body', 'html', 'hr', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'p', 'ol', 'ul', 'dl', 'b', 'strong', 'small', 'a', 'pre', 'code', 'kbd',
            'samp', 'img', 'svg', 'table', 'caption', 'th', 'thead', 'tbody', 'tfoot',
            'tr', 'td', 'th', 'label', 'button', 'input', 'select', 'optgroup', 'textarea',
            '[role=button]', 'iframe', '.lead', '.display-1', '.display-2', # Typography/layout
            '.container', '.row', '.col-', '.g-', '.gx-', '.gy-', # Grid/layout
            '.d-', '.flex-', '.justify-', '.align-', '.order-', '.m-', '.p-', # Utilities
            '.position-', '.top-', '.bottom-', '.start-', '.end-', '.translate-', # Positioning
            '.border-', '.rounded-', '.visible', '.invisible' # Borders, visibility
        ]
        return any(selector.startswith(s) or s in selector for s in base_selectors)

    # Write to files
    with open('base.css', 'w', encoding='utf-8') as f:
        f.write(''.join(base_css))
    with open('light.css', 'w', encoding='utf-8') as f:
        f.write(''.join(light_css))
    with open('dark.css', 'w', encoding='utf-8') as f:
        f.write(''.join(dark_css))

    print("CSS split complete: base.css, light.css, dark.css created.")

# Run the function
if __name__ == "__main__":
    input_file = '_styles.css'
    if os.path.exists(input_file):
        split_css(input_file)
    else:
        print(f"File {input_file} not found.")
