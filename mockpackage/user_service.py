from flask import Flask, jsonify, request
from functools import wraps

app = Flask(__name__)

# Mock decorators (simulate auth and rate limit)
def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Simulate login check
        return func(*args, **kwargs)
    return wrapper

def rate_limit(limit):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Simulate rate limiting
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Mock user context
class User:
    def __init__(self, name, email, role):
        self.name = name
        self.email = email
        self.role = role

@app.route("/profile")
@rate_limit(limit=10)
@login_required
def get_user_profile():
    """
    Returns the currently logged-in user's profile.

    Returns:
        dict: User metadata including name, email, and role.
    """
    # Simulate user object normally set by authentication middleware
    user = User(name="Alice", email="alice@example.com", role="admin")
    return jsonify({
        "name": user.name,
        "email": user.email,
        "role": user.role
    })

if __name__ == "__main__":
    app.run(debug=True)
