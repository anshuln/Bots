import json
import pickle
import time
import uuid
import base64

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


def scrape_email(filename):
    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)
        service = build('gmail', 'v1', credentials=creds)

    message = service.users().messages().list(userId="me", q="filename:txt from:anshulnasery@gmail.com has:attachment",maxResults=1).execute()
    msg_id = message['messages'][0]['id']

    message = service.users().messages().get(userId="me", id=msg_id).execute()

    for part in message['payload'].get('parts', ''):
        if part['filename'] and part['filename']==filename:
            if 'data' in part['body']:
                data=part['body']['data']
            else:
                att_id=part['body']['attachmentId']
                att=service.users().messages().attachments().get(userId="me", messageId=msg_id,id=att_id).execute()
                data=att['data']
            file_data = base64.urlsafe_b64decode(data.encode('UTF-8'))
            path = 'messages.txt'

            with open(path, 'wb') as f:
                f.write(file_data)

    service.users().messages().delete(userId="me", id=msg_id).execute()

