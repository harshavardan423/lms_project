"""Placeholder notification service. Replace with real email/SMS providers."""

def send_email(to_address, subject, body):
    """Placeholder: send email notification."""
    print(f"[EMAIL STUB] To: {to_address} | Subject: {subject}")
    return True

def send_sms(phone_number, message):
    """Placeholder: send SMS notification."""
    print(f"[SMS STUB] To: {phone_number} | Message: {message[:50]}...")
    return True

def notify_user(user, announcement):
    """Send in-app, email, or SMS based on announcement channel."""
    channel = announcement.channel
    if channel == 'email' and user.email:
        send_email(user.email, announcement.title, announcement.body)
    elif channel == 'sms' and user.phone:
        send_sms(user.phone, f"{announcement.title}: {announcement.body[:100]}")
    # in_app is handled by DB query, no push needed
    return True
