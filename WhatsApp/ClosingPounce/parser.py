#Reads the text file and extracts questions
#TODOs - 1. Extract messages -- DONE
#        2. Decide if they are questions -- DONE
#        3. Save into an object with timestamp, author, question number and                     question, with a pretty printer function -- DONE
#        4. Upload to required thing
FILENAME = 'messages.txt'
NUMBER   = 1
import re
from upload import Slides_uploader
class Question():
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
		string = "Number:{}\nDate:{}\nTime:{}\nUser:{}\nMessage:{}\n".format(self.qnumber,self.date,self.time,self.QM,self.message)
		return string

def extract_messages(text):
	'''
	Given a text, extracts all messages into a list of strings
	''' 
	sl = Slides_uploader(presentation_id)
	Question.number = NUMBER 
	file = open("Rejects.txt","w")
	regex_pattern = re.compile(r'^(?P<date>\d{2}\/\d{2}\/\d{4})\, (?P<time>\d{2}\:\d{2}) \- (?P<QM>[\w\+ ]+)\: (?P<message>[\s\S]+?)(?=^\d{2}|\Z)',re.MULTILINE)
	messages = regex_pattern.finditer(text)

	for m in messages:
		# # printer(m)
		# # print(m)
		# if len(m.group('message').split()) > 15:
		# 	printer(m)
		q = Question(m)
		if q.is_valid():
			print(str(q))
			print("\n______\n")
			Question.number += 1
			sl.upload_question(q)
		else:
			file.write("\n______\n")
			file.write(q.message)
text = open(FILENAME,"r").read()
# print(text)
extract_messages(text)