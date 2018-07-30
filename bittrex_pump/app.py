#!/usr/bin/env python3

from bittrex import Bittrex, API_V2_0, API_V1_1
from apscheduler.schedulers.blocking import BlockingScheduler
import time
from datetime import datetime
import requests
import sys

check_iter = 5

def telegrambot(bot_msg):
	data = {
		'message': bot_msg
	}

	url = "YOUR_TELEGRAMBOT_WEBHOOK_URL"
	try:
		req = requests.post(url, data=data)
	except:
		pass

def calctrend():
	my_bittrex = Bittrex(None, None, api_version=API_V2_0)  # or defaulting to v1.1 as Bittrex(None, None)
	counter = check_iter
	bigdata = {}
	res_dict = {}
	res_notif = {"UP": '', "DOWN": ''}
	while counter > 0:
		grandresult = my_bittrex.get_market_summaries()
		if grandresult["success"]:
			print('Счетчик - {}, Время - {}'.format(counter, datetime.strftime(datetime.now(), "%d.%m.%Y %H:%M:%S")))
			#time.sleep(10)
			for onemarket in grandresult["result"]:
				onemarket_logo = onemarket["Market"]["LogoUrl"]
				onemarket_name = onemarket["Summary"]["MarketName"]
				onemarket_last = onemarket["Summary"]["Last"]
				if bigdata.get(onemarket_name) != None:
					bigdata[onemarket_name].append(onemarket_last)
				else:
					bigdata[onemarket_name] = [onemarket_last,]
			counter -= 1
			if counter > 0:
				time.sleep(300)

	for onecurr in bigdata.items():
		for oneprice in onecurr[1]:
			if res_dict.get(onecurr[0]) == None:
				res_dict[onecurr[0]] = {"up_cnt": 1, "down_cnt": 1, "prev_price": oneprice}
			else:
				if res_dict[onecurr[0]]["prev_price"] < oneprice:
					res_dict[onecurr[0]]["up_cnt"] += 1
				elif res_dict[onecurr[0]]["prev_price"] > oneprice:
					res_dict[onecurr[0]]["down_cnt"] +=1
				res_dict[onecurr[0]]["prev_price"] = oneprice

	for key, value in res_dict.items():
		if value["up_cnt"] == check_iter:
			res_notif["UP"] = res_notif["UP"] + str(key) + ', '
		elif value["down_cnt"] == check_iter:
			res_notif["DOWN"] = res_notif["DOWN"] + str(key) + ', '

	print(res_notif)
	telegrambot("Possible uptrend - {}\n\nPossible downtrend - {}".format(res_notif["UP"], res_notif["DOWN"]))


if __name__ == '__main__':
    scheduler = BlockingScheduler()
    scheduler.add_job(calctrend, 'cron', hour='9,11,13,15,17,19,21,23')

    try:
        scheduler.start()
    except:
        sys.exit()
