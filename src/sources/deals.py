# Deals sources - CheapShark, Nuuvem

import requests
import re
from typing import List, Dict, Any
from src.config import SOURCES

def fetch_cheapshark_sales(min_discount: int = 50, max_results: int = 50) -> List[Dict[str, Any]]:
    """Fetch deals from CheapShark."""
    items = []
    try:
        params = {
            "pageSize": max_results,
            "sortBy": "Savings",
            "desc": "1",
            "lowerPrice": "1",
        }
        resp = requests.get(SOURCES["cheapshark"]["api"], params=params, timeout=15)
        resp.raise_for_status()
        deals = resp.json()
        
        stores = {
            "1": "Steam", "2": "GamersGate", "3": "GreenManGaming",
            "4": "Amazon", "5": "GameStop", "6": "Direct2Drive",
            "7": "GOG", "8": "Origin", "9": "Ubisoft Store",
            "11": "Humble Bundle", "14": "Fanatical", "15": "IndieGala",
            "23": "Epic Games", "25": "Itch.io", "27": "Microsoft Store",
        }
        
        for deal in deals:
            savings = float(deal.get("savings", 0))
            if savings < min_discount:
                continue
                
            title = deal.get("title", "")
            deal_id = deal.get("dealID", "")
            url = f"https://www.cheapshark.com/redirect?dealID={deal_id}"
            normal_price = deal.get("normalPrice", "")
            sale_price = deal.get("salePrice", "")
            store_id = deal.get("storeID", "")
            store_name = stores.get(store_id, "Loja")
            
            items.append({
                "title": title,
                "summary": f"{savings:.0f}% de desconto na {store_name}.",
                "url": url,
                "source": "cheapshark",
                "_extra": {
                    "sale_price": sale_price,
                    "normal_price": normal_price,
                    "discount": f"{savings:.0f}%",
                    "store": store_name,
                }
            })
    except Exception as e:
        print(f"Error fetching CheapShark: {e}")
    
    return items

def fetch_nuuvem_sales() -> List[Dict[str, Any]]:
    """Fetch sales from Nuuvem (Brazil-focused)."""
    items = []
    try:
        from bs4 import BeautifulSoup
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        resp = requests.get(SOURCES["nuuvem"]["sale_url"], headers=headers, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # Nuuvem uses product cards - adapt selectors as needed
        products = soup.select(".product-card, .product-item, [data-product], .product")[:30]
        
        for prod in products:
            title_elem = prod.select_one(".product-title, h3, .name, .product-name, a[title]")
            price_elem = prod.select_one(".price, .sale-price, .discount, .product-price")
            link_elem = prod.select_one("a[href]")
            
            if not title_elem or not link_elem:
                continue
                
            title = title_elem.get_text(strip=True)
            url = link_elem.get("href", "")
            if url and not url.startswith("http"):
                url = f"https://www.nuuvem.com{url}"
            
            price_text = price_elem.get_text(strip=True) if price_elem else ""
            discount_match = re.search(r'(\d+)%', price_text)
            discount = discount_match.group(1) if discount_match else "?"
            
            items.append({
                "title": title,
                "summary": f"Promoção na Nuuvem com {discount}% de desconto.",
                "url": url,
                "source": "nuuvem",
                "_extra": {
                    "price_text": price_text,
                    "discount": f"{discount}%",
                }
            })
    except Exception as e:
        print(f"Error fetching Nuuvem: {e}")
    
    return items