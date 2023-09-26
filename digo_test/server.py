"""Сервер Telegram бота, запускаемый непосредственно"""
import logging
import os

import aiohttp
from aiogram import Bot, Dispatcher, executor, types

import exceptions
import expenses
import todos
import quiz
from categories import Categories
from middlewares import AccessMiddleware


logging.basicConfig(level=logging.INFO)

API_TOKEN = "5622719505:AAF5EWHGxI6dbkQqRu4JMwgNdIsoR6IuCTY"
ACCESS_ID = "5883625804"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(AccessMiddleware(ACCESS_ID))

def auth(func):

    async def wrapper(message):
        """if message['from']['id'] != 5883625804:
        retur await message.reply("Access Denied", reply=False)"""
        return await func(message)

    return wrapper

# @dp.message_handler(commands=['start', 'help'])
# @auth
# async def send_welcome(message: types.Message):
#     """Отправляет приветственное сообщение и помощь по боту,
#        запускает курс"""
#     await message.answer(
#         "Бот для учёта финансов\n\n"
#         "Добавить расход: 250 такси\n"
#         "Сегодняшняя статистика: /today\n"
#         "За текущий месяц: /month\n"
#         "Последние внесённые расходы: /expenses\n"
#         "Категории трат: /categories")

@bot.message_handler(commands=["start"])
@auth
async def start(message: types.Message):
    user = Users().get_all_users(message.chat.id)

	if user["is_passed"]:
		bot.send_message(message.from_user.id, "Вы уже прошли эту викторину")
		return

	if user["is_passing"]:
		return

	db.set_user(message.chat.id, {"question_index": 0, "is_passing": True})

	user = db.get_user(message.chat.id)
	post = get_question_message(user)
	if post is not None:
		bot.send_message(message.from_user.id, post["text"], reply_markup=post["keyboard"])


@bot.callback_query_handler(func=lambda query: query.data.startswith("?ans"))
def answered(query):
	user = db.get_user(query.message.chat.id)

	if user["is_passed"] or not user["is_passing"]:
		return

	user["answers"].append(int(query.data.split("&")[1]))
	db.set_user(query.message.chat.id, {"answers": user["answers"]})

	post = get_answered_message(user)
	if post is not None:
		bot.edit_message_text(post["text"], query.message.chat.id, query.message.id,
						 reply_markup=post["keyboard"])

@bot.callback_query_handler(func=lambda query: query.data == "?next")
def next(query):
	user = db.get_user(query.message.chat.id)

	if user["is_passed"] or not user["is_passing"]:
		return

	user["question_index"] += 1
	db.set_user(query.message.chat.id, {"question_index": user["question_index"]})

	post = get_question_message(user)
	if post is not None:
		bot.edit_message_text(post["text"], query.message.chat.id, query.message.id,
						 reply_markup=post["keyboard"])        


@dp.message_handler(lambda message: message.text.startswith('/del'))
@auth
async def del_expense(message: types.Message):
    """Удаляет одну запись о расходе по её идентификатору"""
    row_id = int(message.text[4:])
    expenses.delete_expense(row_id)
    answer_message = "Удалил"
    await message.answer(answer_message)


@dp.message_handler(commands=['categories'])
@auth
async def categories_list(message: types.Message):
    """Отправляет список категорий расходов"""
    categories = Categories().get_all_categories()
    answer_message = "Категории трат:\n\n* " +\
            ("\n* ".join([c.name+' ('+", ".join(c.aliases)+')' for c in categories]))
    await message.answer(answer_message)


@dp.message_handler(commands=['today'])
@auth
async def today_statistics(message: types.Message):
    """Отправляет сегодняшнюю статистику трат"""
    answer_message = expenses.get_today_statistics()
    await message.answer(answer_message)


@dp.message_handler(commands=['month'])
@auth
async def month_statistics(message: types.Message):
    """Отправляет статистику трат текущего месяца"""
    answer_message = expenses.get_month_statistics()
    await message.answer(answer_message)


@dp.message_handler(commands=['expenses'])
@auth
async def list_expenses(message: types.Message):
    """Отправляет последние несколько записей о расходах"""
    last_expenses = expenses.last()
    if not last_expenses:
        await message.answer("Расходы ещё не заведены")
        return

    last_expenses_rows = [
        f"{expense.amount} руб. на {expense.category_name} — нажми "
        f"/del{expense.id} для удаления"
        for expense in last_expenses]
    answer_message = "Последние сохранённые траты:\n\n* " + "\n\n* "\
            .join(last_expenses_rows)
    await message.answer(answer_message)


@dp.message_handler()
@auth
async def add_expense(message: types.Message):
    """Добавляет новый расход"""
    try:
        expense = expenses.add_expense(message.text)
    except exceptions.NotCorrectMessage as e:
        await message.answer(str(e))
        return
    answer_message = (
        f"Добавлены траты {expense.amount} е на {expense.category_name}.\n\n"
        f"{expenses.get_today_statistics()}")
    await message.answer(answer_message)

@dp.message_handler()
@auth
async def add_expense(message: types.Message):
    """Добавляет новый урок"""
    try:
        tutorial = expenses.add_expense(message.text)
    except exceptions.NotCorrectMessage as e:
        await message.answer(str(e))
        return
    answer_message = (
        f"Добавлены траты {expense.amount} е на {expense.category_name}.\n\n"
        f"{expenses.get_today_statistics()}")
    await message.answer(answer_message)




if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
