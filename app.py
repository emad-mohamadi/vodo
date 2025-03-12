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
    assistant = AI()
    response = assistant.chat(prompt=query)
    return jsonify({"history": response})


@app.route('/tasks/add')
def add_task():
    from logic import DataBase
    from llm import AI
    from uuid import uuid1
    task_data = {
        "uuid": uuid1().__str__(),
        "name": request.args.get('name'),
        "description": request.args.get('description'),
        "completed": False,
        "tags": [tag for tag in request.args.get('tags', '').split()],
        "expected_duration": (int(request.args.get('expected_hours', '0'))) * 60 + int(request.args.get('expected_minutes', '0')),
        "real_duration": None,
        "datetime": request.args.get('datetime'),
        "repeat": request.args.get('repeat'),
        "comment": None,
        "feedback": None,
        "color": request.args.get('color'),
    }

    if not task_data["name"]:
        return jsonify({"result": False})

    task_data_llm = f"""
                    Task: {task_data['name']}\n({task_data['description']})\nCurrent Tags:{task_data['tags']}\nExpected Duration: {task_data['expected_duration']} min\nDate and Time: {task_data['datetime']}\nRepeat:{task_data['repeat']}
    """

    assistant = AI(id=1, save=False)
    task_data["tags"] = {
        "user": task_data["tags"],
        "project": request.args.get('project'),
        "assistant": assistant.get_tags(task_data=task_data_llm),
    }
    data = DataBase()
    if task_data["tags"]["project"]:
        if task_data["tags"]["project"] == "null":
            task_data["tags"]["project"] = ""
        else:
            data.add_to_project(
                project_id=task_data["tags"]["project"],
                task_id=task_data["uuid"],
            )

    data.add_task(
        data=task_data,
        user_id=1
    )

    return jsonify({"result": True})


@app.route('/tasks/edit')
def edit_task():
    from logic import DataBase
    task_data = {
        "name": request.args.get('name'),
        "description": request.args.get('description'),
        "tags": {
            "user": request.args.get('tags', '').split(),
            "assistant": [],
            "project": request.args.get('project'),
        },
        "expected_duration": (int(request.args.get('expected_hours', '0'))) * 60 + int(request.args.get('expected_minutes', '0')),
        "datetime": request.args.get('datetime'),
        "repeat": request.args.get('repeat'),
    }

    if not task_data["name"]:
        return jsonify({"result": False})

    data = DataBase()
    data.edit_task(
        task_data,
        task_id=request.args.get('uuid'),
    )

    return jsonify({"result": True})


@app.route('/tasks/delete')
def delete_task():
    from logic import DataBase
    data = DataBase()
    data.delete_task(
        task_id=request.args.get('uuid'),
        project_id=request.args.get('project'),
    )

    return jsonify({"result": True})


@app.route('/tasks/check')
def check_task():
    from logic import DataBase
    data = DataBase()
    data.check_task(
        uuid=request.args.get('uuid'),
        check=(request.args.get('check') == 'true'),
    )
    return jsonify({"result": request.args.get('check') == 'true'})


@app.route('/tasks/feedback')
def get_feedback():
    from logic import DataBase

    task_id = request.args.get('uuid')
    if not task_id:
        return jsonify({"result": False})
    task_data = {
        "completed_at": request.args.get('completed_at'),
        "feedback": request.args.get('feedback'),
        "comment": request.args.get('comment'),
        "real_duration": int(request.args.get('duration', '0')),
    }

    data = DataBase()
    data.edit_task(
        data=task_data,
        task_id=task_id,
    )

    return jsonify({"result": True})


@app.route('/projects/add')
def add_project():
    from logic import DataBase
    from uuid import uuid1
    project_data = {
        "uuid": uuid1().__str__(),
        "name": request.args.get('name'),
        "description": request.args.get('description'),
        "completed": False,
        "deadline": request.args.get('deadline'),
        "tasks": [],
        "feedback": None,
        "color": request.args.get('color'),
    }

    if not project_data["name"]:
        return jsonify({"result": False})

    data = DataBase()
    data.add_project(
        data=project_data,
    )
    return jsonify({"result": True})

@app.route('/projects/edit')
def edit_project():
    from logic import DataBase
    project_id = request.args.get('uuid')
    project_data = {
        "name": request.args.get('name'),
        "description": request.args.get('description'),
        "deadline": request.args.get('deadline'),
    }

    if not project_data["name"]:
        return jsonify({"result": False})
    data = DataBase()
    data.edit_project(
        data=project_data,
        project_id=project_id,
    )
    return jsonify({"result": True})

@app.route('/projects/delete')
def delete_project():
    from logic import DataBase
    project_id = request.args.get('uuid')
    data = DataBase()
    data.delete_project(
        project_id=project_id,
        keep_tasks=(request.args.get('keep_tasks')=="true"),
    )
    return jsonify({"result": True})

@app.route('/tasks/get')
def get_tasks():
    from logic import DataBase
    data = DataBase()
    ongoing_tasks, today_tasks, overdue_tasks = data.get_tasks()
    return jsonify({
        "ongoing_tasks": ongoing_tasks,
        "today_tasks": today_tasks,
        "overdue_tasks": overdue_tasks
    })


@app.route('/projects/get')
def get_projects():
    from logic import DataBase
    data = DataBase()
    projects = data.get_projects()
    return jsonify({
        "projects": [
            {
                "name": "No project",
                "uuid": None,
                "color": "#000000",
            }
        ] + projects,
    })



@app.route('/ai/new-review')
def new_review():
    from logic import DataBase
    from llm import AI
    from datetime import datetime as dt
    data = DataBase()
    response = data.table("tasks").select("*").execute().data
    response.sort(key=lambda t: dt.strptime(t["datetime"], "%Y-%m-%dT%H:%M:%S.%f%z"))

    tasks_data = ""
    for taskinfo in response:
        name_str = f"{taskinfo['name']}"
        description_str = taskinfo['description'] if taskinfo['description'] else "No Description"
        datetime_str = f"{taskinfo['datetime']}"
        expected_duration_str = f"{taskinfo['expected_duration']}"
        repeat_str = f"{taskinfo['repeat']}"
        if not taskinfo['tags']['project']:
            project_str = "No Project"
        else:
            try:
                project_properties = data.table("projects").select("*").eq("uuid", taskinfo['tags']['project']).execute().data
                # print(taskinfo['tags']['project'])
                project_str = project_properties[0]["name"] + " (" + project_properties[0]["description"] + ")"
            except:
                project_str = project_properties[0]["name"]
        # project_str = taskinfo['tags']['project'] if taskinfo['tags']['project'] else "No Project"
        
        tags_str = ", ".join(taskinfo['tags']['user']) +", "+ ", ".join(taskinfo['tags']['assistant'])
        ifcompleted_str = "Yes" if taskinfo['completed'] else "No"
        completed_at_str = f"{taskinfo['completed_at']}"
        real_duration_str = f"{taskinfo['real_duration']}"
        comment_str = f"{taskinfo['comment']}"
        feedback_str = f"{taskinfo['feedback']}"
        tasks_data += 'Name: '+name_str+"\n"+"Description: "+description_str+"\n"+"Date and Time: "+datetime_str+"\n"+"Estimated Duration: "+expected_duration_str+" min"+"\n"+"Repeat: "+repeat_str+"\n"+"Project: "+project_str+"\n"+"Tags: "+tags_str+"\n"+"Done? "+ifcompleted_str
        if taskinfo['completed']:
            if completed_at_str:
                tasks_data += "\n"+"Completed at "+completed_at_str
            if real_duration_str:
                tasks_data += "\n"+"Real Duration: "+real_duration_str
            if feedback_str:
                tasks_data += "\n"+"Feedback: "+feedback_str
            if comment_str:
                tasks_data += "\n"+"User Comment: "+comment_str
        tasks_data += "\n\n"
    assistant = AI()
    review = assistant.get_review(tasks_data=tasks_data)
    
    # print(tasks_data)
    print(review)

new_review()
