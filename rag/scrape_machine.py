import requests
from bs4 import BeautifulSoup
import time

def scrape_cnbc():
    urls = ["https://www.cnbc.com/finance/", 
            "https://www.cnbc.com/technology/", 
            "https://www.cnbc.com/world/", 
            "https://www.cnbc.com/markets/", 
            "https://www.cnbc.com/investing/"]
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    for url in urls:
        print("fetching: ", url)
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        articles = soup.select("div.Card-titleContainer a")
        news_data = []

        for tag in articles:
            print("tag: ", tag)
            title = tag.text.strip()
            link = tag.get("href")

            if not title or not link or not link.startswith("http") or "/video/" in link:
                continue

            # Get full article content
            try:
                article_response = requests.get(link, headers=headers, timeout=10)
                article_soup = BeautifulSoup(article_response.text, "html.parser")
                paragraphs = article_soup.select("div.ArticleBody-articleBody p")
                article_text = " ".join([p.text.strip() for p in paragraphs if p.text.strip()])
                print("article_text: ", article_text)
            except Exception as e:
                article_text = f"[ERROR] Failed to fetch article: {e}"

            news_data.append({
                "title": title,
                "content": article_text if article_text else "⚠️ Article content not available (may be a video or non-HTML article)"
            })
            time.sleep(2)  # be polite

    return news_data


def fetch_article(url):

    """Fetch the article page and return content."""
    resp = requests.get(url, headers=HEADERS, timeout=10)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # Article content
    content_div = soup.find("div", class_="content_wrapper") or soup.find("div", class_="arti-flow")
    if content_div:
        paragraphs = content_div.find_all("p")
    else:
        paragraphs = soup.find_all("p")
    content = "\n".join(p.get_text(strip=True) for p in paragraphs)

    return content

def scrape_moneycontrol(pages=5):
    base_url = "https://www.moneycontrol.com"
    sections = ["/news", "/news/business", "/news/business/market", "/news/business/stocks", "/news/business/economy", "/news/business/companies"]
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/122.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.google.com/",
        "Connection": "keep-alive"
    }
    articles = []

    for section in sections:
        section_path = section
        for page in range(1, pages + 1):
            url = base_url + section_path if page == 1 else base_url + section_path + f"{page}/"
            print(f"🔍 Scraping page {page}: {url}")
            
            try:
                resp = requests.get(url, headers=headers)
                resp.raise_for_status()
                resp.encoding = resp.apparent_encoding
            except Exception as e:
                print(f"❌ Failed to fetch page {page}: {e}")
                continue

            soup = BeautifulSoup(resp.text, "html.parser")

            for li in soup.find_all("li", class_="clearfix"):
                a = li.find("a", href=True)
                if not a:
                    continue

                title = a.get_text(strip=True)
                href = a["href"]
                href = base_url + href if href.startswith("/") else href

                print(f"➡️  Fetching article: {title}")
                try:
                    content = fetch_article(href)
                except Exception as e:
                    print(f"   ⚠️  Failed to fetch {href}: {e}")
                    content = ""

                articles.append({
                    "title": title,
                    "content": content if content else "⚠️ Article content not available (may be a video or non-HTML article)"
                })

                time.sleep(2)  # be polite
        

    return articles


BASE_URL    = "https://www.businesstoday.in"
HEADERS     = {"User-Agent": "Mozilla/5.0"}

def fetch_article_page(url):
    resp = requests.get(url, headers=HEADERS, timeout=10)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")

def parse_article(url):
    soup = fetch_article_page(url)

    content_div = (
        soup.find("div", class_="storydetail")
        or soup.find("div", class_="articlecontent")
    )
    if content_div:
        paras = content_div.find_all("p")
    else:
        paras = soup.find_all("p")

    content = "\n".join(p.get_text(strip=True) for p in paras)
    return content[:3000]  # truncate for safety

def scrape_businesstoday(max_articles=50):
    urls = ["/personal-finance/investment", "/india", "/world/us", "/bt-tv/market-today"]

    seen = set()
    results = []

    for path in urls:
        full_listing_url = BASE_URL + path
        print(f"\n🌐 Visiting: {full_listing_url}")

        try:
            resp = requests.get(full_listing_url, headers=HEADERS, timeout=10)
            resp.raise_for_status()
        except Exception as e:
            print(f"❌ Failed to fetch {full_listing_url}: {e}")
            continue

        listing_soup = BeautifulSoup(resp.text, "html.parser")
        for a in listing_soup.find_all("a", href=True):
            href = a["href"]
            if "/story/" in href:
                title = a.get_text(strip=True)
                if not title:
                    continue
                full_url = href if href.startswith("http") else BASE_URL + href
                if full_url in seen:
                    continue
                seen.add(full_url)

                print(f"➡️ Scraping: {title[:60]}…")
                try:
                    content = parse_article(full_url)
                except Exception as e:
                    content = f"[ERROR] {e}"

                results.append({
                    "title": title,
                    "content": content
                })

                if len(results) >= max_articles:
                    return results

                time.sleep(2)

    return results
