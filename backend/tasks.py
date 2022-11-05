import schedule
import time
from backend.models import Task,Todo,User
from extensions import twilio_client,twilio_number

def send_message(msg,phno):
    twilio_client.messages.create(
                              body=msg,
                              from_=f'whatsapp:{twilio_number}',
                              to=f'whatsapp:{phno.strip()}'
                          )


def reminder_task(task_id,user_id):

    print("starting reminder")

    user = User.query.filter_by(id=user_id).first()
    task = Task.query.filter_by(id=task_id).first()

    if (
        task==None or
        task.is_canceled == True or
        task.is_completed == True or
        user==None
        ):
        print("cancelling reminder.")
        return schedule.CancelJob

    user_phno = user.phone_number

    todos_pending = Todo.query.filter_by(task=task_id,is_inprogress=True).all()
    latest_todo = Todo.query.filter_by(task=task_id,is_completed=False).first()
    if len(todos_pending)!=0:
        # print(f"Dude get up you have {len(todos_pending)} task pending. You have to Complete {task.title}.")
        send_message(
                f"Dude get up you have {len(todos_pending)} task pending. You have to Complete {task.title}.",
                user_phno
            )

    elif latest_todo!=None:
        # print(f"Hey Reminder! You have to read {latest_todo.title}. Small efforts can make big Impacts.")
        send_message(
                f"Hey Reminder! You have to read {latest_todo.title}. Small efforts can make big Impacts.",
                user_phno
            )

    