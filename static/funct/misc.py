# Miscellaneous functions

import datetime
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import Encoders


def emailResults(userEmail, body):
    msg = MIMEMultipart()
    msg['Subject'] = 'TwitterMining Results'
    msg['From'] = 'results@twittermining.com'
    msg['To'] = userEmail
    #body = 'Thank you for using Twittermining.com\n\n'
    msg.attach(MIMEText(body))

    #attachment = 'templates/%s.txt' % pdRoute
    #part = MIMEBase('application', "octet-stream")
    # part.set_payload(body)
    # Encoders.encode_base64(part)
    # part.add_header('Content-Disposition',
    #                'attachment; filename="TwM Results.txt"')
    # msg.attach(part)

    smtpserver = smtplib.SMTP("mail.twittermining.com", 26)
    smtpserver.ehlo()
    smtpserver.starttls()
    smtpserver.ehlo
    smtpserver.login(msg['From'], '')

    try:
        smtpserver.sendmail(msg['From'], userEmail, msg.as_string())
    except Exception as e:
        action = 'Problem sending email - %s' % e
        writeLog('Page Email', 'ERROR', action)
    finally:
        smtpserver.close()


def sendPW(userEmail, code):
    msg = MIMEMultipart()
    msg['Subject'] = 'TwitterMining Password Recovery'
    msg['From'] = 'results@twittermining.com'
    msg['To'] = userEmail
    body = 'Hello!\nYour TwitterMining password has been reset to: \
            %s\n\nThanks!\n\nTwitterMining.com' % code
    msg.attach(MIMEText(body))

    smtpserver = smtplib.SMTP("mail.twittermining.com", 26)
    smtpserver.ehlo()
    smtpserver.starttls()
    smtpserver.ehlo
    smtpserver.login(msg['From'], '')

    try:
        smtpserver.sendmail(msg['From'], userEmail, msg.as_string())
        action = 'Password recovery for %s' % userEmail
        writeLog('INFO', action)
    except Exception as e:
        action = 'Problem sending recovery email - %s' % e
        writeLog('ERROR', action)
    finally:
        smtpserver.close()


def writeLog(entry_type, action):
    l = open('TwM.log', "a")
    try:
        l.write('%s,%s,%s\n' %
                (str(datetime.datetime.now()), entry_type, action))
    except IOError:
        pass
    finally:
        l.close
