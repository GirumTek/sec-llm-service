import requests

class CIKLookup:
    def __init__(self):
        url = "https://www.sec.gov/files/company_tickers.json"
        headers = {
            "User-Agent": "Girum Tekle thegirumtekle@gmail.com"
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

    def quarterly_filing(self, cik, year, quarter):
        url = "https://www.sec.gov/files/company_tickers.json"
        
        headers = {
            "User-Agent": "Girum Tekle thegirumtekle@gmail.com"
        }
        padded_cik = cik.zfill(10)
        url = f"https://data.sec.gov/submissions/CIK{padded_cik}.json"

        # Step 2: fetch + parse JSON
        response = requests.get(url, headers=headers)
        data = response.json()

        # Step 3: pull out the four arrays (form, filingDate, accessionNumber, primaryDocument)
        form = data["filings"]["recent"]["form"]
        accessionNumber = data["filings"]["recent"]["accessionNumber"]
        filingDate = data["filings"]["recent"]["filingDate"]
        primaryDocument = data["filings"]["recent"]["primaryDocument"]

        # Step 4: loop with enumerate, collect indexes where form is "10-Q" and year matches
        filing_list = []
        
        for i, f in enumerate(form):
            if f == "10-Q" and filingDate[i][0:4]== str(year):
                filing_list.append((accessionNumber[i], filingDate[i],primaryDocument[i]))
        # Step 5: reverse the collected list
        filing_list = filing_list[::-1]

        # Step 6: pick out the entry at index (quarter - 1)
        accession, date, doc = filing_list[quarter - 1]

        # Step 7: build and return the document URL
        accession_no_dashes = accession.replace("-", "")
  
        return f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession_no_dashes}/{doc}"

    
    def annual_filing(self, cik, year):
        padded_cik = cik.zfill(10)
        url = f"https://data.sec.gov/submissions/CIK{padded_cik}.json"
        headers = {
            "User-Agent": "Girum Tekle thegirumtekle@gmail.com"
        }

        response = requests.get(url, headers=headers)
        data = response.json()

        form = data["filings"]["recent"]["form"]
        filingDate = data["filings"]["recent"]["filingDate"]
        accessionNumber = data["filings"]["recent"]["accessionNumber"]
        primaryDocument = data["filings"]["recent"]["primaryDocument"]

        
        for i, f in enumerate(form):
            if f == "10-K" and filingDate[i][0:4]== str(year):
                accession_no_dashes = accessionNumber[i].replace("-", "")
                return f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession_no_dashes}/{primaryDocument[i]}"

  