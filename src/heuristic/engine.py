"""Heuristic orchestrator for grooming stage detection."""

import re
from typing import Optional
from . import keywords
from . import patterns


class HeuristicEngine:
    """
    Rule-based engine for detecting grooming behavioral patterns.

    Scores text against keyword lists, regex patterns,
    and behavioral signals (frequency, timing, platform migration).

    Returns confidence scores (0.0-1.0) for each of 6 grooming stages:
    - FRIENDSHIP: Initial contact, personal info gathering
    - RELATIONSHIP: Building emotional connection
    - RISK_ASSESSMENT: Testing victim's protective factors
    - EXCLUSIVITY: Isolating victim from support network
    - SEXUAL: Sexual desensitization
    - APPROACH: Arranging physical contact
    """

    # Grooming stages
    GROOMING_STAGES = [
        "FRIENDSHIP",
        "RELATIONSHIP",
        "RISK_ASSESSMENT",
        "EXCLUSIVITY",
        "SEXUAL",
        "APPROACH",
    ]

    def __init__(self):
        """Initialize the heuristic engine with rules and keywords."""
        self.keywords_map = keywords.RISK_KEYWORDS
        self.patterns_map = patterns.PATTERNS
        self._validate_setup()

    def _validate_setup(self) -> None:
        """Validate that all stages have keywords and patterns."""
        for stage in self.GROOMING_STAGES:
            if stage not in self.keywords_map and stage not in self.patterns_map:
                if stage != "RELATIONSHIP":  # RELATIONSHIP might only have patterns
                    pass  # Warn but don't fail

    def score_message(self, text: str) -> dict[str, float]:
        """
        Score a message against heuristic rules.

        Checks for:
        1. Keyword matches from risk keywords lists
        2. Regex pattern matches
        3. High-risk lexicon (prize offers, platforms, etc.)

        Args:
            text: Message text (should be cleaned/lowercased by preprocessing)

        Returns:
            Dictionary mapping each grooming stage to confidence score (0.0-1.0).
            Example:
            {
                "FRIENDSHIP": 0.3,
                "RELATIONSHIP": 0.2,
                "RISK_ASSESSMENT": 0.85,
                "EXCLUSIVITY": 0.5,
                "SEXUAL": 0.1,
                "APPROACH": 0.7
            }
        """
        text_lower = text.lower()
        scores = {}

        for stage in self.GROOMING_STAGES:
            score = self._score_stage(text_lower, stage)
            scores[stage] = score

        return scores

    def _score_stage(self, text: str, stage: str) -> float:
        """
        Score text for a specific grooming stage.

        Combines keyword matches, pattern matches, and high-risk lexicon.

        Args:
            text: Lowercased message text
            stage: Grooming stage name

        Returns:
            Confidence score (0.0-1.0)
        """
        keyword_score = self._score_keywords(text, stage)
        pattern_score = self._score_patterns(text, stage)
        high_risk_score = self._score_high_risk_lexicon(text)

        # Combine scores: keyword + pattern + high_risk boost
        # If any high-risk lexicon is present, slightly boost the score
        combined = (keyword_score + pattern_score) / 2.0

        if high_risk_score > 0 and stage in ["RISK_ASSESSMENT", "APPROACH"]:
            combined = min(1.0, combined + high_risk_score * 0.2)

        return min(1.0, combined)

    def _score_keywords(self, text: str, stage: str) -> float:
        """
        Score based on keyword matches.

        Counts how many keywords from the stage appear in the text.
        Normalized by total keywords in the stage.

        Args:
            text: Lowercased message text
            stage: Grooming stage name

        Returns:
            Score (0.0-1.0)
        """
        if stage not in self.keywords_map:
            return 0.0

        keywords_list = self.keywords_map[stage]
        if not keywords_list:
            return 0.0

        matches = 0
        for keyword in keywords_list:
            # Exact phrase match (word boundaries)
            if re.search(r"\b" + re.escape(keyword) + r"\b", text):
                matches += 1

        # Normalize: matches / total_keywords
        score = matches / len(keywords_list)
        return min(1.0, score)

    def _score_patterns(self, text: str, stage: str) -> float:
        """
        Score based on regex pattern matches.

        Checks if any regex patterns for the stage match the text.
        Binary: if any match found, return 0.5; else 0.0
        Can return higher if multiple patterns match.

        Args:
            text: Lowercased message text
            stage: Grooming stage name

        Returns:
            Score (0.0-1.0)
        """
        if stage not in self.patterns_map:
            return 0.0

        patterns_list = self.patterns_map[stage]
        if not patterns_list:
            return 0.0

        matching_patterns = patterns.get_matching_patterns(text, patterns_list)
        if not matching_patterns:
            return 0.0

        # Multiple pattern matches = higher confidence
        # 1 match = 0.5, 2+ matches = 0.8, 3+ = 1.0
        if len(matching_patterns) >= 3:
            return 1.0
        elif len(matching_patterns) >= 2:
            return 0.8
        else:
            return 0.5

    def _score_high_risk_lexicon(self, text: str) -> float:
        """
        Score based on high-risk lexicon (prize offers, platforms, etc.).

        These are strong indicators of grooming/scam attempts.

        Args:
            text: Lowercased message text

        Returns:
            Score (0.0-1.0)
        """
        if "HIGH_RISK_LEXICON" not in self.keywords_map:
            return 0.0

        high_risk_list = self.keywords_map["HIGH_RISK_LEXICON"]
        matches = 0

        for item in high_risk_list:
            if re.search(r"\b" + re.escape(item) + r"\b", text, re.IGNORECASE):
                matches += 1

        if not matches:
            return 0.0

        # High-risk lexicon is very suspicious
        score = min(1.0, matches / 2.0)  # 2+ items = 1.0 confidence
        return score

    def score_conversation(self, messages: list[dict]) -> dict[str, float]:
        """
        Score a conversation (multiple messages from same sender).

        Averages scores across all messages in the conversation.
        Can be extended to include behavioral signals (frequency, timing).

        Args:
            messages: List of message dicts with "text" key.
                     Example: [{"text": "hello"}, {"text": "where are you from"}]

        Returns:
            Aggregated scores for the entire conversation
        """
        if not messages:
            return {stage: 0.0 for stage in self.GROOMING_STAGES}

        all_scores = []
        for message in messages:
            if "text" not in message:
                continue
            score = self.score_message(message["text"])
            all_scores.append(score)

        # Average scores across all messages
        aggregated = {stage: 0.0 for stage in self.GROOMING_STAGES}
        for stage in self.GROOMING_STAGES:
            stage_scores = [s[stage] for s in all_scores if stage in s]
            if stage_scores:
                aggregated[stage] = sum(stage_scores) / len(stage_scores)

        return aggregated
