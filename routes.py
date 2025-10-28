from flask import Blueprint, render_template

variance_simulator_bp = Blueprint(
    'variance_simulator', 
    __name__, 
    template_folder='templates',
)

@variance_simulator_bp.route('/tools/variance-simulator', methods=['GET'])
def variance_simulator_page():
    """Renders the main page for the Poker Variance Simulator."""
    return render_template('tools/variance_simulator.html')
