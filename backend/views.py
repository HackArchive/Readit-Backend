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
