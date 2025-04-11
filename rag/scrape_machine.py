import requests
from bs4 import BeautifulSoup

def scrape_cnbc_headlines():
    url = "https://www.cnbc.com/buisiness/"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    print("cnbc: ", soup)

    articles = soup.select("div.Card-titleContainer a")
    news_data = []

    for tag in articles:
        title = tag.text.strip()
        link = tag.get("href")

        if not title or not link or not link.startswith("http") or "/video/" in link:
            continue

        # Fetch article content
        article_response = requests.get(link, headers=headers)
        article_soup = BeautifulSoup(article_response.text, "html.parser")
        paragraphs = article_soup.select("div.ArticleBody-articleBody p")
        article_text = " ".join([p.text.strip() for p in paragraphs if p.text.strip()])

        news_data.append({
            "headline": title,
            "url": link,
            "content": article_text if article_text else "⚠️ Content not available"
        })

    return news_data
print(scrape_cnbc_headlines())

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
}

def fetch_article_content(url):
    try:
        resp = requests.get(url, headers=HEADERS)
        if resp.status_code != 200:
            return f"[ERROR] Status {resp.status_code}", False

        soup = BeautifulSoup(resp.text, 'html.parser')

        paragraphs = soup.find_all('p')
        if paragraphs:
            content = "\n".join(p.get_text(strip=True) for p in paragraphs)
            if len(content) > 200:
                return content[:3000], True

        return "[ERROR] Content not found or too short", False

    except Exception as e:
        return f"[EXCEPTION] {str(e)}", False


def scrape_moneycontrol():
    articles = []
    soup = BeautifulSoup(requests.get("https://www.moneycontrol.com/news/business/", headers=HEADERS).text, 'html.parser')

    for item in soup.find_all('li', class_='clearfix'):
        title_tag = item.find('h2')
        link_tag = item.find('a')
        if title_tag and link_tag:
            title = title_tag.get_text(strip=True)
            link = link_tag.get('href')
            content, success = fetch_article_content(link)
            articles.append({'source': 'Moneycontrol', 'title': title, 'url': link, 'content': content, 'success': success})
    return articles
