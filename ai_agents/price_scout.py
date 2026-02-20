import sys
import os

# Add local lib to path for dependencies
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))

import requests
from bs4 import BeautifulSoup
import json
import logging
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger("price_scout")
logging.basicConfig(level=logging.INFO)

class PriceScoutAgent:
    def __init__(self):
        self.headers = {
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        }

    def scout_tiki(self, query):
        """Scouts Tiki using their public search API."""
        url = f"https://tiki.vn/api/v2/products?limit=5&q={query}"
        try:
            resp = requests.get(url, headers=self.headers, timeout=10)
            if resp.status_code == 200:
                data = resp.json().get('data', [])
                results = []
                for item in data:
                    results.append({
                        "platform": "Tiki",
                        "title": item.get('name'),
                        "price": item.get('price'),
                        "link": f"https://tiki.vn/{item.get('url_path')}",
                        "thumbnail": item.get('thumbnail_url'),
                        "type": "New"
                    })
                return results
        except Exception as e:
            logger.error(f"Tiki scouting error: {e}")
        return []

    def scout_fahasa(self, query):
        """Scouts Fahasa using web scraping."""
        url = f"https://www.fahasa.com/catalogsearch/result/?q={query}"
        try:
            resp = requests.get(url, headers=self.headers, timeout=10)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                items = soup.select('.product-item')
                results = []
                for item in items[:5]:
                    title_elem = item.select_one('h2.product-name-no-ellipsis a')
                    price_elem = item.select_one('.price')
                    if title_elem and price_elem:
                        title = title_elem.get_title().strip() if hasattr(title_elem, 'get_title') else title_elem.text.strip()
                        price_text = price_elem.text.strip()
                        price = int(''.join(filter(str.isdigit, price_text)))
                        link = title_elem['href']
                        img_elem = item.select_one('img')
                        thumbnail = img_elem['src'] if img_elem else ""
                        results.append({
                            "platform": "Fahasa",
                            "title": title,
                            "price": price,
                            "link": link,
                            "thumbnail": thumbnail,
                            "type": "New"
                        })
                return results
        except Exception as e:
            logger.error(f"Fahasa scouting error: {e}")
        return []

    def scout_oreka(self, query):
        """Scouts Oreka (Used Books) using web scraping."""
        url = f"https://www.oreka.vn/search?keyword={query}"
        try:
            resp = requests.get(url, headers=self.headers, timeout=10)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                # Use a more generic selector for the product card links
                items = soup.select('a[class*="ProductCard_wrapContent"]')
                results = []
                for item in items[:5]:
                    title_elem = item.select_one('h3')
                    price_elem = item.select_one('p') # Price is usually in a p tag in the card
                    if title_elem and price_elem:
                        title = title_elem.text.strip()
                        price_text = price_elem.text.strip()
                        # Extract digits for price
                        digits = ''.join(filter(str.isdigit, price_text))
                        price = int(digits) if digits else 0
                        link = "https://www.oreka.vn" + item['href'] if item['href'].startswith('/') else item['href']
                        results.append({
                            "platform": "Oreka",
                            "title": title,
                            "price": price,
                            "link": link,
                            "type": "Used"
                        })
                return results
        except Exception as e:
            logger.error(f"Oreka scouting error: {e}")
        return []

    def compare(self, book_title):
        """Runs scouts in parallel and aggregates results."""
        logger.info(f"Comparing prices for: {book_title}")
        with ThreadPoolExecutor(max_workers=3) as executor:
            tiki_future = executor.submit(self.scout_tiki, book_title)
            fahasa_future = executor.submit(self.scout_fahasa, book_title)
            oreka_future = executor.submit(self.scout_oreka, book_title)
            
            all_results = []
            all_results.extend(tiki_future.result())
            all_results.extend(fahasa_future.result())
            all_results.extend(oreka_future.result())
            
        # Sort by price
        all_results.sort(key=lambda x: x['price'] if x['price'] > 0 else float('inf'))
        return all_results

if __name__ == "__main__":
    agent = PriceScoutAgent()
    res = agent.compare("Nhà giả kim")
    print(json.dumps(res, indent=2, ensure_ascii=False))
