from abc import ABC, abstractmethod
import ast
from functools import lru_cache
import logging
import re
from typing import List, Union
import pandas as pd

from ..timestamp_parser import TimestampParser
from ..etl_configuration import MappingPath, TransformerConfig, SourceTargetMapping
from ..logging_utils import summarize_list

ALLOWED_AST = (
    ast.Expression,
    ast.BinOp,
    ast.UnaryOp,
    ast.Add,
    ast.Sub,
    ast.Mult,
    ast.Div,
    ast.UAdd,
    ast.USub,
    ast.Name,
    ast.Load,
    ast.Constant,
)


def _canonicalize_expr(expr: str) -> str:
    # normalize whitespace for cache hits; parentheses remain intact
    return re.sub(r"\s+", "", expr)


@lru_cache(maxsize=256)
def _compile_arithmetic_expr_canon(expr_no_ws: str):
    tree = ast.parse(expr_no_ws, mode="eval")
    for node in ast.walk(tree):
        if not isinstance(node, ALLOWED_AST):
            raise ValueError(
                "Only +, -, *, / with 'x' and numeric literals are allowed."
            )
        if isinstance(node, ast.Name) and node.id != "x":
            raise ValueError("Only the variable 'x' is allowed.")
        if isinstance(node, ast.Constant):
            val = node.value
            if isinstance(val, bool) or not isinstance(val, (int, float)):
                raise ValueError("Only numeric literals are allowed.")
    return compile(tree, "<expr>", "eval")


def _compile_arithmetic_expr(expr: str):
    return _compile_arithmetic_expr_canon(_canonicalize_expr(expr))


logger = logging.getLogger(__name__)


class Transformer(ABC):
    def __init__(self, transformer_config: TransformerConfig):
        self.cfg = transformer_config
        self.timestamp = transformer_config.timestamp
        self.timestamp_parser = TimestampParser(self.timestamp)

    @abstractmethod
    def transform(self, *args, **kwargs) -> None:
        pass

    @property
    def needs_datastreams(self) -> bool:
        return False

    def standardize_dataframe(
        self, df: pd.DataFrame, mappings: List[SourceTargetMapping]
    ):
        logger.debug(
            "Standardizing extracted dataframe (rows=%s, columns=%s).",
            len(df),
            len(df.columns),
        )
        logger.debug(
            "Extracted dataframe columns (sample): %s",
            summarize_list(list(df.columns), max_items=30),
        )
        if not df.empty:
            # Avoid dumping full rows; just log a compact preview.
            preview = df.iloc[0].to_dict()
            for k, v in list(preview.items()):
                if isinstance(v, str) and len(v) > 128:
                    preview[k] = v[:128] + "...(truncated)"
            logger.debug("Extracted dataframe first-row preview: %s", preview)

        # 1) Normalize timestamp column
        df.rename(columns={self.timestamp.key: "timestamp"}, inplace=True)
        if "timestamp" not in df.columns:
            msg = f"Timestamp column '{self.timestamp.key}' not found in data."
            logger.error(
                "%s Available columns=%s",
                msg,
                summarize_list(list(df.columns), max_items=30),
            )
            raise ValueError(msg)
        logger.debug(
            "Normalized timestamp column '%s' -> 'timestamp' (timezoneMode=%r, format=%r).",
            self.timestamp.key,
            getattr(self.timestamp, "timezone_mode", None),
            getattr(self.timestamp, "format", None),
        )

        df["timestamp"] = self.timestamp_parser.parse_series(df["timestamp"])
        df = df.drop_duplicates(subset=["timestamp"], keep="last")

        def _resolve_source_col(s_id: Union[str, int]) -> str:
            if isinstance(s_id, int) and s_id not in df.columns:
                try:
                    return df.columns[s_id]
                except IndexError:
                    logger.error(
                        "Source index %s is out of range. Extracted columns count=%s, columns(sample)=%s",
                        s_id,
                        len(df.columns),
                        summarize_list(list(df.columns), max_items=30),
                    )
                    raise ValueError(
                        f"Source index {s_id} is out of range for extracted data."
                    )
            if s_id not in df.columns:
                logger.error(
                    "Source column %r not found. Available columns=%s",
                    s_id,
                    summarize_list(list(df.columns), max_items=30),
                )
                raise ValueError(f"Source column '{s_id}' not found in extracted data.")
            return s_id

        def _apply_transformations(series: pd.Series, path: MappingPath) -> pd.Series:
            out = series  # accumulator for sequential transforms
            if out.dtype == "object":
                out = pd.to_numeric(out, errors="coerce")

            for transformation in path.data_transformations:
                if transformation.type == "expression":
                    code = _compile_arithmetic_expr(transformation.expression)
                    try:
                        out = eval(code, {"__builtins__": {}}, {"x": out})
                    except Exception as ee:
                        logger.exception(
                            "Data transformation failed for target=%r expression=%r",
                            path.target_identifier,
                            transformation.expression,
                        )
                        raise
                else:
                    msg = f"Unsupported transformation type: {transformation.type}"
                    logger.error(msg)
                    raise ValueError(msg)
            return out

        # source target mappings may be one to many. Therefore, create a new column for each target and apply transformations
        transformed_df = pd.DataFrame(index=df.index)
        logger.debug(
            "Applying %s source mapping(s): %s",
            len(mappings),
            summarize_list([m.source_identifier for m in mappings], max_items=30),
        )
        for m in mappings:
            src_col = _resolve_source_col(m.source_identifier)
            base = df[src_col]
            for path in m.paths:
                target_col = str(path.target_identifier)
                transformed_df[target_col] = _apply_transformations(base, path)

        # 6) Keep only timestamp + target columns
        df = pd.concat([df[["timestamp"]], pd.DataFrame(transformed_df)], axis=1)

        logger.debug("Standardized dataframe created: %s", df.shape)

        return df
