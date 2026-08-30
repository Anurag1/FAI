"""FAI: compact reasoning engine assembled from Anurag1's research themes.

Design goal: improve capability by composing small deterministic operators around
an external language model, rather than building a new heavyweight model.

Pipeline: observe -> retrieve -> hypothesize -> challenge -> synthesize -> score.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Iterable, Sequence
import re


@dataclass
class Memory:
    facts: list[str] = field(default_factory=list)

    def add(self, *items: str) -> None:
        for item in items:
            item = item.strip()
            if item and item not in self.facts:
                self.facts.append(item)

    def retrieve(self, query: str, k: int = 5) -> list[str]:
        terms = set(re.findall(r"[a-z0-9]+", query.lower()))
        ranked = []
        for fact in self.facts:
            score = len(terms & set(re.findall(r"[a-z0-9]+", fact.lower())))
            if score:
                ranked.append((score, fact))
        return [fact for score, fact in sorted(ranked, reverse=True)[:k]]


@dataclass(frozen=True)
class Hypothesis:
    claim: str
    evidence: tuple[str, ...]
    counterquestions: tuple[str, ...]


class FAI:
    """Small orchestration layer for reasoning-first AI applications."""

    def __init__(self, model: Callable[[str], str] | None = None):
        self.model = model or (lambda prompt: prompt)
        self.memory = Memory()

    def observe(self, text: str) -> dict:
        text = text.strip()
        return {
            "text": text,
            "terms": re.findall(r"[a-zA-Z0-9_]+", text),
            "questions": [f"What assumption could make this false?"],
        }

    def hypothesize(self, observation: dict) -> Hypothesis:
        evidence = tuple(self.memory.retrieve(observation["text"]))
        claim = observation["text"]
        counterquestions = (
            "What evidence contradicts this?",
            "What would falsify this claim?",
            "What important variable is missing?",
        )
        return Hypothesis(claim, evidence, counterquestions)

    def reason(self, text: str) -> dict:
        observation = self.observe(text)
        hypothesis = self.hypothesize(observation)
        context = "\n".join(f"- {x}" for x in hypothesis.evidence) or "- none"
        challenge = "\n".join(f"- {x}" for x in hypothesis.counterquestions)
        prompt = (
            "You are a verification-oriented reasoning engine.\n"
            f"Claim/input: {hypothesis.claim}\n"
            f"Relevant memory:\n{context}\n"
            f"Challenges:\n{challenge}\n"
            "Return: answer, assumptions, uncertainty, and one testable next step."
        )
        answer = self.model(prompt)
        result = {
            "observation": observation,
            "hypothesis": hypothesis,
            "answer": answer,
            "confidence": self._confidence(hypothesis, answer),
        }
        self.memory.add(text, answer)
        return result

    @staticmethod
    def _confidence(h: Hypothesis, answer: str) -> float:
        """Heuristic epistemic score; not a calibrated probability."""
        score = 0.25
        if h.evidence:
            score += 0.25
        if answer.strip():
            score += 0.20
        lowered = answer.lower()
        if "uncertain" in lowered or "cannot verify" in lowered:
            score -= 0.10
        if "assumption" in lowered and "test" in lowered:
            score += 0.15
        return max(0.0, min(1.0, round(score, 2)))


def demo() -> dict:
    engine = FAI(model=lambda prompt: "Answer: reasoned response; assumptions: explicit; uncertainty: low; test: run a falsification check.")
    engine.memory.add("Graphs expose relationships between entities.", "Contradictions can generate useful questions.")
    return engine.reason("How can graph structure improve AI discovery?")


if __name__ == "__main__":
    import json
    print(json.dumps(demo(), default=lambda x: x.__dict__, indent=2))
