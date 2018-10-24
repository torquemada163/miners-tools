import telebot
import os
from flask import Flask, request
import time
import psycopg2
import psycopg2.extras
import json
import datetime

bot = telebot.TeleBot('BOT_ID')

app = Flask(__name__)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, 'Hello, ' + message.from_user.first_name)

@bot.message_handler(commands=['reg'])
def reg(message):
    with psycopg2.connect(database='database_name', user='user_name', host='host', password='password') as conn:
        with conn.cursor() as cur:
            sql = "SELECT * FROM regusers WHERE chat_id=%s" % (message.chat.id)
            cur.execute(sql)
            data = cur.fetchone()
            if data:
                bot.reply_to(message, "Already registered!")
            else:
                bot.reply_to(message, "Registering......")
                sql1 = "INSERT INTO regusers (chat_id, user_id) VALUES (%s, %s)" % (message.chat.id, message.from_user.id)
                cur.execute(sql1)
                conn.commit()
                cur.execute(sql)
                data1 = cur.fetchone()
                if data1:
                    bot.reply_to(message, "Success registered!")
                else:
                    bot.reply_to(message, "Something wrong...")
        conn.close()

@bot.message_handler(commands=['stat'])
def stat(message):
	with psycopg2.connect(database='database_name', user='user_name', host='host', password='password') as conn:
		with conn.cursor() as cur:
			sql = "SELECT * FROM rigsmon"
			cur.execute(sql)
			rows = cur.fetchall()
			if not rows:
				bot.reply_to(message, "No records!")
			else:
				for row in rows:
					resulttext ="Последнее время обмена - {0}\nИмя рига - {1}\nКоличество GPU - {2}\nВремя работы майнера - {3}\nОбщий хешрейт - {4}\nХешрейт по GPU - {5}\nТемпература по GPU - {6}\nПул - {7}".format(row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8])
					bot.reply_to(message, resulttext)
	conn.close()

# @bot.message_handler(func=lambda message: True, content_types=['text'])
# def echo_message(message):
#     bot.reply_to(message, message.text)

@app.route("/bot", methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200

@app.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url="heroku-url")
    return "!", 200

@app.route("/alert", methods=['POST'])
def sendAlert():
    with psycopg2.connect(database='database_name', user='user_name', host='host', password='password') as conn:
        with conn.cursor() as cur:
            sql = "SELECT chat_id FROM regusers"
            cur.execute(sql)
            rows = cur.fetchall()
            for row in rows:
                bot.send_message(row[0], request.form.get('message'))
    return "!", 200

@app.route("/updstat", methods=['POST'])
def updateRegMonDB():
	work_dict = json.loads(request.form.get('message'))
	if not work_dict['error']:
		req_time = datetime.datetime.fromtimestamp(work_dict['req_time']).strftime('%H:%M:%S %d/%m/%Y')
		rigname = str(work_dict['rigname'])
		gpus_count = len(work_dict['result'])
		miner_starttime = datetime.timedelta(minutes=int(work_dict['miner_starttime']))
		total_hashrate = round(float(work_dict['total_hashrate'])/1000)
		pool = work_dict['pool']
		gpus_hashrate = ''
		gpus_temp = ''
		for onegpu in work_dict['result']:
			gpus_hashrate += (str(round(float(onegpu['hashrate'])/1000,1))+' ')
			gpus_temp += (onegpu['temp']+' ')

		print("Request time - {0}".format(req_time))
		print("Rig name - {0}".format(rigname))
		print("GPU count - {0}".format(gpus_count))
		print("Miner working time - {0}".format(miner_starttime))
		print("Total hashrate - {0}".format(total_hashrate))
		print("GPUs hashrate - {0}".format(gpus_hashrate))
		print("GPUs temp - {0}".format(gpus_temp))
		print("Pool - {0}".format(pool))
	else:
		print('ERROR')

	with psycopg2.connect(database='database_name', user='user_name', host='host', password='password') as conn:
		with conn.cursor() as cur:
			sql = "SELECT * FROM rigsmon WHERE rigname='%s'" % (rigname,)
			cur.execute(sql)
			data = cur.fetchone()
			if data:
				sql1 = "UPDATE rigsmon SET req_time='%s', gpus_count=%s, miner_starttime='%s', total_hashrate=%s, \
				gpus_hashrate='%s', gpus_temp='%s', pool='%s' \
				WHERE rigname='%s'" % (req_time, gpus_count, miner_starttime, total_hashrate, gpus_hashrate, gpus_temp, pool, rigname,)
				cur.execute(sql1)
				conn.commit()
			else:
				sql1 = "INSERT INTO rigsmon (req_time, rigname, gpus_count, miner_starttime, total_hashrate, gpus_hashrate, gpus_temp, pool) VALUES ('%s', '%s', %s, '%s', %s, '%s', '%s', '%s')" % (req_time, rigname, gpus_count, miner_starttime, total_hashrate, gpus_hashrate, gpus_temp, pool,)
				cur.execute(sql1)
				conn.commit()
	conn.close()
	return "!", 200

if __name__ == "__main__":
	app.run(host="0.0.0.0", port=os.environ.get('PORT', 5000))
