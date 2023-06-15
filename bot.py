# Рязанов И. - импорт необходимых библиотек для работы с телеграмм-ботом, объявление доступа к телеграмм-боту и сервису
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

# Мурзин И. - объявление состояний разговора для бота и создание 2-х кнопочных клавиатур
(FIRST_CHOOSE, SECOND_CHOOSE, TYPING1, TYPING2, TYPING2A, TYPING3, TYPING3A, TYPING4, TYPING4A, TYPING5, TYPING5A,
 TYPING6, TYPING6A, TYPING7, TYPING7A, TYPING8, TYPING8A, TYPING9, TYPING9A, OUTPUT1, OUTPUT2, OUTPUT3) = range(22)


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


args = []


# Уразаев А. - реализация функции вывода для пользователя всех операций с расходниками, имеющихся в базе данных
def all_operations():
    response = requests.get(f"{API_URL}/all_operations", timeout=7)
    if response:
        operations = response.json()
        return "\n".join([f"{operation['id']}, {operation['consume']}, "
                          f"{operation['start_volume']}, {operation['unit_measure']}, "
                          f"{operation['name_employee']}, {operation['position_employee']}, "
                          f"{operation['num_taken']}, {operation['reason']}, "
                          f"{operation['fin_volume']}, {operation['date_volume']}" for operation in operations])


# Уразаев А. - реализация функции получения всех операций с расходниками в базе данных по определенным категориям:
# # название расходника, единица его измерения, остаток на дату и сама дата
def get_volume_consumables():
    url = f"{API_URL}/get_volume_consumables"
    response = requests.get(url, timeout=7)
    if response:
        operations = response.json()
        return "\n".join([f"{operation['consume']}, {operation['unit_measure']}, "
                          f"{operation['fin_volume']}, {operation['date_volume']}" for operation in operations])


# Уразаев А. - реализация функции добавления новой операции с расходниками в базе данных,
# # где отдельно присваивается значение каждому ее признаку
def add_operation(
        consume, start_volume, unit_measure, name_employee,
        position_employee, num_taken, reason, fin_volume, date_volume):
    response = requests.post(f"{API_URL}/add_operation", json={
        'consume': consume, 'start_volume': start_volume, 'unit_measure': unit_measure,
        'name_employee': name_employee, 'position_employee': position_employee, 'num_taken': num_taken,
        'reason': reason, 'fin_volume': fin_volume, 'date_volume': date_volume})
    return response


# Федоренок Е. - реализация функции обновления (замены) характеристик операции с расходниками в базе данных
def update_operation(
        id, consume=None, start_volume=None, unit_measure=None,
        name_employee=None, position_employee=None, num_taken=None,
        reason=None, fin_volume=None, date_volume=None):
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
    if date_volume:
        data['date_volume'] = date_volume
    response = requests.put(url, json=data)
    return response


# Федоренок Е. - реализация функции удаления операции с расходниками в базе данных, а также условие запуска сервиса
def delete_operation(id):
    url = f"{API_URL}/delete_operation/{id}"
    response = requests.delete(url)
    return response


# Федоренок Е. - реализация функции начала работы с телеграмм-ботом
async def start(update, context):
    await context.bot.send_message(
        chat_id=update.message.chat.id,
        text="Hello! Welcome to service about operations with consumables. "
             "You can open the service or read an instruction about functions of service", reply_markup=markup
    )
    return FIRST_CHOOSE


# Федоренок Е. - реализация функции вызова инструкции работы с телеграмм-ботом
async def helping(update, context):
    await context.bot.send_message(
        chat_id=update.message.chat.id, text="Functions of service:\n"
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
        "If you want to continue working wih service, then you should activate button 'Open service' again.",
        reply_markup=markup
    )
    return FIRST_CHOOSE


# Пермякова Ю. - реализация функции возврата к главному меню телеграмм-бота: выбором между началом работы и инструкцией
async def returning(update, context):
    await context.bot.send_message(
        chat_id=update.message.chat.id,
        text="Hello again! You can open the service or read an instruction about functions of service",
        reply_markup=markup
    )
    return FIRST_CHOOSE


# Пермякова Ю. - реализация функции завершения работы телеграмм-бота (переносит к состоянию до команды /start)
async def finish(update, context):
    await context.bot.send_message(
        chat_id=update.message.chat.id, text="Thank you for using this service. Come back later!",
        reply_markup=ReplyKeyboardRemove()
    )
    args.clear()
    return ConversationHandler.END


# Пермякова Ю. - реализация функции перехода после начала работы к выбору необходимой для пользователя функции
async def working(update, context):
    await context.bot.send_message(
        chat_id=update.message.chat.id, text="Choose the most relevant function, which you want to activate:",
        reply_markup=markup1
    )
    return SECOND_CHOOSE


# Пермякова Ю. - реализация функции вывода для пользователя всех операций с расходниками, имеющихся в базе данных
async def handle_all_operations(update, context):
    message_body = all_operations()
    if message_body:
        await context.bot.send_message(
            chat_id=update.message.chat.id, text=message_body, reply_markup=markup1
        )
        return SECOND_CHOOSE
    else:
        await context.bot.send_message(
            chat_id=update.message.chat.id, text="Error, maybe database is empty", reply_markup=markup1
        )
        return SECOND_CHOOSE


# Пермякова Ю. - реализация функции получения всех операций с расходниками в базе данных по определенным категориям:
# # название расходника, единица его измерения, остаток на дату и сама дата
async def handle_get_volume_consumables(update, context):
    msg = get_volume_consumables()
    if msg:
        await context.bot.send_message(
            chat_id=update.message.chat.id, text=msg, reply_markup=markup1
        )
        return SECOND_CHOOSE
    else:
        await context.bot.send_message(
            chat_id=update.message.chat.id, text="Error, maybe database is empty", reply_markup=markup1
        )
        return SECOND_CHOOSE


# Рязанов И. - реализация функции записи в чат индекса операции (для обновления операции)
async def in_id_oper(update, context):
    await context.bot.send_message(
            chat_id=update.message.chat.id, text="Input id of operation:"
    )
    return TYPING1


# Рязанов И. - реализация функции записи в чат индекса операции (для удаления операции)
async def in_id_oper_del(update, context):
    await context.bot.send_message(
            chat_id=update.message.chat.id, text="Input id of operation:"
    )
    return OUTPUT3


# Рязанов И. - реализация функции записи в чат названия расходника и сохранения индекса (для обновления операции)
async def in_cons_oper(update, context):
    id = update.message.text
    args.append(int(id))
    await context.bot.send_message(
            chat_id=update.message.chat.id, text="Input name of consumable:"
    )
    return TYPING2


# Рязанов И. - реализация функции записи в чат названия расходника (для добавления операции)
async def in_cons_oper_add(update, context):
    await context.bot.send_message(
            chat_id=update.message.chat.id, text="Input name of consumable:"
    )
    return TYPING2A


# Рязанов И. - реализация функции записи в чат начального объема расходника на дату и
# сохранения названия (для обновления операции)
async def in_fst_vol_oper(update, context):
    consume = update.message.text
    args.append(consume)
    await context.bot.send_message(
            chat_id=update.message.chat.id, text="Input initial volume of consumable on date:"
    )
    return TYPING3


# Рязанов И. - реализация функции записи в чат начального объема расходника на дату и
# сохранения названия (для добавления операции)
async def in_fst_vol_oper_add(update, context):
    consume = update.message.text
    args.append(consume)
    await context.bot.send_message(
            chat_id=update.message.chat.id, text="Input initial volume of consumable on date:"
    )
    return TYPING3A


# Рязанов И. - реализация функции записи в чат единицы измерения расходника и сохранения
# начального объема (для обновления операции)
async def in_meas_oper(update, context):
    start_value = update.message.text
    args.append(int(start_value))
    await context.bot.send_message(
            chat_id=update.message.chat.id, text="Input unit of measure for consumable:"
    )
    return TYPING4


# Рязанов И. - реализация функции записи в чат единицы измерения расходника и сохранения
# начального объема (для добавления операции)
async def in_meas_oper_add(update, context):
    start_value = update.message.text
    args.append(int(start_value))
    await context.bot.send_message(
            chat_id=update.message.chat.id, text="Input unit of measure for consumable:"
    )
    return TYPING4A


# Уразаев А. - реализация функции записи в чат имени работника, взявшего расходник, и сохранения
# единицы измерения (для обновления операции)
async def in_fio_empl_oper(update, context):
    unit_measure = update.message.text
    args.append(unit_measure)
    await context.bot.send_message(
            chat_id=update.message.chat.id, text="Input name of employee for operation:"
    )
    return TYPING5


# Уразаев А. - реализация функции записи в чат имени работника, взявшего расходник, и сохранения
# единицы измерения (для добавления операции)
async def in_fio_empl_oper_add(update, context):
    unit_measure = update.message.text
    args.append(unit_measure)
    await context.bot.send_message(
            chat_id=update.message.chat.id, text="Input name of employee for operation:"
    )
    return TYPING5A


# Уразаев А. - реализация функции записи в чат должности работника, взявшего расходник, и сохранения
# имени сотрудника (для обновления операции)
async def in_pos_empl_oper(update, context):
    name_employee = update.message.text
    args.append(name_employee)
    await context.bot.send_message(
            chat_id=update.message.chat.id, text="Input position of employee for operation:"
    )
    return TYPING6


# Уразаев А. - реализация функции записи в чат должности работника, взявшего расходник, и сохранения
# имени сотрудника (для добавления операции)
async def in_pos_empl_oper_add(update, context):
    name_employee = update.message.text
    args.append(name_employee)
    await context.bot.send_message(
            chat_id=update.message.chat.id, text="Input position of employee for operation:"
    )
    return TYPING6A


# Уразаев А. - реализация функции записи в чат объема расходника, взятого работником, и сохранения
# должности сотрудника (для обновления операции)
async def in_n_taken_oper(update, context):
    position_employee = update.message.text
    args.append(position_employee)
    await context.bot.send_message(
            chat_id=update.message.chat.id, text="Input taken volume of consumable of operation:"
    )
    return TYPING7


# Уразаев А. - реализация функции записи в чат объема расходника, взятого работником, и сохранения
# должности сотрудника (для добавления операции)
async def in_n_taken_oper_add(update, context):
    position_employee = update.message.text
    args.append(position_employee)
    await context.bot.send_message(
            chat_id=update.message.chat.id, text="Input taken volume of consumable of operation:"
    )
    return TYPING7A


# Уразаев А. - реализация функции записи в чат причины взятия расходника и сохранения
# выбывшего объема расходника (для обновления операции)
async def in_reas_oper(update, context):
    num_taken = update.message.text
    args.append(int(num_taken))
    await context.bot.send_message(
            chat_id=update.message.chat.id, text="Input reason of operation:"
    )
    return TYPING8


# Уразаев А. - реализация функции записи в чат причины взятия расходника и сохранения
# выбывшего объема расходника (для добавления операции)
async def in_reas_oper_add(update, context):
    num_taken = update.message.text
    args.append(int(num_taken))
    await context.bot.send_message(
            chat_id=update.message.chat.id, text="Input reason of operation:"
    )
    return TYPING8A


# Федоренко Е. - реализация функции записи в чат остатка расходника на дату и сохранения
# причины взятия расходника (для обновления операции)
async def in_fin_vol_oper(update, context):
    reason = update.message.text
    args.append(reason)
    await context.bot.send_message(
            chat_id=update.message.chat.id, text="Input remaining volume of consumable on date:"
    )
    return TYPING9


# Федоренко Е. - реализация функции записи в чат остатка расходника на дату и сохранения
# причины взятия расходника (для добавления операции)
async def in_fin_vol_oper_add(update, context):
    reason = update.message.text
    args.append(reason)
    await context.bot.send_message(
            chat_id=update.message.chat.id, text="Input remaining volume of consumable on date:"
    )
    return TYPING9A


# Федоренко Е. - реализация функции записи в чат даты совершения операции с расходником и сохранения
# остатка расходника на дату (для обновления операции)
async def in_dt_vol_oper(update, context):
    fin_volume = update.message.text
    args.append(int(fin_volume))
    await context.bot.send_message(
            chat_id=update.message.chat.id, text="Input date of operation:"
    )
    return OUTPUT1


# Федоренко Е. - реализация функции записи в чат даты совершения операции с расходником и сохранения
# остатка расходника на дату (для добавления операции)
async def in_dt_vol_oper_add(update, context):
    fin_volume = update.message.text
    args.append(int(fin_volume))
    await context.bot.send_message(
            chat_id=update.message.chat.id, text="Input date of operation:"
    )
    return OUTPUT2


# Пермякова Ю. - реализация функции сохранения даты совершения операции с расходником и добавления новой
# операции с расходниками в базе данных, где отдельно присваивается значение каждому ее признаку
async def handle_add_operation(update, context):
    date_volume = update.message.text
    args.append(date_volume)
    (consume, start_value, unit_measure, name_employee, position_employee,
     num_taken, reason, fin_value, data_val) = args
    if add_operation(
            consume, start_value, unit_measure, name_employee, position_employee,
            num_taken, reason, fin_value, data_val):
        await context.bot.send_message(
            chat_id=update.message.chat.id, text="Operation added successfully, result was received! "
                                                 "What else do you want to do?", reply_markup=markup1
        )
        args.clear()
        return SECOND_CHOOSE
    else:
        await context.bot.send_message(chat_id=update.message.chat.id, text="Error", reply_markup=markup1)
        args.clear()
        return SECOND_CHOOSE


# Рязанов И. - реализация функции сохранения даты совершения операции с расходником и обновления
# (замены) характеристик операции с расходниками в базе данных
async def handle_update_operation(update, context):
    date_volume = update.message.text
    args.append(date_volume)
    (id, consume, start_value, unit_measure, name_employee, position_employee,
     num_taken, reason, fin_value, data_val) = args
    if update_operation(
            id, consume, start_value, unit_measure, name_employee, position_employee,
            num_taken, reason, fin_value, data_val):
        await context.bot.send_message(
            chat_id=update.message.chat.id, text="Operation updated successfully, result was received! "
                                                 "What else do you want to do?", reply_markup=markup1
        )
        args.clear()
        return SECOND_CHOOSE
    else:
        await context.bot.send_message(chat_id=update.message.chat.id, text="Error", reply_markup=markup1)
        args.clear()
        return SECOND_CHOOSE


# Уразаев А. - реализация функции сохранения индекса операции с расходником и удаления операции
# с расходниками в базе данных
async def handle_delete_operation(update, context):
    num = update.message.text
    args.append(int(num))
    id = args[0]
    if delete_operation(id):
        await context.bot.send_message(
            chat_id=update.message.chat.id, text="Operation deleted successfully, result was received! "
                                                 "What else do you want to do?", reply_markup=markup1
        )
        args.clear()
        return SECOND_CHOOSE
    else:
        await context.bot.send_message(chat_id=update.message.chat.id, text="Error", reply_markup=markup1)
        args.clear()
        return SECOND_CHOOSE


# Мурзин И. - реализация функции обработчиков сообщений от пользователя телеграмм-ботом:
# начало разговора, доступные состояния, в которые он может перейти, и условия его окончания
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
                MessageHandler(filters.Regex("^Add operation with consumables$"), in_cons_oper_add),
                MessageHandler(filters.Regex("^Update operation with consumables$"), in_id_oper),
                MessageHandler(filters.Regex("^Delete operation with consumables$"), in_id_oper_del),
                MessageHandler(filters.Regex("^Return to start$"), returning)
            ],
            TYPING1: [MessageHandler(filters.TEXT, in_cons_oper)],
            TYPING2: [MessageHandler(filters.TEXT, in_fst_vol_oper)],
            TYPING2A: [MessageHandler(filters.TEXT, in_fst_vol_oper_add)],
            TYPING3: [MessageHandler(filters.TEXT, in_meas_oper)],
            TYPING3A: [MessageHandler(filters.TEXT, in_meas_oper_add)],
            TYPING4: [MessageHandler(filters.TEXT, in_fio_empl_oper)],
            TYPING4A: [MessageHandler(filters.TEXT, in_fio_empl_oper_add)],
            TYPING5: [MessageHandler(filters.TEXT, in_pos_empl_oper)],
            TYPING5A: [MessageHandler(filters.TEXT, in_pos_empl_oper_add)],
            TYPING6: [MessageHandler(filters.TEXT, in_n_taken_oper)],
            TYPING6A: [MessageHandler(filters.TEXT, in_n_taken_oper_add)],
            TYPING7: [MessageHandler(filters.TEXT, in_reas_oper)],
            TYPING7A: [MessageHandler(filters.TEXT, in_reas_oper_add)],
            TYPING8: [MessageHandler(filters.TEXT, in_fin_vol_oper)],
            TYPING8A: [MessageHandler(filters.TEXT, in_fin_vol_oper_add)],
            TYPING9: [MessageHandler(filters.TEXT, in_dt_vol_oper)],
            TYPING9A: [MessageHandler(filters.TEXT, in_dt_vol_oper_add)],
            OUTPUT1: [MessageHandler(filters.TEXT, handle_update_operation)],
            OUTPUT2: [MessageHandler(filters.TEXT, handle_add_operation)],
            OUTPUT3: [MessageHandler(filters.TEXT, handle_delete_operation)]
        },
        fallbacks=[MessageHandler(filters.Regex("^Finish the session$"), finish)]
    )

    application.add_handler(conv_handler)
    application.run_polling()


if __name__ == '__main__':
    main()
