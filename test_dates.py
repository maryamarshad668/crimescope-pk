import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

url = "https://www.dawn.com/pakistan"
response = requests.get(url, headers=HEADERS, timeout=10)
soup = BeautifulSoup(response.text, "html.parser")

# Check what date tags actually exist
print("=== META TAGS ===")
for meta in soup.find_all("meta", {"property": "article:published_time"})[:3]:
    print(meta)

print("\n=== TIME TAGS ===")
for t in soup.find_all("time")[:5]:
    print(t)

print("\n=== FIRST ARTICLE HTML ===")
article = soup.find("article")
if article:
    print(article.prettify()[:2000])