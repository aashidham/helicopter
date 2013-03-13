import BaseHTTPServer
import Cookie
import httplib2
import StringIO
import urlparse
import sys, datetime, json, hashlib, sqlite3
from collections import defaultdict
from feed.date.rfc3339 import *

from apiclient.discovery import build
from oauth2client.client import AccessTokenRefreshError
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.file import Storage

flow = OAuth2WebServerFlow("771424049558.apps.googleusercontent.com","66_YXKM5FfTAF02nZI3dV9Yn",['https://www.googleapis.com/auth/calendar.readonly','https://www.googleapis.com/auth/userinfo.email'],redirect_uri='http://helicopter-app.com/callback')

def login():
	return flow.step1_get_authorize_url()

def callback(code):
	credentials = flow.step2_exchange(code)
	http = httplib2.Http()
	http = credentials.authorize(http)
	service = build('calendar', 'v3', http=http)
	user_info_service = build('oauth2','v2',http=http)
	now = datetime.datetime.utcnow()
	later = now + datetime.timedelta(days=14)
	before = now - datetime.timedelta(days=1)
	
	now = now.isoformat("T")+"Z"
	later = later.isoformat("T")+"Z"
	before = before.isoformat("T")+"Z"
	request = service.events().list(calendarId='primary',timeMax=later,timeMin=now,singleEvents="true")
	toReturn = []
	while request != None:
		response = request.execute()
		for event in response.get('items', []):
			start = tf_from_timestamp(event["start"]["dateTime"])*1000
			end = tf_from_timestamp(event["end"]["dateTime"])*1000
			toReturn.append({"summary":event["summary"],"start":start,"end":end})
		request = service.events().list_next(request, response)
	email = user_info_service.userinfo().get().execute()["email"]
	toReturn = json.dumps(toReturn,sort_keys=True)
	email_hash = hashlib.sha224(email).hexdigest()
	
	conn = sqlite3.connect('example.db')
	c = conn.cursor()
	c.execute("insert or replace into events (tasks,email,data) values ((select tasks from events where email=:email),:email,:data)",{"email":email_hash,"data":toReturn})
	conn.commit()
	conn.close()
	return email_hash

	