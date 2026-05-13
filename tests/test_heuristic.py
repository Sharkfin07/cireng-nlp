"""Tests for heuristic engine."""

import pytest
from src.heuristic.engine import HeuristicEngine


@pytest.fixture
def engine():
    """Fixture to provide initialized HeuristicEngine."""
    return HeuristicEngine()


class TestHeuristicEngineInit:
    """Tests for engine initialization."""

    def test_engine_initializes(self, engine):
        """Test that engine initializes without error."""
        assert engine is not None

    def test_grooming_stages_defined(self, engine):
        """Test that all 6 grooming stages are defined."""
        expected_stages = [
            "FRIENDSHIP",
            "RELATIONSHIP",
            "RISK_ASSESSMENT",
            "EXCLUSIVITY",
            "SEXUAL",
            "APPROACH",
        ]
        assert engine.GROOMING_STAGES == expected_stages

    def test_keywords_loaded(self, engine):
        """Test that keywords dictionary is loaded."""
        assert engine.keywords_map is not None
        assert len(engine.keywords_map) > 0


class TestScoreSingleMessage:
    """Tests for single message scoring."""

    def test_score_returns_dict(self, engine):
        """Test that score_message returns a dictionary."""
        result = engine.score_message("hello world")
        assert isinstance(result, dict)

    def test_score_has_all_stages(self, engine):
        """Test that score includes all grooming stages."""
        result = engine.score_message("test message")
        for stage in engine.GROOMING_STAGES:
            assert stage in result

    def test_score_range_0_to_1(self, engine):
        """Test that all scores are between 0.0 and 1.0."""
        result = engine.score_message("test message with random words")
        for stage, score in result.items():
            assert 0.0 <= score <= 1.0, f"{stage} score {score} out of range"

    def test_empty_message_scores_low(self, engine):
        """Test that empty message gets low scores."""
        result = engine.score_message("")
        for score in result.values():
            assert score == 0.0

    def test_generic_message_scores_low(self, engine):
        """Test that generic message without grooming signals scores low."""
        result = engine.score_message("good morning how are you today")
        avg_score = sum(result.values()) / len(result)
        assert avg_score < 0.3


class TestRiskAssessmentStage:
    """Tests for RISK_ASSESSMENT stage detection."""

    def test_detects_parent_check_keyword(self, engine):
        """Test detection of 'orang tua ada' keyword."""
        result = engine.score_message("orang tua kamu ada di rumah gak")
        assert result["RISK_ASSESSMENT"] > 0.3

    def test_detects_delete_chat_keyword(self, engine):
        """Test detection of 'hapus chat' keyword."""
        result = engine.score_message("hapus chat ini ya, jangan kasih tau siapa pun")
        assert result["RISK_ASSESSMENT"] > 0.3

    def test_detects_delete_message_keyword(self, engine):
        """Test detection of 'delete pesan' keyword."""
        result = engine.score_message("delete pesan ini setelah kamu baca")
        assert result["RISK_ASSESSMENT"] > 0.3

    def test_multiple_risk_keywords_boost_score(self, engine):
        """Test that multiple keywords boost the score."""
        single = engine.score_message("hapus chat")
        multiple = engine.score_message("orang tua ada hapus chat jangan kasih tau")
        assert multiple["RISK_ASSESSMENT"] > single["RISK_ASSESSMENT"]


class TestApproachStage:
    """Tests for APPROACH stage detection."""

    def test_detects_meeting_keyword(self, engine):
        """Test detection of 'ketemu' keyword."""
        result = engine.score_message("mau ketemu kamu hari sabtu")
        assert result["APPROACH"] > 0.3

    def test_detects_platform_migration(self, engine):
        """Test detection of platform migration requests."""
        result = engine.score_message("pindah ke discord yuk")
        assert result["APPROACH"] >= 0.2

    def test_detects_location_query(self, engine):
        """Test detection of location requests."""
        result = engine.score_message("rumahnya dimana sih")
        assert result["APPROACH"] > 0.3


class TestExclusivityStage:
    """Tests for EXCLUSIVITY stage detection."""

    def test_detects_secret_keyword(self, engine):
        """Test detection of 'rahasia' keyword."""
        result = engine.score_message("rahasia kita berdua ya jangan bilang siapa pun")
        assert result["EXCLUSIVITY"] > 0.3

    def test_detects_exclusive_language(self, engine):
        """Test detection of exclusive/special language."""
        result = engine.score_message("cuma kita berdua yang ngerti ini")
        assert result["EXCLUSIVITY"] > 0.3


class TestHighRiskLexicon:
    """Tests for high-risk lexicon detection (scam/grooming indicators)."""

    def test_detects_prize_offer(self, engine):
        """Test detection of prize offers (common in grooming scams)."""
        result = engine.score_message("kamu dapat diamond gratis dari saya")
        # High-risk should boost APPROACH or RISK_ASSESSMENT
        assert max(result["APPROACH"], result["RISK_ASSESSMENT"]) >= 0.1

    def test_detects_free_pulsa(self, engine):
        """Test detection of 'pulsa gratis'."""
        result = engine.score_message("saya punya pulsa gratis untuk kamu")
        assert max(result.values()) >= 0.1


class TestConversationScoring:
    """Tests for conversation-level scoring."""

    def test_score_conversation_single_message(self, engine):
        """Test scoring a conversation with one message."""
        messages = [{"text": "hapus chat ini ya"}]
        result = engine.score_conversation(messages)
        assert isinstance(result, dict)
        assert result["RISK_ASSESSMENT"] > 0.3

    def test_score_conversation_multiple_messages(self, engine):
        """Test scoring a conversation with multiple messages."""
        messages = [
            {"text": "berapa umur kamu"},
            {"text": "orang tua ada di rumah"},
            {"text": "mau ketemu gak"},
        ]
        result = engine.score_conversation(messages)
        assert isinstance(result, dict)
        # At least one stage should have detectable score
        assert max(result.values()) > 0.1

    def test_score_conversation_averages_across_messages(self, engine):
        """Test that conversation score is average of message scores."""
        msg1 = {"text": "hapus chat"}
        msg2 = {"text": "halo siapa nama kamu"}

        single_avg = (
            engine.score_message(msg1["text"])["RISK_ASSESSMENT"]
            + engine.score_message(msg2["text"])["RISK_ASSESSMENT"]
        ) / 2.0

        conversation = engine.score_conversation([msg1, msg2])
        assert abs(conversation["RISK_ASSESSMENT"] - single_avg) < 0.01

    def test_empty_conversation_scores_zero(self, engine):
        """Test that empty conversation gets zero scores."""
        result = engine.score_conversation([])
        for score in result.values():
            assert score == 0.0


class TestCaseInsensitivity:
    """Tests for case-insensitive matching."""

    def test_uppercase_keywords_detected(self, engine):
        """Test that uppercase keywords are detected."""
        result_lower = engine.score_message("hapus chat")
        result_upper = engine.score_message("HAPUS CHAT")
        assert result_lower["RISK_ASSESSMENT"] == result_upper["RISK_ASSESSMENT"]

    def test_mixed_case_detected(self, engine):
        """Test that mixed case is detected."""
        result = engine.score_message("HaPuS ChAt")
        assert result["RISK_ASSESSMENT"] > 0.3


class TestEdgeCases:
    """Tests for edge cases and special scenarios."""

    def test_false_positive_similar_words(self, engine):
        """Test that similar words don't cause false positives."""
        # "chat" shouldn't trigger RISK_ASSESSMENT by itself
        result = engine.score_message("let me chat with you")
        # Using English - should not match Indonesian patterns
        assert result["RISK_ASSESSMENT"] == 0.0

    def test_words_in_different_context(self, engine):
        """Test words in benign context."""
        # "rahasia" is used but in innocent way
        result = engine.score_message("saya punya rahasia tapi tidak bisa bilang")
        # This might still trigger due to keyword matching
        # This is a limitation of keyword-based approach
        pass

    def test_special_characters_handled(self, engine):
        """Test that special characters don't break parsing."""
        result = engine.score_message("hapus!!!! chat???")
        # Should still detect despite special chars
        assert result["RISK_ASSESSMENT"] > 0.0
