import feedparser
import json
import datetime
import requests
from typing import List, Dict
import hashlib
import base64
from urllib.parse import urljoin

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

def image_url_to_base64(image_url: str) -> str:
    """تبدیل URL عکس به رشته Base64"""
    if not image_url:
        return ""
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(image_url, timeout=10, headers=headers)
        if response.status_code == 200:
            # تشخیص نوع عکس
            content_type = response.headers.get('content-type', '')
            if 'jpeg' in content_type or 'jpg' in content_type:
                img_format = 'jpeg'
            elif 'png' in content_type:
                img_format = 'png'
            elif 'gif' in content_type:
                img_format = 'gif'
            else:
                img_format = 'jpeg'  # پیش‌فرض
            
            # تبدیل به Base64
            base64_string = base64.b64encode(response.content).decode('utf-8')
            return f"data:image/{img_format};base64,{base64_string}"
    except Exception as e:
        print(f"    خطا در تبدیل عکس: {e}")
    
    return ""

def fetch_image_from_article(link: str) -> str:
    """استخراج URL عکس از مقاله"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(link, timeout=8, headers=headers)
        if response.status_code == 200:
            import re
            # الگوهای مختلف برای پیدا کردن عکس
            patterns = [
                r'<meta property="og:image" content="([^"]+)"',
                r'<meta name="twitter:image" content="([^"]+)"',
                r'<img[^>]+src="([^"]+)"[^>]*>',
                r'<img[^>]+src=\'([^\']+)\'[^>]*>'
            ]
            for pattern in patterns:
                match = re.search(pattern, response.text, re.IGNORECASE)
                if match:
                    img_url = match.group(1)
                    if img_url.startswith('http'):
                        return img_url
                    elif img_url.startswith('/'):
                        return urljoin(link, img_url)
        return ""
    except Exception as e:
        print(f"    خطا در استخراج عکس: {e}")
        return ""

def fetch_news_from_rss() -> Dict:
    """دریافت اخبار از همه منابع"""
    all_news = []
    world_news = []
    iran_news = []
    
    total_sources = len(NEWS_SOURCES)
    current_source = 0
    
    for source_name, source_info in NEWS_SOURCES.items():
        current_source += 1
        print(f"[{current_source}/{total_sources}] در حال دریافت از {source_name}...")
        
        try:
            feed = feedparser.parse(source_info["rss"])
            count = 0
            
            for entry in feed.entries[:5]:  # هر منبع 5 خبر آخر
                print(f"    پردازش خبر {count+1}...")
                
                # استخراج URL عکس
                image_url = fetch_image_from_article(entry.get("link", ""))
                
                # تبدیل عکس به Base64
                image_base64 = ""
                if image_url:
                    print(f"    دانلود و تبدیل عکس...")
                    image_base64 = image_url_to_base64(image_url)
                    if image_base64:
                        print(f"    ✓ عکس با موفقیت به Base64 تبدیل شد")
                    else:
                        print(f"    ✗ تبدیل عکس ناموفق بود")
                else:
                    print(f"    ✗ عکسی برای این خبر پیدا نشد")
                
                news_item = {
                    "id": hashlib.md5(f"{source_name}{entry.get('link')}".encode()).hexdigest(),
                    "source": source_name,
                    "category": source_info["category"],
                    "title": entry.get("title", "بدون عنوان"),
                    "link": entry.get("link", ""),
                    "published": entry.get("published", entry.get("published_parsed", "")),
                    "summary": entry.get("summary", "")[:300] + "..." if len(entry.get("summary", "")) > 300 else entry.get("summary", ""),
                    "image_base64": image_base64,  # ذخیره عکس به صورت Base64
                    "fetched_at": datetime.datetime.now().isoformat()
                }
                
                all_news.append(news_item)
                
                # دسته‌بندی
                if source_info["category"] == "iran":
                    iran_news.append(news_item)
                else:
                    world_news.append(news_item)
                
                count += 1
            
            print(f"  ✓ {count} خبر از {source_name} دریافت شد\n")
            
        except Exception as e:
            print(f"  ✗ خطا در {source_name}: {e}\n")
    
    # مرتب‌سازی بر اساس تاریخ (جدیدترین اول)
    all_news.sort(key=lambda x: x.get("published", ""), reverse=True)
    world_news.sort(key=lambda x: x.get("published", ""), reverse=True)
    iran_news.sort(key=lambda x: x.get("published", ""), reverse=True)
    
    # محدودیت برای جلوگیری از بزرگ شدن JSON (حداکثر 50 خبر)
    all_news = all_news[:50]
    world_news = world_news[:30]
    iran_news = iran_news[:20]
    
    # محاسبه حجم تقریبی JSON
    total_size = 0
    
    return {
        "last_updated": datetime.datetime.now().isoformat(),
        "total_news": len(all_news),
        "world_news_count": len(world_news),
        "iran_news_count": len(iran_news),
        "world_news": world_news,
        "iran_news": iran_news,
        "all_news": all_news
    }

def save_to_json(news_data: Dict):
    """ذخیره در فایل JSON (جایگزینی کامل)"""
    with open("news.json", "w", encoding="utf-8") as f:
        json.dump(news_data, f, ensure_ascii=False, indent=2)
    
    # محاسبه حجم فایل
    file_size = len(json.dumps(news_data, ensure_ascii=False)) / (1024 * 1024)
    
    print(f"\n✅ خبرهای ذخیره شد:")
    print(f"   - کل اخبار: {news_data['total_news']}")
    print(f"   - اخبار جهان: {news_data['world_news_count']}")
    print(f"   - اخبار ایران: {news_data['iran_news_count']}")
    print(f"   - حجم فایل JSON: {file_size:.2f} MB")
    
    # هشدار اگر حجم زیاد شد
    if file_size > 5:
        print(f"\n⚠️ هشدار: حجم فایل JSON زیاد است! (بیش از 5 مگابایت)")
        print("   ممکن است در GitHub Pages با مشکل نمایش مواجه شود.")

if __name__ == "__main__":
    print("=" * 50)
    print("شروع دریافت اخبار با ذخیره عکس به صورت Base64...")
    print("=" * 50 + "\n")
    
    news_data = fetch_news_from_rss()
    save_to_json(news_data)
    
    print("\n✨ فرآیند با موفقیت به پایان رسید!")
