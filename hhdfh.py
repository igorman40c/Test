import os
import logging
import requests
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters


TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
API_URL = os.getenv('API_URL')


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(message)s',
    level=logging.INFO
)


def all_operations():
    response = requests.get(f"{API_URL}/all_operations")
    if response:
        operations = response.json()
        return "\n".join([f"{operation['id']}, {operation['consume']}, "
                          f"{operation['start_value']}, {operation['unit_measure']}, "
                          f"{operation['name_employee']}, {operation['position_employee']}, "
                          f"{operation['num_taken']}, {operation['reason']}, "
                          f"{operation['fin_value']}, {operation['data_val']}" for operation in operations])


def get_value_consumables():
    url = f"{API_URL}/get_value_consumables"
    response = requests.get(url)
    if response:
        operations = response.json()
        return "\n".join([f"{operation['consume']}, {operation['unit_measure']}, "
                          f"{operation['fin_value']}, {operation['data_val']}" for operation in operations])


def add_operation(
        consume, start_value, unit_measure, name_employee,
        position_employee, num_taken, reason, fin_value, data_val):
    response = requests.post(f"{API_URL}/add_operation", json={
        'consume': consume, 'start_value': start_value, 'unit_measure': unit_measure,
        'name_employee': name_employee, 'position_employee': position_employee, 'num_taken': num_taken,
        'reason': reason, 'fin_value': fin_value, 'data_val': data_val})
    return response


def update_operation(
        id, consume=None, start_value=None, unit_measure=None,
        name_employee=None, position_employee=None, num_taken=None,
        reason=None, fin_value=None, data_val=None):
    url = f"{API_URL}/update_operation/{id}"
    data = {}
    if consume:
        data['consume'] = consume
    if start_value:
        data['start_value'] = start_value
    if unit_measure:
        data['unit_measure'] = unit_measure
    if name_employee:
        data['name_employee'] = name_employee
    if position_employee:
        data['position_employee'] = position_employee
    if num_taken:
        data['num_taken'] = num_taken
    if reason:
        data['reason'] = reason
    if fin_value:
        data['fin_value'] = fin_value
    if data_val:
        data['data_val'] = data_val
    response = requests.put(url, json=data)
    return response


def delete_operation(id):
    url = f"{API_URL}/delete_operation/{id}"
    response = requests.delete(url)
    return response


async def start(update, context):
    await context.bot.send_message(chat_id=update.message.chat.id, text="Welcome to service about consumables")


async def handle_all_operations(update, context, args):
    message_body = all_operations()
    if message_body:
        await context.bot.send_message(chat_id=update.message.chat.id, text=message_body)
    else:
        await context.bot.send_message(chat_id=update.message.chat.id,
                                       text="Error, maybe database is empty")


async def handle_get_value_consumables(update, context, args):
    msg = get_value_consumables()
    if msg:
        await context.bot.send_message(chat_id=update.message.chat.id, text=msg)
    else:
        await context.bot.send_message(chat_id=update.message.chat.id,
                                       text="Error, maybe database is empty")


async def handle_add_operation(update, context, args):
    if len(args) == 9:
        (consume, start_value, unit_measure, name_employee, position_employee,
         num_taken, reason, fin_value, data_val) = args
        if add_operation(
                consume, start_value, unit_measure, name_employee,
                position_employee, num_taken, reason, fin_value, data_val):
            await context.bot.send_message(chat_id=update.message.chat.id, text="Operation added successfully")
        else:
            await context.bot.send_message(chat_id=update.message.chat.id, text="Error")
    else:
        await context.bot.send_message(chat_id=update.message.chat.id, text="Need more arguments for search")


async def handle_update_operation(update, context, args):
    if len(args) == 10:
        (id, consume, start_value, unit_measure, name_employee,
         position_employee, num_taken, reason, fin_value, data_val) = args
        if update_operation(
                id, consume, start_value, unit_measure, name_employee,
                position_employee, num_taken, reason, fin_value, data_val):
            await context.bot.send_message(chat_id=update.message.chat.id, text="Operation updated successfully")
        else:
            await context.bot.send_message(chat_id=update.message.chat.id, text="Error")
    else:
        await context.bot.send_message(chat_id=update.message.chat.id, text="Need more arguments for update")


async def handle_delete_operation(update, context, args):
    if len(args) == 1:
        id = args[0]
        if delete_operation(id):
            await context.bot.send_message(chat_id=update.message.chat.id, text="Operation deleted successfully")
        else:
            await context.bot.send_message(chat_id=update.message.chat.id, text="Error")


async def handle_request(update, context):
    text = update.message.text.lower().split(' ')
    command, args = text[0], text[1:]
    if command == '/all_operations':
        await handle_all_operations(update, context, args)
    elif command == '/get_value_consumables':
        await handle_get_value_consumables(update, context, args)
    elif command == '/add_operation':
        await handle_add_operation(update, context, args)
    elif command == '/update_operation':
        await handle_update_operation(update, context, args)
    elif command == '/delete_operation':
        await handle_delete_operation(update, context, args)
    else:
        await context.bot.send_message(chat_id=update.message.chat, text='Invalid command')


def main():
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)
    api_handler = MessageHandler(filters.TEXT, handle_request)
    application.add_handler(api_handler)
    application.run_polling()


if __name__ == '__main__':
    main()
