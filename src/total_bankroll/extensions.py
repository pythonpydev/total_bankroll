from flask_bcrypt import Bcrypt
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_mailman import Mail
from flask_principal import Principal

bcrypt = Bcrypt()
limiter = Limiter(key_func=get_remote_address)
mail = Mail()
principal = Principal()