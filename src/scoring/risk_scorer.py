"""Risk score aggregation from heuristic and NLP scores."""


def combine_scores(heuristic_scores: dict, nlp_scores: dict) -> tuple[float, list[dict]]:
    """
    Combine heuristic and NLP scores into final risk assessment.

    Args:
        heuristic_scores: Scores from rule-based engine
        nlp_scores: Scores from IndoBERTweet classifier

    Returns:
        Tuple of (risk_score: 0-100, labels_with_confidence: list[dict])
    """
    pass


def apply_threshold(risk_score: float, threshold: float = 50.0) -> bool:
    """
    Determine if risk score exceeds alert threshold.

    Args:
        risk_score: Combined risk score (0-100)
        threshold: Alert threshold (default 50)

    Returns:
        True if score >= threshold
    """
    return risk_score >= threshold
