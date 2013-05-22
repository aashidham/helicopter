#!/usr/bin/python -tt
from werkzeug.wrappers import Response, Request
from werkzeug.serving import run_simple
import posixpath, urllib, os, mimetypes, json, sqlite3
from operator import attrgetter
import get_events, datetime
import combine
import time

from feed.date.rfc3339 import *

def manage_db():
	conn = sqlite3.connect('example.db')
	conn.row_factory = sqlite3.Row
	c = conn.cursor()
	yield c
	conn.commit()
	conn.close()
	
def application(environ, start_response):
	request = Request(environ)
	path = translate_path(request.path)
	try:
		f = open(path,'rb')
	except IOError:
		if "login" in request.path: 
			response = Response()
			response.status_code = 301
			response.location = get_events.login()
			return response(environ, start_response)
		if "callback" in request.path:
			email = get_events.callback(request.args.get("code"))
			response = Response()
			response.status_code = 301
			response.location = "/static/app.html"
			response.set_cookie("blah",email,expires=datetime.datetime.now() + datetime.timedelta(days=1))
			return response(environ, start_response)
		if "addtask" in request.path:
			deadline = tf_from_timestamp(request.form["deadline"]) * 1000
			name = request.form["name"]
			hours = int(request.form["hours"])
			minutes = int(request.form["minutes"])
			duration = 3600*hours + 60*minutes
			new_task = {"summary":name,"deadline":deadline,"duration":duration}
			email = request.cookies.get("blah")
			for c in manage_db():
				c.execute("select * from events where email=?",(email,))
				curr_tasks = []
				result = c.fetchone()
				if result['tasks'] is not None:
					curr_tasks = json.loads(result['tasks'])
				curr_tasks.append(new_task)
				curr_tasks.sort(key=lambda x: x["duration"], reverse=True)
				curr_tasks.sort(key=lambda x: x["deadline"])
				c.execute("insert or replace into events (tasks,email,data) values (:tasks,:email,(select data from events where email=:email))",{"email":email,"tasks":json.dumps(curr_tasks)})
			response = Response("a")
			return response(environ, start_response)
		if "removetasks" in request.path:
			position = int(request.form["position"])
			email = request.cookies.get("blah")
			response = Response()
			for c in manage_db():
				c.execute("select * from events where email=?",(email,))
				result = c.fetchone()
				if result is not None and result['tasks'] is not None:
					curr_tasks = json.loads(result['tasks'])
					del curr_tasks[position]
					c.execute("insert or replace into events (tasks,email,data) values (:tasks,:email,(select data from events where email=:email))",{"email":email,"tasks":json.dumps(curr_tasks)})
				else:
					response.status_code = 404
			return response(environ, start_response)
		if "edittask" in request.path:
			deadline = tf_from_timestamp(request.form["deadline"]) * 1000
			name = request.form["name"]
			hours = int(request.form["hours"])
			minutes = int(request.form["minutes"])
			duration = 3600*hours + 60*minutes
			position = int(request.form["position"])
			email = request.cookies.get("blah")
			response = Response()
			for c in manage_db():
				c.execute("select * from events where email=?",(email,))
				result = c.fetchone()
				curr_tasks = json.loads(result['tasks'])
				curr_tasks[position] = {"summary":name,"deadline":deadline,"duration":duration}
				c.execute("insert or replace into events (tasks,email,data) values (:tasks,:email,(select data from events where email=:email))",{"email":email,"tasks":json.dumps(curr_tasks)})
			return response(environ, start_response)
		if "loadtasks" in request.path:
			email = request.cookies.get("blah")
			for c in manage_db():
				c.execute("select tasks from events where email=?",(email,))
				result = c.fetchone()
			tasks = json.loads(result['tasks'])
			currtime = time.time() * 1000
			for task in tasks:
				if task['deadline'] < currtime or task['duration'] == 0:
					task['showAlertPane'] = True
			response = Response(json.dumps(tasks), mimetype="application/json")
			return response(environ, start_response)
		if "loadall" in request.path:
			email = request.cookies.get("blah")
			for c in manage_db():
				c.execute("select * from events where email=?",(email,))
				result = c.fetchone()
				events = json.loads(result['data'])
				tasks = json.loads(result['tasks'])
			currtime = time.time() * 1000
			tasks = [task for task in tasks if not (task['deadline'] < currtime or task['duration'] == 0)]
			events = [combine.Thing(x) for x in events]
			tasks = [combine.Thing(x) for x in tasks]
			events = sorted(events,key=lambda k:k.start)
			tasks = sorted(tasks,key=lambda k:k.start)
			toReturn = combine.combine(events,tasks)
			toReturn = [x.__dict__ for x in toReturn]
			globalError = False
			for elem in toReturn:
				if elem["type"] != 3:
					if elem["start"] < currtime:
						globalError = True
			response = Response(json.dumps({"error":globalError,"data":toReturn}), mimetype="application/json")
			return response(environ, start_response)
		if "startstop" in request.path:
			email = request.cookies.get("blah")
			position = int(request.form["position"])
			taskInProgress = False
			for c in manage_db():
				c.execute("select tasks from events where email=?",(email,))
				tasks = json.loads(c.fetchone()['tasks'])
				for task in tasks:
					if "startedTime" in task:
						taskInProgress = True
						task["duration"] = max(task["duration"] - (time.time() - task["startedTime"]),0)
						del task["startedTime"]
						c.execute("insert or replace into events (tasks,email,data) values (:tasks,:email,(select data from events where email=:email))",{"email":email,"tasks":json.dumps(tasks)})
						break
				if not taskInProgress:
					tasks[position]["startedTime"] = time.time()
					c.execute("insert or replace into events (tasks,email,data) values (:tasks,:email,(select data from events where email=:email))",{"email":email,"tasks":json.dumps(tasks)})
			response = Response()
			return response(environ, start_response)
		# if not, 404 this sucker
		response = Response()
		response.status_code = 404
		return response(environ, start_response)
	response = Response(f.read(), mimetype=mimetypes.guess_type(request.path)[0])
	return response(environ, start_response)
	
def translate_path(path):
	# abandon query parameters
	path = path.split('?',1)[0]
	path = path.split('#',1)[0]
	path = posixpath.normpath(urllib.unquote(path))
	words = path.split('/')
	words = filter(None, words)
	path = os.getcwd()
	for word in words:
		drive, word = os.path.splitdrive(word)
		head, word = os.path.split(word)
		if word in (os.curdir, os.pardir): continue
		path = os.path.join(path, word)
	return path

"""
def guess_type(path):
   extensions_map = mimetypes.types_map.copy()
   extensions_map.update({
        '': 'application/octet-stream', # Default
        '.c': 'text/plain',
        '.h': 'text/plain',
        })
   base, ext = posixpath.splitext(path)
   print base,ext
   if ext in extensions_map:
	   return extensions_map[ext]
   ext = ext.lower()
   if ext in extensions_map:
	   return extensions_map[ext]
   else:
	   return extensions_map['']
"""

if __name__ == '__main__':
	run_simple('0.0.0.0', 80, application, use_debugger=True, use_reloader=True)