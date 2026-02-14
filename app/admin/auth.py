"""
Admin Authentication Module for MobilityGraph
Session-based authentication with fixed credentials
"""
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Request, HTTPException, Response

# Fixed admin credentials
ADMIN_USERNAME = "adminsuper"
ADMIN_PASSWORD = "admin12345"

# Session storage (in-memory for simplicity)
# In production, use Redis or database
sessions = {}

# Session configuration
SESSION_COOKIE_NAME = "mobilitygraph_session"
SESSION_EXPIRY_HOURS = 24


def hash_password(password: str) -> str:
    """Simple password hashing"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_credentials(username: str, password: str) -> bool:
    """Verify admin credentials"""
    return username == ADMIN_USERNAME and password == ADMIN_PASSWORD


def create_session(username: str) -> str:
    """Create a new session and return session ID"""
    session_id = secrets.token_urlsafe(32)
    sessions[session_id] = {
        "username": username,
        "created_at": datetime.now(),
        "expires_at": datetime.now() + timedelta(hours=SESSION_EXPIRY_HOURS)
    }
    return session_id


def validate_session(session_id: str) -> Optional[dict]:
    """Validate session and return session data if valid"""
    if not session_id or session_id not in sessions:
        return None
    
    session = sessions[session_id]
    
    # Check expiry
    if datetime.now() > session["expires_at"]:
        del sessions[session_id]
        return None
    
    return session


def destroy_session(session_id: str) -> bool:
    """Destroy a session"""
    if session_id in sessions:
        del sessions[session_id]
        return True
    return False


def get_session_from_request(request: Request) -> Optional[dict]:
    """Get session from request cookies"""
    session_id = request.cookies.get(SESSION_COOKIE_NAME)
    if not session_id:
        return None
    return validate_session(session_id)


def login_user(response: Response, username: str) -> str:
    """Login user and set session cookie"""
    session_id = create_session(username)
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=session_id,
        httponly=True,
        max_age=SESSION_EXPIRY_HOURS * 3600,
        samesite="lax"
    )
    return session_id


def logout_user(request: Request, response: Response) -> bool:
    """Logout user and clear session"""
    session_id = request.cookies.get(SESSION_COOKIE_NAME)
    if session_id:
        destroy_session(session_id)
    response.delete_cookie(SESSION_COOKIE_NAME)
    return True


def require_admin(request: Request):
    """
    Dependency to require admin authentication
    Raises HTTPException if not authenticated
    """
    session = get_session_from_request(request)
    if not session:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated. Please login."
        )
    return session


def require_admin_redirect(request: Request):
    """
    Check if admin is authenticated, redirect to login if not
    Returns session if authenticated, None otherwise
    """
    session = get_session_from_request(request)
    return session


class AdminRequired:
    """Dependency class for admin authentication"""
    
    def __init__(self, redirect_to_login: bool = True):
        self.redirect_to_login = redirect_to_login
    
    def __call__(self, request: Request):
        session = get_session_from_request(request)
        if not session:
            if self.redirect_to_login:
                return None  # Will be handled by route to redirect
            raise HTTPException(status_code=401, detail="Not authenticated")
        return session
