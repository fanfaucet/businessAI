"""Weighted DistilBERT/TextBlob sentiment fusion with safe fallbacks."""

from __future__ import annotations

import importlib
from collections import deque
from statistics import mean, pstdev

from annabanai.models.runtime import SentimentResult


class SentimentEngine:
    """Analyze text with optional contextual and lexical sentiment models."""

    def __init__(self, window_size: int = 25, distilbert_weight: float = 0.7, textblob_weight: float = 0.3) -> None:
        self.window_size = window_size
        self.distilbert_weight = distilbert_weight
        self.textblob_weight = textblob_weight
        self._scores: deque[float] = deque(maxlen=window_size)
        self._pipeline = None

    def _distilbert_score(self, text: str) -> tuple[float | None, float]:
        if self._pipeline is None:
            transformers = importlib.import_module("transformers")
            self._pipeline = transformers.pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english",
            )
        result = self._pipeline(text[:512])[0]
        signed = float(result["score"]) if result["label"] == "POSITIVE" else -float(result["score"])
        return signed, float(result["score"])

    def _textblob_score(self, text: str) -> float | None:
        textblob = importlib.import_module("textblob")
        return float(textblob.TextBlob(text).sentiment.polarity)

    def analyze(self, text: str) -> SentimentResult:
        distilbert_score = None
        distilbert_confidence = 0.0
        textblob_score = None
        errors = []

        try:
            distilbert_score, distilbert_confidence = self._distilbert_score(text)
        except Exception as exc:  # Optional model boundary.
            errors.append(f"distilbert unavailable: {exc}")

        try:
            textblob_score = self._textblob_score(text)
        except Exception as exc:  # Optional lexical boundary.
            errors.append(f"textblob unavailable: {exc}")

        weighted_scores = []
        if distilbert_score is not None:
            weighted_scores.append((distilbert_score, self.distilbert_weight * max(distilbert_confidence, 0.1)))
        if textblob_score is not None:
            weighted_scores.append((textblob_score, self.textblob_weight))

        if weighted_scores:
            total_weight = sum(weight for _, weight in weighted_scores)
            fused_score = sum(score * weight for score, weight in weighted_scores) / total_weight
            confidence = min(1.0, total_weight)
        else:
            fused_score = 0.0
            confidence = 0.0

        self._scores.append(fused_score)
        rolling_average = mean(self._scores) if self._scores else 0.0
        volatility = pstdev(self._scores) if len(self._scores) > 1 else 0.0
        label = "positive" if fused_score > 0.1 else "negative" if fused_score < -0.1 else "neutral"
        return SentimentResult(
            label=label,
            score=round(fused_score, 4),
            confidence=round(confidence, 4),
            distilbert_score=distilbert_score,
            textblob_score=textblob_score,
            rolling_average=round(rolling_average, 4),
            volatility=round(volatility, 4),
            metadata={"errors": errors},
        )
