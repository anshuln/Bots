import sqlite3
import json
import argparse

from upload import *
from parser import *
from scraper import *

DB       = 'questions_.db'
CONFIG   = 'config.json'

def dict_factory(cursor, row):
	d = {}
	for idx, col in enumerate(cursor.description):
		d[col[0]] = row[idx]
	return d

if __name__ == "__main__":
	parser = argparse.ArgumentParser()

	parser.add_argument("-p","--parse", help="Parse the input file",action="store_true")
	parser.add_argument("-f","--file", help="Message file to parse",default="messages.txt")
	parser.add_argument("-u","--upload", help="Upload questions",action="store_true")
	parser.add_argument("-e","--email", help="Scrape from email",action="store_true")
	# parser.add_argument("-e","--epochs",help="Num of epochs",type=int, default=50)

	args = parser.parse_args()

	config = json.load(open(CONFIG,"r"))

	if args.email:
		scrape_email(config['msg_file'])
	if args.parse:
		text = open(args.file,"r").read()
		# print(text)
		extract_messages(text,config['database'],config['mode'],config['keywordq'],config['keyworda'])

	con = sqlite3.connect(config['database'])
	con.row_factory = dict_factory
	cursor = con.cursor()
	if args.upload:
		uploader = Slides_uploader(presentation_id=config['presentation_id'])
		# TODO argparse to control what all to do, between scraping, uploading etc.
		max_num = upload_all(cursor,uploader,config['max_num'])
		config['max_num'] = max_num
		json.dump(config,open(CONFIG,"w"))

	con.close()