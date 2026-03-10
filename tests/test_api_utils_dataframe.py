import pandas as pd

from hydroserverpy.api.utils import hydro_list_to_flat_df


class MockItem:
    def __init__(self, uid, name, tags=None, value=None):
        self.uid = uid
        self.name = name
        self.tags = tags
        self.value = value


class MockCollection:
    def __init__(self, items, total_pages=None, page_size=None):
        self.items = items
        self.total_pages = total_pages
        self.page_size = page_size


def mock_list_fetch_all(fetch_all=True, **kwargs):
    items = [
        MockItem("1", "Station A", {"Divert ID": 123}, "10"),
        MockItem("2", "Station B", {"Divert ID": 456}, "20"),
    ]
    return MockCollection(items)


def test_hydro_list_to_flat_df_basic():

    df = hydro_list_to_flat_df(mock_list_fetch_all)

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2

    assert "uid" in df.columns
    assert "name" in df.columns
    assert "Divert ID" in df.columns
    assert "value" in df.columns


def test_hydro_list_to_flat_df_numeric_cast():

    df = hydro_list_to_flat_df(
        mock_list_fetch_all,
        auto_cast_numeric=True
    )

    assert pd.api.types.is_numeric_dtype(df["value"])


def test_hydro_list_to_flat_df_no_flatten():

    df = hydro_list_to_flat_df(
        mock_list_fetch_all,
        flatten_dicts=False
    )

    assert "tags" in df.columns
    assert "Divert ID" not in df.columns


def test_flattened_values_correct():

    df = hydro_list_to_flat_df(mock_list_fetch_all)

    assert df.loc[0, "Divert ID"] == 123
    assert df.loc[1, "Divert ID"] == 456


def mock_list_paginated(page=1, **kwargs):

    if page == 1:
        return MockCollection(
            [MockItem("1", "Station A"), MockItem("2", "Station B")],
            total_pages=2,
            page_size=2
        )

    return MockCollection(
        [MockItem("3", "Station C")],
        total_pages=2,
        page_size=2
    )


def test_hydro_list_to_flat_df_manual_pagination():

    df = hydro_list_to_flat_df(
        mock_list_paginated,
        fetch_all=True
    )

    assert len(df) == 3
    assert list(df["name"]) == [
        "Station A",
        "Station B",
        "Station C"
    ]
