import os
import json
from flask import current_app, url_for
from markupsafe import Markup

def vite_asset(filename):
    """
    Generates the URL for a Vite-managed asset.
    In development, it points to the Vite dev server.
    In production, it reads the manifest.json to get the hashed filename.
    """
    # Check if we're in development mode with Vite dev server running
    vite_dev_server = os.environ.get('VITE_DEV_SERVER', 'false').lower() == 'true'
    
    if vite_dev_server:
        # In development, point to Vite dev server
        return f'http://localhost:5173/{filename}'
    
    # In production, read from manifest.json
    manifest_path = os.path.join(current_app.static_folder, 'assets', '.vite', 'manifest.json')
    
    if not os.path.exists(manifest_path):
        raise FileNotFoundError(f"Vite manifest.json not found at {manifest_path}. Did you run 'npm run build'?")

    with open(manifest_path, 'r') as f:
        manifest = json.load(f)

    # The key in the manifest is the original filename relative to the Vite root
    if filename not in manifest:
        raise KeyError(f"Asset '{filename}' not found in Vite manifest.json.")

    # The manifest value contains the actual output path
    output_filename = manifest[filename]['file']
    return url_for('static', filename=f'assets/{output_filename}')

def init_vite_asset_helper(app):
    """
    Registers the vite_asset function as a Jinja2 global.
    """
    @app.context_processor
    def inject_vite_asset():
        return dict(vite_asset=vite_asset)