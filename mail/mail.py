import sys
import os.path
import re
import datetime
import time
import smtplib
from email.mime.text import MIMEText
import requests


NO_DATA = "Нет данных"


class Mail:
    """Класс CurrencyChecker реализует отправку почты.

    Поля:
        Данные ИТ-аккаунта (прописаны в коде)
        - self.it_email: e-mail ИТ-отдела;
        - self.it_email_password: пароль от e-mail ИТ-отдела;
        - self.it_email_smtp_server: SMTP-сервер для e-mail ИТ-отдела;
        - self.it_email_smtp_port: SMTP-порт для e-mail сервера ИТ-отдела;
        Данные руководителя
        - self.client_name: ФИО руководителя;
        - self.client_email: e-mail руководителя.
        Прочее
        - self.log_filename: имя файла для логгирования;
        - self.msg: письмо для отправки (email.mime.text).

    Методы:
      - self._log(): вывод события на экран и в лог-файл;
      - self.run(): бесконечный цикл работы - получение данных и их отправка;
      - self.get_info(): получение котировок с сайта;
      - self._create_message(): формирование текста сообщения для отправки.
    """

    def __init__(self, client_name, client_email):
        """Конструктор класса."""
        # клиент
        self.client_name = client_name
        self.client_email = client_email

        # ит акк
        self.it_email = 'gravewormed@gmail.com'
        self.it_email_password = 'wnqf5ee1'
        self.it_email_smtp_server = "smtp.gmail.com"
        self.it_email_smtp_port = 587

        # хардкодим лог файл
        app_path = os.path.abspath(os.path.dirname(sys.argv[0]))
        self.log_filename = os.path.join(app_path, "log.txt")
        self.msg = ""

    def __str__(self):
        """Вернуть информацию о классе."""
        return "CurrencyChecker v 0.1"

    def _log(self, message):
        """Вывести на экран 'message' с указанием текущего времени
        формате 0001-01-01 00:00:00 (год, месяц, число, часы, минуты, секунды):
          - на экран;
          - в лог-файл (дописать в конец файла).
        """
        date = datetime.datetime.today()
        line = "{date} | {message}".format(
            date=date.strftime("%Y-%m-%d %X"),
            message=message)

        # вывод в консоль
        print(line)

        # вывод в log.txt
        with open(self.log_filename, "a", encoding="utf-8") as fh:
            fh.write("\n"+line)

    def run(self, timeout, currencies):
        """Каждые 'timeout секунд':
        - запросить информацию о курсах;
        - отправить их на почту.
        """
        while True:
            try:
                info = self.get_info(currencies)
                self._log("Данные получены: " + str(sorted(info.items())))

                text = self._create_message(info)
                self.send_mail(text)
                self._log("Письмо успешно отправлено!")
            except Exception as err:
                self._log("Произошла ошибка: " + str(err))
            finally:
                time.sleep(timeout)

    @staticmethod
    def get_info(currencies):
        """Вернуть курсы валют.

        Источник: http://www.finanz.ru/valyuty/v-realnom-vremeni-rub.

        Параметры:
            - currencies: список валют, например: ['USD', 'EUR'].

        Результат:
            - словарь вида {
                              'USD': (20, "10:23:00"),
                              'EUR': (30, "10:23:00")
                            }
                , где значение (кортеж) содержит:
                  - значение покупки (3-й столбец);
                  - дату получения значения с биржи (последний столбец).

              Если валюта из 'currencies' или какое-либо значение не найдено,
              валюта добавляется в словарь со значением "Не известно".
        """

        def _value_to_float(value):
            """Вернуть 'value' как вещественное число (если возможно)
            или вернуть 'NO_DATA'."""
            try:
                return float(value.replace(',', '.'))
            except ValueError:
                return NO_DATA

        # 1. По умолчанию о каждой валюте ничего не известно
        res = dict()
        for currence in currencies:
            res[currence] = tuple()

        # 2. Поиск информации о валютах
        # . не захватывает переносы строки по умолчанию, поэтому при создании
        # regex-объекта необходимо указать флаг re.DOTALL
        r = requests.get("http://www.finanz.ru/valyuty/v-realnom-vremeni-rub")

        for currence in res:
            reg_ex = \
                r"title=\"" + \
                "(?:{name}\/RUB)".format(name=currence) + \
                r"(?:(?:.+\n){3}.+>)" + \
                r"(?P<value>\d+,\d+)" + \
                r"(?:(?:.+\n){3}.+>)" + \
                r"(?P<time>\d+:\d+:\d+)"

            match = re.search(reg_ex, r.text)
            if match:
                match_dict = match.groupdict()
                res[currence] = (
                    _value_to_float(match_dict["value"]),
                    match_dict["time"])
            else:
                res[currence] = (NO_DATA, NO_DATA)

        return res

    def _create_message(self, info):
        """Составить и вернуть текст письма.

        Параметры:
          - info: словарь из self.get_info().

        Результат:
          - текст письма (str).
        """

        res = """\
{ceo_name}!

Обновленные курсы валют:
{info_str}

С уважением, ИТ-отдел.\
"""
        info_str = "\n"
        pattern_str = "  - {name}: {value} ({time})\n"
        for key, value in sorted(info.items()):
            info_str += pattern_str.format(
                name=key,
                value=value[0],
                time=value[1])

        return res.format(
            ceo_name=self.client_name,
            info_str=info_str[:-1])

    def send_mail(self, text):
        """Отправить текст 'text' на почтовый адрес
        'self.ceo_email' для 'self.ceo_name'.
        """
        # 1. Формирование сообщения (MIMEText)
        self.msg = MIMEText(text)
        data = datetime.datetime.today()
        self.msg["Subject"] = "Курсы валют на {date}".format(
            date=data.strftime("%Y-%d-%m %X"))
        self.msg["From"] = self.it_email
        self.msg["To"] = self.client_email

        # 2. Подклюение к серверу и отправка письма
        server = smtplib.SMTP(
            self.it_email_smtp_server,
            self.it_email_smtp_port)
        try:
            server.starttls()
            server.login(self.it_email, self.it_email_password)
            server.send_message(self.msg)
        except Exception:
            raise
        finally:
            server.quit()
