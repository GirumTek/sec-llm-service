import requests

class CIKLookup:
    def __init__(self):
        url = "https://www.sec.gov/files/company_tickers.json"
        headers = {
            "User-Agent": "Girum girum@example.com"
        }

        response = requests.get(url, headers=headers)
        data = response.json()

        self.by_name = {}
        self.by_ticker = {}

        for entry in data.values():
            cik = entry["cik_str"]
            name = entry["title"].upper()
            ticker = entry["ticker"].upper()

            self.by_name[name] = (cik, name, ticker)
            self.by_ticker[ticker] = (cik, name, ticker)

    def name_to_cik(self, name):
        return self.by_name.get(name.upper())

    def ticker_to_cik(self, ticker):
        return self.by_ticker.get(ticker.upper())