"""Skill Analysis Agent — updates a student's mastery/confidence estimate
for one skill from one piece of real evidence.

IMPORTANT (enforcement is the backend's responsibility, not this module's):
`update_mastery` must NEVER be invoked purely because a lesson was marked
"complete". It exists to fold in real *evidence* of demonstrated skill —
an assessment attempt, a graded exercise, or a project review. Marking a
lesson read/complete is not evidence of mastery and must not call this
agent. The backend is responsible for only invoking this from those real
evidence-producing flows (assessment grading, project review, etc.).

This module is pure deterministic math — no LLM involved, by design: an
LLM shouldn't be inventing a student's skill level from a single number.
"""

from __future__ import annotations

import math

# Source weight: how much a piece of evidence should move mastery. A real
# project is the strongest signal of applied skill; a light exercise is the
# weakest (easy to pass without real mastery).
_SOURCE_WEIGHTS = {
    "project": 1.0,
    "assessment": 0.85,
    "quiz": 0.6,
    "exercise": 0.45,
}
_DEFAULT_SOURCE_WEIGHT = 0.5

# Difficulty multiplier: harder evidence, correctly answered, is stronger
# proof of mastery (and wrong-on-hard is stronger proof of a gap) than easy
# evidence, so it moves the estimate further in either direction.
_DIFFICULTY_WEIGHTS = {
    "easy": 0.7,
    "medium": 1.0,
    "hard": 1.3,
}
_DEFAULT_DIFFICULTY_WEIGHT = 1.0

_BASE_LEARNING_RATE = 0.35
_MIN_LEARNING_RATE = 0.05


def _clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))


def _level_from_mastery(mastery: float) -> str:
    if mastery >= 0.9:
        return "expert"
    if mastery >= 0.7:
        return "advanced"
    if mastery >= 0.4:
        return "intermediate"
    return "beginner"


class SkillAnalysisAgent:
    def update_mastery(self, current: dict, evidence: dict) -> dict:
        """Fold one piece of evidence into a skill's mastery/confidence.

        `current`: {"mastery": float, "confidence": float, "attempts": int}
        (all default to 0 for a skill the student has no prior record for).
        `evidence`: {"score_percent": 0-1, "difficulty": "easy"|"medium"|"hard",
        "source": "assessment"|"quiz"|"exercise"|"project"}.

        Formula (exponential moving average, EMA):
            effective_lr = max(MIN_LR, BASE_LR / sqrt(1 + attempts))
                           * source_weight * difficulty_weight
            new_mastery  = old_mastery + effective_lr * (score_percent - old_mastery)

        The `1/sqrt(1+attempts)` term shrinks the learning rate as more
        attempts accumulate, so mastery becomes a more stable, harder-to-move
        estimate over time (early evidence swings it a lot; the 50th piece
        of evidence barely moves it) — a standard EMA-with-decaying-rate
        approach. `source_weight` and `difficulty_weight` scale how much a
        single piece of evidence counts (a hard project result should move
        the needle more than an easy quiz).

        Confidence rises toward 1.0 with consistent attempts (more evidence
        => more confident estimate) and takes a hit when new evidence
        strongly disagrees with the current mastery estimate (a surprising
        result means we were less sure than we thought).
        """

        current = current or {}
        evidence = evidence or {}

        old_mastery = _clamp(float(current.get("mastery", 0.0)))
        old_confidence = _clamp(float(current.get("confidence", 0.0)))
        attempts = max(0, int(current.get("attempts", 0)))

        score_percent = _clamp(float(evidence.get("score_percent", 0.0)))
        source_weight = _SOURCE_WEIGHTS.get(evidence.get("source"), _DEFAULT_SOURCE_WEIGHT)
        difficulty_weight = _DIFFICULTY_WEIGHTS.get(evidence.get("difficulty"), _DEFAULT_DIFFICULTY_WEIGHT)

        decay = 1.0 / math.sqrt(1 + attempts)
        effective_lr = max(_MIN_LEARNING_RATE, _BASE_LEARNING_RATE * decay) * source_weight * difficulty_weight
        effective_lr = _clamp(effective_lr, 0.0, 1.0)

        new_mastery = _clamp(old_mastery + effective_lr * (score_percent - old_mastery))

        # Confidence: base growth from accumulating attempts (asymptotic to
        # 1.0), reduced when this evidence disagreed sharply with the prior
        # estimate (a surprise means the old estimate was less trustworthy).
        new_attempts = attempts + 1
        confidence_growth = 1.0 - (1.0 / (1.0 + 0.5 * new_attempts))
        surprise = abs(score_percent - old_mastery)
        disagreement_penalty = surprise * 0.5
        new_confidence = _clamp(max(old_confidence, confidence_growth) - disagreement_penalty)
        # Still let confidence trend upward overall with repeated evidence,
        # even after a penalty, via a floor tied to attempt count.
        new_confidence = _clamp(max(new_confidence, confidence_growth * 0.5))

        return {
            "mastery": round(new_mastery, 4),
            "confidence": round(new_confidence, 4),
            "level": _level_from_mastery(new_mastery),
            "attempts": new_attempts,
        }
