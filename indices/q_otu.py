"""Computation of the composite ecological resilience index Q_OTU."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class IndexWeights:
    """Weights used in the linear combination part of the index."""

    k_vi: float = 0.35
    k_si: float = 0.35
    k_bi: float = 0.30

    def normalized(self) -> "IndexWeights":
        total = self.k_vi + self.k_si + self.k_bi
        if total == 0:
            return IndexWeights(1 / 3, 1 / 3, 1 / 3)
        return IndexWeights(self.k_vi / total, self.k_si / total, self.k_bi / total)


def compute_q_otu(
    *,
    q_vi: float,
    q_si: float,
    q_bi: float,
    q_relief: float,
    weights: IndexWeights | None = None,
) -> float:
    """Return the final ecological sustainability score in [0, 1]."""

    params = (weights or IndexWeights()).normalized()
    linear_part = params.k_vi * q_vi + params.k_si * q_si + params.k_bi * q_bi
    result = linear_part * q_relief
    return max(0.0, min(1.0, result))
