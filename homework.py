import logging
import os
import time

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(
    format='%(asctime)s, %(levelname)s, %(message)s, %(name)s'
)


PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')


def parse_homework_status(homework):
    homework_name = homework.get('homework_name')
    if homework_name is None:
        return 'Что-то пошло не так. Домашки нет!'
    homework_status = homework.get('status')
    if homework_status is None:
        return 'Что-то пошло не так. Статуса домашки нет!'
    if homework_status == 'rejected':
        verdict = 'К сожалению в работе нашлись ошибки.'
    elif homework_status == 'reviewing':
        verdict = 'Работа взята в ревью. Ждём результатов.'
        return f'У вас проверяют работу "{homework_name}"!\n\n{verdict}'
    else:
        verdict = ('Ревьюеру всё понравилось, '
                   'можно приступать к следующему уроку.')
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    if current_timestamp is None:
        current_timestamp = int(time.time())
    params = {
        'from_date': current_timestamp
    }
    headers = {
        'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'
    }
    url = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
    try:
        homework_statuses = requests.get(
            url=url,
            params=params,
            headers=headers
        )
    except requests.RequestException as e:
        logging.error(e, exc_info=True)
        return None
    return homework_statuses.json()


def send_message(message, bot_client):
    return bot_client.send_message(CHAT_ID, message)


def main():
    # проинициализировать бота здесь
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())  # начальное значение timestamp

    logging.debug('Бот запущен')
    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(
                    parse_homework_status(new_homework.get('homeworks')[0]),
                    bot
                )
                logging.info('Сообщение отправлено')
            current_timestamp = new_homework.get(
                'current_date',
                current_timestamp
            )  # обновить timestamp
            time.sleep(300)  # опрашивать раз в пять минут

        except Exception as e:
            logging.error(e, exc_info=True)
            send_message(str(e), bot)
            logging.info('Сообщение отправлено')
            time.sleep(5)


if __name__ == '__main__':
    main()
