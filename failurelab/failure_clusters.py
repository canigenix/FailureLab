from __future__ import annotations

from dataclasses import dataclass

from failurelab.failure_correlation import (
    StressCorrelationResult,
)


@dataclass(frozen=True)
class FailureCluster:
    stresses: list[str]
    pair_count: int
    mean_correlation: float


def build_failure_clusters(
    correlations: list[StressCorrelationResult],
    minimum_correlation: float = 0.75,
) -> list[FailureCluster]:
    if not 0.0 <= minimum_correlation <= 1.0:
        raise ValueError(
            "minimum_correlation must be between 0.0 and 1.0."
        )

    adjacency: dict[str, set[str]] = {}
    pair_values: dict[
        tuple[str, str],
        float,
    ] = {}

    for row in correlations:
        if row.correlation < minimum_correlation:
            continue

        adjacency.setdefault(
            row.stress_a,
            set(),
        ).add(
            row.stress_b
        )

        adjacency.setdefault(
            row.stress_b,
            set(),
        ).add(
            row.stress_a
        )

        key = tuple(
            sorted(
                (
                    row.stress_a,
                    row.stress_b,
                )
            )
        )

        pair_values[key] = row.correlation

    visited = set()
    clusters = []

    for stress in adjacency:
        if stress in visited:
            continue

        stack = [
            stress
        ]

        component = set()

        while stack:
            current = stack.pop()

            if current in visited:
                continue

            visited.add(
                current
            )

            component.add(
                current
            )

            stack.extend(
                adjacency.get(
                    current,
                    set(),
                )
            )

        stresses = sorted(
            component
        )

        correlations_in_cluster = []

        for index, stress_a in enumerate(
            stresses
        ):
            for stress_b in stresses[
                index + 1:
            ]:
                key = tuple(
                    sorted(
                        (
                            stress_a,
                            stress_b,
                        )
                    )
                )

                if key in pair_values:
                    correlations_in_cluster.append(
                        pair_values[key]
                    )

        if correlations_in_cluster:
            clusters.append(
                FailureCluster(
                    stresses=stresses,
                    pair_count=len(
                        correlations_in_cluster
                    ),
                    mean_correlation=(
                        sum(
                            correlations_in_cluster
                        )
                        / len(
                            correlations_in_cluster
                        )
                    ),
                )
            )

    return sorted(
        clusters,
        key=lambda cluster: (
            len(
                cluster.stresses
            ),
            cluster.mean_correlation,
        ),
        reverse=True,
    )

def build_report_clusters(
    report,
    minimum_correlation: float = 0.75,
) -> list[FailureCluster]:
    return build_failure_clusters(
        report.correlations,
        minimum_correlation=minimum_correlation,
    )