from flask import Blueprint, render_template

charts_bp = Blueprint("charts", __name__)

@charts_bp.route("/charts")
def charts_page():
    """Charts page."""
    return render_template("charts.html")