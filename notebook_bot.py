import telebot
import json
import re

notebook = []

API_TOKEN = ''
bot = telebot.TeleBot(API_TOKEN)

def load_file():
    with open('notebook.json', 'r', encoding = "utf-8") as nb:
        global notebook
        notebook = json.load(nb)

def send_succuss(message):
    bot.send_message(message.chat.id, 'Изменения успешно сохранены.')

def send_loaded_notebook(message):
    bot.send_message(message.chat.id, "Телефонный справочник был успешно загружен")



@bot.message_handler(commands=['start'])
def start_message(message):
    try:
        load_file()
        send_loaded_notebook(message)
    except:
        global notebook
        notebook = {
            "Петров Василий" : {'phone_numbers': [11111, 22222], 'date_of_birth': '10.10.2001', 'email': 'petrov@mail.ru'},
            "Иванов Сергей" : {'phone_numbers': [742454, 464878713212], 'date_of_birth': '09.12.1998', 'email': 'ivanovs@gmail.com'}
            }
        bot.send_message(message.chat.id, "Телефонный справочник был загружен по умолчанию")
    bot.send_message(message.chat.id, 'Используйте /help для получения инструкции по использованию')

@bot.message_handler(commands=['help'])
def show_instruction(message):
    bot.send_message(message.chat.id, f'/start - запуск справочника\n/show - просмотр всего справочника\n/add - добавление нового контакта\n/change - внесение изменений в имеющийся контакт\n/delete - удаление одного из контактов\n/save - сохранение справочника\n/load - загрузка справочника из файла\n/search - поиск контакта\n')

@bot.message_handler(commands=['show'])
def show_all(message):
    if notebook:
        bot.send_message(message.chat.id,"Все сохранённые контакты: ")
        for key, value in notebook.items():
            bot.send_message(message.chat.id, f'{key}: {value}')
    else:
        bot.send_message(message.chat.id, "Телефонный справочник пуст")

@bot.message_handler(commands=['add'])
def add_contact(message):
    ask_for_second_name(message)
def ask_for_second_name(message):
    bot.send_message(message.chat.id,"Введите фамилию: ")
    bot.register_next_step_handler(message, ask_for_first_name)
def ask_for_first_name(message):
    global second_name
    second_name = message.text
    bot.send_message(message.chat.id,"Введите имя: ")
    bot.register_next_step_handler(message, ask_for_patronymic_surname)
def ask_for_patronymic_surname(message):
    global first_name
    first_name = message.text
    bot.send_message(message.chat.id,"Введите отчество: ")
    bot.register_next_step_handler(message, ask_phone_number)
def ask_phone_number(message):
    global name
    patronymic_surname = message.text
    name = second_name + " " + first_name + " " + patronymic_surname
    notebook[name] = {'phone_numbers' : []}
    bot.send_message(message.chat.id, 'Пожалуйста, введите номер телефона контакта: ')
    bot.register_next_step_handler(message, ask_for_additional_num)
def ask_for_additional_num(message):
    notebook[name]['phone_numbers'].append(message.text)
    bot.send_message(message.chat.id, "Хотели бы вы внести ещё один номер телефона? Если да - ответьте 'да', если нет - ответьте 'нет' \n")
    bot.register_next_step_handler(message, add_additional_num)
def add_additional_num(message):
    if message.text.lower() == "да":
        bot.send_message(message.chat.id, 'Пожалуйста, введите номер телефона контакта: ')
        bot.register_next_step_handler(message, ask_for_additional_num)
    # elif message.text == "нет":
    #     bot.send_message(message.chat.id, 'Введите дату рождения контакта: ')
    #     bot.register_next_step_handler(message, add_date)
    else:
        bot.send_message(message.chat.id, 'Введите дату рождения контакта: ')
        bot.register_next_step_handler(message, add_date)

def add_date(message):
    notebook[name]['date_of_birth'] = message.text
    bot.send_message(message.chat.id, 'Введите электронную почту контакта: ')
    bot.register_next_step_handler(message, add_email)
def add_email(message):
    notebook[name]['email'] = message.text
    bot.send_message(message.chat.id, 'Контакт был успешно добавлен в записную книгу')

@bot.message_handler(commands=['change'])
def change(message):
    bot.send_message(message.chat.id, 'Введите ФИО контакта, который Вы хотели бы изменить: ')
    bot.register_next_step_handler(message, ask_for_name)
def ask_for_name(message):
    global name
    name = message.text
    try:
        notebook[name]
        bot.send_message(message.chat.id, 'Введите номер изменения, которое бы вы хотели внести:\n 1. Изменить имя контакта\n 2. Внести дополнительный номер телефона\n 3. Изменить имеющийся номер телефона\n 4. Удалить имеющийся номер телефона\n 5. Изменить дату рождения\n 6. Изменить email\n ')
        bot.register_next_step_handler(message, choose_change)
    except:
        bot.send_message(message.chat.id, 'К сожалению, контакт с таким именем отсутствует в справочнике. Возможно, в запросе присутствует опечатка.')
def choose_change(message):
    change = message.text
    if change == '1':
        bot.send_message(message.chat.id,"Введите новую фамилию: ")
        bot.register_next_step_handler(message, ask_to_change_first_name)
    elif change == '2':
        bot.send_message(message.chat.id, 'Пожалуйста, введите номер телефона контакта: ')
        bot.register_next_step_handler(message, ask_for_add_num)
    elif change == '3':
        bot.send_message(message.chat.id, 'Введите порядковый номер телефона, который Вы хотели бы изменить: ')
        if len(notebook[name]['phone_numbers']) > 1:
            numbers = list(enumerate(notebook[name]['phone_numbers'], 1))
            for i in numbers:
                j = i[0]
                k = i[1]
                bot.send_message(message.chat.id, f'{j}. {k}')
            bot.register_next_step_handler(message, ask_num_to_change)
        else:
            bot.send_message(message.chat.id, 'Введите новый номер телефона: ')
            num = int(1)
            bot.register_next_step_handler(message, change_num(num))
    elif change == '4':
        bot.send_message(message.chat.id, 'Введите порядковый номер телефона, который Вы хотели бы удалить: ')
        if len(notebook[name]['phone_numbers']) > 1:
            numbers = list(enumerate(notebook[name]['phone_numbers'], 1))
            for i in numbers:
                j = i[0]
                k = i[1]
                bot.send_message(message.chat.id, f'{j}. {k}')
            bot.register_next_step_handler(message, ask_num_to_del)
        else:
            del notebook[name]['phone_numbers'][0]
            send_succuss(message)
    elif change == '5':
        bot.send_message(message.chat.id, 'Введите новую дату рождения: ')
        bot.register_next_step_handler(message, change_date)
    elif change == '6':
        bot.send_message(message.chat.id, 'Введите электронную почту контакта: ')
        bot.register_next_step_handler(message, change_email)
    else:
        bot.send_message(message.chat.id, 'К сожалению, выбранный номер отсутствует в списке. Также, пожалуйста, убедитесь в отсутствии пробелов и знаков пунктуации при вводе номера')
def change_email(message):
    notebook[name]['email'] = message.text
    send_succuss(message)
def change_date(message):
    notebook[name]['date_of_birth'] = message.text
    send_succuss(message)
def ask_num_to_del(message):
    global num
    num = int(message.text)
    del notebook[name]['phone_numbers'][num - 1]
    send_succuss(message)
def ask_num_to_change(message):
    global num
    num = int(message.text)
    bot.send_message(message.chat.id, 'Введите новый номер телефона: ')
    bot.register_next_step_handler(message, change_num)
def change_num(message):
    notebook[name]['phone_numbers'][num - 1] = message.text
    send_succuss(message)
def ask_for_add_num(message):
    notebook[name]['phone_numbers'].append(message.text)
    bot.send_message(message.chat.id, "Хотели бы вы внести ещё один номер телефона? Если да - ответьте 'да', если нет - ответьте 'нет' \n")
    bot.register_next_step_handler(message, add_new_num)
def add_new_num(message):
    if message.text == "да":
        bot.send_message(message.chat.id, 'Пожалуйста, введите номер телефона контакта: ')
        bot.register_next_step_handler(message, ask_for_add_num)
    else:
        send_succuss(message)
def ask_to_change_first_name(message):
        global second_name
        second_name = message.text
        bot.send_message(message.chat.id,"Введите новое имя: ")
        bot.register_next_step_handler(message, ask_to_change_patronymic_surname)
def ask_to_change_patronymic_surname(message):
        global first_name
        first_name = message.text
        bot.send_message(message.chat.id,"Введите новое отчество: ")
        bot.register_next_step_handler(message, save_name)
def save_name(message):
        global name
        patronymic_surname = message.text
        new_name = second_name + " " + first_name + " " + patronymic_surname
        notebook[new_name] = notebook.pop(name)
        send_succuss(message)

@bot.message_handler(commands=['delete'])
def delete_contact(message):
    bot.send_message(message.chat.id, 'Введите ФИО контакта, который Вы хотели бы удалить: ')
    bot.register_next_step_handler(message, final_delete)
def final_delete(message):
    contact = message.text
    try:
        del notebook[contact]
        bot.send_message(message.chat.id, 'Контакт был успешно удалён из справочника.')
    except:
        bot.send_message(message.chat.id, 'К сожалению, контакт с таким именем отсутствует в справочнике. Возможно, в запросе присутствует опечатка.')

@bot.message_handler(commands=['search'])
def find_contact(message):
    bot.send_message(message.chat.id, 'Введите имя для поиска: ')
    bot.register_next_step_handler(message, find_one)
def find_one(message):
    contact = message.text
    count_all = 0
    count_in = 0
    for i in notebook.keys():
        if re.search(contact, i):
            bot.send_message(message.chat.id, f'{i} : {notebook[i]}')
            count_in += 1
        count_all += 1
        if count_all == len(notebook.keys()) and count_in == 0:
            bot.send_message(message.chat.id, 'К сожалению, контакт с таким именем отсутствует в справочнике. Возможно, в запросе присутствует опечатка.')

@bot.message_handler(commands=['save'])
def save_all(message):
    with open('notebook.json', 'w', encoding = "utf-8") as nb:
        nb.write(json.dumps(notebook, ensure_ascii = False))
    bot.send_message(message.chat.id, "Телефонный справочник был успешно сохранён")

@bot.message_handler(commands=['load'])
def load(message):
    try:
        load_file()
        send_loaded_notebook(message)
    except:
        global notebook
        notebook = {
            "Петров Василий" : {'phone_numbers': [11111, 22222], 'date_of_birth': '10.10.2001', 'email': 'petrov@mail.ru'},
            "Иванов Сергей" : {'phone_numbers': [742454, 464878713212], 'date_of_birth': '09.12.1998', 'email': 'ivanovs@gmail.com'}
            }
        bot.send_message(message.chat.id, "Телефонный справочник был загружен по умолчанию")

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    bot.send_message(message.chat.id, 'Неизвестная команда. Пожалуйста, прочтите инструкцию по использованию телефонного справочника, используя команду /help')

# @bot.message_handler(content_types=['text'])
# def get_text_messages(message):
#     if "дела" in message.text.lower():
#         bot.send_message(message.chat.id, "Дела у меня хорошо, сам как?")

bot.polling()