import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))

import requests
from bs4 import BeautifulSoup
import json

def scout_tiki(book_title):
    print(f"Searching Tiki: {book_title}")
    # Tiki API often needs specific headers or is rate limited
    url = f"https://tiki.vn/api/v2/products?limit=5&q={book_title}"
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    }
    try:
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            data = resp.json().get('data', [])
            results = []
            for item in data:
                results.append({
                    "platform": "Tiki",
                    "title": item.get('name'),
                    "price": item.get('price'),
                    "link": f"https://tiki.vn/{item.get('url_path')}"
                })
            return results
    except Exception as e:
        print(f"Tiki Error: {e}")
    return []

def scout_fahasa(book_title):
    print(f"Searching Fahasa: {book_title}")
    url = f"https://www.fahasa.com/catalogsearch/result/?q={book_title}"
    headers = {"user-agent": "Mozilla/5.0"}
    try:
        resp = requests.get(url, headers=headers)
        soup = BeautifulSoup(resp.text, 'html.parser')
        # Typical Fahasa structure
        items = soup.select('.product-item')
        results = []
        for item in items[:5]:
            title = item.select_one('.product-name-no-ellipsis').text.strip()
            price_text = item.select_one('.price').text.strip()
            price = int(''.join(filter(str.isdigit, price_text)))
            link = item.select_one('a')['href']
            results.append({
                "platform": "Fahasa",
                "title": title,
                "price": price,
                "link": link
            })
        return results
    except Exception as e:
        print(f"Fahasa Error: {e}")
    return []

def scout_oreka(book_title):
    print(f"Searching Oreka (Used): {book_title}")
    url = f"https://www.oreka.vn/search?keyword={book_title}"
    headers = {"user-agent": "Mozilla/5.0"}
    try:
        resp = requests.get(url, headers=headers)
        soup = BeautifulSoup(resp.text, 'html.parser')
        # typical Oreka item class
        items = soup.select('.book-item') # Placeholder selector
        results = []
        # Parse logic would go here after inspecting DOM
        return [{"platform": "Oreka", "info": "Scraper logic in progress"}]
    except Exception as e:
        print(f"Oreka Error: {e}")
    return []

if __name__ == "__main__":
    title = "Nha gia kim"
    print(scout_tiki(title))
    # Fahasa/Oreka might need more specific selectors
