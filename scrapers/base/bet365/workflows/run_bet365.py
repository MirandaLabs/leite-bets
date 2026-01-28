from scrapers.base.bet365.collector import collect_futebol_1x2


def run():
    return collect_futebol_1x2(max_items=5)
