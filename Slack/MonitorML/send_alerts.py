import requests
import json
import sys

#TODO - ideas - 1. Sending images, 2. Read messages according to time, user to respond, can respond with either stats/ do some other action later
def send_alert(text,url):
    headers = {"Content-type":"application/json"}
    data = {"text":text}
    response = requests.post(url,json=data,headers=headers)
    # print(response.text)

def get_commands(user,token,channel_id,ts):
    '''
    Returns a list of commands
    '''
    # TODO update timestamp
    # TODO convert all to a class 
    headers  = {"Content-type":"application/json"}
    url      = "https://slack.com/api/conversations.history?token={}&channel={}".format(token,channel_id)  
    response = requests.get(url,headers=headers)
    commands = [x['text'] for x in response.json()['messages'] if 'user' in x.keys() and x['user'] == user and float(x['ts']) > ts]
    return commands

config = json.load(open("config.json","r")) 

url = config["webhook_url"]
user = config["user"]
token = config["token"]
channel_id = config["channel_id"]
ts = config["ts"]
print(get_commands(user,token,channel_id,ts))
# send_alert(sys.argv[1],url)