from logic import DB_Manager
from config import *
from telebot import TeleBot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telebot import types

bot = TeleBot(TOKEN)
hideBoard = types.ReplyKeyboardRemove()

cancel_button = "Cancel 🚫" 
def cancel(message):
    bot.send_message(message.chat.id, "Use /info to get commands list", reply_markup=hideBoard)
  
def no_tasks(message):
    bot.send_message(message.chat.id, "You don't have any tasks yet.\nUse /new_project to create one!")

def gen_inline_markup(rows):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    for row in rows:
        markup.add(InlineKeyboardButton(row, callback_data=row))
    return markup

def gen_markup(rows):
    markup = ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.row_width = 1
    for row in rows:
        markup.add(KeyboardButton(row))
    markup.add(KeyboardButton(cancel_button))
    return markup

attributes_of_projects = {"Task name" : ["Enter new task name", "task_name"],
                          "Status" : ["Select new task status", "status_id"]}

def info_task(message, user_id, task_name):
    info = manager.get_task_info(user_id, task_name)[0]
    bot.send_message(message.chat.id, f"Task name: {info[0]} Status: {info[1]}")

@bot.message_handler(commands=['start'])
def start_command(message):
    bot.send_message(message.chat.id, """Hi! I'm a task manager bot.
I'll help you save your tasks and their status!) 
""")
    info(message)
    
@bot.message_handler(commands=['info'])
def info(message):
    bot.send_message(message.chat.id,
"""
List of commands:

/new_task -> add a new task
/tasks -> list of tasks
/delete -> delete task""")
    

@bot.message_handler(commands=['new_task'])
def addtask_command(message):
    bot.send_message(message.chat.id, "Enter task name:")
    bot.register_next_step_handler(message, name_task)

def name_task(message):
    name = message.text
    user_id = message.from_user.id
    data = [user_id, name]
    statuses = [x[0] for x in manager.get_statuses()]
    bot.send_message(
        message.chat.id,
        "Select status:",
        reply_markup=gen_markup(statuses)
    )
    bot.register_next_step_handler(
        message,
        callback_task,
        data=data,
        statuses=statuses
    )

def callback_task(message, data, statuses):
    status = message.text
    if message.text == cancel_button:
        cancel(message)
        return
    if status not in statuses:
        bot.send_message(message.chat.id, "You have selected a status not from the list, please try again!", reply_markup=gen_markup(statuses))
        bot.register_next_step_handler(message, callback_task, data=data, statuses=statuses)
        return
    status_id = manager.get_status_id(status)
    data.append(status_id)
    manager.insert_task([tuple(data)])
    bot.send_message(message.chat.id, "The task has been saved successfully!")

@bot.message_handler(commands=['tasks'])
def get_tasks(message):
    user_id = message.from_user.id
    tasks = manager.get_tasks(user_id)
    if tasks:
        text = "\n".join([f"Task name:{x[2]}" for x in tasks])
        bot.send_message(message.chat.id, text, reply_markup=gen_inline_markup([x[2] for x in tasks]))
    else:
        no_tasks(message)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    task_name = call.data
    info_task(call.message, call.from_user.id, task_name)

@bot.message_handler(commands=['delete'])
def delete_handler(message):
    user_id = message.from_user.id
    tasks = manager.get_tasks(user_id)
    if tasks:
        text = "\n".join([f"Task name:{x[2]}" for x in tasks])
        tasks = [x[2] for x in tasks]
        bot.send_message(message.chat.id, text, reply_markup=gen_markup(tasks))
        bot.register_next_step_handler(message, delete_task, tasks=tasks)
    else:
        no_tasks(message)

def delete_task(message, tasks):
    task = message.text
    user_id = message.from_user.id

    if message.text == cancel_button:
        cancel(message)
        return
    if task not in tasks:
        bot.send_message(message.chat.id, "You don't have this task, please try select task again!", reply_markup=gen_markup(tasks))
        bot.register_next_step_handler(message, delete_task, tasks=tasks)
        return
    task_id = manager.get_task_id(task, user_id)
    manager.delete_task(user_id, task_id)
    bot.send_message(message.chat.id, f"Task {task} deleted!")


if __name__ == '__main__':
    manager = DB_Manager(DATABASE)
    bot.infinity_polling()    
