from extensions import ma
from backend.models import User,Todo,Task


class UserSchema(ma.SQLAlchemySchema):
    
    class Meta:
        model = User
        fields = ("name","email","phone_number","password")

    name = ma.auto_field(required=True)
    email = ma.auto_field(required=True)
    phone_number = ma.auto_field(required=False)
    password = ma.auto_field(required=True)

class TaskSchema(ma.SQLAlchemySchema):

    class Meta:
        model = Task
        fields = ("title",)
    
    title = ma.auto_field(required=True)

class TodoSchema(ma.SQLAlchemySchema):

    class Meta:
        model = Todo
        fields = ("title",)
    
    title = ma.auto_field(required=True)
