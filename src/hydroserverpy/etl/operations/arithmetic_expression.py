import re
import ast
import logging
import pandas as pd
from pydantic import BaseModel, model_validator
from typing import Any, Literal
from ..exceptions import ETLError


logger = logging.getLogger(__name__)


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


class ArithmeticExpressionOperation(BaseModel):
    type: Literal["arithmetic_expression"] = "arithmetic_expression"
    expression: str
    target_identifier: str
    _compiled: Any = None

    @model_validator(mode="after")
    def compile_expression(self) -> "ArithmeticExpressionOperation":
        """
        Validate and compile the expression on initialization.
        Whitespace is canonicalized before compilation.
        """

        canonical = re.sub(r"\s+", "", self.expression)

        try:
            tree = ast.parse(canonical, mode="eval")
        except (ValueError, AssertionError) as e:
            raise ValueError(
                f"Failed to compile arithmetic expression for data target: {self.target_identifier}. "
                f"Failing expression: {self.expression}. "
                f"{str(e)}"
            )
        except Exception:
            raise ValueError(
                f"Failed to compile arithmetic expression for data target: {self.target_identifier}. "
                f"Failing expression: {self.expression}. "
                f"Encountered an unexpected error."
            )

        for node in ast.walk(tree):
            if not isinstance(node, ALLOWED_AST):
                raise ValueError(
                    f"Failed to compile arithmetic expression for data target: {self.target_identifier}. "
                    f"Failing expression: {self.expression}. "
                    "Only +, -, *, / with 'x' and numeric literals are allowed in arithmetic expressions."
                )
            if isinstance(node, ast.Name) and node.id != "x":
                raise ValueError(
                    f"Failed to compile arithmetic expression for data target: {self.target_identifier}. "
                    f"Failing expression: {self.expression}. "
                    "Only the variable 'x' is allowed in arithmetic expressions. "
                    f"Provided variable: {node.id}"
                )
            if isinstance(node, ast.Constant):
                val = node.value
                if isinstance(val, bool) or not isinstance(val, (int, float)):
                    raise ValueError(
                        f"Failed to compile arithmetic expression for data target: {self.target_identifier}. "
                        f"Failing expression: {self.expression}. "
                        "Only numeric literals are allowed in arithmetic expressions. "
                        f"Provided value: {val}"
                    )

        self._compiled = compile(tree, "<expr>", "eval")
        return self

    def apply(self, series: pd.Series) -> pd.Series:
        """
        Apply the compiled arithmetic expression to a Pandas Series.

        The variable 'x' in the expression represents the input series.
        """

        try:
            return eval(self._compiled, {"__builtins__": {}}, {"x": series})
        except Exception as e:
            raise ETLError(
                f"Failed to evaluate arithmetic expression for data target: {self.target_identifier}. "
                f"Failing expression: {self.expression}"
            ) from e
