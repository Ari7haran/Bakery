"""
Backward compatibility facade for auth router.
Re-exports router from app.api.v1.auth and dependencies from app.core.dependencies.
"""
from app.api.v1.auth import router, register, login, login_form, me
from app.core.dependencies import get_current_user, get_current_admin, oauth2_scheme

__all__ = ["router", "register", "login", "login_form", "me", "get_current_user", "get_current_admin", "oauth2_scheme"]
