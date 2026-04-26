import requests
from bs4 import BeautifulSoup
import json
import datetime

# مثال: گرفتن تیترهای خبری از یک سایت ساده (مثلاً وقت‌نوری)
# توجه: حتما robots.txt سایت را بررسی کنید
url = "https://vazey.com"  # فقط مثال، یک سایت خبری ساده

response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

news_list = []
# این سلکتور با توجه به ساختار سایت عوض می‌شود
for item in soup.select(".news-item a"):  # مثال
    news_list.append({
        "title": item.get_text(strip=True),
        "link": item.get("href"),
        "fetched_at": datetime.datetime.now().isoformat()
    })

# ذخیره در JSON
with open("news.json", "w", encoding=""utf-8"") as f:
    json.dump(news_list, f, ensure_ascii=False, indent=2)

print(f"{len(news_list)} خبر ذخیره شد")
