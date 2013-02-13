#!/usr/bin/python -tt
from werkzeug.wrappers import Response, Request
from werkzeug.serving import run_simple
import posixpath, urllib, os, mimetypes, json

def do_py_stuff(environ, start_response):
	request = Request(environ)
	return json.dumps({"date":request.args.get("date")})
	
def application(environ, start_response):
	request = Request(environ)
	path = translate_path(request.path)
	try:
		f = open(path,'rb')
	except IOError:
		response = Response("404!", mimetype='text/html')
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