import os
import logging
import requests
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, ConversationHandler, MessageHandler, filters


TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
API_URL = os.getenv('API_URL')


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(message)s',
    level=logging.INFO
)


(FIRST_CHOOSE, SECOND_CHOOSE, TYPING1, TYPING2, TYPING3, TYPING4, TYPING5, TYPING6, TYPING7,
 TYPING8, TYPING9, OUTPUT) = range(12)


reply_keyboard = [
    ["Open service", "Instruction"]
]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


reply_keyboard1 = [
    ["See all operations with consumables", "Get some info about consumables"],
    ["Add operation with consumables", "Update operation with consumables", "Delete operation with consumables"],
    ["Return to start", "Finish the session"]
]
markup1 = ReplyKeyboardMarkup(reply_keyboard1, one_time_keyboard=True)


def all_operations():
    response = requests.get(f"{API_URL}/all_operations")
    if response:
        operations = response.json()
        return "\n".join([f"{operation['id']}, {operation['consume']}, "
                          f"{operation['start_volume']}, {operation['unit_measure']}, "
                          f"{operation['name_employee']}, {operation['position_employee']}, "
                          f"{operation['num_taken']}, {operation['reason']}, "
                          f"{operation['fin_volume']}, {operation['data_volume']}" for operation in operations])


def get_volume_consumables():
    url = f"{API_URL}/get_volume_consumables"
    response = requests.get(url)
    if response:
        operations = response.json()
        return "\n".join([f"{operation['consume']}, {operation['unit_measure']}, "
                          f"{operation['fin_volume']}, {operation['data_volume']}" for operation in operations])


def add_operation(
        consume, start_volume, unit_measure, name_employee,
        position_employee, num_taken, reason, fin_volume, data_volume):
    response = requests.post(f"{API_URL}/add_operation", json={
        'consume': consume, 'start_volume': start_volume, 'unit_measure': unit_measure,
        'name_employee': name_employee, 'position_employee': position_employee, 'num_taken': num_taken,
        'reason': reason, 'fin_volume': fin_volume, 'data_volume': data_volume})
    return response


def update_operation(
        id, consume=None, start_volume=None, unit_measure=None,
        name_employee=None, position_employee=None, num_taken=None,
        reason=None, fin_volume=None, data_volume=None):
    url = f"{API_URL}/update_operation/{id}"
    data = {}
    if consume:
        data['consume'] = consume
    if start_volume:
        data['start_volume'] = start_volume
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
    if fin_volume:
        data['fin_volume'] = fin_volume
    if data_volume:
        data['data_volume'] = data_volume
    response = requests.put(url, json=data)
    return response


def delete_operation(id):
    url = f"{API_URL}/delete_operation/{id}"
    response = requests.delete(url)
    return response


async def start(update, context):
    await update.message.reply_text(
        "Hello! Welcome to service about operations with consumables. "
        "You can open the service or read an instruction about functions of service",
        reply_markup=markup
    )
    return FIRST_CHOOSE


async def helping(update, context):
    await update.message.reply_text(
        "Functions of service:\n"
        "1) See all operations with consumables - it allows to see all database: title of consumable; "
        "its initial volume on date; unit of its measure; name of employee, who took the consumable; "
        "position of employee; volume of consumable, taken by him; reason of employee's operation; "
        "remaining volume of consumable on date; date of operation.\n"
        "2) Get some info about consumables - it allows to see: title of consumable, unit of its measure, "
        "remaining volume of consumable on date, date of operation.\n"
        "3) Add operation with consumables - it allows to add operation with <name of consumable>, "
        "<initial volume on date>, <unit of measure>, <name of employee>, "
        "<position of employee>, <volume of taken consumables>, <reason of operation>, "
        "<remaining volume on date>, <date of operation>, which you input.\n"
        "4) Update operation with consumables - it allows to update details of operation with <id>, "
        "<name of consumable>, <initial volume on date>, <unit of measure>, <name of employee>, "
        "<position of employee>, <volume of taken consumables>, <reason of operation>, "
        "<remaining volume on date>, <date of operation>, which you input.\n"
        "5) Delete operation with consumables - it allows to delete operation with <id>, which you input.\n"
        "If you want to continue working wih service, then you should activate command '/start' again.",
        reply_markup=markup
    )
    return FIRST_CHOOSE


async def returning(update, context):
    await update.message.reply_text(
        "Hello again! You can open the service or read an instruction about functions of service",
        reply_markup=markup
    )
    return FIRST_CHOOSE


async def finish(update, context):
    await update.message.reply_text(
        "Thank you for using this service. Come back later!",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


async def working(update, context):
    await update.message.reply_text(
        "Choose the most relevant function, which you want to activate:",
        reply_markup=markup1
    )
    return SECOND_CHOOSE


async def handle_all_operations(update, context):
    message_body = all_operations()
    if message_body:
        await update.message.reply_text(message_body, "Result was received! What else do you want to do?",
                                        reply_markup=markup1)
        return SECOND_CHOOSE
    else:
        await update.message.reply_text("Error, maybe database is empty", reply_markup=markup1)
        return SECOND_CHOOSE


async def handle_get_volume_consumables(update, context):
    msg = get_volume_consumables()
    if msg:
        await update.message.reply_text(msg, "Result was received! What else do you want to do?",
                                        reply_markup=markup1)
        return SECOND_CHOOSE
    else:
        await update.message.reply_text("Error, maybe database is empty", reply_markup=markup1)
        return SECOND_CHOOSE


async def input_id_operation(update, context):
    await update.message.reply_text("Input id of operation:")
    return TYPING1


async def input_consumable_operation(update, context):
    await update.message.reply_text("Input name of consumable:")
    return TYPING2


async def input_start_volume_operation(update, context):
    await update.message.reply_text("Input initial volume of consumable on date:")
    return TYPING3


async def input_unit_measure_operation(update, context):
    await update.message.reply_text("Input unit of measure for consumable:")
    return TYPING4


async def input_name_employee_operation(update, context):
    await update.message.reply_text("Input name of employee for operation:")
    return TYPING5


async def input_position_employee_operation(update, context):
    await update.message.reply_text("Input position of employee for operation:")
    return TYPING6


async def input_num_taken_operation(update, context):
    await update.message.reply_text("Input taken volume of consumable of operation:")
    return TYPING7


async def input_reason_operation(update, context):
    await update.message.reply_text("Input reason of operation:")
    return TYPING8


async def input_fin_volume_operation(update, context):
    await update.message.reply_text("Input remaining volume of consumable on date:")
    return TYPING9


async def input_data_volume_operation(update, context):
    await update.message.reply_text("Input date of operation:")
    return OUTPUT


async def handle_add_operation(update, context):
    if add_operation(
            input_consumable_operation(), input_start_volume_operation(), input_unit_measure_operation(),
            input_name_employee_operation(), input_position_employee_operation(), input_num_taken_operation(),
            input_reason_operation(), input_fin_volume_operation(), input_data_volume_operation()):
        await update.message.reply_text("Operation added successfully, result was received! "
                                        "What else do you want to do?", reply_markup=markup1)
        return SECOND_CHOOSE
    else:
        await update.message.reply_text("Error", reply_markup=markup1)
        return SECOND_CHOOSE


async def handle_update_operation(update, context):
    if update_operation(
            input_id_operation(), input_consumable_operation(), input_start_volume_operation(),
            input_unit_measure_operation(), input_name_employee_operation(), input_position_employee_operation(),
            input_num_taken_operation(), input_reason_operation(), input_fin_volume_operation(),
            input_data_volume_operation()):
        await update.message.reply_text("Operation updated successfully, result was received! "
                                        "What else do you want to do?", reply_markup=markup1)
        return SECOND_CHOOSE
    else:
        await update.message.reply_text("Error", reply_markup=markup1)
        return SECOND_CHOOSE


async def handle_delete_operation(update, context):
    if delete_operation(input_id_operation()):
        await update.message.reply_text("Operation deleted successfully, result was received! "
                                        "What else do you want to do?", reply_markup=markup1)
        return SECOND_CHOOSE
    else:
        await update.message.reply_text("Error", reply_markup=markup1)
        return SECOND_CHOOSE


def main():
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            FIRST_CHOOSE: [
                MessageHandler(filters.Regex("^Open service$"), working),
                MessageHandler(filters.Regex("^Instruction$"), helping)
            ],
            SECOND_CHOOSE: [
                MessageHandler(filters.Regex("^See all operations with consumables$"), handle_all_operations),
                MessageHandler(filters.Regex("^Get some info about consumables$"), handle_get_volume_consumables),
                MessageHandler(filters.Regex("^Add operation with consumables$"), input_consumable_operation),
                MessageHandler(filters.Regex("^Update operation with consumables$"), input_id_operation),
                MessageHandler(filters.Regex("^Delete operation with consumables$"), input_id_operation),
                MessageHandler(filters.Regex("^Return to start$"), returning)
            ],
            TYPING1: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, input_consumable_operation),
            ],
            TYPING2: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, input_start_volume_operation),
            ],
            TYPING3: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, input_unit_measure_operation),
            ],
            TYPING4: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, input_name_employee_operation),
            ],
            TYPING5: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, input_position_employee_operation),
            ],
            TYPING6: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, input_num_taken_operation),
            ],
            TYPING7: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, input_reason_operation),
            ],
            TYPING8: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, input_fin_volume_operation),
            ],
            TYPING9: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, input_data_volume_operation),
            ],
            OUTPUT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_add_operation),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_update_operation),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_delete_operation)
            ]
        },
        fallbacks=[MessageHandler(filters.Regex("^Finish the session$"), finish)]
    )

    application.add_handler(conv_handler)
    application.run_polling()


if __name__ == '__main__':
    main()
