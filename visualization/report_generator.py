"""Simple textual report builder for simulation batches."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ReportEntry:
    """Single bullet item describing a key outcome."""

    label: str
    value: str


def build_report(entries: list[ReportEntry]) -> str:
    """Serialize report entries into a markdown-ish string."""

    lines = ["# Monte Carlo Summary"]
    for entry in entries:
        lines.append(f"- {entry.label}: {entry.value}")
    return "\n".join(lines)
