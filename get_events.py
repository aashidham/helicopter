import BaseHTTPServer
import Cookie
import httplib2
import StringIO
import urlparse
import sys, datetime, json
from collections import defaultdict
from feed.date.rfc3339 import *

from apiclient.discovery import build
from oauth2client.client import AccessTokenRefreshError
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.file import Storage

flow = OAuth2WebServerFlow("771424049558.apps.googleusercontent.com","66_YXKM5FfTAF02nZI3dV9Yn",'https://www.googleapis.com/auth/calendar',redirect_uri='http://helicopter-app.com/callback')

def login():
	return flow.step1_get_authorize_url()

def callback(code):
	credentials = flow.step2_exchange(code)
	http = httplib2.Http()
	http = credentials.authorize(http)
	service = build('calendar', 'v3', http=http)
	#now = datetime.datetime.utcnow().isoformat("T")+"Z"
	#later = datetime.datetime.utcnow()+datetime.timedelta(days=14)
	#later = later.isoformat("T")+"Z"
	now = datetime.datetime.utcnow()
	later = now + datetime.timedelta(days=14)
	before = now - datetime.timedelta(days=1)
	later = later.isoformat("T")+"Z"
	before = before.isoformat("T")+"Z"
	request = service.events().list(calendarId='primary',timeMax=later,timeMin=before,singleEvents="true")
	toReturn = defaultdict(list)
	while request != None:
		response = request.execute()
		for event in response.get('items', []):
			epoch_seconds = tf_from_timestamp(event["start"]["dateTime"])
			currdate = datetime.date.fromtimestamp(epoch_seconds)
			currdate = currdate.isoformat()
			toReturn[currdate].append({"summary":event["summary"],"start":event["start"]["dateTime"],"end":event["end"]["dateTime"]})
		request = service.events().list_next(request, response)
	return json.dumps(toReturn,sort_keys=True)