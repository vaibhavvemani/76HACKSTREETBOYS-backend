from flask import Flask, request, jsonify
from flask_cors import CORS
from rag.chat import financial_chain

app = Flask(__name__)
CORS(app)

@app.route('/retreive_data', methods=['POST'])
def retreive_data():

    query = request.form.get('query')
    reply = financial_chain.invoke({"question": query})
    return jsonify(reply["answer"])

