# backend/test_sources.py
import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

sites = {
    "samaa": "https://www.samaa.tv/news/pakistan",
    "express": "https://www.express.pk/category/pakistan/",
    "ary": "https://arynews.tv/category/pakistan/",
    "bol": "https://www.bolnews.com/pakistan/",
    "dunya": "https://dunyanews.tv/index.php/en/Pakistan",
}
print("\n=== DUNYA FULL ARTICLE ===")
r = requests.get("https://dunyanews.tv/index.php/en/Pakistan", headers=HEADERS, timeout=10)
soup = BeautifulSoup(r.text, "html.parser")
# Find h2 with a link
for h2 in soup.find_all("h2"):
    parent = h2.find_parent("div") or h2.find_parent("li")
    if parent:
        print(parent.prettify()[:1000])
        break







for name, url in sites.items():
    print(f"\n{'='*20} {name.upper()} {'='*20}")
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        # Find first article/heading
        for tag in ["article", "h2", "h3"]:
            found = soup.find(tag)
            if found:
                print(f"First <{tag}>:")
                print(found.prettify()[:800])
                break
    except Exception as e:
        print(f"Error: {e}")

# add to test_sources.py and run
import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

print("\n=== SAMAA (different user agent) ===")
try:
    headers2 = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"}
    r = requests.get("https://www.samaa.tv/news/pakistan", headers=headers2, timeout=10)
    print(f"Status: {r.status_code}")
    soup = BeautifulSoup(r.text, "html.parser")
    for tag in ["article", "h2", "h3"]:
        found = soup.find(tag)
        if found:
            print(f"First <{tag}>:")
            print(found.prettify()[:1000])
            break
except Exception as e:
    print(f"Error: {e}")

print("\n=== EXPRESS ENGLISH ===")

try:
    r = requests.get(
        "https://tribune.com.pk/pakistan",
        headers=HEADERS,
        timeout=10
    )

    print(f"Status: {r.status_code}")

    soup = BeautifulSoup(r.text, "html.parser")

    for tag in ["article", "h2", "h3"]:
        found = soup.find(tag)
        if found:
            print(f"First <{tag}>:")
            print(found.prettify()[:1000])
            break

except Exception as e:
    print(f"Error: {e}")

# add this to test_sources.py
print("\n=== EXPRESS TRIBUNE FULL ARTICLE ===")
try:
    r = requests.get("https://tribune.com.pk/pakistan", headers=HEADERS, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")
    for h2 in soup.find_all("h2"):
        parent = h2.find_parent("article") or h2.find_parent("div")
        if parent:
            print(parent.prettify()[:1500])
            break
except Exception as e:
    print(f"Error: {e}")    