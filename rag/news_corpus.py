from scrape_machine import scrape_cnbc, scrape_moneycontrol, scrape_businesstoday
from embedder import process_articles, load_vectorstore
import os

os.environ["GOOGLE_API_KEY"] = "AIzaSyBF-wxgd4Fm_3sTFcAL3u-WaZQh7aLzqAM"

def process_data():

    cnbc_data = scrape_cnbc()
    money_data = scrape_moneycontrol()
    buisiness_today = scrape_businesstoday()

    process_articles(cnbc_data)
    process_articles(money_data)
    process_articles(buisiness_today)

def search(query):
    vectorstore, metadata = load_vectorstore()
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    results = retriever.get_relevant_documents(query)

    print("\n🔍 Search Results:\n")
    for doc in results:
        print(f"• {doc.metadata.get('title')}\nSummary: {doc.page_content[:200]}...\n")

process_data()
