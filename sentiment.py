# Feedback sentiment analysis functions.

# sentiment.py

from nltk.sentiment import SentimentIntensityAnalyzer
import nltk

# Download the VADER lexicon once (safe if already downloaded)
nltk.download('vader_lexicon')

analyzer = SentimentIntensityAnalyzer()

# Common misleading phrases that need override
NEGATIVE_TRIGGERS = [
    "didn't help", "not helpful", "not useful", "waste of time",
    "no improvement", "irrelevant", "useless", "bad advice",
    "did not help", "made it worse", "nothing changed"
]

def analyze_sentiment(text):
    if not text.strip():
        return "Neutral"

    lowered = text.lower()

    # Manual override for known bad feedback
    if any(phrase in lowered for phrase in NEGATIVE_TRIGGERS):
        return "Negative"

    scores = analyzer.polarity_scores(text)
    compound = scores["compound"]

    if compound >= 0.05:
        return "Positive"
    elif compound <= -0.05:
        return "Negative"
    else:
        return "Neutral"


