#!/usr/bin/env python3

#
# Startup mail & telegram bot notification scrypt v.1.1
# Created by TORQUEMADA163 (a.nakhimov@gmail.com, github - vottghern) 
# for forum https://forum.bits.media
# 2017
#

import socket
import time
import smtplib
import requests
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Функция отправки почты
def mailalert(subj_msg, body_msg):
	fromaddr = "YOUR_GMAIL@gmail.com"	# С какого адреса отправлять
	mypass = "YOUR_PASS"					# Пароль от ящика
	toaddr = "YOUR_GMAIL@gmail.com"		# Ящик-назначение
	msg = MIMEMultipart()

	msg['From'] = fromaddr
	msg['To'] = toaddr
	msg['Subject'] = subj_msg
 
	body = body_msg
	msg.attach(MIMEText(body, 'plain'))
 
	server = smtplib.SMTP('smtp.gmail.com', 587)
	server.starttls()
	server.login(fromaddr, mypass)
	text = msg.as_string()
	server.sendmail(fromaddr, toaddr, text)
	server.quit()

# Функция отправки боту Телеграм
def telegrambot(bot_msg):
	data = {
		'message': bot_msg
	}

	url = "YOUR_TELEGRAMM_WEBHOOK_URL"

	try:
		req = requests.post(url, data=data)
	except:
		pass

mailalert("Host %s is started" % socket.gethostname(), "Host %s is started" % socket.gethostname())
telegrambot("Host %s is started" % socket.gethostname())
