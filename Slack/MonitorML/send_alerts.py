import requests
import json
import sys

def send_alert(text,url):
	headers = {"Content-type":"application/json"}
	data = {"text":text}
	response = requests.post(url,json=data,headers=headers)
	# print(response.text)

config = json.load(open("config.json","r")) 

url = config["webhook_url"]
send_alert(sys.argv[1],url)