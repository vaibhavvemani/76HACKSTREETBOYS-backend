🧠 NewsSense — Why Is My Fund Down?

NewsSense is an intelligent news-driven explanation engine that answers financial queries by analyzing real-time news scraped directly from the internet—without relying on any scraper APIs or news APIs. Designed for hackathons and finance enthusiasts, it helps users understand the causes behind mutual fund or stock fluctuations by tracing connections through company holdings and market events.

⸻

🚀 Features
	•	🔍 Query-Based Insight: Users ask questions like “Why is QQQ down today?” and get concise, news-based answers.
	•	🧠 LLM-Powered Ticker Detection: Fast and accurate ticker symbol extraction using Groq’s blazing fast inference engine.
	•	🗂️ Context-Aware RAG Pipeline: Built with LangChain, the system fetches fund holdings, searches relevant news, and returns contextual insights.
	•	🏛️ Holdings-Based Search: If the query is about a mutual fund, its underlying holdings are used to perform a deeper news correlation search.
	•	🌐 Pure Web Scraping: Web scraping is done without any news APIs—fully custom HTML parsing from live sources.
	•	🧩 Vector Database with FAISS: All relevant news is embedded and stored in a vector DB for high-speed semantic retrieval.

⸻

🧰 Tech Stack
	•	LangChain — Orchestrates the multi-step pipeline.
	•	Groq LLMs — Fast inference for ticker identification.
	•	FAISS — For storing and retrieving semantically similar news content.
	•	SQLite — Lightweight DB to store historical fund and holdings data.
	•	Custom Scrapers — Parses articles from the open web using raw HTML parsing.
	•	Gemini / OpenAI — Powers the summarization and explanation generation step.

⸻

🧠 How It Works
	1.	User Query: A user asks a question like “Why is ARKK falling?”
	2.	Ticker Extraction: The query is passed through Groq to extract the relevant ticker (e.g., ARKK).
	3.	Fund Holdings Lookup: If the ticker corresponds to a mutual fund or ETF, its holdings are retrieved from stored SQLite data.
	4.	News Scraping: Relevant financial articles are scraped from the web.
	5.	Embedding + Vector Search: Articles are embedded and stored in FAISS. The system performs a similarity search based on holdings and query context.
	6.	Answer Generation: An LLM summarizes the retrieved information into a human-readable explanation.

⸻

📸 Example

🧾 Query:
"Why did QQQ drop this week?"

🤖 NewsSense:
"QQQ, which holds major tech stocks like Apple, Amazon, and Microsoft, saw a decline largely due to a recent drop in Big Tech earnings and a hawkish Fed statement signaling rate hikes. The market reacted negatively to this macroeconomic signal."


⸻

📦 Setup Instructions
	1.	Clone the repo

git clone https://github.com/yourusername/newsense.git
cd newsense

	2.	Install dependencies

pip install -r requirements.txt

	3.	Run the app

python app.py

	4.	Environment Setup

Make sure to set up your .env file with necessary credentials (Groq API key, LLM provider API key, etc.).

⸻

🧪 Hackathon Highlights

This project was originally built for a finance-focused hackathon, targeting the theme of interpretability and explainability in investing. The idea was to empower casual and retail investors with quick, credible, and interpretable explanations sourced from publicly available news.

⸻

🧠 Future Improvements
	•	Add UI for inputting queries and visualizing fund data
	•	Scheduled scraping and automatic news updates
	•	Integration with official financial data APIs for validation (optional)
	•	More sophisticated sentiment + trend analysis

⸻

📜 License

This project is licensed under the MIT License.
