"""
This module contains the routes for legal and informational pages like
the Privacy Policy and Terms of Service.
"""
from flask import Blueprint, render_template

legal_bp = Blueprint('legal', __name__, template_folder='../templates')


@legal_bp.route('/privacy-policy')
def privacy_policy():
    """Renders the Privacy Policy page."""
    return render_template('privacy_policy.html')

@legal_bp.route('/terms-of-service')
def terms_of_service():
    """Renders the Terms of Service page."""
    return render_template('core/terms_of_service.html')