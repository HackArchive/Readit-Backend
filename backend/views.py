import json
import os
import schedule
from flask import Blueprint, request, make_response
from backend.auth import is_authenticated
from werkzeug.utils import secure_filename
from uuid import uuid1
from extensions import UPLOAD_FOLDER
from backend.models import Book,Chapter,User
from backend.serializers import ChapterSchema,BookSchema
from marshmallow.exceptions import ValidationError
from backend.utils import month_to_minutes,days_to_minutes,hours_to_minutes
from extensions import db
from backend.tasks import reminder_task,send_message
from ocr.reader import image_to_text

views = Blueprint("views",__name__)

@views.route('/',methods=['GET'])
@is_authenticated
def list_book_view(user):
    

    books = Book.query.filter_by(user_id=user.id).all()
    books_data = []
    for book in books:

        completed_chapters = len(Chapter.query.filter_by(book=book.id,is_completed=True).all())
        total_chapters = len(Chapter.query.filter_by(book=book.id).all())

        data = {
            "id":book.id,
            "title":book.title,
            "completed":f"{(completed_chapters/total_chapters)*100}%",
            "duration_in_min":book.duration_to_complete_in_minutes,
            "is_completed":book.is_completed,
            "is_canceled":book.is_canceled,
        }

        books_data.append(data)
    
    return make_response(books_data,200)




@views.route('/<pk>',methods=['GET'])
@is_authenticated
def show_book_view(user,pk):

    # does user created the book that is queried
    book = Book.query.filter_by(id=int(pk),user_id=user.id).first()

    if book == None:
        return make_response({"book":"book not found"},404)

    chapters = Chapter.query.filter_by(book=int(pk)).all()
        
    chapters_data = [
            {
                "id":chapter.id,
                "title": chapter.title,
                "is_completed":chapter.is_completed,
                "is_inprogress":chapter.is_inprogress     
            } for chapter in chapters
        ]

    return make_response(chapters_data,200)



@views.route('/add',methods=['POST'])
@is_authenticated
def add_book_view(user):

    images = request.files.getlist("images")  
    data = json.loads(request.form["data"])
    
    chapter_serializer = ChapterSchema()

    try:
        chapter_serializer.load({"title":data["title"]})
    except ValidationError as err:
        return make_response(err.messages,400)


    if len(images)==1 and images[0].content_type==None:
        return make_response({"images":"upload at least 1 image"},400)

    chapters_text = []
    for image in images:
        if image.content_type!=None:
            image_name = secure_filename(image.filename)
            image_name = str(uuid1()) + "_" + image_name
            image.save(os.path.join(UPLOAD_FOLDER,image_name))
            chapters_text += image_to_text(os.path.join(UPLOAD_FOLDER,image_name))

    if len(chapters_text)==0:
        return make_response({"chapters":"Cannot read index properly."},400)

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


    new_book = Book(
        title = data["title"],
        user_id = user.id,
        duration_to_complete_in_minutes = total_duration
    )

    db.session.add(new_book)
    db.session.commit()

    
    chapters_obj = []
    for chapter in chapters_text:
        new_chapter = Chapter(
            title = chapter,
            book = new_book.id
        )

        chapters_obj.append(new_chapter)
    
    db.session.add_all(chapters_obj)
    db.session.commit()

    # dividing chapters and scheduling book
    total_chapters = len(chapters_obj)
    total_minutes = total_duration

    schedule.every((total_minutes/total_chapters)*60).seconds.do(reminder_task,new_book.id,user.id)
    send_message(f"Awesome {user.name}! Making new goals and Achieving them makes you stronger.",user.phone_number.strip())

    return make_response({})


@views.route('/update_chapter/<pk>',methods=['POST'])
@is_authenticated
def update_chapter_view(user,pk):
    
    data = request.json

    chapter = Chapter.query.filter_by(id=int(pk)).first()
    
    if chapter==None:
        return make_response({"chapter":"does not exists"},404)
    
    chapter.is_completed = data["is_completed"]
    chapter.is_inprogress = data["is_inprogress"]


    db.session.add(chapter)
    db.session.commit()

    return make_response({},200)

@views.route('/update_book/<pk>',methods=['POST'])
@is_authenticated
def update_book_view(user,pk):
    
    data = request.json

    if data["is_canceled"] == data["is_completed"]:
        return make_response({"complete":"cannot cancel and complete at same time."},400)

    book = Book.query.filter_by(id=int(pk)).first()
    
    if book==None:
        return make_response({"book":"does not exists"},404)
    
    if data["is_canceled"]:
        book.is_canceled = data["is_canceled"]
        db.session.add(book)
        db.session.commit()
        return make_response({"Book":"canceled"},200)
    
    book_remaining = Chapter.query.filter_by(book=book.id,is_completed=False).first()
    if book_remaining:
        return make_response({"cannot complete":"chapters still pending"},400)

    book.is_completed = data["is_completed"]

    return make_response({},200)


@views.route('/profile/',methods=['GET'])
@is_authenticated
def user_profile_view(user):

    books_pending = len(Book.query.filter_by(is_canceled=False,is_completed=False).all())
    books_canceled = len(Book.query.filter_by(is_canceled=True,is_completed=False).all())
    books_completed = len(Book.query.filter_by(is_canceled=False,is_completed=True).all())

    profile_data = {
        "name":user.name,
        "email":user.email,
        "phone_number":user.phone_number,
        "books_pending":books_pending,
        "books_completed":books_completed,
        "books_canceled":books_canceled
    }
    
    return make_response(profile_data,200)
