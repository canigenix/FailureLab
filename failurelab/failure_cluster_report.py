from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

from failurelab.failure_clusters import (
    FailureCluster,
    build_report_clusters,
)
from failurelab.failure_correlation_report import (
    FailureCorrelationReport,
)


@dataclass(frozen=True)
class FailureClusterReport:
    suite_name: str
    minimum_correlation: float
    clusters: list[FailureCluster]

    @property
    def cluster_count(self) -> int:
        return len(self.clusters)

    @property
    def largest_cluster(
        self,
    ) -> FailureCluster | None:
        if not self.clusters:
            return None

        return max(
            self.clusters,
            key=lambda cluster: len(
                cluster.stresses
            ),
        )

    def to_dict(self) -> dict:
        largest = self.largest_cluster

        return {
            "suite_name": self.suite_name,
            "minimum_correlation": (
                self.minimum_correlation
            ),
            "cluster_count": self.cluster_count,
            "largest_cluster_size": (
                0
                if largest is None
                else len(largest.stresses)
            ),
            "clusters": [
                {
                    "stresses": cluster.stresses,
                    "stress_count": len(
                        cluster.stresses
                    ),
                    "pair_count": cluster.pair_count,
                    "mean_correlation": (
                        cluster.mean_correlation
                    ),
                }
                for cluster in self.clusters
            ],
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


def build_failure_cluster_report(
    report: FailureCorrelationReport,
    minimum_correlation: float = 0.75,
) -> FailureClusterReport:
    return FailureClusterReport(
        suite_name=report.suite_name,
        minimum_correlation=minimum_correlation,
        clusters=build_report_clusters(
            report,
            minimum_correlation=minimum_correlation,
        ),
    )