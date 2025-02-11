from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route('/hello')
def hello():
    return jsonify({"result": "Hello"})


@app.route('/search')
def search():
    query = request.args.get('q')
    return jsonify({"result": f"You searched {query}"})


@app.route('/chat')
def llm_chat():
    from llm import chat
    query = request.args.get('q')
    return jsonify({"result": chat(query)})
