#!/usr/bin/python -tt
from werkzeug.wrappers import Response, Request
from werkzeug.serving import run_simple
import posixpath, urllib, os, mimetypes, json
import get_events, sqlite3

from feed.date.rfc3339 import *

def do_py_stuff(environ, start_response):
	request = Request(environ)
	email = request.form.get("blah")
	conn = sqlite3.connect('example.db')
	conn.row_factory = sqlite3.Row
	c = conn.cursor()
	c.execute("select data from events where email=?",(email,))
	toReturn = c.fetchone()['data']
	conn.commit()
	conn.close()
	return toReturn

	
def application(environ, start_response):
	request = Request(environ)
	path = translate_path(request.path)
	try:
		f = open(path,'rb')
	except IOError:
		# check if url is one of the accepted ones
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
			response.set_cookie("blah",email)
			return response(environ, start_response)	
		# if not, 404 this sucker
		response = Response()
		response.status_code = 404
		return response(environ, start_response)
	if posixpath.splitext(path)[1] == ".py":
		json = do_py_stuff(environ, start_response)
		response = Response(json, mimetype="application/json")
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