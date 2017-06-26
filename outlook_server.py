import os
import urllib.request
import urllib.parse
import webbrowser
import requests
import requests.auth
from requests_oauthlib import OAuth2Session
import json
import threading
import time

from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import jsonify
app = Flask(__name__)

client_id = os.environ['CALENDAR_API_TEST_ID']
client_secret = os.environ['CALENDAR_API_TEST_PASSWORD']

authority = 'https://login.microsoftonline.com'
authorize_url = '{0}{1}'.format(authority, '/common/oauth2/v2.0/authorize?{0}')
token_url = '{0}{1}'.format(authority, '/common/oauth2/v2.0/token')
redirect_uri = 'http://localhost:8000/gettoken'
scopes = ['User.Read', 'Mail.Read', 'Calendars.Read']

outlook = OAuth2Session(client_id,scope=scopes,redirect_uri=redirect_uri)
authorization_url, state = outlook.authorization_url(authorize_url)

token = ''
graph_endpoint = 'https://graph.microsoft.com/v1.0{0}'

@app.route("/")
def hello():
    return redirect(authorization_url)

def query(route, token):
    headers = {
        "Authorization": "Bearer {0}".format(token['access_token']),
        "Content-Type": "application/json"
    }
    o = requests.get(graph_endpoint.format(route), headers=headers)
    return o.content

@app.route("/gettoken")
def gettoken():
    code = request.args.get('code')
    if (not code):
        return redirect("/")
    client_auth = requests.auth.HTTPBasicAuth(client_id, client_secret)
    post_data = {
        'grant_type': 'authorization_code',
        'code': code,
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri
    }
    response = requests.post(token_url,
                             auth=client_auth,
                             data=post_data)
    token = response.json()
    print(query('/me', token))
    print(query('/me/events', token))
    return render_template("logged_in.html")

URL = 'http://localhost:8000'

def start_browser():
    print("[Browser Thread] waiting for server to start")
    while True:
        try:
            urllib.request.urlopen(url=URL)
            break
        except Exception as e:
            print(e)
            time.sleep(0.5)
    print("[Browser Thread] opening browser")
    webbrowser.open(URL)

threading.Thread(target=start_browser).start()

app.run(host='localhost', port=8000)
