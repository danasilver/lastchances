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
from models import CrushUser as User, Crush, Match, db
from cas import CASClient
from dndlookup import lookup
import requests
import redis


redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
redis = redis.from_url(redis_url)

app = Flask(__name__)
SESSION_TYPE = 'redis'
SESSION_REDIS = redis
app.config.from_object(__name__)
Session(app)

if os.getenv('DEBUG', False):
    app.debug = True
    SERVICE_URL = 'http://localhost:5000/login'

else:
    SERVICE_URL = 'http://lastchances.herokuapp.com/login'


CAS_URL = 'https://login.dartmouth.edu/cas/'


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
        return redirect('/entry')

    return render_template('index.html')

@app.route('/entry', methods=['GET', 'POST'])
def entry():
    if not session.get('user'):
        return redirect(url_for('index'))

    user = session.get('user')
    u = User.select().where(User.username == user)[0]

    already_entered = Crush.select().where(Crush.user == u)

    if request.method == 'POST':
        entries = filter(None, request.form.getlist("entry"))

        if len(entries) > 5:
            return redirect('entry')

        captcha = request.form.get('g-recaptcha-response')

        captcha_r = requests.post('https://www.google.com/recaptcha/api/siteverify',
                                  data={'secret': '6Lcd-gcTAAAAANlxsT-ptOTxsgRiJKTGTut2VgLk',
                                        'response': captcha,
                                        'remoteip': request.remote_addr})

        if not captcha_r.json()['success']:
            return render_template('entry.html', user=user, entries=entries,
                                    already_entered=already_entered,
                                    already_entered_count=already_entered.count())

        if not any(entries):
            return redirect('entry')

        suggestions = map(lookup, entries)

        for i, entry in enumerate(entries):
            if entry not in suggestions[i]:
                return render_template('entry.html', user=user,
                                                     entries=entries,
                                                     suggestions=suggestions,
                                                     already_entered=already_entered,
                                                     already_entered_count=already_entered.count())

        for entry in entries:
            exists = Crush.select().where(Crush.user == u, Crush.crush == entry).count()
            if not exists:
                Crush.create(user=u, crush=entry)

                crush_user_exists = User.select().where(User.username == entry).count()
                if crush_user_exists:
                    crush_user = User.select().where(User.username == entry)[0]
                    crush_user_crushes = map(lambda m: m.crush, Crush.select().where(Crush.user == crush_user))
                    if crush_user and u.username in crush_user_crushes:
                        Match.create(user_1 = u, user_2 = crush_user)

        return redirect('/matches')

    return render_template('entry.html', user=user,
                            already_entered=already_entered,
                            already_entered_count=already_entered.count())

@app.route('/matches')
def matches():
    if not session.get('user'):
        return redirect('/login')

    user = User.select().where(User.username == session.get('user'))[0]

    count = Crush.select().where(Crush.crush == session.get('user')).count()

    matches_1 = map(lambda m: m.user_2.username, Match.select().where(Match.user_1 == user))
    matches_2 = map(lambda m: m.user_1.username, Match.select().where(Match.user_2 == user))

    matches_1.extend(matches_2)

    return render_template('match.html', matches=matches_1, count=count, user=user.username)

@app.route('/login')
def login():
    if session.get('user'):
        exists = User.select().where(User.username == session.get('user')).count()
        print exists
        if not exists:
            User.create(username=session.get('user'))
        return redirect(url_for('entry'))

    cas = CASClient(CAS_URL, SERVICE_URL)
    id = cas.Authenticate(request.args.get('ticket', None))

    if id:
        session['user'] = id[:id.find('@')]
        exists = User.select().where(User.username == session.get('user')).count()
        print exists
        if not exists:
            User.create(username=session.get('user'))
        return redirect(url_for('entry'))

    return redirect(CAS_URL + 'login?service=' + urllib.quote(SERVICE_URL))

@app.route('/logout')
def logout():
    if session.get('user'):
        session.clear()

    return redirect(url_for('index'))
