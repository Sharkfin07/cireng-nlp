"""Behavioral signals for grooming detection (frequency, timing, patterns)."""


def detect_message_frequency(messages: list[dict]) -> bool:
    """
    Detect unusually high message frequency (>20 messages/hour).

    Args:
        messages: List of message dicts with timestamps

    Returns:
        True if abnormal frequency detected
    """
    pass


def detect_night_activity(messages: list[dict]) -> bool:
    """
    Detect messages between 22:00-04:00 (suspicious timing).

    Args:
        messages: List of message dicts with timestamps

    Returns:
        True if late-night activity detected
    """
    pass


def detect_platform_migration(text: str) -> bool:
    """
    Detect requests to move conversation (Discord, WhatsApp, etc).

    Args:
        text: Message text

    Returns:
        True if platform migration request detected
    """
    pass
