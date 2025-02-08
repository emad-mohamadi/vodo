from flask import Flask, jsonify

app = Flask(__name__)


@app.route('/hello')
def hello():
    return jsonify({"result": "Hello"})


if __name__ == '__main__':
    app.run(debug=True)
