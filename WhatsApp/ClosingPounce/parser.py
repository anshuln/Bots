#Reads the text file and extracts questions
#TODOs - 1. Extract messages -- DONE
#        2. Decide if they are questions -- DONE
#        3. Save into an object with timestamp, author, question number and                     question, with a pretty printer function -- DONE
#        4. Upload to required thing -- DONE for slides
#        5. Write a driver file
#        6. Put stuff in a db -- DONE
#        7. Scrape whatsapp in a different way
#		 8. Handle questions spanninng multiple messages
FILENAME = 'messages.txt'
DB       = 'questions.sqlite'
NUMBER   = 1
import re
import sqlite3
from upload import Slides_uploader

class Question():
	#TODO get max question number
	#TODO init from database
	number = NUMBER
	def __init__(self,match):
		self.date     = match.group('date')
		self.time  	  = match.group('time')
		self.QM  	  = match.group('QM')
		self.message  = match.group('message')
		self.qnumber  = Question.number

	def is_valid(self):
		#Returns true if the message is a question
		# TODO get better heuristics
		split = self.message.split()
		split = [x.lower() for x in split] 

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
		string = "Number:{}\nDate:{}\nTime:{}\nUser:{}\nMessage:{}\n".format(self.qnumber,self.date,self.time,self.QM,self.message)
		return string

	def update_db(self,cursor):
		sqlite_insert_with_param = """INSERT INTO 'questions'
		                          ('Number','Date','Time','QM','Question') 
		                          VALUES (?, ?, ?,?,?);"""
		data = (self.qnumber,self.date,self.time,self.QM,self.message)	
		cursor.execute(sqlite_insert_with_param, data)

	def update_question(self,regex):
		self.message += "\n{}".format(regex.group('message'))

def extract_messages(text):
	'''
	Given a text, extracts all messages into a list of strings
	''' 
	sqliteConnection = sqlite3.connect('questions.db')
	cursor = sqliteConnection.cursor()

	# sl = Slides_uploader(presentation_id)
	Question.number = NUMBER 
	file = open("Rejects.txt","w")
	regex_pattern = re.compile(r'^(?P<date>\d{2}\/\d{2}\/\d{4})\, (?P<time>\d{2}\:\d{2}) \- (?P<QM>[\w\+ ]+)\: (?P<message>[\s\S]+?)(?=^\d{2}|\Z)',re.MULTILINE)
	
	messages  = regex_pattern.finditer(text)
	msg_stack = []	#Stack ensures that multi-message questions are interpreted well enough
	
	for m in messages:
		q = Question(m)
		if len(msg_stack) == 0:
			if q.is_valid():
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
				if q.is_valid():
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