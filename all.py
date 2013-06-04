#!/usr/bin/python -tt
from werkzeug.wrappers import Response, Request
from werkzeug.serving import run_simple
import posixpath, urllib, os, mimetypes, json, sqlite3
from operator import attrgetter
import get_events, datetime
import combine
import time
import itertools

from feed.date.rfc3339 import *

def manage_db():
	conn = sqlite3.connect('example.db')
	conn.row_factory = sqlite3.Row
	c = conn.cursor()
	yield c
	conn.commit()
	conn.close()

def coalesce_blocking(l):
	while True:
		hit = False
		for a,b in itertools.combinations(range(len(l)),2):
			if l[a]["end"] > l[b]["start"] and l[a]["start"] < l[b]["end"]:
				hit = True
				elema = l[a]
				elemb = l[b]
				del l[b]
				del l[a]
				l.append({"start":min(elema["start"],elemb["start"]),"end":max(elema["end"],elemb["end"])})
				break
		if not hit:
			break
	return l

	
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
			repeat = request.form["repeat"]
			new_task = {"summary":name,"deadline":deadline,"duration":duration,"repeat":repeat}
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
			repeat = request.form["repeat"]
			email = request.cookies.get("blah")
			response = Response()
			for c in manage_db():
				c.execute("select * from events where email=?",(email,))
				result = c.fetchone()
				curr_tasks = json.loads(result['tasks'])
				curr_tasks[position] = {"summary":name,"deadline":deadline,"duration":duration,"repeat":repeat}
				curr_tasks.sort(key=lambda x: x["duration"], reverse=True)
				curr_tasks.sort(key=lambda x: x["deadline"])
				c.execute("insert or replace into events (tasks,email,data) values (:tasks,:email,(select data from events where email=:email))",{"email":email,"tasks":json.dumps(curr_tasks)})
			return response(environ, start_response)
		if "repeattask" in request.path:
			position = int(request.form["position"])
			email = request.cookies.get("blah")
			response = Response()
			for c in manage_db():
				c.execute("select * from events where email=?",(email,))
				result = c.fetchone()
				curr_tasks = json.loads(result['tasks'])
				repeat = curr_tasks[position]["repeat"]
				if repeat == "weekly":
					curr_tasks[position]["deadline"] += 604800000
				if repeat == "daily":
					curr_tasks[position]["deadline"] += 86400000
				curr_tasks.sort(key=lambda x: x["duration"], reverse=True)
				curr_tasks.sort(key=lambda x: x["deadline"])
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
			tasks = sorted(tasks,key=lambda k:k.end)
			toReturn = combine.combine(events,tasks)
			toReturn = [x.__dict__ for x in toReturn]
			
			freetime = 0
			latestTime = 0
			for elem in toReturn:
				if elem["type"] != 3:
					latestTime = elem["start"]
					break
			if latestTime == 0:
				response = Response(json.dumps({"data":toReturn,"firstBlock":[]}), mimetype="application/json")
				return response(environ, start_response)
			else:
				if latestTime < currtime:
					freetime = latestTime - currtime
				else:
					blocking_duration = 0
					blocking_events = []
					for elem in toReturn:
						if elem["end"] < latestTime and currtime < elem["end"]:
							blocking_events.append(elem)
					blocking_events = coalesce_blocking(blocking_events)
					for elem in blocking_events:
							blocking_duration = blocking_duration + elem["end"] - elem["start"]
							if elem["start"] < currtime:
								blocking_duration = blocking_duration - (currtime - elem["start"])
					freetime = latestTime - currtime - blocking_duration
				first_block_names = []
				for elem in toReturn:
					if "firstBlock" in elem:
						first_block_names.append(elem["name"])
				first_block_names = list(set(first_block_names))
				response = Response(json.dumps({"data":toReturn,"firstBlock":first_block_names,"freetime":freetime}), mimetype="application/json")
				return response(environ, start_response)
		if "startstop" in request.path:
			email = request.cookies.get("blah")
			position = int(request.form["position"])
			taskInProgress = False
			for c in manage_db():
				c.execute("select tasks from events where email=?",(email,))
				tasks = json.loads(c.fetchone()['tasks'])
				for idx,task in enumerate(tasks):
					if "startedTime" in task:
						if idx == position:
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