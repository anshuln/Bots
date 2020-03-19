#This file uploads stuff to various places, either as a MD file, blogpost or HTML
#TODO throttle to limit number of requests
import json
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import uuid

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

	def upload_question(self,question):
		titleId = gen_uuid()
		bodyId  = gen_uuid()
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
					"objectId": titleId,
					},
					{
					"layoutPlaceholder": {
					"type": "BODY",
					"index": 0
					},
					"objectId": bodyId,
					},
				],

				}
			},
			{
			"insertText": {
			        "objectId": titleId,
			        "text": "{}".format(question.qnumber),
			    }

			},
			{
			"insertText": {
			        "objectId": bodyId,
			        "text": "{}".format(question.message),
			    }

			},

		]

		body = {
		'requests': requests
		}
		response = self.service.presentations() \
		.batchUpdate(presentationId=self.presentation_id, body=body).execute()
		create_slide_response = response.get('replies')[0].get('createSlide')



# presentation_id = '1HSdfhNbAkL_wCNuwtmANQXDMgeg2te1LLu_KGMNO-dY'

# sl = Slides_uploader('1HSdfhNbAkL_wCNuwtmANQXDMgeg2te1LLu_KGMNO-dY')
# sl.upload_question()