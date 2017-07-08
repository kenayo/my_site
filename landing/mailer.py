import sys
import os.path
import datetime
import smtplib
from email.mime.text import MIMEText


class Mailer:
    """Класс Mailer реализует отправку почты.

    Поля:
        Данные аккаунта для отправки сообщений:
        - self.it_email;
        - self.it_email_password;
        - self.it_email_smtp_server;
        - self.it_email_smtp_port;
        Данные для отправки сообщения:
        - self.client_name
        - self.client_email
        Прочее:
        - self.log_filename: имя файла для логгирования;
        - self.msg: письмо для отправки (email.mime.text).

    Методы:
      - self._log(): вывод события на экран и в лог-файл;
      - self.run(): отправка письма
    """

    def __init__(self, client_name, client_email):
        """Конструктор класса."""

        # кому отправляем письмо
        self.client_name = client_name
        self.client_email = client_email

        # аккаунт для отправки почты
        self.it_email = 'kenato.noreply@gmail.com'
        self.it_email_password = 'Neaera139'
        self.it_email_smtp_server = "smtp.gmail.com"
        self.it_email_smtp_port = 587

        # файлы с логами и сообщением
        app_path = os.path.abspath(os.path.dirname(sys.argv[0]))
        self.log_filename = os.path.join(app_path, "static/log.txt")
        self.msg_filename = os.path.join(app_path, "static/msg.txt")
        self.msg = ""


    def __str__(self):
        """Вернуть информацию о классе."""
        return "Mailer v 0.1"

    def _log(self, log_msg):
        """Записать в лог информацию об отправке сообщения
        """
        date = datetime.datetime.today()
        line = log_msg + ' ' + str(date)

        # вывод в консоль
        print(line)

        # вывод в log.txt
        with open(self.log_filename, "a", encoding="utf-8") as fh:
            fh.write("\n"+line)

    def run(self):
        """ Получить сообщение из заранее
        сгенерированного файла и отправить его
        """
        try:
            with open(self.msg_filename, "r", encoding="utf-8") as fh:
                text = fh.read()
            self.send_mail(text.format(self.client_name))
            log_msg = "Сообщение для {} успешно отправлено"\
                      .format(self.client_email)
            self._log(log_msg)
        except Exception as err:
            self._log("Произошла ошибка: " + str(err))

    def send_mail(self, text):
        """Отправить текст 'text' на почтовый адрес
        'self.client_email' для 'self.client_name'.
        """
        # 1. Формирование сообщения (MIMEText)
        self.msg = MIMEText(text)
        self.msg["Subject"] = 'Вы оставили свои контакты у меня тут'
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
