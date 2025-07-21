import pandas as pd
from typing import Optional, Any, List, TYPE_CHECKING
from dataclasses import dataclass
from requests import Response
from pydantic.alias_generators import to_snake

if TYPE_CHECKING:
    from hydroserverpy.api.models import Datastream


@dataclass
class ObservationCollection:
    dataframe: pd.DataFrame
    filters: Optional[dict[str, Any]] = None
    order_by: Optional[List[str]] = None
    page: Optional[int] = None
    page_size: Optional[int] = None
    total_pages: Optional[int] = None
    total_count: Optional[int] = None

    def __init__(
        self,
        datastream: "Datastream",
        response: Optional[Response] = None,
        **data
    ):
        self.filters = data.get("filters")
        self.order_by = data.get("order_by")
        self.page = data.get("page") or (int(response.headers.get("X-Page")) if response else None)
        self.page_size = data.get("page_size") or (int(response.headers.get("X-Page-Size")) if response else None)
        self.total_pages = data.get("total_pages") or (int(response.headers.get("X-Total-Pages")) if response else None)
        self.total_count = data.get("total_count") or (int(response.headers.get("X-Total-Count")) if response else None)
        self.datastream = datastream

        if "dataframe" in data:
            self.dataframe = data["dataframe"]
        elif response is not None:
            data = response.json()
            self.dataframe = pd.DataFrame({to_snake(k): v for k, v in data.items()})
            if "phenomenon_time" in self.dataframe.columns:
                self.dataframe["phenomenon_time"] = pd.to_datetime(self.dataframe["phenomenon_time"], utc=True)
        else:
            self.dataframe = pd.DataFrame()

    def next_page(self):
        """Fetches the next page of data from HydroServer."""

        return self.datastream.get_observations(
            **(self.filters or {}),
            page=(self.page or 0) + 1,
            page_size=self.page_size or 100000,
            order_by=self.order_by or ...,
        )

    def previous_page(self):
        """Fetches the previous page of data from HydroServer."""

        if not self.page or self.page <= 1:
            return None

        return self.datastream.get_observations(
            **(self.filters or {}),
            page=self.page - 1,
            page_size=self.page_size or 100000,
            order_by=self.order_by or ...,
        )

    def fetch_all(self) -> "ObservationCollection":
        """Fetches all pages of data from HydroServer for this collection."""

        all_dataframes = []
        page_num = 1

        while self.total_pages is None or page_num <= self.total_pages:
            if page_num == self.page:
                all_dataframes.append(self.dataframe)
            else:
                observations = self.datastream.get_observations(
                    **(self.filters or {}),
                    page=page_num,
                    page_size=self.page_size or 100000,
                    order_by=self.order_by or ...,
                )
                if observations.dataframe.empty:
                    break
                all_dataframes.append(observations.dataframe)

            page_num += 1

        merged_dataframe = pd.concat(all_dataframes, ignore_index=True)

        return self.__class__(
            dataframe=merged_dataframe,
            datastream=self.datastream,
            filters=self.filters,
            order_by=self.order_by or ...,
            page=1,
            page_size=len(merged_dataframe),
            total_pages=1,
            total_count=len(merged_dataframe)
        )
