#Reads the text file and extracts questions
#TODOs - 1. Extract messages -- DONE
#        2. Decide if they are questions -- DONE
#        3. Save into an object with timestamp, author, question number and                     question, with a pretty printer function -- DONE
#        4. Upload to required thing -- DONE for slides
#        5. Write a driver file
#        6. Put stuff in a db -- DONE
#        7. Scrape whatsapp in a different way
#		 8. Handle questions spanninng multiple messages -- DONE
FILENAME = 'messages.txt'
DB       = 'questions.sqlite'
# NUMBER   = 1

import re
import sqlite3
import datetime

from upload import Slides_uploader

class Question():
	#TODO get max question number
	#TODO init from database
	number = 0
	def __init__(self,match):
		self.date     = datetime.datetime(int(match.group('year')),int(match.group('month')),int(match.group('day')),int(match.group('hour')),int(match.group('minute'))).timestamp()
		# self.time  	  = match.group('time')
		self.QM  	  = match.group('QM')
		self.message  = match.group('message')
		self.qnumber  = Question.number

	def is_valid(self,max_time):
		#Returns true if the message is a question
		# TODO get better heuristics
		split = self.message.split()
		split = [x.lower() for x in split] 
		if self.date < max_time:
			#The record is already in the database if its time is less
			return False
		if 'quiz' in split or 'quizzes' in split: #or 'team' in split:
			return False

		if len(split) > 25:
			return True
		if 'id' in split: #'i\'d' in split:
			return True 
		if ('?' in split or 'x' in split or '_' in split or 'named' in split) and len(split)>15:
			return True  
		return False
	def __str__(self):
		#TODO add different stringers for MD, HTML, blogs etc
		string = "Number:{}\ntimestamp:{}\nUser:{}\nMessage:{}\n".format(self.qnumber,self.date,self.QM,self.message)
		return string

	def update_db(self,cursor):
		sqlite_insert_with_param = """INSERT INTO 'questions'
		                          ('Number','Timestamp','QM','Question') 
		                          VALUES (?, ?, ?, ?);"""
		data = (self.qnumber,self.date,self.QM,self.message)	
		cursor.execute(sqlite_insert_with_param, data)

	def update_question(self,regex):
		self.message += "\n{}".format(regex.group('message'))

def extract_messages(text):
	'''
	Given a text, extracts all messages into a list of strings
	''' 
	sqliteConnection = sqlite3.connect('questions.db')
	cursor = sqliteConnection.cursor()
	cursor.execute('''select max(Number) from questions''')

	NUMBER = cursor.fetchall()[0][0]

	Question.number = NUMBER + 1
	cursor.execute('''select max(Timestamp) from questions''')
	max_time = cursor.fetchall()[0][0]

	file = open("Rejects.txt","w")

	regex_pattern = re.compile(r'^(?P<day>\d{2})\/(?P<month>\d{2})\/(?P<year>\d{4})\, (?P<hour>\d{2})\:(?P<minute>\d{2}) \- (?P<QM>[\w\+ ]+)\: (?P<message>[\s\S]+?)(?=^\d{2}|\Z)',re.MULTILINE)
	
	messages  = regex_pattern.finditer(text)
	msg_stack = []	#Stack ensures that multi-message questions are interpreted well enough
	
	for m in messages:
		q = Question(m)
		if len(msg_stack) == 0:
			if q.is_valid(max_time):
				# print(str(q))
				# print("\n______\n")
				Question.number += 1
				msg_stack.append(q)
			else:
				file.write("\n______\n")
				file.write(q.message)
		else:
			if msg_stack[-1].QM == q.QM:
				print("Found one with multiple parts")
				print(msg_stack[-1].qnumber)
				msg_stack[-1].update_question(m)
			else:
				msg_stack[-1].update_db(cursor)
				msg_stack.pop()
				if q.is_valid(max_time):
					# print(str(q))
					# print("\n______\n")
					Question.number += 1
					msg_stack.append(q)
				else:
					file.write("\n______\n")
					file.write(q.message)

	for q in msg_stack:
		q.update_db(cursor)

	sqliteConnection.commit()

text = open(FILENAME,"r").read()
# print(text)
extract_messages(text)