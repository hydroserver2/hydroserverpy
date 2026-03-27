from uuid import UUID
from typing import Union, Optional, Any
from pydantic.alias_generators import to_camel

import inspect
import requests


def normalize_uuid(
    obj: Optional[Union[str, UUID, Any]],
    attr: str = "uid"
):
    if obj is ...:
        return ...
    if obj is None:
        return None
    if obj and hasattr(obj, attr):
        return str(getattr(obj, attr))
    return str(obj)


def order_by_to_camel(s: str) -> str:
    if s.startswith('-'):
        return '-' + to_camel(s[1:])
    return to_camel(s)


def _to_serializable(value):
    """Convert values like UUIDs into DataFrame-friendly objects."""
    if isinstance(value, UUID):
        return str(value)
    return value


def _flatten_all_dict_columns(df):
    """Flatten one level of dict-valued columns."""
    import pandas as pd

    df_out = df.copy()

    for col in list(df_out.columns):
        if df_out[col].apply(lambda x: isinstance(x, dict)).any():
            mask = df_out[col].apply(lambda x: isinstance(x, dict))
            expanded = pd.json_normalize(df_out.loc[mask, col])
            expanded.index = df_out.loc[mask].index
            df_out = df_out.drop(columns=[col]).join(expanded, how="left")

    return df_out


def _auto_cast_numeric_columns(df):
    """Convert mostly-numeric object columns to numeric dtype."""
    import pandas as pd

    for col in df.columns:
        if df[col].dtype == "object":
            converted = pd.to_numeric(df[col], errors="coerce")
            non_null = df[col].notna().sum()
            numeric_success = converted.notna().sum()

            if non_null > 0 and numeric_success / non_null > 0.9:
                df[col] = converted

    return df


def hydro_list_to_flat_df(
    list_fn,
    fetch_all=True,
    flatten_dicts=True,
    order_by=None,
    auto_cast_numeric=True,
    default_sort_endpoints=("things", "datastreams"),
    default_order_by_for_sorted_endpoints=("name",),
    **list_kwargs
):
    """
    Convert a HydroServer `.list()` response into a pandas DataFrame.

    Parameters
    ----------
    list_fn : callable
        A HydroServer endpoint `.list()` method (e.g. hs_api.things.list).
    fetch_all : bool
        Retrieve all pages when supported.
    flatten_dicts : bool
        Expand dictionary fields (e.g. tags) into columns.
    order_by : list[str] | None
        Optional sort fields.
    auto_cast_numeric : bool
        Convert numeric-like columns to numeric dtype.

    Returns
    -------
    pandas.DataFrame
        Clean tabular representation of the API objects.
    """

    try:
        import pandas as pd
    except ImportError as exc:
        raise ImportError(
            "hydro_list_to_flat_df requires pandas. "
            "Install it with: pip install pandas"
        ) from exc

    if order_by is None:
        fn_id = (
            getattr(list_fn, "__qualname__", "") + " " +
            getattr(list_fn, "__name__", "") + " " +
            repr(list_fn)
        ).lower()

        should_default_sort = any(
            ep in fn_id for ep in default_sort_endpoints
        )

        if should_default_sort:
            order_by = [default_order_by_for_sorted_endpoints[0]]
        else:
            order_by = None

    candidates = [order_by, None] if order_by is not None else [None]

    items = []
    collection = None
    last_err = None

    def _call_list(*, ob, **kwargs):
        call_kwargs = dict(kwargs)
        if ob is not None:
            call_kwargs["order_by"] = ob
        return list_fn(**call_kwargs)

    if fetch_all:
        sig = inspect.signature(list_fn)
        supports_fetch_all = "fetch_all" in sig.parameters

        if supports_fetch_all:
            for ob in candidates:
                try:
                    collection = _call_list(
                        ob=ob,
                        fetch_all=True,
                        **list_kwargs
                    )
                    items = collection.items
                    break
                except requests.HTTPError as exc:
                    last_err = exc
                    resp = getattr(exc, "response", None)
                    if resp is None or resp.status_code != 422:
                        raise

            if collection is None:
                raise last_err

        else:
            for ob in candidates:
                try:
                    page = 1
                    items = []

                    while True:
                        collection = _call_list(
                            ob=ob,
                            page=page,
                            **list_kwargs
                        )

                        page_items = getattr(collection, "items", [])
                        items.extend(page_items)

                        total_pages = getattr(collection, "total_pages", None)
                        if total_pages and page >= total_pages:
                            break

                        page_size = getattr(collection, "page_size", None)
                        if total_pages is None and page_size and len(page_items) < page_size:
                            break

                        if not page_items:
                            break

                        page += 1

                    break

                except requests.HTTPError as exc:
                    last_err = exc
                    resp = getattr(exc, "response", None)
                    if resp is None or resp.status_code != 422:
                        raise

            if collection is None and last_err is not None:
                raise last_err

    else:
        for ob in candidates:
            try:
                collection = _call_list(ob=ob, **list_kwargs)
                items = collection.items
                break
            except requests.HTTPError as exc:
                last_err = exc
                resp = getattr(exc, "response", None)
                if resp is None or resp.status_code != 422:
                    raise

        if collection is None:
            raise last_err

    if not items:
        return pd.DataFrame()

    rows = [
        {
            k: _to_serializable(v)
            for k, v in vars(item).items()
            if not k.startswith("_")
        }
        for item in items
    ]

    df = pd.DataFrame(rows)

    if flatten_dicts and not df.empty:
        df = _flatten_all_dict_columns(df)

    if auto_cast_numeric and not df.empty:
        df = _auto_cast_numeric_columns(df)

    return df
