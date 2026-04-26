import feedparser
import json
import datetime
import requests
from typing import List, Dict
import hashlib
import base64

# لیست 10 سایت خبری معتبر با RSS
NEWS_SOURCES = {
    "BBC News": {
        "rss": "http://feeds.bbci.co.uk/news/rss.xml",
        "category": "world"
    },
    "Al Jazeera English": {
        "rss": "https://www.aljazeera.com/xml/rss/all.xml",
        "category": "world"
    },
    "Reuters": {
        "rss": "https://www.reutersagency.com/feed/?best-topics=technews&post_type=best",
        "category": "world"
    },
    "The Guardian": {
        "rss": "https://www.theguardian.com/world/rss",
        "category": "world"
    },
    "CNN": {
        "rss": "http://rss.cnn.com/rss/edition.rss",
        "category": "world"
    },
    "New York Times": {
        "rss": "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
        "category": "world"
    },
    "The Independent": {
        "rss": "https://www.independent.co.uk/news/uk/rss",
        "category": "world"
    },
    "BBC Persian": {
        "rss": "https://www.bbc.com/persia/index.xml",
        "category": "iran"
    },
    "Radio Farda": {
        "rss": "https://www.radiofarda.com/api/zpcqzdzqgq",
        "category": "iran"
    },
    "Iran International": {
        "rss": "https://www.iranintl.com/en/rss.xml",
        "category": "iran"
    }
}

def fetch_image_from_article(link: str) -> str:
    """تلاش برای استخراج عکس از لینک مقاله"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(link, timeout=5, headers=headers)
        if response.status_code == 200:
            # جستجوی ساده برای تصاویر در HTML
            import re
            # الگوهای مختلف برای پیدا کردن عکس
            patterns = [
                r'<meta property="og:image" content="([^"]+)"',
                r'<img[^>]+src="([^"]+)"[^>]*>',
                r'<meta name="twitter:image" content="([^"]+)"'
            ]
            for pattern in patterns:
                match = re.search(pattern, response.text)
                if match:
                    img_url = match.group(1)
                    if img_url.startswith('http'):
                        return img_url
                    elif img_url.startswith('/'):
                        from urllib.parse import urljoin
                        return urljoin(link, img_url)
        return ""
    except:
        return ""

def fetch_news_from_rss() -> Dict:
    """دریافت اخبار از همه منابع"""
    all_news = []
    world_news = []
    iran_news = []
    
    for source_name, source_info in NEWS_SOURCES.items():
        print(f"در حال دریافت از {source_name}...")
        
        try:
            feed = feedparser.parse(source_info["rss"])
            count = 0
            
            for entry in feed.entries[:5]:  # هر منبع 5 خبر آخر
                # دریافت تصویر از مقاله
                image_url = fetch_image_from_article(entry.get("link", ""))
                
                news_item = {
                    "id": hashlib.md5(f"{source_name}{entry.get('link')}".encode()).hexdigest(),
                    "source": source_name,
                    "category": source_info["category"],
                    "title": entry.get("title", "بدون عنوان"),
                    "link": entry.get("link", ""),
                    "published": entry.get("published", entry.get("published_parsed", "")),
                    "summary": entry.get("summary", "")[:300] + "..." if len(entry.get("summary", "")) > 300 else entry.get("summary", ""),
                    "image": image_url if image_url.startswith('http') else "",
                    "fetched_at": datetime.datetime.now().isoformat()
                }
                
                all_news.append(news_item)
                
                # دسته‌بندی
                if source_info["category"] == "iran":
                    iran_news.append(news_item)
                else:
                    world_news.append(news_item)
                
                count += 1
            
            print(f"  ✓ {count} خبر دریافت شد")
            
        except Exception as e:
            print(f"  ✗ خطا در {source_name}: {e}")
    
    # مرتب‌سازی بر اساس تاریخ (جدیدترین اول)
    all_news.sort(key=lambda x: x.get("published", ""), reverse=True)
    world_news.sort(key=lambda x: x.get("published", ""), reverse=True)
    iran_news.sort(key=lambda x: x.get("published", ""), reverse=True)
    
    return {
        "last_updated": datetime.datetime.now().isoformat(),
        "total_news": len(all_news),
        "world_news": world_news,
        "iran_news": iran_news,
        "all_news": all_news[:50]  # حداکثر 50 خبر برای جلوگیری از بزرگ شدن JSON
    }

def save_to_json(news_data: Dict):
    """ذخیره در فایل JSON (جایگزینی کامل)"""
    with open("news.json", "w", encoding="utf-8") as f:
        json.dump(news_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ خبرهایی ذخیره شد:")
    print(f"   - کل اخبار: {news_data['total_news']}")
    print(f"   - اخبار جهان: {len(news_data['world_news'])}")
    print(f"   - اخبار ایران: {len(news_data['iran_news'])}")

if __name__ == "__main__":
    print("شروع دریافت اخبار...\n")
    news_data = fetch_news_from_rss()
    save_to_json(news_data)
