from .parser import parse_bet365


def process_file(path: str):
    with open(path, encoding="utf-8") as f:
        html = f.read()

    return parse_bet365(html)
