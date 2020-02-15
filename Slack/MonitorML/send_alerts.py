import requests
import json
import sys

from time import time
#TODO - ideas - 1. Sending images, 2. Read messages according to time, user to respond, can respond with either stats/ do some other action later
def send_alert(text,url):
	headers = {"Content-type":"application/json"}
	data = {"text":text}
	response = requests.post(url,json=data,headers=headers)
	# print(response.text)

def get_commands(config_dict_path,log_file_path):
	'''
	Returns a list of commands
	'''
	# TODO update timestamp
	# TODO convert all to a class 
	config = json.load(open(config_dict_path,"r")) 

	headers  = {"Content-type":"application/json"}
	url      = "https://slack.com/api/conversations.history?token={}&channel={}".format(config["token"],config["channel_id"]) 
	user     = config["user"]
	ts       = config["ts"] 
	response = requests.get(url,headers=headers)
	print(response)
	commands = [(x['text'],x['ts']) for x in response.json()['messages'] if 'user' in x.keys() and x['user'] == user and float(x['ts']) > ts]
	config['ts'] = time()

	json.dump(config,open(config_dict_path,"w"))
	with open(log_file_path, "a") as logfile:
	    logfile.write('\n'.join(["{}: {}".format(x[1],x[0]) for x in commands]))
	return commands


print(get_commands("config.json","log.txt"))
