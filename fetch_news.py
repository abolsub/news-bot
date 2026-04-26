import feedparser
import json
import datetime
from typing import List, Dict

# لیست RSS معروف انگلیسی
RSS_FEEDS = {
    "BBC News": "http://feeds.bbci.co.uk/news/rss.xml",
    "Al Jazeera English": "https://www.aljazeera.com/xml/rss/all.xml",
    "Reuters": "https://www.reutersagency.com/feed/?best-topics=technews&post_type=best",
    "The Guardian": "https://www.theguardian.com/world/rss"
}

def fetch_news_from_rss() -> List[Dict]:
    all_news = []
    
    for source_name, feed_url in RSS_FEEDS.items():
        print(f"در حال گرفتن خبر از {source_name}...")
        
        try:
            feed = feedparser.parse(feed_url)
            
            for entry in feed.entries[:10]:  # از هر منبع ۱۰ خبر آخر
                news_item = {
                    "source": source_name,
                    "title": entry.get("title", "بدون عنوان"),
                    "link": entry.get("link", ""),
                    "published": entry.get("published", entry.get("published_parsed", "")),
                    "summary": entry.get("summary", "")[:200],  # حداکثر ۲۰۰ کاراکتر
                    "fetched_at": datetime.datetime.now().isoformat()
                }
                all_news.append(news_item)
                
        except Exception as e:
            print(f"خطا در دریافت {source_name}: {e}")
    
    return all_news

def save_to_json(news_data: List[Dict]):
    output = {
        "last_updated": datetime.datetime.now().isoformat(),
        "total_news": len(news_data),
        "news": news_data
    }
    
    with open("news.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ {len(news_data)} خبر در فایل news.json ذخیره شد.")

if __name__ == "__main__":
    print("شروع دریافت اخبار از RSS...\n")
    news_list = fetch_news_from_rss()
    save_to_json(news_list)
