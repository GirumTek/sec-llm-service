import html
from html.parser import HTMLParser

class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.text = []
        self.in_script_or_style = False

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style","ix:header"):
            self.in_script_or_style = True

    def handle_endtag(self, tag):
        if tag in ("script", "style","ix:header"):
            self.in_script_or_style = False

        if tag in ("p", "div", "h1", "h2", "h3", "h4", "h5", "h6", "li"):
            self.text.append("\n\n")

    def handle_data(self, data):
        if not self.in_script_or_style:
            self.text.append(data)

    def handle_entityref(self, name):
        if name == "nbsp":
            self.text.append(" ")
        else:
            self.text.append(html.unescape(f"&{name};"))

    def handle_charref(self, name):
        if name.startswith("x") or name.startswith("X"):
            code_point = int(name[1:], 16)
        else:
            code_point = int(name)
        self.text.append(chr(code_point))


def clean_whitespace(text):
    text = text.replace("\xa0", " ")
    text = text.replace("\t", " ")
    lines = text.split("\n")
    lines = [line.strip() for line in lines]
    lines = [line for line in lines if line]
    return "\n\n".join(lines)

def estimate_tokens(text):
    return len(text) // 4

def truncate_to_budget(text, max_tokens):
    paragraphs = text.split("\n\n")
    kept = []
    total_tokens = 0

    for paragraph in paragraphs:
        paragraph_tokens = estimate_tokens(paragraph)
        if total_tokens + paragraph_tokens > max_tokens:
            break
        kept.append(paragraph)
        total_tokens += paragraph_tokens

    return "\n\n".join(kept)

def extract_text(html, max_tokens):
    extractor = TextExtractor()
    extractor.feed(html)
    full_text = "".join(extractor.text)
    cleaned = clean_whitespace(full_text)
    truncated = truncate_to_budget(cleaned, max_tokens)
    return truncated

def get_latest_10q_url(ticker):
    lookup = CIKLookup()
    cik = str(lookup.ticker_to_cik(ticker)[0])
    padded_cik = cik.zfill(10)

    headers = {"User-Agent": "Girum Tekle thegirumtekle@gmail.com"}
    url = f"https://data.sec.gov/submissions/CIK{padded_cik}.json"
    response = requests.get(url, headers=headers)
    data = response.json()

    form = data["filings"]["recent"]["form"]
    accessionNumber = data["filings"]["recent"]["accessionNumber"]
    primaryDocument = data["filings"]["recent"]["primaryDocument"]

    for i, f in enumerate(form):
        if f == "10-Q":
            accession_no_dashes = accessionNumber[i].replace("-", "")
            return f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession_no_dashes}/{primaryDocument[i]}"

    return None


if __name__ == "__main__":
    import requests
    from cik_lookup import CIKLookup

    tickers = ["AAPL", "GOOGL", "META"]
    headers = {"User-Agent": "Girum Tekle thegirumtekle@gmail.com"}

    for ticker in tickers:
        doc_url = get_latest_10q_url(ticker)
        response = requests.get(doc_url, headers=headers)
        raw_html = response.text

        result = extract_text(raw_html, max_tokens=5000)

        print(f"--- {ticker} ---")
        print("URL:", doc_url)
        print("Raw HTML character count:", len(raw_html))
        print("Extracted text character count:", len(result))
        print()