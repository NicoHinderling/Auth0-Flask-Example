import json
import os
import requests
from functools import wraps
from dotenv import Dotenv
from flask import Flask, redirect, render_template, \
    request, send_from_directory, session

import constants

# Load Env variables
env = None

try:
    env = Dotenv('./.env')
except IOError:
    env = os.environ

app = Flask(__name__, static_url_path='')
app.secret_key = constants.SECRET_KEY
app.debug = True

# Requires authentication annotation
def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if constants.PROFILE_KEY not in session:
            return redirect('/')
        return f(*args, **kwargs)
    return decorated

# Controllers API
@app.route('/')
def index():
    return render_template('index.html', env=env)

@app.route('/home')
def home():
    return render_template('home.html', env=env)

@app.route('/dashboard')
@requires_auth
def dashboard():
    return render_template('dashboard.html', user=session[constants.PROFILE_KEY])

@app.route('/public/<path:filename>')
def static_files(filename):
    return send_from_directory('./public', filename)

@app.route('/callback')
def callback_handling():
    code = request.args.get(constants.CODE_KEY)
    json_header = {constants.CONTENT_TYPE_KEY: constants.APP_JSON_KEY}
    token_url = 'https://guestmealme.auth0.com/oauth/token'.format(domain=env[constants.AUTH0_DOMAIN])
    token_payload = {
        constants.CLIENT_ID_KEY : env[constants.AUTH0_CLIENT_ID],
        constants.CLIENT_SECRET_KEY : env[constants.AUTH0_CLIENT_SECRET],
        constants.REDIRECT_URI_KEY : env[constants.AUTH0_CALLBACK_URL],
        constants.CODE_KEY : code,
        constants.GRANT_TYPE_KEY : constants.AUTHORIZATION_CODE_KEY
    }

    token_info = requests.post(token_url, data=json.dumps(token_payload),
                               headers=json_header).json()
    user_url = 'https://guestmealme.auth0.com/userinfo?access_token={access_token}'.format(
        domain=env[constants.AUTH0_DOMAIN], access_token=token_info[constants.ACCESS_TOKEN_KEY])
    user_info = requests.get(user_url).json()
    session[constants.PROFILE_KEY] = user_info
    return redirect('/dashboard')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 3000)))

