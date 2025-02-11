from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route('/hello')
def hello():
    return jsonify({"result": "Hello"})


@app.route('/search')
def search():
    query = request.args.get('q')
    return jsonify({"result": f"You searched {query}"})


# if __name__ == '__main__':
#     app.run(debug=True)
