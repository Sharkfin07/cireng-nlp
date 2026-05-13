"""Explainability module for model predictions."""


def extract_label_triggers(text: str, labels: list[dict]) -> list[str]:
    """
    Extract text fragments that triggered each label.

    Args:
        text: Input message
        labels: Detected labels with scores

    Returns:
        List of triggering text fragments (max 50 chars each)
    """
    pass


def format_explanation(risk_score: float, labels: list[dict]) -> dict:
    """
    Format model output with explainability data.

    Args:
        risk_score: Final risk score (0-100)
        labels: Detected grooming stages with confidence

    Returns:
        Structured explanation dict
    """
    pass
