from typing import Union
from .rating_curve import RatingCurveDataOperation
from .arithmetic_expression import ArithmeticExpressionOperation


DataOperation = Union[ArithmeticExpressionOperation, RatingCurveDataOperation]
