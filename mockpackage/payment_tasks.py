from functools import wraps

# Simulated shared_task decorator (no Celery required)
def shared_task(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"[Task Queued] {func.__name__} with args={args}, kwargs={kwargs}")
        return func(*args, **kwargs)
    return wrapper

# Mock mail sending logic
def send_email(user_id, subject, message):
    print(f"[Email Sent to User {user_id}]")
    print(f"Subject: {subject}")
    print(f"Message: {message}")

@shared_task
def process_failed_payment(user_id, reason):
    """
    Background task to notify users about failed payments.
    """
    subject = "Payment Failed"
    message = f"Your payment failed due to: {reason}"
    send_email(user_id=user_id, subject=subject, message=message)

if __name__ == "__main__":
    # Run test
    process_failed_payment(42, "Insufficient funds")
