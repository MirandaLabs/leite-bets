# scrapers/shared/response.py

def success(source: str, data: list, extra: dict | None = None):
    payload = {
        "status": "ok",
        "source": source,
        "items": len(data),
        "data": data,
    }

    if extra:
        payload.update(extra)

    return payload


def error(source: str, message: str):
    return {
        "status": "error",
        "source": source,
        "error": message,
    }
