import imaplib
import time
import email
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from mailer import Mailer
from mailer import Message

from icalendar import Calendar, Event
from datetime import datetime



imap_host = 'imap.gmail.com'
imap_user = ""
imap_pass = ""
config_file = "account.config" #Read this file for the username and password of email you are sending from

def create_calendar():
    cal = Calendar()
    cal.add('prodid', '-//My calendar product//mxm.dk//')
    cal.add('version', '2.0')

    event = Event()
    event.add('summary', 'Python meeting about calendaring')
    event.add('dtstart', datetime(2005, 4, 4, 8, 0, 0))
    event.add('dtend', datetime(2005, 4, 4, 10, 0, 0))
    event.add('dtstamp', datetime(2005, 4, 4, 0, 10, 0))
    event['uid'] = '20050115T101010/27346262376@mxm.dk'
    event.add('priority', 5)

    cal.add_component(event)

    f = open('example.ics', 'wb')
    f.write(cal.to_ical())
    f.close()

def read_calendar():
    g = open('test.ics', 'rb')
    gcal = Calendar.from_ical(g.read())
    for component in gcal.walk():
        if component.name == "VEVENT":
            print(component.get('summary'))
            start = component.get('dtstart')
            end = component.get('dtend')
            print(start.dt)
            print(end.dt)
    g.close()

def open_config():
    global imap_pass, imap_user
    file = open(config_file, 'r')
    imap_user = file.readline().rstrip() #read in username, get rid of trailing whitespaces and newlines
    imap_pass = file.readline().rstrip() #read in password

def parse_command(command, sender):
    if command.lower() == 'schedule':
        send_email(imap_user, imap_pass, sender, command, "Yo")


def send_email(user, pwd, recipient, subject, body):

    gmail_user = user
    gmail_pwd = pwd
    FROM = user
    TO = recipient if type(recipient) is list else [recipient]
    SUBJECT = subject
    TEXT = body

    message = Message(From=FROM,
                      To=TO)

    message.Subject = SUBJECT
    message.Html = """
                        <html>
                          <head></head>
                          <body>
                            <p>Hi! You've requested the UTNC practice schedule<br>
                               How are you?<br>
                               Here is the <a href="http://www.python.org">link</a> you wanted.
                            </p>
                          </body>
                        </html>
                        """

    sender = Mailer('smtp.gmail.com',port=587, use_tls=True, usr=gmail_user, pwd=gmail_pwd)
    sender.send(message)


def check_email():
    ## open a connection
    open_config()
    mail = imaplib.IMAP4_SSL(imap_host)

    ## login
    mail.login(imap_user, imap_pass)
    mail.select("inbox")
    ## get status for the mailbox (folder) INBOX
    n = 0
    (retcode, messages) = mail.search(None, '(UNSEEN)')
    print(retcode, messages)

    if retcode == 'OK':
        for num in messages[0].split():
            n = n + 1
            typ, data = mail.fetch(num, '(RFC822)')
            for response_part in data:
                if isinstance(response_part, tuple):
                    original = email.message_from_bytes(response_part[1])
                    print(original['From'])
                    print(original['Subject'])
                    parse_command(original['Subject'], original['From'])
                    #typ, data = mail.store(num, '+FLAGS', '\\UNSEEN')

#check_email()
#create_calendar()
read_calendar()