import requests
from typing import List, Dict, Any
import re

from src.database import make_item_id, is_posted

CHEAPSHARK_API = "https://www.cheapshark.com/api/1.0/deals"
ITAD_API = "https://api.isthereanydeal.com/v02/deals/"
NUUVEM_URL = "https://www.nuuvem.com/br-pt/sale"

def fetch_cheapshark_sales(min_discount: int = 50, max_results: int = 30) -> List[Dict[str, Any]]:
    """Fetch deals from CheapShark."""
    items = []
    try:
        params = {
            "pageSize": max_results,
            "sortBy": "Savings",
            "desc": "1",
            "lowerPrice": "1",
        }
        resp = requests.get(CHEAPSHARK_API, params=params, timeout=15)
        resp.raise_for_status()
        deals = resp.json()
        
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
            
            stores = {
                "1": "Steam", "2": "GamersGate", "3": "GreenManGaming",
                "4": "Amazon", "5": "GameStop", "6": "Direct2Drive",
                "7": "GOG", "8": "Origin", "9": "Ubisoft Store",
                "11": "Humble Bundle", "14": "Fanatical", "15": "IndieGala",
                "23": "Epic Games", "25": "Itch.io", "27": "Microsoft Store",
            }
            store_name = stores.get(store_id, "Loja")
            
            item_id = make_item_id("cheapshark", url, title)
            if is_posted(item_id):
                continue
            
            items.append({
                "category": "sale",
                "title": title,
                "summary": f"{savings:.0f}% de desconto na {store_name}.",
                "date_info": "Enquanto durar o estoque",
                "price_info": f"{sale_price} (era {normal_price}) — {savings:.0f}% OFF",
                "platforms": f"PC ({store_name})",
                "url": url,
                "source": "cheapshark",
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
        resp = requests.get(NUUVEM_URL, headers=headers, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # Nuuvem uses product cards - adapt selectors as needed
        products = soup.select(".product-card, .product-item, [data-product]")[:20]
        
        for prod in products:
            title_elem = prod.select_one(".product-title, h3, .name")
            price_elem = prod.select_one(".price, .sale-price, .discount")
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
            
            item_id = make_item_id("nuuvem", url, title)
            if is_posted(item_id):
                continue
            
            items.append({
                "category": "sale",
                "title": title,
                "summary": f"Promoção na Nuuvem com {discount}% de desconto.",
                "date_info": "Enquanto durar o estoque",
                "price_info": f"{discount}% OFF — {price_text}",
                "platforms": "PC (Nuuvem/Steam/Ubisoft/Epic)",
                "url": url,
                "source": "nuuvem",
            })
    except Exception as e:
        print(f"Error fetching Nuuvem: {e}")
    
    return items