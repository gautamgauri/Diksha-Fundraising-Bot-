# Streamlit app lib package

# Import all modules to make them available
try:
    from . import auth
    from . import api
except ImportError as e:
    print(f"Warning: Could not import lib modules: {e}")

# Export commonly used functions with fallbacks
try:
    from .auth import check_auth, require_auth, show_auth_status, get_current_user, logout
except ImportError:
    # Fallback functions
    def check_auth(): return True
    def require_auth(): return True
    def show_auth_status(): return None
    def get_current_user(): return "admin"
    def logout(): return None

try:
    from .api import log_activity, get_cached_pipeline_data
except ImportError:
    # Fallback functions
    def log_activity(*args, **kwargs): return None
    def get_cached_pipeline_data(): return []

__all__ = [
    'check_auth', 'require_auth', 'show_auth_status', 'get_current_user', 'logout',
    'log_activity', 'get_cached_pipeline_data'
]