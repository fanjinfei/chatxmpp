from flask import Flask, request
from flask import make_response, current_app
from flask import render_template, redirect, g, url_for, abort
from flask import send_from_directory
from flask import Response
import requests
from datetime import timedelta
from functools import update_wrapper

app = Flask("demo")

def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator

@app.route('/<path:path>', methods=['POST', 'GET'])
def proxy(path):
  cookies = request.cookies
  dj = dict(cookies)
  s = requests.Session()
  try:
      if request.method == 'GET':
        res = s.get('http://localhost:5280/{path}'.format(path=path), cookies=dj)
        if "NotfoundAction_index_Form" in res.content or res.status_code != requests.codes.ok:
            return "Not found", 404
        response = make_response(res.content, 200)
        response.headers['Content-type'] = res.headers['Content-type']
        for k,v in dict(s.cookies).items():
            response.set_cookie(k,v)
        return response
      else:
        request.get_data()
        data = request.data
        res =  s.post('http://localhost:5280/{path}'.format(path=path), data=data, cookies=dj)
        response = make_response(res.content, 200)
        for k,v in dict(s.cookies).items():
            response.set_cookie(k,v)
        print(data)
        print(res.content)
        return response
  except:
        return  "Not found", 404

@app.route("/")
@crossdomain(origin='*')
def root_index():
#	return "hello"
	return render_template('index.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
