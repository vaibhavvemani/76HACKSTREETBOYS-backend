from rag.data_worker import retrieve_data
from rag.embedder import load_vectorstore

from langchain_google_genai import GoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain.prompts import PromptTemplate
from langchain_community.vectorstores import FAISS
from langchain.schema.runnable import RunnablePassthrough

from typing import Dict, List, Any
import json
import os

os.environ["GOOGLE_API_KEY"] = "AIzaSyBF-wxgd4Fm_3sTFcAL3u-WaZQh7aLzqAM"

llm_model = GoogleGenerativeAI(model="gemini-2.0-flash")
embeddings = GoogleGenerativeAIEmbeddings(model="embedding-001")

vectorstore, metadata = load_vectorstore()
retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

ticker_prompt = PromptTemplate(
    input_variables=["question"],
    template="""
You are a helpful financial assistant.

Given the user question, extract the most relevant fund **ticker** or **sector name**.

Only return the ticker or sector name. Respond with only the value — no extra words or formatting.

Question: {question}
Ticker:
"""
)

# Debug print function
def debug_print(name, value):
    print(f"DEBUG - {name}: {value}")
    return value

# Process ticker to ensure it's just the symbol (no dictionary structure)
def process_ticker(llm_output):
    ticker = llm_output.strip()
    print(f"DEBUG - LLM returned ticker: '{ticker}'")
    return ticker

ticker_chain = ticker_prompt | llm_model | process_ticker

# Chain it all together with proper LangChain workflow - completely rewritten with debug prints
def fund_analysis_workflow():
    # First step: Extract question and get ticker
    def extract_ticker(input_dict):
        question = input_dict["question"]
        print(f"DEBUG - Received question: {question}")
        
        ticker = ticker_chain.invoke({"question": question})
        print(f"DEBUG - Extracted ticker: {ticker}")
        
        return {
            "question": question,
            "ticker": ticker
        }
    
    # Second step: Get fund data
    def get_fund_data(input_dict):
        question = input_dict["question"]
        ticker = input_dict["ticker"]
        print(f"DEBUG - Getting fund data for ticker: {ticker}")
        
        try:
            fund_data = retrieve_data(ticker)
            print(f"DEBUG - Retrieved fund data keys: {fund_data.keys() if isinstance(fund_data, dict) else 'not a dict'}")
        except Exception as e:
            print(f"DEBUG - Error retrieving fund data: {e}")
            fund_data = {"fund_prices": "N/A", "fund_holdings": "N/A", "fund_sectors": "N/A"}
        
        return {
            "question": question,
            "ticker": ticker,
            "fund_data": fund_data
        }
    
    # Third step: Get relevant documents
    def get_relevant_docs(input_dict):
        question = input_dict["question"]
        ticker = input_dict["ticker"]
        fund_data = input_dict["fund_data"]
        print(f"DEBUG - Getting relevant docs for question: {question}")
        
        try:
            # Enhance the search query with fund context
            sectors = fund_data.get('sectors', [])
            sectors_text = ' '.join(sectors) if isinstance(sectors, list) else ''
            search_text = f"{question} {sectors_text}"
            
            # Get relevant documents
            docs = retriever.get_relevant_documents(search_text)
            print(f"DEBUG - Retrieved {len(docs)} relevant documents")
            
            # Format the documents for better context
            formatted_docs = []
            for doc in docs:
                doc_dict = json.loads(doc.page_content) if isinstance(doc.page_content, str) and doc.page_content.startswith("{") else {"content": doc.page_content}
                # Add metadata if available
                if hasattr(doc, "metadata"):
                    doc_dict.update(doc.metadata)
                formatted_docs.append(doc_dict)
            
        except Exception as e:
            print(f"DEBUG - Error retrieving relevant docs: {e}")
            formatted_docs = [{"content": "No relevant documents found."}]
        
        return {
            "question": question,
            "ticker": ticker,
            "fund_data": fund_data,
            "relevant_docs": formatted_docs
        }
    
    # Fourth step: Generate answer
    def generate_answer(input_dict):
        print(f"DEBUG - Generating answer with keys: {input_dict.keys()}")
        
        response = answer_prompt.format(
            question=input_dict["question"],
            ticker=input_dict["ticker"],
            fund_data=input_dict["fund_data"],
            relevant_docs=input_dict["relevant_docs"]
        )
        
        # Pass to LLM
        answer = llm_model.invoke(response)
        print(f"DEBUG - Generated answer")
        
        return {"answer": answer}
    
    # Create the sequential workflow
    workflow = RunnableLambda(extract_ticker).pipe(
        RunnableLambda(get_fund_data)
    ).pipe(
        RunnableLambda(get_relevant_docs)
    ).pipe(
        RunnableLambda(generate_answer)
    )
    
    return workflow

# 4. Answer Generation Chain
answer_prompt = PromptTemplate(
    input_variables=["question", "ticker", "fund_data", "relevant_docs"],
    template="""You are a financial advisor assistant specialized in fund analysis.
    Answer the user's question using the provided fund data and relevant news articles.
    
    User Question: {question}
    
    Fund Ticker: {ticker}
    
    Fund Data:
    - Recent Prices: {fund_data[fund_prices]}
    - Top Holdings: {fund_data[fund_holdings]}
    - Sectors: {fund_data[fund_sectors]}
    
    Relevant News:
    {relevant_docs}
    
    Provide a comprehensive but concise answer with specific references to the data provided when applicable.
    Focus on directly answering the user's question with relevant information."""
)

# Create the workflow
financial_chain = fund_analysis_workflow()

# Example usage
# if __name__ == "__main__":
#     user_question = "What's the latest on QQQ fund?"
#     print("📦 Loaded FAISS vectorstore and metadata")
#     result = financial_chain.invoke({"question": user_question})
#     print("\n✅ Final Answer:\n", result["answer"])