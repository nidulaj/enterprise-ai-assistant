import os
import datetime
import uuid
import urllib.parse
from functools import wraps
import jwt
import bcrypt
import requests
from flask import Blueprint, request, jsonify, make_response, redirect, g
from dotenv import load_dotenv
from supabase import create_client
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

load_dotenv()

auth_bp = Blueprint("auth", __name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
JWT_SECRET = os.getenv(
    "JWT_SECRET",
    "enterprise-ai-assistant-jwt-secret-key-production-super-secure-32bytes-min"
)

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:5000")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL or SUPABASE_KEY is missing from environment variables.")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
COOKIE_NAME = "access_token"
TOKEN_EXPIRY_DAYS = 7


def create_jwt_token(user_record: dict) -> str:
    """Generates a cryptographically signed application JWT token."""
    exp_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=TOKEN_EXPIRY_DAYS)
    iat_time = datetime.datetime.now(datetime.timezone.utc)

    token_payload = {
        "id": user_record["id"],
        "username": user_record["username"],
        "exp": exp_time,
        "iat": iat_time
    }

    return jwt.encode(token_payload, JWT_SECRET, algorithm="HS256")


def set_auth_cookie(response, token: str):
    """Sets HttpOnly access_token cookie on the response."""
    is_production = os.getenv("FLASK_ENV") == "production"
    max_age = TOKEN_EXPIRY_DAYS * 24 * 3600

    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="Lax",
        secure=is_production,
        max_age=max_age,
        path="/"
    )
    return response


def find_or_create_google_user(email: str, name: str = None) -> dict:
    """
    Finds an existing user in Supabase 'users' table by email or username,
    or creates a new record if not yet registered.
    """
    clean_email = email.strip().lower()
    prefix = clean_email.split("@")[0]

    # 1. Search by exact email
    try:
        res = supabase.table("users").select("id, username").eq("username", clean_email).limit(1).execute()
        if res and res.data and len(res.data) > 0:
            return res.data[0]
    except Exception as e:
        print(f"[Supabase email check warning] {e}")

    # 2. Search by prefix
    try:
        res = supabase.table("users").select("id, username").eq("username", prefix).limit(1).execute()
        if res and res.data and len(res.data) > 0:
            return res.data[0]
    except Exception as e:
        print(f"[Supabase prefix check warning] {e}")

    # 3. Create new user in Supabase 'users' table
    username_to_use = clean_email
    generated_password = f"google_oauth_{uuid.uuid4().hex[:16]}"

    try:
        insert_res = supabase.table("users").insert({
            "username": username_to_use,
            "password": generated_password
        }).execute()

        if insert_res and insert_res.data and len(insert_res.data) > 0:
            return insert_res.data[0]
    except Exception as e:
        print(f"[Google User Creation Warning] {e}")

    # Fallback: check again if another process inserted it
    try:
        fallback = supabase.table("users").select("id, username").eq("username", username_to_use).limit(1).execute()
        if fallback and fallback.data and len(fallback.data) > 0:
            return fallback.data[0]
    except Exception as e:
        print(f"[Supabase fallback check warning] {e}")

    # Final fallback: return safe virtual record
    return {"id": int(hash(clean_email) % 1000000), "username": username_to_use}


def extract_token_from_request():
    """Extracts JWT token from HTTP-only cookie or Authorization header."""
    # 1. Primary: check HTTP-only cookie
    token = request.cookies.get(COOKIE_NAME)
    if token:
        return token

    # 2. Check fallback cookie name
    token = request.cookies.get("enterprise_jwt_session")
    if token:
        return token

    # 3. Secondary: check Authorization header
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header.split(" ")[1]

    # 4. JSON body if provided
    if request.is_json and request.json and "token" in request.json:
        return request.json.get("token")

    return None


def token_required(f):
    """
    Decorator to protect API routes with JWT authentication.
    Checks HTTP-only cookie first, then Authorization Bearer header.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = extract_token_from_request()

        if not token:
            return jsonify({"error": "Authentication required. Please sign in."}), 401

        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            request.current_user = payload
            g.current_user = payload
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Session expired. Please sign in again."}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid authentication token."}), 401

        return f(*args, **kwargs)

    return decorated


@auth_bp.route("/auth/login", methods=["POST"])
def login():
    """
    Authenticates username and password against Supabase 'users' table.
    Issues a cryptographically signed JWT token and sets an HttpOnly cookie.
    """
    data = request.json or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    if not username or not password:
        return jsonify({"error": "Username and password are required."}), 400

    try:
        # Query user record from Supabase 'users' table
        response = (
            supabase.table("users")
            .select("id, username, password")
            .eq("username", username)
            .limit(1)
            .execute()
        )
        user_record = response.data[0] if (response and response.data and len(response.data) > 0) else None

        if not user_record:
            return jsonify({"error": "Invalid username or password."}), 401

        db_password = str(user_record.get("password") or "")
        is_valid = False

        # 1. Plain-text password comparison
        if db_password == password:
            is_valid = True
        # 2. Bcrypt hashed password comparison
        elif db_password.startswith("$2a$") or db_password.startswith("$2b$") or db_password.startswith("$2y$"):
            try:
                is_valid = bcrypt.checkpw(password.encode("utf-8"), db_password.encode("utf-8"))
            except Exception:
                is_valid = False

        if not is_valid:
            return jsonify({"error": "Invalid username or password."}), 401

        token = create_jwt_token(user_record)

        res = make_response(jsonify({
            "success": True,
            "token": token,
            "user": {
                "id": user_record["id"],
                "username": user_record["username"]
            }
        }), 200)

        set_auth_cookie(res, token)
        return res

    except Exception as e:
        print(f"[Auth Error] {e}")
        return jsonify({"error": "Internal authentication server error."}), 500


# ============================================================================
# GOOGLE AUTHENTICATION ENDPOINTS
# ============================================================================

@auth_bp.route("/auth/google", methods=["GET"])
def google_oauth_redirect():
    """
    Initiates Google OAuth 2.0 Web flow.
    Redirects the user to the Google Account consent screen.
    Requests openid, email, profile, and Google Calendar scopes.
    """
    client_id = GOOGLE_CLIENT_ID or os.getenv("GOOGLE_CLIENT_ID")
    if not client_id:
        return jsonify({"error": "GOOGLE_CLIENT_ID is not configured in backend/.env"}), 500

    redirect_uri = os.getenv(
        "GOOGLE_REDIRECT_URI",
        f"{BACKEND_URL}/auth/google/callback"
    )

    scope = "openid email profile https://www.googleapis.com/auth/calendar"
    state = str(uuid.uuid4())

    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": scope,
        "access_type": "offline",
        "prompt": "consent",
        "state": state
    }

    google_auth_url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(params)
    return redirect(google_auth_url)


@auth_bp.route("/auth/google/callback", methods=["GET"])
def google_oauth_callback():
    """
    Handles Google OAuth 2.0 redirect callback.
    Exchanges code for tokens, synchronizes user in Supabase,
    sets HttpOnly session cookie, and redirects user to /chat.
    """
    code = request.args.get("code")
    error = request.args.get("error")

    frontend_redirect_url = os.getenv("FRONTEND_URL", "http://localhost:3000")

    if error or not code:
        return redirect(f"{frontend_redirect_url}/?error={error or 'google_auth_denied'}")

    client_id = GOOGLE_CLIENT_ID or os.getenv("GOOGLE_CLIENT_ID")
    client_secret = GOOGLE_CLIENT_SECRET or os.getenv("GOOGLE_CLIENT_SECRET")
    redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", f"{BACKEND_URL}/auth/google/callback")

    try:
        # Exchange authorization code for Google access token and ID token
        token_endpoint = "https://oauth2.googleapis.com/token"
        token_payload = {
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code"
        }

        res = requests.post(token_endpoint, data=token_payload, timeout=10)
        token_data = res.json()

        if "error" in token_data:
            err_desc = token_data.get("error_description", token_data["error"])
            print(f"[Google OAuth Callback Error] {err_desc}")
            return redirect(f"{frontend_redirect_url}/?error={urllib.parse.quote(err_desc)}")

        # Decode ID token or query userinfo to get user details
        google_user = None
        id_token_jwt = token_data.get("id_token")

        if id_token_jwt:
            try:
                google_user = id_token.verify_oauth2_token(
                    id_token_jwt,
                    google_requests.Request(),
                    client_id,
                    clock_skew_in_seconds=10
                )
            except Exception as e:
                print(f"[ID Token verify warning] {e}")

        if not google_user and "access_token" in token_data:
            userinfo_res = requests.get(
                "https://www.googleapis.com/oauth2/v3/userinfo",
                headers={"Authorization": f"Bearer {token_data['access_token']}"},
                timeout=10
            )
            google_user = userinfo_res.json()

        if not google_user or not google_user.get("email"):
            return redirect(f"{frontend_redirect_url}/?error=Google user profile not found.")

        email = google_user["email"]
        name = google_user.get("name") or email.split("@")[0]

        # Find or create user in Supabase 'users' table
        user_record = find_or_create_google_user(email, name)

        # Automatically persist Google tokens for Calendar Agent (so token.json is synced)
        try:
            import json
            token_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "token.json")
            with open(token_path, "w") as tf:
                json.dump(token_data, tf)
            print("[Google Auth] Synced calendar credentials to token.json")
        except Exception as te:
            print(f"[Token Save Notice] {te}")

        # Issue application JWT token
        app_token = create_jwt_token(user_record)

        # Redirect user directly to the authenticated /chat workspace with cookie set
        response = make_response(redirect(f"{frontend_redirect_url}/chat"))
        set_auth_cookie(response, app_token)
        return response

    except Exception as e:
        print(f"[Google OAuth Exception] {e}")
        return redirect(f"{frontend_redirect_url}/?error=Google authentication failed.")


@auth_bp.route("/auth/google", methods=["POST"])
def google_verify_credential():
    """
    Accepts Google ID token (from Google Identity Services popup / One Tap),
    verifies it with Google, finds/creates user in Supabase, and sets the HttpOnly session cookie.
    """
    data = request.json or {}
    credential = data.get("credential") or data.get("token") or data.get("id_token")

    if not credential:
        return jsonify({"error": "Google credential token is required."}), 400

    client_id = GOOGLE_CLIENT_ID or os.getenv("GOOGLE_CLIENT_ID")

    try:
        google_user = id_token.verify_oauth2_token(
            credential,
            google_requests.Request(),
            client_id,
            clock_skew_in_seconds=10
        )
    except Exception as e:
        print(f"[Google Credential Verify Error] {e}")
        return jsonify({"error": f"Invalid Google credential: {str(e)}"}), 401

    email = google_user.get("email")
    if not email:
        return jsonify({"error": "Google token does not contain an email address."}), 400

    name = google_user.get("name") or email.split("@")[0]
    user_record = find_or_create_google_user(email, name)

    app_token = create_jwt_token(user_record)

    res = make_response(jsonify({
        "success": True,
        "token": app_token,
        "user": {
            "id": user_record["id"],
            "username": user_record["username"],
            "email": email
        }
    }), 200)

    set_auth_cookie(res, app_token)
    return res


@auth_bp.route("/auth/logout", methods=["GET", "POST"])
def logout():
    """
    Clears the authentication HttpOnly cookie.
    """
    res = make_response(jsonify({"success": True, "message": "Logged out successfully"}), 200)
    res.set_cookie(
        key=COOKIE_NAME,
        value="",
        httponly=True,
        samesite="Lax",
        expires=0,
        max_age=0,
        path="/"
    )
    return res


@auth_bp.route("/auth/me", methods=["GET"])
def get_current_user():
    """
    Decodes the JWT cookie on the backend and returns the current authenticated user.
    """
    token = extract_token_from_request()

    if not token:
        return jsonify({"authenticated": False, "error": "Not authenticated."}), 401

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return jsonify({
            "authenticated": True,
            "user": {
                "id": payload.get("id"),
                "username": payload.get("username")
            }
        }), 200
    except jwt.ExpiredSignatureError:
        return jsonify({"authenticated": False, "error": "Session expired."}), 401
    except jwt.InvalidTokenError:
        return jsonify({"authenticated": False, "error": "Invalid authentication token."}), 401


@auth_bp.route("/auth/verify", methods=["GET", "POST"])
def verify():
    """
    Verifies JWT token and returns validity and user payload.
    """
    token = extract_token_from_request()

    if not token:
        return jsonify({"valid": False, "error": "Token missing"}), 401

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return jsonify({
            "valid": True,
            "user": {
                "id": payload.get("id"),
                "username": payload.get("username")
            }
        }), 200
    except jwt.ExpiredSignatureError:
        return jsonify({"valid": False, "error": "Token expired"}), 401
    except jwt.InvalidTokenError as e:
        return jsonify({"valid": False, "error": f"Invalid token: {str(e)}"}), 401
