
def public_fn():
    pass

@login_required
def handle_login(user):
    """Handles user login."""
    return True

@login_required
def handle_logout():
    return False
