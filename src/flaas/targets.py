from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class Targets:
    master_lufs: float = -10.5
    true_peak_ceiling_dbfs: float = -1.0  # placeholder until TP estimator exists
    stem_peak_ceiling_dbfs: float = -6.0

DEFAULT_TARGETS = Targets()
