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
# def load_vectorstore():
#     if os.path.exists(os.path.join(INDEX_DIR, "index.faiss")) and os.path.exists(os.path.join(INDEX_DIR, "index.pkl")):
#         try:
#             # Check the pickle file before loading
#             with open(os.path.join(INDEX_DIR, "index.pkl"), "rb") as f:
#                 try:
#                     loaded_data = pickle.load(f)
#                     print(f"Loaded data type: {type(loaded_data)}")
#                     print(f"Loaded data content: {loaded_data if not isinstance(loaded_data, tuple) else f'Tuple of length {len(loaded_data)}'}")
                    
#                     # If the data isn't properly formatted, we'll create a new store
#                     if not isinstance(loaded_data, tuple) or len(loaded_data) != 2:
#                         raise ValueError("Pickle file does not contain expected data format")
#                 except Exception as e:
#                     print(f"Error checking pickle file: {e}")
#                     raise
            
#             # Now try to load the vectorstore
#             vectorstore = FAISS.load_local(
#                 folder_path=INDEX_DIR, 
#                 embeddings=embedding_model, 
#                 allow_dangerous_deserialization=True
#             )
            
#             # Load metadata if it exists
#             if os.path.exists(META_PATH):
#                 with open(META_PATH, "rb") as f:
#                     metadata = pickle.load(f)
#             else:
#                 metadata = []
                
#             print("📦 Loaded FAISS index + metadata")
#         except Exception as e:
#             print(f"Error loading existing index: {e}")
#             # Delete corrupted files
#             try:
#                 if os.path.exists(os.path.join(INDEX_DIR, "index.faiss")):
#                     os.remove(os.path.join(INDEX_DIR, "index.faiss"))
#                 if os.path.exists(os.path.join(INDEX_DIR, "index.pkl")):
#                     os.remove(os.path.join(INDEX_DIR, "index.pkl"))
#                 print("Deleted corrupted index files")
#             except Exception as delete_error:
#                 print(f"Error deleting corrupted files: {delete_error}")
                
#             # Create new vectorstore
#             index = faiss.IndexFlatL2(EMBED_DIM)
#             docstore = InMemoryDocstore()
#             index_to_docstore_id = {}
#             vectorstore = FAISS(
#                 embedding_function=embedding_model,
#                 index=index,
#                 docstore=docstore,
#                 index_to_docstore_id=index_to_docstore_id,
#             )
#             metadata = []
#             print("🆕 Created new FAISS store due to loading error")
#     else:
#         # Create new vectorstore
#         index = faiss.IndexFlatL2(EMBED_DIM)
#         docstore = InMemoryDocstore()
#         index_to_docstore_id = {}
#         vectorstore = FAISS(
#             embedding_function=embedding_model,
#             index=index,
#             docstore=docstore,
#             index_to_docstore_id=index_to_docstore_id,
#         )
#         metadata = []
#         print("🆕 Created new FAISS store (files didn't exist)")
    
#     return vectorstore, metadata


# Save the components individually
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
# def save_vectorstore(vectorstore, metadata):
#     # Create directory if it doesn't exist
#     os.makedirs(INDEX_DIR, exist_ok=True)
    
#     # Save the FAISS index file
#     faiss.write_index(vectorstore.index, os.path.join(INDEX_DIR, "index.faiss"))
    
#     # Print debug info before saving
#     print(f"Saving docstore type: {type(vectorstore.docstore)}")
#     print(f"Saving index_to_docstore_id type: {type(vectorstore.index_to_docstore_id)}")
    
#     # Save docstore and index_to_docstore_id as a tuple
#     with open(os.path.join(INDEX_DIR, "index.pkl"), "wb") as f:
#         data_to_save = (vectorstore.docstore, vectorstore.index_to_docstore_id)
#         pickle.dump(data_to_save, f)
        
#     # Verify the save worked correctly
#     with open(os.path.join(INDEX_DIR, "index.pkl"), "rb") as f:
#         loaded_data = pickle.load(f)
#         print(f"Verification - loaded data length: {len(loaded_data) if isinstance(loaded_data, tuple) else 'not a tuple'}")
    
#     # Save metadata separately
#     with open(META_PATH, "wb") as f:
#         pickle.dump(metadata, f)
    
#     print("💾 Saved vectorstore + metadata")

def process_articles(articles):
    vectorstore, metadata = load_vectorstore()
    existing_titles = {m["title"] for m in metadata}

    for article in articles:
        title = article.get("headline")
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
            Article: {content}
            Summary: """
            response = llm.invoke(prompt)
            summary = response.strip()

            # Create a LangChain document
            doc = Document(page_content=summary, metadata={"title": title})

            # Add to FAISS
            vectorstore.add_documents([doc])
            metadata.append({"title": title, "summary": summary})
            print(f"✅ Processed: {title}")

        except Exception as e:
            print(f"❌ Failed: {title} — {e}")

    save_vectorstore(vectorstore, metadata)
