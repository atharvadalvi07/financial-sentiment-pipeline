import requests
import json
import os
from datetime import datetime, timedelta

API_KEY = "2b41fb2dd3bf435f8b9a7d2c15eec233"  

TICKERS = ["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN"]

OUTPUT_DIR = "/home/jovyan/work/data/raw"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def fetch_articles(ticker: str) -> list:
    """Fetch news articles for a given ticker from NewsAPI."""
    
    to_date = datetime.today().strftime("%Y-%m-%d")
    from_date = (datetime.today() - timedelta(days=7)).strftime("%Y-%m-%d")
    
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": ticker,
        "from": from_date,
        "to": to_date,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 20,      
        "apiKey": API_KEY,
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code != 200:
        print(f"[ERROR] {ticker}: {response.status_code} — {response.text}")
        return []
    
    data = response.json()
    articles = data.get("articles", [])
    print(f"[INFO] {ticker}: fetched {len(articles)} articles")
    return articles


def save_raw(ticker: str, articles: list):
    """Save raw articles to a JSON file."""
    if not articles:
        return
    
    output = {
        "ticker": ticker,
        "fetched_at": datetime.utcnow().isoformat(),
        "article_count": len(articles),
        "articles": articles,
    }
    
    filepath = os.path.join(OUTPUT_DIR, f"{ticker}_raw.json")
    with open(filepath, "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"[INFO] Saved {ticker} → {filepath}")


if __name__ == "__main__":
    for ticker in TICKERS:
        articles = fetch_articles(ticker)
        save_raw(ticker, articles)
    
    print("\n[DONE] All tickers fetched and saved.")