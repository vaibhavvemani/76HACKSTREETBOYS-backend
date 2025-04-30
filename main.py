from flask import Flask, request, jsonify
from flask_cors import CORS
from rag.chat import financial_chain
# from rag.data_worker import retrieve_data
# from rag.news_corpus import search

app = Flask(__name__)
CORS(app)

@app.route('/retreive_data', methods=['POST'])
def retreive_data():

    query = request.form.get('query')
    reply = financial_chain.invoke({"question": query})
    return jsonify(reply["answer"])

# @app.route("/seach", methods=["POST"])
# def search():
#     ticker = request.form.get('ticker')
#     fund_data = retrieve_data(ticker)
#     return jsonify(fund_data)

# @app.route("/news", methods=["GET"])
# def news():
#     latest_news = search()
#     return jsonify(latest_news)
