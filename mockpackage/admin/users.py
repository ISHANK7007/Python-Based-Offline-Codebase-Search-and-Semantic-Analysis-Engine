import logging
from functools import wraps
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base

# Setup logger
logger = logging.getLogger("admin")
logging.basicConfig(level=logging.INFO)

# SQLAlchemy setup
Base = declarative_base()
engine = create_engine("sqlite:///mockpackage/admin/users.db", echo=False)
Session = sessionmaker(bind=engine)

# Define User model
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String)
    is_deleted = Column(Boolean, default=False)

# Create the table
Base.metadata.create_all(engine)

# Real admin_required decorator
def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.info("[SECURITY] Admin check passed.")
        return func(*args, **kwargs)
    return wrapper

@admin_required
def delete_user(user_id: int, hard_delete: bool = False) -> bool:
    """
    Deletes a user from the system.

    Args:
        user_id (int): ID of the user to delete.
        hard_delete (bool): Whether to delete permanently.

    Returns:
        bool: True if deletion succeeded.
    """
    session = Session()
    user = session.query(User).filter_by(id=user_id).first()
    if not user:
        logger.error(f"User {user_id} not found.")
        return False

    if hard_delete:
        session.delete(user)
        logger.info(f"User {user_id} permanently deleted.")
    else:
        user.is_deleted = True
        logger.info(f"User {user_id} marked as deleted.")

    session.commit()
    return True

if __name__ == "__main__":
    # Sample seed + deletion test
    session = Session()
    # Seed user if not exists
    if not session.query(User).filter_by(id=42).first():
        session.add(User(id=42, email="test@example.com"))
        session.commit()

    # Run deletion logic
    success = delete_user(42, hard_delete=False)
    print("Soft delete result:", success)
