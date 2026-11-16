import os
import datetime
from functools import wraps
import jwt
import bcrypt
from flask import Blueprint, request, jsonify, make_response, g
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

auth_bp = Blueprint("auth", __name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
JWT_SECRET = os.getenv(
    "JWT_SECRET",
    "enterprise-ai-assistant-jwt-secret-key-production-super-secure-32bytes-min"
)

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL or SUPABASE_KEY is missing from environment variables.")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
COOKIE_NAME = "access_token"
TOKEN_EXPIRY_DAYS = 7


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
            .maybe_single()
            .execute()
        )
        user_record = response.data

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

        # Generate JWT token with expiration
        exp_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=TOKEN_EXPIRY_DAYS)
        iat_time = datetime.datetime.now(datetime.timezone.utc)

        token_payload = {
            "id": user_record["id"],
            "username": user_record["username"],
            "exp": exp_time,
            "iat": iat_time
        }

        token = jwt.encode(token_payload, JWT_SECRET, algorithm="HS256")

        # Create response and attach HttpOnly cookie
        res = make_response(jsonify({
            "success": True,
            "token": token,
            "user": {
                "id": user_record["id"],
                "username": user_record["username"]
            }
        }), 200)

        is_production = os.getenv("FLASK_ENV") == "production"
        max_age = TOKEN_EXPIRY_DAYS * 24 * 3600

        res.set_cookie(
            key=COOKIE_NAME,
            value=token,
            httponly=True,
            samesite="Lax",
            secure=is_production,
            max_age=max_age,
            path="/"
        )

        return res

    except Exception as e:
        print(f"[Auth Error] {e}")
        return jsonify({"error": "Internal authentication server error."}), 500


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
