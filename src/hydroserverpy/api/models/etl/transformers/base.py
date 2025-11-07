from abc import ABC, abstractmethod
import ast
from functools import lru_cache
import logging
import re
from typing import List, Union
import pandas as pd

from ..timestamp_parser import TimestampParser
from ..etl_configuration import MappingPath, TransformerConfig, SourceTargetMapping

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
        if not df.empty:
            logging.info(f"Read payload into dataframe: {df.iloc[0].to_dict()}")
        else:
            logging.info("Read payload into dataframe: [empty dataframe]")

        # 1) Normalize timestamp column
        df.rename(columns={self.timestamp.key: "timestamp"}, inplace=True)
        if "timestamp" not in df.columns:
            msg = f"Timestamp column '{self.timestamp.key}' not found in data."
            logging.error(msg)
            raise ValueError(msg)
        logging.info(f"Renamed timestamp column to 'timestamp'")

        df["timestamp"] = self.timestamp_parser.parse_series(df["timestamp"])
        df = df.drop_duplicates(subset=["timestamp"], keep="last")

        def _resolve_source_col(s_id: Union[str, int]) -> str:
            if isinstance(s_id, int) and s_id not in df.columns:
                try:
                    return df.columns[s_id]
                except IndexError:
                    raise ValueError(
                        f"Source index {s_id} is out of range for extracted data."
                    )
            if s_id not in df.columns:
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
                        logging.exception(
                            "Data transformation failed for expression=%r",
                            transformation.expression,
                        )
                        raise
                else:
                    msg = f"Unsupported transformation type: {transformation.type}"
                    logging.error(msg)
                    raise ValueError(msg)
            return out

        # source target mappings may be one to many. Therefore, create a new column for each target and apply transformations
        transformed_df = pd.DataFrame(index=df.index)
        for m in mappings:
            src_col = _resolve_source_col(m.source_identifier)
            base = df[src_col]
            for path in m.paths:
                target_col = str(path.target_identifier)
                transformed_df[target_col] = _apply_transformations(base, path)

        # 6) Keep only timestamp + target columns
        df = pd.concat([df[["timestamp"]], pd.DataFrame(transformed_df)], axis=1)

        logging.info(f"standardized dataframe created: {df.shape}")

        return df
