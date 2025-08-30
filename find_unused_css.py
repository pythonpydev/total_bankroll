import os
from filtercss import filter_css
from bs4 import BeautifulSoup

def find_unused_css():
    """
    Finds unused CSS selectors in the project's stylesheets.
    """
    css_file_path = "/home/ed/Insync/e.f.bird@outlook.com/OneDrive/Dev/total_bankroll/src/total_bankroll/static/css/styles.css"
    templates_dir = "/home/ed/Insync/e.f.bird@outlook.com/OneDrive/Dev/total_bankroll/src/total_bankroll/templates/"
    cleaned_css_file_path = "/home/ed/Insync/e.f.bird@outlook.com/OneDrive/Dev/total_bankroll/src/total_bankroll/static/css/cleaned.css"

    with open(css_file_path, "r") as f:
        css = f.read()

    html = ""
    for root, _, files in os.walk(templates_dir):
        for file in files:
            if file.endswith(".html"):
                file_path = os.path.join(root, file)
                print(f"Parsing {file_path}...")
                try:
                    with open(file_path, "r") as f:
                        html_content = f.read()
                        BeautifulSoup(html_content, "html.parser")
                        html += html_content
                except Exception as e:
                    print(f"Error parsing {file_path}: {e}")
                    return

    cleaned_css = filter_css(css, html)

    with open(cleaned_css_file_path, "w") as f:
        f.write(cleaned_css)

    print(f"Cleaned CSS written to {cleaned_css_file_path}")

if __name__ == "__main__":
    find_unused_css()
