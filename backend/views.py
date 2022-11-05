import json
import os
import schedule
from flask import Blueprint, request, make_response
from backend.auth import is_authenticated
from werkzeug.utils import secure_filename
from uuid import uuid1
from extensions import UPLOAD_FOLDER
from backend.models import Task,Todo,User
from backend.serializers import TodoSchema,TaskSchema
from marshmallow.exceptions import ValidationError
from backend.utils import month_to_minutes,days_to_minutes,hours_to_minutes
from extensions import db
from backend.tasks import reminder_task
from ocr.reader import image_to_text

views = Blueprint("views",__name__)

@views.route('/',methods=['GET'])
@is_authenticated
def list_task_view(user):
    

    tasks = Task.query.filter_by(user_id=user.id).all()
    task_data = []
    for task in tasks:

        completed_todos = len(Todo.query.filter_by(task=task.id,is_completed=True).all())
        total_todos = len(Todo.query.filter_by(task=task.id).all())

        data = {
            "id":task.id,
            "title":task.title,
            "duration_in_min":task.duration_to_complete_in_minutes,
            "completed":f"{(completed_todos/total_todos)*100}%",
        }

        task_data.append(data)
    
    return make_response(task_data,200)




@views.route('/<pk>',methods=['GET'])
@is_authenticated
def show_task_view(user,pk):

    # does user created the task that is queried
    task = Task.query.filter_by(id=int(pk),user_id=user.id).first()

    if task == None:
        return make_response({"task":"Task not found"},404)

    todos = Todo.query.filter_by(task=int(pk))
    
    if todos.first()==None:
        return make_response({"task":"Task not found"},404)
    
    todos_data = []

    for todo in todos:

        data = {
            "id":todo.id,
            "title": todo.title,
            "is_completed":todo.is_completed,
            "is_inprogress":todo.is_inprogress            
        }

        todos_data.append(data)

    return make_response(todos_data,200)



@views.route('/add',methods=['POST'])
@is_authenticated
def add_todo_view(user):

    images = request.files.getlist("images")  
    data = json.loads(request.form["data"])
    
    todo_serializer = TodoSchema()
    task_serializer = TaskSchema()

    try:
        todo_serializer.load({"title":data["title"]})
    except ValidationError as err:
        return make_response(err.messages,400)


    if len(images)==1 and images[0].content_type==None:
        return make_response({"images":"upload at least 1 image"},400)

    todos_text = []
    for image in images:
        if image.content_type!=None:
            image_name = secure_filename(image.filename)
            image_name = str(uuid1()) + "_" + image_name
            image.save(os.path.join(UPLOAD_FOLDER,image_name))
            todos_text += image_to_text(os.path.join(UPLOAD_FOLDER,image_name))

    if len(todos_text)==0:
        return make_response({"Todos":"Cannot read index properly."},400)

    total_duration = 0
    if data["duration_type"]=="months":
        total_duration = month_to_minutes(data["duration"])
    elif data["duration_type"]=="days":
        total_duration = days_to_minutes(data["duration"])
    elif data["duration_type"]=="hours":
        total_duration = hours_to_minutes(data["duration"])
    elif data["duration_type"]=="minutes":
        total_duration = data["duration"]
    else:
        return make_response({"duration_type":"invalid duration type"})


    new_task = Task(
        title = data["title"],
        user_id = user.id,
        duration_to_complete_in_minutes = total_duration
    )

    db.session.add(new_task)
    db.session.commit()

    
    todos_obj = []
    for todo in todos_text:
        new_todo = Todo(
            title = todo,
            task = new_task.id
        )

        todos_obj.append(new_todo)
    
    db.session.add_all(todos_obj)
    db.session.commit()

    # dividing todos and scheduling task
    total_todos = len(todos_obj)
    total_minutes = total_duration

    schedule.every((total_minutes/total_todos)*60).seconds.do(reminder_task,new_task.id,user.id)

    return make_response({})


@views.route('/update_todo/<pk>',methods=['POST'])
@is_authenticated
def update_todo_view(user,pk):
    
    data = request.json

    todo = Todo.query.filter_by(id=int(pk)).first()
    
    if todo==None:
        return make_response({"todo":"does not exists"},404)
    
    todo.is_completed = data["is_completed"]
    todo.is_inprogress = data["is_inprogress"]


    db.session.add(todo)
    db.session.commit()

    return make_response({},200)

@views.route('/update_task/<pk>',methods=['POST'])
@is_authenticated
def update_task_view(user,pk):
    
    data = request.json
    if data["is_canceled"] == data["is_completed"]:
        return make_response({"complete":"cannot cancel and complete at same time."},400)

    task = Task.query.filter_by(id=int(pk)).first()
    
    if task==None:
        return make_response({"task":"does not exists"},404)
    
    if data["is_canceled"]:
        task.is_canceled = data["is_canceled"]
        db.session.add(task)
        db.session.commit()
        return make_response({"Task":"canceled"},200)
    
    todo_remaining = Todo.query.filter_by(task=task.id).first()
    if todo_remaining:
        return make_response({"cannot complete":"todos still pending"},400)

    task.is_completed = data["is_completed"]

    return make_response({},200)

