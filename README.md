# 🧠 NewsSense — *Why Is My Fund Down?*

**NewsSense** is an intelligent, news-based explanation engine that helps users understand why a particular stock or mutual fund is rising or falling — by analyzing **real-time news scraped directly from the web**, with **zero reliance on scraper APIs or news APIs**.

Built with a powerful **LangChain pipeline**, NewsSense tracks indirect relationships between mutual fund holdings and the latest financial events to generate smart, relevant answers.

---

## 🚀 Features

- 🔍 **Ask Anything Finance** — Enter queries like _"Why is QQQ down today?"_ and get an AI-generated explanation from recent news.
- ⚡ **Groq-Powered Ticker Detection** — Ultra-fast extraction of company or fund tickers from natural language.
- 🧠 **LangChain RAG Pipeline** — Retrieval-Augmented Generation pipeline that connects tickers, holdings, and news stories.
- 🏦 **Holdings Intelligence** — If a fund is queried, its holdings are used to identify potential causes in the market ecosystem.
- 📰 **Custom Web Scraping** — Scrapes real-time news from the open web using in-house HTML parsing — **no APIs involved**.
- 📚 **Vector Database (FAISS)** — Stores semantically embedded news articles for fast and relevant similarity search.

---

## 🧰 Tech Stack

| Tool         | Purpose                                 |
|--------------|------------------------------------------|
| **LangChain** | Building the multi-step RAG pipeline    |
| **Groq**      | Fast LLM inference for ticker detection |
| **FAISS**     | Semantic vector search                  |
| **SQLite**    | Fund and holdings data storage          |
| **BeautifulSoup** | HTML scraping of financial news     |
| **Gemini / OpenAI** | Summarization and explanation     |

---

## 🧠 How It Works

1. **User Query** — e.g., _"Why is ARKK falling today?"_
2. **Ticker Extraction** — Groq identifies the relevant ticker (`ARKK`).
3. **Fund Holdings Lookup** — If it’s a mutual fund/ETF, we fetch its top holdings.
4. **News Scraping** — Recent articles from the web are scraped and parsed.
5. **Embedding + Search** — Articles are embedded and stored in **FAISS**. A similarity search retrieves the most relevant ones based on fund/company data.
6. **LLM Explanation** — The retrieved context is passed to an LLM to generate a concise explanation.

---

## 🖼 Example

> **🧾 Query**:  
> _"Why did QQQ drop this week?"_

> **🤖 NewsSense**:  
> _"QQQ, which holds major tech stocks like Apple, Amazon, and Microsoft, saw a decline largely due to a recent drop in Big Tech earnings and a hawkish Fed statement signaling rate hikes. The market reacted negatively to this macroeconomic signal."_
