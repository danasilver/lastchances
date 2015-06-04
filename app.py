import urllib
import os
from flask import ( Flask,
                    render_template,
                    request,
                    g,
                    session,
                    redirect,
                    url_for)
from flask.ext.session import Session
from models import User, Crush, Match, db
from cas import CASClient
from dnd import fetch as dnd

app = Flask(__name__)
SESSION_TYPE = 'redis'
app.config.from_object(__name__)
Session(app)
app.debug = True



CAS_URL = 'https://login.dartmouth.edu/cas/'
SERVICE_URL = 'http://localhost:5000/login'

@app.before_request
def before_request():
    g.db = db
    g.db.connect()

@app.after_request
def after_request(response):
    g.db.close()
    return response

@app.route('/')
def index():
    if session.get('user'):
        return session.get('user')

    return render_template('index.html')

@app.route('/entry')
def entry():
    if not session.get('user'):
        return redirect(url_for('index'))

    return render_template('entry.html')

@app.route('/login')
def login():
    if session.get('user'):
        return redirect(url_for('entry'))

    cas = CASClient(CAS_URL, SERVICE_URL)
    id = cas.Authenticate(request.args.get('ticket', None))

    if id:
        session['user'] = id[:id.find('@')]
        print session.get('user')
        return redirect(url_for('entry'))

    return redirect(CAS_URL + 'login?service=' + urllib.quote(SERVICE_URL))
