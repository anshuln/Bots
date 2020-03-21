#This file uploads stuff to various places, either as a MD file, blogpost or HTML
#TODO throttle to limit number of requests
import json
import pickle
import time
import uuid

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


gen_uuid = lambda : str(uuid.uuid4())  # get random UUID string
class Slides_uploader():
	def __init__(self,presentation_id,credentials_file='token.pickle'):
		# flow = InstalledAppFlow.from_client_secrets_file(
		#     'credentials.json', SCOPES)
		# creds = flow.run_local_server(port=0)
		# Save the credentials for the next run
		with open('token.pickle', 'rb') as token:
			self.creds = pickle.load(token)
			self.presentation_id = presentation_id
			self.service = build('slides', 'v1', credentials=self.creds)

	def upload_question(self,qnumber,message,user,answer):
		#Todo add answer slide
		titleIdq = gen_uuid()
		bodyIdq  = gen_uuid()
		titleIda = gen_uuid()
		bodyIda  = gen_uuid()
		requests = [
			{
			'createSlide': {
				'slideLayoutReference': {
				'predefinedLayout': 'TITLE_AND_BODY'
					},
				"placeholderIdMappings": [
					{
					"layoutPlaceholder": {
					"type": "TITLE",
					"index": 0
					},
					"objectId": titleIdq,
					},
					{
					"layoutPlaceholder": {
					"type": "BODY",
					"index": 0
					},
					"objectId": bodyIdq,
					},
				],

				}
			},
			{
			'createSlide': {
				'slideLayoutReference': {
				'predefinedLayout': 'TITLE_AND_BODY'
					},
				"placeholderIdMappings": [
					{
					"layoutPlaceholder": {
					"type": "TITLE",
					"index": 0
					},
					"objectId": titleIda,
					},
					{
					"layoutPlaceholder": {
					"type": "BODY",
					"index": 0
					},
					"objectId": bodyIda,
					},
				],

				}
			},          
			{
			"insertText": {
					"objectId": titleIdq,
					"text": "{}. <set by {}>".format(qnumber,user.split()[0]),
				}

			},
			{
			"insertText": {
					"objectId": bodyIdq,
					"text": "{}".format(message.replace("sphinx","")),
				}

			},      
			{
			"insertText": {
					"objectId": titleIda,
					"text": "Answer",
				}

			},
			{
			"insertText": {
					"objectId": bodyIda,
					"text": "{}".format(answer.replace("#oedipus","")),
				}

			},

		]

		body = {
		'requests': requests
		}
		response = self.service.presentations() \
		.batchUpdate(presentationId=self.presentation_id, body=body).execute()
		create_slide_response = response.get('replies')[0].get('createSlide')




def upload_all(cursor,uploader,max_num):
	'''
	Reads records from db, uploads them if the question number is greater than config
	Returns question number of last question uploaded
	'''
	query = '''select * from questions where Number>{}'''.format(max_num)
	cursor.execute(query)
	for row in cursor.fetchall():
		try:    
			#Google sometimes blocks requests
			uploader.upload_question(row["Number"],row["Question"],row["QM"],str(row["Answer"]))
		except:
			print("API refused connection with number {}".format(max_num))
			return max_num
		time.sleep(0.02)    #Hack to prevent throttling
		max_num = max(max_num,row["Number"])
	return max_num

