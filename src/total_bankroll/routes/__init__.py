"""total_bankroll package."""
__version__ = "0.1.0"

# Core application routes
from .home import home_bp
from .about import about_bp
from .help import help_bp
from .legal import legal_bp

# User authentication and management
from .auth import auth_bp
from .settings import settings_bp

# Main features
from .poker_sites import poker_sites_bp
from .assets import assets_bp
from .deposit import deposit_bp
from .withdrawal import withdrawal_bp
from .add_deposit import add_deposit_bp
from .add_withdrawal import add_withdrawal_bp
from .charts import charts_bp
from .goals import goals_bp
from .achievements import achievements_bp

# Content and tools
from .articles import articles_bp
from .tools import tools_bp
from .hand_eval import hand_eval_bp
from .common import common_bp
from .reset_db import reset_db_bp