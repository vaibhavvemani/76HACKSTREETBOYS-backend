import os
import pickle
import numpy as np
import faiss
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_google_genai import GoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.docstore.document import Document

os.environ["GOOGLE_API_KEY"] = "AIzaSyBF-wxgd4Fm_3sTFcAL3u-WaZQh7aLzqAM"

EMBED_DIM = 768
INDEX_DIR = "news_index"
META_PATH = os.path.join(INDEX_DIR, "index.pkl")

llm = GoogleGenerativeAI(model="models/gemini-2.0-flash-thinking-exp")
embedding_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

# === Load or Create Vectorstore ===
def load_vectorstore():
    try:
        index_path = os.path.join(INDEX_DIR, "index.faiss")
        pickle_path = os.path.join(INDEX_DIR, "index.pkl")

        if os.path.exists(index_path) and os.path.exists(pickle_path):
            index = faiss.read_index(index_path)
            with open(pickle_path, "rb") as f:
                docstore, index_to_docstore_id = pickle.load(f)

            vectorstore = FAISS(
                embedding_function=embedding_model,
                index=index,
                docstore=docstore,
                index_to_docstore_id=index_to_docstore_id
            )

            if os.path.exists(META_PATH):
                with open(META_PATH, "rb") as f:
                    metadata = pickle.load(f)
            else:
                metadata = []

            print("📦 Loaded FAISS vectorstore and metadata")
            return vectorstore, metadata

        else:
            raise FileNotFoundError("FAISS index or pickle file not found.")

    except Exception as e:
        print(f"⚠️ Failed to load vectorstore: {e}")
        print("🆕 Creating a new empty vectorstore...")

        index = faiss.IndexFlatL2(EMBED_DIM)
        docstore = InMemoryDocstore()
        index_to_docstore_id = {}

        vectorstore = FAISS(
            embedding_function=embedding_model,
            index=index,
            docstore=docstore,
            index_to_docstore_id=index_to_docstore_id
        )

        return vectorstore, []

INDEX_DIR = "news_index"
META_PATH = os.path.join(INDEX_DIR, "news_metadata.pkl")

def save_vectorstore(vectorstore, metadata):
    os.makedirs(INDEX_DIR, exist_ok=True)

    # Save FAISS index
    faiss.write_index(vectorstore.index, os.path.join(INDEX_DIR, "index.faiss"))

    # Save FAISS internal docstore and index map
    with open(os.path.join(INDEX_DIR, "index.pkl"), "wb") as f:
        pickle.dump((vectorstore.docstore, vectorstore.index_to_docstore_id), f)

    # Save your additional metadata
    with open(META_PATH, "wb") as f:
        pickle.dump(metadata, f)

    print("💾 Saved vectorstore and metadata")

def process_articles(articles):
    vectorstore, metadata = load_vectorstore()
    existing_titles = {m["title"] for m in metadata}

    for article in articles:
        title = article.get("title")
        content = article.get("content")

        if not title or "⚠️" in content or not content.strip():
            continue
        if title in existing_titles:
            print(f"⏭️ Already processed: {title}")
            continue

        try:
            # Summarize with Gemini
            prompt = f"""The following article is a financial news piece. 
            Summarize it clearly while preserving the financial context, including company and ticker names.
            Be thorough with your summary, include all important details.
            Article: {content}
            Summary: """
            response = llm.invoke(prompt)
            summary = response.strip()
            print(f"🔍 Summarized: {summary}")

            doc = Document(page_content=summary, metadata={"title": title})

            vectorstore.add_documents([doc])
            print(f"Loaded vectorstore with {vectorstore.index.ntotal} entries")
            metadata.append({
                "title": title,
                "summary": summary
            })
            print(f"✅ Processed: {title}")

        except Exception as e:
            print(f"❌ Failed: {title} — {e}")

    save_vectorstore(vectorstore, metadata)
