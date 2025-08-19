from typing import Optional
from .models import NotificationType

# Stubs to integrate with real providers

def send_notification(notification_type: NotificationType, to: str, content: str) -> None:
    # Replace with actual email/SMS provider logic
    print(f"Notify[{notification_type}] -> {to}: {content}")


def format_order_notification(prefix: str, receipt_number: str, status: str, extra: Optional[str] = None) -> str:
    details = f"{prefix} | Order {receipt_number} status: {status}"
    if extra:
        details += f" | {extra}"
    return details