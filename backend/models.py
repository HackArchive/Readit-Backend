from extensions import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class Todo(db.Model):
    
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(150),nullable=False)
    task = db.Column(db.Integer,db.ForeignKey('task.id'))
    is_completed = db.Column(db.Boolean,default=False)
    is_inprogress = db.Column(db.Boolean,default=False)


class Task(db.Model):

    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(120),nullable=False)
    todos = db.relationship('Todo',backref='task_todos')
    duration_to_complete_in_minutes = db.Column(db.Integer,nullable=False)
    started_on = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    is_canceled = db.Column(db.Boolean,default=False)
    is_completed = db.Column(db.Boolean,default=False)


class User(db.Model,UserMixin):

    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(50),nullable=False)
    email = db.Column(db.String(200),unique=True,nullable=False)
    phone_number = db.Column(db.String(16),nullable=True)
    password = db.Column(db.String(16),nullable=False)
    tasks = db.relationship('Task',backref='user_tasks')

    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    update_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())

