from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route('/')
def welcome():
    return "Under development"


@app.route('/hello')
def hello():
    return jsonify({"result": "Hello"})


@app.route('/search')
def search():
    query = request.args.get('q')
    return jsonify({"result": f"You searched {query}"})


@app.route('/chat')
def llm_chat():
    from llm import AI
    query = request.args.get('q')
    assistant = AI(id='admin')
    response = assistant.chat(prompt=query)
    return jsonify({"result": response})


@app.route('/tasks/add')
def add_task():
    from logic import DataBase
    id = request.args.get('id')
    data = DataBase()
    data.add_task(
        {
            "name": request.args.get('name'),
            "description": request.args.get('description'),
            "completed": request.args.get('completed', False),
            "tags": request.args.get('tags', []),
            "expected_duration": request.args.get('expected_duration'),
            "real_duration": request.args.get('real_duration'),
            "date": request.args.get('date'),
            "repeat": request.args.get('repeat'),
            "feedback": request.args.get('feedback'),
        },
        user_id=1   # Default to user 1 for now
    )
    return jsonify({"result": True})


@app.route('/tasks/get')
def get_tasks():
    from logic import DataBase
    data = DataBase()
    user_id = int(request.args.get('user_id', 1))   # Default to user 1 for now
    ongoing_tasks, today_tasks, overdue_tasks = data.get_tasks(user_id)
    return jsonify({
        "ongoing_tasks": ongoing_tasks,
        "today_tasks": today_tasks,
        "overdue_tasks": overdue_tasks
    })


@app.route('/tasks/check')
def check_task():
    from logic import DataBase
    data = DataBase()
    data.check_task(
        index=int(request.args.get('i')),
        check=(request.args.get('check') == 'true'),
        id=1
    )
    return jsonify({"result": request.args.get('check') == 'true'})
