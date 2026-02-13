from flask_bcrypt import Bcrypt
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_mailman import Mail
from flask_principal import Principal
from flask_wtf.csrf import CSRFProtect
from flask import request
import logging

logger = logging.getLogger(__name__)

def get_real_ip():
    """
    Extract the real client IP address from proxied requests.
    
    PythonAnywhere (and most production deployments) use reverse proxies,
    which means request.remote_addr returns the proxy's IP, not the client's.
    
    The real IP is in the X-Forwarded-For header, which may contain multiple IPs:
    X-Forwarded-For: client_ip, proxy1_ip, proxy2_ip
    
    We want the leftmost (first) IP, which is the original client.
    """
    # Try to get IP from X-Forwarded-For header (standard for proxies)
    forwarded_for = request.headers.get('X-Forwarded-For')
    
    if forwarded_for:
        # X-Forwarded-For can be a comma-separated list of IPs
        # Format: "client_ip, proxy1_ip, proxy2_ip"
        # We want the first (leftmost) IP which is the real client
        client_ip = forwarded_for.split(',')[0].strip()
        logger.debug(f"Rate limiter using X-Forwarded-For IP: {client_ip}")
        return client_ip
    
    # Fallback to X-Real-IP (used by some proxies like nginx)
    real_ip = request.headers.get('X-Real-IP')
    if real_ip:
        logger.debug(f"Rate limiter using X-Real-IP: {real_ip}")
        return real_ip
    
    # Final fallback to direct connection IP
    remote_addr = request.remote_addr
    logger.debug(f"Rate limiter using remote_addr: {remote_addr}")
    return remote_addr

bcrypt = Bcrypt()
cache = Cache()
limiter = Limiter(key_func=get_real_ip)
mail = Mail()
principal = Principal()
csrf = CSRFProtect()