from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Protocol

from .platforms import Target


@dataclass
class AlternativeCandidate:
    name: str
    homepage: str | None = None


class AlternativeStrategy(Protocol):
    """
    Strategy interface: given a software name and a target platform,
    return up to N alternative tools for that platform.
    """

    def find_alternatives(
        self, name: str, target: Target, limit: int = 2
    ) -> list[AlternativeCandidate]:
        ...


class NoopAlternativeStrategy:
    """
    Default stub: does not attempt to find alternatives, just returns empty.

    This keeps the code path explicit while we design a concrete strategy
    (e.g. using a search engine API or a curated mapping).
    """

    def find_alternatives(
        self, name: str, target: Target, limit: int = 2
    ) -> list[AlternativeCandidate]:
        return []


def ensure_limit(items: Iterable[AlternativeCandidate], limit: int = 2) -> list[AlternativeCandidate]:
    result: list[AlternativeCandidate] = []
    for item in items:
        result.append(item)
        if len(result) >= limit:
            break
    return result

