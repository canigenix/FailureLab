from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path

from failurelab.suite_runner import SuiteResult


@dataclass(frozen=True)
class HistoryEntry:
    suite_name: str
    timestamp: str
    status: str
    worst_stress: str
    worst_drop: float
    maximum_drop: float | None


class SuiteHistory:
    def __init__(self, entries: list[HistoryEntry] | None = None):
        self.entries = entries or []

    def add_result(
        self,
        result: SuiteResult,
    ) -> HistoryEntry:
        entry = HistoryEntry(
            suite_name=result.name,
            timestamp=datetime.now(
                timezone.utc
            ).isoformat(),
            status=result.status,
            worst_stress=result.worst_result.name,
            worst_drop=result.worst_drop,
            maximum_drop=result.maximum_drop,
        )

        self.entries.append(entry)

        return entry

    def latest_for_suite(
        self,
        suite_name: str,
    ) -> HistoryEntry | None:
        matching = [
            entry
            for entry in self.entries
            if entry.suite_name == suite_name
        ]

        if not matching:
            return None

        return matching[-1]

    def trend(
        self,
        suite_name: str,
        tolerance: float = 0.01,
    ) -> str:
        if tolerance < 0:
            raise ValueError(
                "tolerance cannot be negative."
            )

        matching = [
            entry
            for entry in self.entries
            if entry.suite_name == suite_name
        ]

        if len(matching) < 2:
            return "insufficient_history"

        previous = matching[-2]
        latest = matching[-1]

        delta = (
            latest.worst_drop
            - previous.worst_drop
        )

        if delta > tolerance:
            return "regressed"

        if delta < -tolerance:
            return "improved"

        return "stable"

    def to_dict(self) -> dict:
        return {
            "entries": [
                {
                    "suite_name": entry.suite_name,
                    "timestamp": entry.timestamp,
                    "status": entry.status,
                    "worst_stress": entry.worst_stress,
                    "worst_drop": entry.worst_drop,
                    "maximum_drop": entry.maximum_drop,
                }
                for entry in self.entries
            ]
        }

    def save_json(
        self,
        path: str | Path,
    ) -> None:
        path = Path(path)

        path.write_text(
            json.dumps(
                self.to_dict(),
                indent=2,
            ),
            encoding="utf-8",
        )

    @classmethod
    def load_json(
        cls,
        path: str | Path,
    ) -> "SuiteHistory":
        path = Path(path)

        if not path.exists():
            return cls()

        data = json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )

        raw_entries = data.get(
            "entries",
            [],
        )

        entries = [
            HistoryEntry(
                suite_name=row["suite_name"],
                timestamp=row["timestamp"],
                status=row["status"],
                worst_stress=row["worst_stress"],
                worst_drop=float(
                    row["worst_drop"]
                ),
                maximum_drop=(
                    None
                    if row.get("maximum_drop") is None
                    else float(
                        row["maximum_drop"]
                    )
                ),
            )
            for row in raw_entries
        ]

        return cls(entries=entries)