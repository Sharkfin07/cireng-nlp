"""Demo script showing heuristic engine in action."""

from src.heuristic.engine import HeuristicEngine
import json


def demo_single_messages():
    """Demonstrate scoring of individual messages."""
    engine = HeuristicEngine()

    test_messages = [
        "Berapa umur kamu? Aku suka apa sih?",
        "orang tua kamu ada di rumah gak?",
        "Hapus chat ini ya, jangan kasih tau siapa pun",
        "Rahasia kita berdua ya, jangan bilang ke siapa pun",
        "Mau ketemu aku? Aku bisa jemput kamu",
        "Kamu dapat diamond gratis dari saya",
        "Pindah ke discord yuk, private aja",
        "Halo, apa kabar? Cuaca bagus hari ini",
    ]

    print("=" * 80)
    print("HEURISTIC ENGINE DEMO - Single Message Scoring")
    print("=" * 80)

    for msg in test_messages:
        print(f"\nMessage: '{msg}'")
        scores = engine.score_message(msg)

        # Sort by score, show top 3
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        print("Scores:")
        for stage, score in sorted_scores[:3]:
            bar_length = int(score * 30)
            bar = "#" * bar_length + "-" * (30 - bar_length)
            print(f"  {stage:18} [{bar}] {score:.2f}")


def demo_conversation():
    """Demonstrate scoring of full conversation."""
    engine = HeuristicEngine()

    conversation = [
        {"text": "Assalamualaikum, siapa nama kamu?"},
        {"text": "Berapa umur kamu, dari mana asal?"},
        {"text": "Orang tua kamu ada di rumah gak?"},
        {"text": "Sendirian aja? Bisa kita chat privat"},
        {"text": "Hapus chat ini ya, jangan kasih tau siapa pun"},
        {"text": "Mau ketemu aku? Aku bisa jemput kamu malam ini"},
    ]

    print("\n" + "=" * 80)
    print("HEURISTIC ENGINE DEMO - Full Conversation Scoring")
    print("=" * 80)

    for i, msg in enumerate(conversation, 1):
        print(f"\nMessage {i}: '{msg['text']}'")
        scores = engine.score_message(msg["text"])
        top_stage = max(scores.items(), key=lambda x: x[1])
        print(f"  -> Top signal: {top_stage[0]} ({top_stage[1]:.2f})")

    print("\n" + "-" * 80)
    print("Overall Conversation Score (Average):")
    print("-" * 80)

    conv_scores = engine.score_conversation(conversation)
    sorted_scores = sorted(conv_scores.items(), key=lambda x: x[1], reverse=True)

    for stage, score in sorted_scores:
        bar_length = int(score * 30)
        bar = "#" * bar_length + "-" * (30 - bar_length)
        print(f"  {stage:18} [{bar}] {score:.2f}")

    # Risk assessment
    high_risk = conv_scores["RISK_ASSESSMENT"]
    approach = conv_scores["APPROACH"]

    print("\n" + "-" * 80)
    if high_risk > 0.5 or approach > 0.5:
        print("[ALERT] This conversation shows signs of grooming behavior!")
    else:
        print("[OK] No strong grooming signals detected.")


if __name__ == "__main__":
    demo_single_messages()
    demo_conversation()
