# scrapers/shared/http.py

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def create_session(headers: dict | None = None):
    session = requests.Session()

    retries = Retry(
        total=3,
        backoff_factor=1.5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )

    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    if headers:
        session.headers.update(headers)

    return session
