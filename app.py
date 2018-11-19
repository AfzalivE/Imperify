# External imports
from flask import Flask, redirect, request, url_for
from urllib.parse import quote
import requests
import base64
import json

# Local imports
from settings import Settings
from credentials import my_client_id, my_client_secret, device_transfer_id

app = Flask(__name__)
auth_redirect_uri = 'http://localhost:5000/success'
scopes = 'user-read-playback-state user-modify-playback-state'
settings = Settings()

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/devices')
def devices():
    token = settings.get_token()
    if (type(token) == type(None)):
        return redirect(url_for('login'))

    # refresh token when expired

    print("Access token: " + token["access_token"])
    headers = { "Authorization" : "Bearer " + token["access_token"] }
    res = requests.get("https://api.spotify.com/v1/me/player/devices", headers=headers)
    return res.content

@app.route('/transfer')
def transfer():
    token = settings.get_token()
    if (type(token) == type(None)):
        return "no token"
        # return redirect(url_for('login'))

    id = device_transfer_id
    headers = { "Authorization" : "Bearer " + token["access_token"] }
    res = requests.put("https://api.spotify.com/v1/me/player", data=json.dumps({
        "device_ids": [id]
    }), headers=headers)
    print(res.request.body)
    return str(res.status_code)

@app.route('/refresh_token')
def refresh_token():
    access_token = settings.get_token()
    if (type(access_token) == type(None)):
        return redirect(url_for('login'))

    print("Access token: " + settings.get_token())
    response = requests.post("https://accounts.spotify.com/api/token", data={
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }, auth=(my_client_id, my_client_secret)).content

    settings.set_token(response)
    return redirect(url_for('devices'))

@app.route('/success')
def success():
    code = request.args.get('code')
    response = requests.post("https://accounts.spotify.com/api/token", data={
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": auth_redirect_uri
    }, auth=(my_client_id, my_client_secret))
    settings.set_token(response.text)
    return redirect(url_for('devices'))

@app.route('/login')
def login():
    return redirect('https://accounts.spotify.com/authorize' +
    '?response_type=code' +
    '&client_id=' + my_client_id +
    '&scope=' + quote(scopes.encode("utf-8")) +
    '&redirect_uri=' + quote(auth_redirect_uri.encode("utf-8")))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
