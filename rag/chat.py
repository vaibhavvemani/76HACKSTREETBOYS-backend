from rag.data_worker import retrieve_data

from langchain_google_genai import GoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.runnables import RunnableLambda
from langchain.prompts import PromptTemplate
from langchain_community.vectorstores import FAISS
import faiss
import pickle
import json
import os

os.environ["GOOGLE_API_KEY"] = "AIzaSyBF-wxgd4Fm_3sTFcAL3u-WaZQh7aLzqAM"

llm_model = GoogleGenerativeAI(model="models/gemini-2.0-flash")

embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
index_dir = "rag/news_index"
def load_vectorstore():
    print(f"Loading vectorstore from: {os.path.abspath(index_dir)}")
    
    index_path = os.path.join(index_dir, "index.faiss")
    pickle_path = os.path.join(index_dir, "index.pkl")
    metadata_path = os.path.join(index_dir, "news_metadata.pkl")
    
    print(f"Checking index file: {index_path} (exists: {os.path.exists(index_path)})")
    print(f"Checking pickle file: {pickle_path} (exists: {os.path.exists(pickle_path)})")
    
    try:
        if os.path.exists(index_path) and os.path.exists(pickle_path):
            index = faiss.read_index(index_path)
            print(f"FAISS index loaded with {index.ntotal} entries")
            
            with open(pickle_path, "rb") as f:
                docstore, index_to_docstore_id = pickle.load(f)
            
            vectorstore = FAISS(
                embedding_function=embeddings,
                index=index,
                docstore=docstore,
                index_to_docstore_id=index_to_docstore_id
            )
            
            metadata = []
            if os.path.exists(metadata_path):
                with open(metadata_path, "rb") as f:
                    metadata = pickle.load(f)
                    print(f"Metadata loaded with {len(metadata)} entries")
            
            return vectorstore, metadata
        else:
            raise FileNotFoundError(f"Required index files not found in {index_dir}")
            
    except Exception as e:
        print(f"Error loading vectorstore: {str(e)}")
        import traceback
        traceback.print_exc()
        raise
vectorstore, metadata = load_vectorstore()
def inspect_vectorstore(vs):
    try:
        print(f"DEBUG - Vectorstore type: {type(vs)}")
        if hasattr(vs, "index"):
            print(f"DEBUG - Index size: {vs.index.ntotal}")
            
        # For document inspection, try to get a sample
        sample_query = "fund"
        sample_docs = vs.similarity_search(sample_query, k=2)
        print(f"DEBUG - Sample query '{sample_query}' returned {len(sample_docs)} docs")
        if sample_docs:
            print(f"DEBUG - Sample doc: {sample_docs[0].page_content[:100]}...")
    except Exception as e:
        print(f"DEBUG - Error inspecting vectorstore: {e}")

inspect_vectorstore(vectorstore)

retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 5, "fetch_k": 10,}
    
)

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

def debug_print(name, value):
    print(f"DEBUG - {name}: {value}")
    return value

def process_ticker(llm_output):
    ticker = llm_output.strip()
    print(f"DEBUG - LLM returned ticker: '{ticker}'")
    return ticker

ticker_chain = ticker_prompt | llm_model | process_ticker

def fund_analysis_workflow():
    def extract_ticker(input_dict):
        question = input_dict["question"]
        print(f"DEBUG - Received question: {question}")
        
        ticker = ticker_chain.invoke({"question": question})
        print(f"DEBUG - Extracted ticker: {ticker}")
        
        return {
            "question": question,
            "ticker": ticker
        }
    
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
    
    def get_relevant_docs(input_dict):
        question = input_dict["question"]
        ticker = input_dict["ticker"]
        fund_data = input_dict["fund_data"]
        print(f"DEBUG - Getting relevant docs for question: {question}")
        
        try:
            search_text = question 
            sectors = fund_data.get('sectors', [])
            sectors_text = ' '.join(sectors) if isinstance(sectors, list) else ''
            
            docs = retriever.get_relevant_documents(search_text)
            if len(docs) < 2:
                print(f"DEBUG - Few results, trying search with ticker: {ticker}")
                docs = retriever.get_relevant_documents(f"{ticker} {question}")
                
            if len(docs) < 2 and sectors_text:
                print(f"DEBUG - Still few results, trying with sectors: {sectors_text}")
                docs = retriever.get_relevant_documents(sectors_text)
            print(f"DEBUG - Retrieved {len(docs)} relevant documents")
            
            formatted_docs = []
            for doc in docs:
                try:
                    if isinstance(doc.page_content, str) and doc.page_content.strip().startswith("{"):
                        doc_dict = json.loads(doc.page_content)
                    else:
                        doc_dict = {"content": doc.page_content}
                        
                    print(f"DEBUG - Doc content preview: {doc.page_content[:100]}...")
                        
                    if hasattr(doc, "metadata"):
                        doc_dict.update(doc.metadata)
                    formatted_docs.append(doc_dict)
                except Exception as e:
                    print(f"DEBUG - Error parsing document: {e}")
                    formatted_docs.append({"content": doc.page_content})
            
        except Exception as e:
            print(f"DEBUG - Error retrieving relevant docs: {e}")
            formatted_docs = [{"content": "No relevant documents found."}]
        
        return {
            "question": question,
            "ticker": ticker,
            "fund_data": fund_data,
            "relevant_docs": formatted_docs
        }
    
    def generate_answer(input_dict):
        print(f"DEBUG - Generating answer with keys: {input_dict.keys()}")
        
        response = answer_prompt.format(
            question=input_dict["question"],
            ticker=input_dict["ticker"],
            fund_data=input_dict["fund_data"],
            relevant_docs=input_dict["relevant_docs"]
        )
        
        answer = llm_model.invoke(response)
        print(f"DEBUG - Generated answer")
        
        return {"answer": answer}
    
    workflow = RunnableLambda(extract_ticker).pipe(
        RunnableLambda(get_fund_data)
    ).pipe(
        RunnableLambda(get_relevant_docs)
    ).pipe(
        RunnableLambda(generate_answer)
    )
    
    return workflow

answer_prompt = PromptTemplate(
    input_variables=["question", "ticker", "fund_data", "relevant_docs"],
    template="""
    You are a financial advisor assistant specialized in fund analysis.
    Given the user question, fund ticker, fund data, and relavant news articles, provide a comprehensive analysis.
    Your response should be clear, concise, and actionable. Render key points in bold.

    Here is the data:

    User Question: {question}   

    Fund Ticker: {ticker}

    Fund Data:
    - Recent Prices: {fund_data[fund_prices]}
    - Top Holdings: {fund_data[fund_holdings]}
    - Sectors: {fund_data[fund_sectors]}

    Relevant News:
    {relevant_docs}

    Respond in the following format:
    (render this in bold)News Analysis:
    - Analyse how the news affects the fund/sector, reason over the users provided data
    - Mention whether the effects are positive or negative and why
    - Summarize all articles provided and give a short consise and clear answer in a maximum of 4 sentences

    Relevant Stock Price (if provided):
    - List percentage of change in the stock price
    - if not provided, don't mention this section

    Relevant Holdings (if provided):
    - Mention any top holdings directly affected by the news or the user’s question
    - if not provided, don't mention this section

    Relevant Sectors (if provided):
    - Include sectors that are sensitive to or impacted by the issue in the question
    - if not provided, don't mention this section

    (render in bold)Suggestions:
    - Share investment guidance, like which sectors look strong or whether to stay cautious
    - Keep it actionable and relevant to the user's question
    - Your suggestions can be your own answers feel free to use the data provided or take your own data.
    - Keep your suggestions short and concise, no more than 2 sentences
    """
)
financial_chain = fund_analysis_workflow()
