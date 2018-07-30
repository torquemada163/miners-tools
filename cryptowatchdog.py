#!/usr/bin/env python3

#
# CRYPTOWATCHDOG 3.1 - watchdog for NVIDIA GPU based on NVIDIA-SMI.
# Created by TORQUEMADA163 (a.nakhimov@gmail.com) for forum https://forum.bits.media
# 2017
#

import subprocess
import os
import socket
import logging
import time
import smtplib
import requests
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Порог падения загруженности GPU, в процентах
UTIL_TRESHOLD = 50

# Количество циклов проверки, в течении которых одна и та же GPU
# должна показать снижения хешрейта для того,
# чтобы быть признанной сбойной
COUNT_TRESHOLD = 5

# Пауза между циклами проверки
TIME_DELAY = 20

# Имя лог-файла
# LOG_FILE = "cryptowatchdog.log"
LOG_DIR = os.path.expanduser("~") + "/custom_services/custom_logs"
LOG_FILE = LOG_DIR + "/cryptowatchdog.log"
os.makedirs(LOG_DIR, 0o755, True)

# Создание логгера
logger = logging.getLogger("cryptowatchdog")
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler(LOG_FILE)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

# Зафиксированное состояние всех GPU после соответствующего 
# количества циклов проверки
last_gpu_state = 0b0

# Функция проверки интернета
def is_internet():
	try:
		host = socket.gethostbyname("yandex.ru")
		s = socket.create_connection((host, 80), 2)
		return True
	except:
		pass
	return False


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

	url = "YOUR_TELEGRAMBOT_WEBHOOK_URL"

	try:
		req = requests.post(url, data=data)
	except:
		logger.error("Error from send message to Telegram Bot")



# Начало работы
time.sleep(120)

# Проверка наличия интернета, количества GPU, начальные записи в лог
last_internet_state = is_internet()
logger.info("Watchdog started")
logger.info("Having internet - %s", last_internet_state)

gpu_raw = subprocess.run(["nvidia-smi", "--query-gpu=count", "--format=csv,noheader,nounits"], check=True, stdout=subprocess.PIPE, universal_newlines=True).stdout.split()
gpu_count = len(gpu_raw)
logger.info("GPU's count - %d", gpu_count)


# Старт бесконечного цикла watchdog
while True:
	
	# Получение массива загруженности всех GPU		
	utilization_raw = subprocess.run(["nvidia-smi", "--query-gpu=utilization.gpu", "--format=csv,noheader,nounits"], check=True, stdout=subprocess.PIPE, universal_newlines=True).stdout.split()
	
	# Инициализация переменной для хранения состояния всех GPU в двоичной форме
	current_gpu_state = ""

	# Проход по массиву загруженности GPU, попытка перевести результат в десятичный вид,
	# в случае невозможности - фатальный сбой, потеря карты. Запись в лог
	for index, onegpu in enumerate(utilization_raw):
		try:
			onegpu_util = int(onegpu)
		except:
			logger.critical("Lost GPU%d", index)

			# Если интернет есть, то отправка почты, пауза 5 секунд для завершения отправки и перезагрузка
			# Если интернета нет, то нет смысла в перезагрузке
			if is_internet():
				mailalert("Watchdog on %s" % socket.gethostname(), "Lost GPU%d on %s" % (index, socket.gethostname()))
				telegrambot("Lost GPU%d on %s" % (index, socket.gethostname()))
				time.sleep(5)
				break

		# Прверка значения загрузки GPU на предмет ниже значения порога.
		# Если меньше - записать 0, если больше - 1
		if onegpu_util < UTIL_TRESHOLD:
			current_gpu_state = current_gpu_state + "0"
		else:
			current_gpu_state = current_gpu_state + "1"

	# Провести ПОБИТОВОЕ ИЛИ полученного двоичного числа, отображающего текущее состояние всех GPU
	# с сохраненным предыдущим состоянием. Если на протяжении установленного цикла проверки
	# у GPU хоть раз будет 1, то GPU признается нормально работающей.
	compare_gpu = last_gpu_state | int(current_gpu_state, 2)

	# Сохранить текущее состояние, как последнее
	last_gpu_state = compare_gpu

	# Уменьшить количество циклов на 1
	COUNT_TRESHOLD -= 1

	# Инициализация переменной, где будут храниться номера сбойных GPU, если таковые будут
	fault_gpu = ""

	# Если цикл закончен, то преобразовать последнее состоянии в строку двоичного вида, с количеством
	# символов, равным количеству GPU
	if COUNT_TRESHOLD == 0:
		gpu_result = bin(last_gpu_state)[2:].zfill(gpu_count)

		# Проход по полученной строке на предмет проверки наличия сбойных GPU
		for index, onebitgpu in enumerate(gpu_result):
			if onebitgpu == "0":
				fault_gpu = fault_gpu + " " + str(index) +","
		
		# Если переменная, хранящая номера сбойных GPU не пуста, то сделать запись в лог
		if fault_gpu != "":
			logger.error("Detected decrease hashrate: %s", gpu_result)
			logger.error("Fault GPU's: %s", fault_gpu)

			# Если есть интернет, то отправить почту и подождать 5 секунд, после чего, можно, например, перезагрузить риг, иначе ....
			if is_internet():
				mailalert("Watchdog on %s" % socket.gethostname(), "Fault GPU's: %s on %s" % (fault_gpu, socket.gethostname()))
				telegrambot("Fault GPU's: %s on %s" % (fault_gpu, socket.gethostname()))
				time.sleep(5)

				# Проверка сохраненного состояния интернета, если до этого его не было,
				# то сделать запись в лог о том, что интернет появился
				if last_internet_state == False:
					last_internet_state = True
					logger.warn("Internet connection established")

			# .... если интернет был раньше, а теперь его нет, то сделать запись в лог об этом,
			# перезагружать риг - бессмысленно
			else:
				if last_internet_state == True:
					last_internet_state = False
					logger.error("Lost internet connection")

		# Обнуление последнего состояния GPU, количества циклов проверки
		last_gpu_state = 0b0
		COUNT_TRESHOLD = 5
	
	# Задержка и новый запуск всех проверок
	time.sleep(TIME_DELAY)
