#!/usr/bin/env python3

import psutil, requests, json, time, socket
import datetime

RIGNAME = 'rig01'


def telegrambot(bot_msg):
	data = {
		'message': bot_msg
	}

	url = "YOUR_TELEGRAMBOT_WEBHOOK_URL"

	try:
		req = requests.post(url, data=data)
	except:
		pass


def minerDetect():
	# EWBF
	# CCMINER
	# ETHDCRMINER64 - CLAYMORE
	# ETHMINER
	miner_name = []

	try:
		pid = next(item for item in psutil.process_iter() if item.name() == 'miner').pid
		miner_name.append('EWBF')
	except:
		pass
	try:
		pid = next(item for item in psutil.process_iter() if item.name() == 'ccminer').pid
		miner_name.append('CCMINER')
	except:
		pass
	try:
		pid = next(item for item in psutil.process_iter() if item.name() == 'ethdcrminer64').pid
		miner_name.append('CLAYMORE')
	except:
		pass
	try:
		pid = next(item for item in psutil.process_iter() if item.name() == 'ethminer').pid
		miner_name.append('ETHMINER')
	except:
		pass

	if len(miner_name) == 0:
		# Записать в лог, что ни один майнер не запущен или майнер не поддерживается мониторингом
		return 'None'
	if len(miner_name) > 1:
		# Записать в лог, что запущено больше одного майнера
		return 'DOUBLE'
	else:
		# print('Current miner - ', miner_name[0])
		return miner_name[0]


def getEWBFjson():
	try:
		onerig = requests.get('http://127.0.0.1:42000/getstat').json()
		output_dict = {'rigname': RIGNAME, 'req_time': time.time(), 'miner': 'EWBF'}
		if onerig['error'] == None:
			allgpu_list = []
			allgpus = onerig['result']
			for onegpu in allgpus:
				onegpu_dict = {}
				onegpu_dict = {'gpuid': onegpu['gpuid'], 'hashrate': onegpu['speed_sps'], 'temp': onegpu['temperature']}
				allgpu_list.append(onegpu_dict)
			output_dict['error'] = None
			output_dict['result'] = allgpu_list
			output_dict['pool'] = onerig['current_server']
			output_dict['miner_starttime'] = onerig['start_time']
		else:
			output_dict['error'] = 1
		return json.dumps(output_dict)
	except:
		output_dict = {}
		output_dict['error'] = 1
		return json.dumps(output_dict)


def getETHCLAYjson(miner):
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect(('localhost', 3333))
		s.sendall('{"id":0,"jsonrpc":"2.0","method":"miner_getstat1"}\n'.encode('utf-8'))
		raw_response = bytearray()
		while True:
			data = s.recv(4096)
			raw_response += data
			if not data or b'\n' in data:
				break
		s.close()
		json_response = json.loads(raw_response.decode('utf-8'))

		output_dict = {'rigname': RIGNAME, 'req_time': time.time(), 'miner': miner}
		allgpus_hashrate = json_response['result'][3].split(';')
		allgpus_temp = json_response['result'][6].replace(' ', '').split(';')[::2]
		# Строка выше. Сначала убираем все пробелы, затем разбиваем по символу ';'
		# на список, в котором каждый нечетный эелемент - температура, а каждый
		# четный - вентилятор.
		# После этого выбираем каждый нечетный элемент списка, т.е., температуру

		allgpus_result = []
		for idx in range(len(allgpus_hashrate)):
			onegpu_result = {}
			onegpu_dict = {'gpuid': 'GPU'+str(idx), 'hashrate': allgpus_hashrate[idx], 'temp': allgpus_temp[idx]}
			allgpus_result.append(onegpu_dict)
		output_dict['result'] = allgpus_result
		output_dict['pool'] = json_response['result'][7]
		output_dict['miner_starttime'] = json_response['result'][1]
		output_dict['total_hashrate'] = json_response['result'][2].split(';')[0]
		output_dict['error'] = None
		return json.dumps(output_dict)

	except:
		output_dict = {}
		output_dict['error'] = 1
		return json.dumps(output_dict)


#switch_dict = {'EWBF': getEWBFjson(), 'CCMINER': 'Miner CCMINER', 'CLAYMORE': getETHCLAYjson('CLAYMORE'), 'ETHMINER': getETHCLAYjson('ETHMINER'), 'None': 'Nothing mining!', 'DOUBLE': 'More than 1 miner!'}

while True:
	try:
		#result = switch_dict[minerDetect()]
		miner = minerDetect()
		if miner == 'EWBF':
			result = getEWBFjson()
		elif miner == 'CLAYMORE':
			result = getETHCLAYjson('CLAYMORE')
		elif miner == 'ETHMINER':
			result = getETHCLAYjson('ETHMINER')
	except:
		print('ERROR!!!!')
	print(result)


	print('FOR DB:')
	telegrambot(result)
	work_dict = json.loads(result)
	if not work_dict['error']:
		print("Request time - {0}".format(datetime.datetime.fromtimestamp(work_dict['req_time']).strftime('%H:%M:%S %d/%m/%Y')))
		print("Rig name - {0}".format(work_dict['rigname']))
		print("GPU count - {0}".format(len(work_dict['result'])))
		print("Miner working time - {0}".format(datetime.timedelta(minutes=int(work_dict['miner_starttime']))))
		print("Total hashrate - {0}".format(round(float(work_dict['total_hashrate'])/1000)))
		gpus_hr = ''
		gpus_temp = ''
		if work_dict['total_hashrate'] != "0":
			for onegpu in work_dict['result']:
				gpus_hr += (str(round(float(onegpu['hashrate'])/1000,1))+' ')
				gpus_temp += (onegpu['temp']+' ')
		else:
			gpus_hr = '0'
			gpus_temp = '0'
		print("GPUs hashrate - {0}".format(gpus_hr))
		print("GPUs temp - {0}".format(gpus_temp))
		print("Pool - {0}".format(work_dict['pool']))
		print('\n')
	else:
		print('ERROR')
	time.sleep(600)