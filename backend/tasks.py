import schedule
import time
from backend.models import Book,Chapter,User
from extensions import twilio_client,twilio_number

def send_message(msg,phno):
    twilio_client.messages.create(
                              body=msg,
                              from_=f'whatsapp:{twilio_number}',
                              to=f'whatsapp:{phno.strip()}'
                          )


def reminder_task(book_id,user_id):

    print("starting reminder")

    user = User.query.filter_by(id=user_id).first()
    book = Book.query.filter_by(id=book_id).first()

    if (
        book==None or
        book.is_canceled == True or
        book.is_completed == True or
        user==None
        ):
        print("cancelling reminder.")
        return schedule.CancelJob

    user_phno = user.phone_number

    chapters_pending = Chapter.query.filter_by(book=book_id,is_inprogress=True).all()
    latest_chapter = Chapter.query.filter_by(book=book_id,is_completed=False).first()
    if len(chapters_pending)!=0:
        # print(f"Dude get up you have {len(todos_pending)} book pending. You have to Complete {book.title}.")
        send_message(
                f"Dude get up you have {len(chapters_pending)} book pending. You have to Complete {book.title}.",
                user_phno
            )

    elif latest_chapter!=None:
        # print(f"Hey Reminder! You have to read {latest_todo.title}. Small efforts can make big Impacts.")
        send_message(
                f"Hey Reminder! You have to read {latest_chapter.title}. Small efforts can make big Impacts.",
                user_phno
            )

    