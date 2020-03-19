import sqlite3
import json
import argparse

from upload import *
from parser import *

DB       = 'questions.sqlite'
CONFIG   = 'config.json'

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

if __name__ == "__main__":
	con = sqlite3.connect("questions.db")
	con.row_factory = dict_factory
	cursor = con.cursor()
	config = json.load(open(CONFIG,"r"))
	uploader = Slides_uploader(presentation_id=config['presentation_id'])
	# TODO argparse to control what all to do, between scraping, uploading etc.
	max_num = upload_all(cursor,uploader,config['max_num'])
	config['max_num'] = max_num
	json.dump(config,open(CONFIG,"w"))