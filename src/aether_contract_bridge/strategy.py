"""Frozen, task-family strategy codebook for generated programs.

The classifier reports observable implementation structure. Operational
suitability remains execution-derived; the static label is not used to override
correctness, cgroup, or timing outcomes.
"""

from __future__ import annotations

import ast
from dataclasses import asdict, dataclass
import re


@dataclass(frozen=True)
class StrategyRecord:
    schema_version: str
    family: str
    primary_strategy: str
    features: tuple[str, ...]
    requires_adjudication: bool
    rationale: tuple[str, ...]

    def to_dict(self) -> dict:
        return asdict(self)


def classify_strategy(family: str, source: str) -> StrategyRecord:
    if family not in {"numerical", "etl"}:
        raise ValueError(f"unsupported task family: {family}")
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        return StrategyRecord(
            "strategy-codebook/v0.1", family, "unparseable", (), True,
            (f"Python AST parse failed at line {exc.lineno}",),
        )
    return _classify_etl(tree, source) if family == "etl" else _classify_numerical(tree, source)


def _calls(tree: ast.AST) -> list[str]:
    names = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        target = node.func
        parts = []
        while isinstance(target, ast.Attribute):
            parts.append(target.attr)
            target = target.value
        if isinstance(target, ast.Name):
            parts.append(target.id)
        names.append(".".join(reversed(parts)))
    return names


def _classify_etl(tree: ast.AST, source: str) -> StrategyRecord:
    calls = _calls(tree)
    lowered = source.lower()
    features = []
    rationale = []
    uses_pandas = any(name.startswith("pandas") or name.startswith("pd.") for name in calls) or "import pandas" in lowered
    read_csv_calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call) and
                      isinstance(node.func, ast.Attribute) and node.func.attr == "read_csv"]
    chunked = any(any(keyword.arg == "chunksize" for keyword in call.keywords) for call in read_csv_calls)
    materializes = "readlines(" in lowered or bool(re.search(r"\blist\s*\(\s*(?:reader|csv)", lowered))
    loops = any(isinstance(node, (ast.For, ast.AsyncFor)) for node in ast.walk(tree))
    csv_reader = any(name.endswith("csv.reader") or name.endswith("csv.DictReader") for name in calls)
    if uses_pandas:
        features.append("pandas")
    if chunked:
        features.append("explicit_chunksize")
    if csv_reader:
        features.append("csv_iterator")
    if materializes:
        features.append("explicit_materialization")
    if chunked:
        primary = "dataframe_chunked"
        rationale.append("read_csv supplies an explicit chunksize")
    elif read_csv_calls:
        primary = "dataframe_eager"
        rationale.append("read_csv has no explicit chunksize")
    elif materializes:
        primary = "stdlib_materialized"
        rationale.append("the source explicitly materializes input rows")
    elif csv_reader and loops:
        primary = "stdlib_streaming"
        rationale.append("a CSV iterator is consumed by a loop without explicit materialization")
    else:
        primary = "other"
        rationale.append("no frozen ETL strategy signature matched")
    return StrategyRecord("strategy-codebook/v0.1", "etl", primary, tuple(sorted(features)),
                          primary == "other", tuple(rationale))


def _classify_numerical(tree: ast.AST, source: str) -> StrategyRecord:
    calls = _calls(tree)
    lowered = source.lower()
    features = []
    rationale = []
    loops = any(isinstance(node, (ast.For, ast.While)) for node in ast.walk(tree))
    matrix_product = any(isinstance(node, ast.BinOp) and isinstance(node.op, ast.MatMult) for node in ast.walk(tree)) or any(
        name.endswith("matmul") or name.endswith("dot") for name in calls
    )
    full_broadcast = bool(re.search(r"\[\s*:\s*,\s*none\s*\]", lowered)) and bool(
        re.search(r"\[\s*none\s*,\s*:\s*\]", lowered)
    )
    mmap = "mmap_mode" in lowered
    triangular = "triu" in lowered or bool(re.search(r"\b(?:j|col|start_j)\w*\s*=\s*(?:i|row|start_i)", lowered))
    in_place = "out=" in lowered or any(isinstance(node, ast.AugAssign) for node in ast.walk(tree))
    float32 = "float32" in lowered
    for enabled, name in ((mmap, "memory_map"), (triangular, "triangular_symmetry"),
                          (in_place, "in_place_update"), (float32, "float32_explicit")):
        if enabled:
            features.append(name)
    if loops and matrix_product:
        primary = "blocked_matrix_product"
        rationale.append("matrix products occur in an explicit iteration structure")
    elif matrix_product or full_broadcast:
        primary = "eager_global_matrix"
        rationale.append("global matrix/broadcast distance construction has no explicit outer blocking loop")
    elif loops:
        primary = "rowwise_or_scalar_streaming"
        rationale.append("distance work is expressed through loops without a matrix-product signature")
    else:
        primary = "other"
        rationale.append("no frozen numerical strategy signature matched")
    return StrategyRecord("strategy-codebook/v0.1", "numerical", primary, tuple(sorted(features)),
                          primary == "other", tuple(rationale))
