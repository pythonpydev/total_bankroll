"""
This module contains the routes for legal and informational pages like
the Privacy Policy and Terms of Service.
"""
from flask import Blueprint, render_template

legal_bp = Blueprint('legal', __name__, template_folder='../templates')


@legal_bp.route('/privacy-policy')
def privacy_policy():
    # template lives in templates/core/ not templates/legal
    return render_template("core/privacy_policy.html")

@legal_bp.route("/terms-of-service")
def terms_of_service():
    """Renders the Terms of Service page."""
    # template lives in templates/core/ not templates/legal
    return render_template("core/terms_of_service.html")