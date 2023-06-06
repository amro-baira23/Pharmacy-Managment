from dataclasses import dataclass
from typing import List, Union

from rest_framework import exceptions

from drf_standardized_errors.formatter import ExceptionFormatter
from drf_standardized_errors.settings import package_settings
from drf_standardized_errors.types import ErrorType, ErrorResponse


@dataclass
class Error:
    detail: str


class MyFormatter(ExceptionFormatter):

    def get_errors(self) -> List[Error]:
        return flatten_errors(self.exc.detail)

    def get_error_response(
        self, error_type: ErrorType, errors: List[Error]
    ) -> ErrorResponse:
        return ErrorResponse(error_type, errors[0].detail)


def flatten_errors(
    detail: Union[list, dict, exceptions.ErrorDetail], attr=None, index=None
) -> List[Error]:

    if not detail:
        return []
    elif isinstance(detail, list):
        first_item, *rest = detail
        if not isinstance(first_item, exceptions.ErrorDetail):
            index = 0 if index is None else index + 1
            if attr:
                new_attr = f"{attr}{package_settings.NESTED_FIELD_SEPARATOR}{index}"
            else:
                new_attr = str(index)
            return flatten_errors(first_item, new_attr, index) + flatten_errors(
                rest, attr, index
            )
        else:
            return flatten_errors(first_item, attr, index) + flatten_errors(
                rest, attr, index
            )
    elif isinstance(detail, dict):
        (key, value), *rest = list(detail.items())
        if attr:
            key = f"{attr}{package_settings.NESTED_FIELD_SEPARATOR}{key}"
        return flatten_errors(value, key) + flatten_errors(dict(rest), attr)
    else:
        if attr:
            return [Error(str(attr) + ": " + str(detail))]
        return [Error(str(detail))]