import json
from requests import HTTPError


def raise_for_hs_status(response):
    try:
        response.raise_for_status()
    except HTTPError as e:
        try:
            http_error_msg = (
                f"{response.status_code} Client Error: "
                f"{str(json.loads(response.content).get('detail'))}"
            )
        except (
            ValueError,
            TypeError,
        ):
            http_error_msg = e
        if 400 <= response.status_code < 500:
            raise HTTPError(http_error_msg, response=response)
        else:
            raise HTTPError(str(e), response=response)
