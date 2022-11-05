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

