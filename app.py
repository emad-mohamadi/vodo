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
    from llm import AI
    task_data = {
        "name": request.args.get('name'),
        "description": request.args.get('description'),
        "completed": False,
        "tags": [tag[1:] for tag in request.args.get('tags', '').split()],
        "expected_duration": (int(request.args.get('expected_hours'))) * 60 + int(request.args.get('expected_minutes')),
        "real_duration": request.args.get('real_duration'),
        "datetime": request.args.get('datetime'),
        "repeat": request.args.get('repeat'),
        "feedback": request.args.get('feedback'),
    }

    if not task_data["name"]:
        return jsonify({"result": False})

    # id = request.args.get('id')
    assistant = AI(id=1)
    task_data["tags"] = {
        "user": task_data["tags"],
        "assistant": assistant.get_tags(task_data=task_data)
    }
    data = DataBase()
    data.add_task(
        data=task_data,
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
        uuid=request.args.get('uuid'),
        check=(request.args.get('check') == 'true'),
        id=1
    )
    return jsonify({"result": request.args.get('check') == 'true'})
