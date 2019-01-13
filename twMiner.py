import random
import re
import string
import sys
from flask import Flask, render_template, request, redirect

sys.path.append('static/funct')
from results import twResults
from misc import writeLog, emailResults, sendPW
from dbconn import userlogin, usercreate, userget, update_plan,\
    add_term, update_pw, get_terms, get_mech

session = {}
session['logged_in'] = False
app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def home():
    error = None
    if request.method == 'POST':
        if request.form['term'] == '':
            error = 'Please enter a search term below:'
        else:
            search_term = request.form['term']
            result_type = request.form.getlist('rtype')
            retweets = request.form.getlist('rtweet')
            if len(result_type) > 0:
                result_type = 'popular'
            else:
                result_type = 'mixed'
            print result_type
            if len(retweets) > 0:
                retweets = False
            else:
                retweets = True
            action = 'TERM: %s, TYPE: %s, RT: %s' % (search_term,
                                                     result_type,
                                                     retweets)
            writeLog('INFO', action)
            result = twResults(search_term, result_type, retweets=retweets)
            session['keyword'] = search_term
            session['words'] = result.out_words
            session['users'] = result.out_users
            session['hashtags'] = result.out_hashtags
            session['dates'] = result.out_dates
            session['tweets'] = result.out_tweets
            session['num_tweets'] = result.num_tweets
            session['email'] = result.email_text
            return redirect('result')
    return render_template('home.html', error=error)


@app.route('/result', methods=['GET', 'POST'])
def result():
    error = None
    if request.method == 'POST':
        if request.form['userEmail'] == '':
            error = 'Please enter your email to send results.'
        else:
            userEmail = request.form['userEmail']
            emailResults(userEmail, session['email'])
            action = 'Results emailed: %s' % userEmail
            writeLog('INFO', action)
            return render_template('thanks.html', message='results')
        writeLog('INFO', 'Results page rendered')
    return render_template('results.html', data=session, error=error)


@app.route('/thanks')
def thanks(message):
    writeLog('INFO', 'Thanks page rendered')
    return render_template('thanks.html', message=message)


@app.route('/instructions')
def instructions():
    writeLog('INFO', 'Instruction page rendered')
    return render_template('instructions.html')


@app.route('/about')
def about():
    writeLog('INFO', 'About page rendered')
    return render_template('about.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    error = None
    if session['logged_in'] is True:
        return redirect('account')
    else:
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']
            data = {'email': email, 'password': password}
            if userlogin(data) is True:
                session['logged_in'] = True
                info = userget(email)
                session['email'] = email
                session['plan'] = info['plan']
                return redirect('account')
            else:
                error = 'Invalid username/password'
                return render_template('login.html', error=error)
        return render_template('login.html', error=error)


@app.route('/recover', methods=['GET', 'POST'])
def recover():
    error = None
    if request.method == 'GET':
        return render_template('recover.html', error=error)
    elif request.method == 'POST':
        email = request.form['email']
        if email == '':
            error = 'Please enter your email to reset pw.'
        elif userget(email) == []:
            error = 'Please enter a valid email address.'
        else:
            code = ''.join(random.choice(string.ascii_uppercase +
                           string.digits) for _ in range(8))
            data = {'email': email, 'password': code}
            update_pw(data)
            sendPW(email, code)
            action = 'Password recovered for %s' % email
            writeLog('INFO', action)
            return render_template('thanks.html', message='your new password')
            writeLog('INFO', 'Results page rendered')
        return render_template('recover.html', error=error)


@app.route('/account', methods=['POST', 'GET'])
def account():
    error = None
    if session['logged_in'] is True:
        if request.method == 'POST':
            password = request.form['password']
            if password != '****':
                data = {'email': session['email'],
                        'password': password}
                update_pw(data)
            terms = []
            terms.append(request.form['terma'])
            if session['plan'] == 'silver':
                terms.append(request.form['termb'])
                terms.append(request.form['termc'])
                terms.append(request.form['termd'])
                terms.append(request.form['terme'])
            elif session['plan'] == 'gold':
                terms.append(request.form['termb'])
                terms.append(request.form['termc'])
                terms.append(request.form['termd'])
                terms.append(request.form['terme'])
                terms.append(request.form['termf'])
                terms.append(request.form['termg'])
                terms.append(request.form['termh'])
                terms.append(request.form['termi'])
                terms.append(request.form['termj'])
            data = {'email': session['email'],
                    'plan': session['plan'],
                    'terms': terms}
            add_term(data)
            return render_template('account.html',
                                   email=session['email'],
                                   plan=session['plan'],
                                   terms=terms,
                                   error=error)
        elif request.method == 'GET':
            terms = get_terms(session['email'])
            return render_template('account.html',
                                   email=session['email'],
                                   plan=session['plan'],
                                   terms=terms,
                                   error=error)
    elif session['logged_in'] is False:
        return redirect('login')


@app.route('/subscribe', methods=['POST', 'GET'])
def subscribe():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']
        data = {'email': email, 'password': password}
        if password != verify:
            error = 'Password and verify do not match'
        elif len(userget(email)) > 0:
            error = 'Email address already exists'
        elif not re.match(r'.+@.+\..+', email):
            error = 'Please enter a valid email address'
        else:
            if usercreate(data) is True:
                session['logged_in'] = True
                session['email'] = email
                return redirect('plan')
    return render_template('subscribe.html', error=error)


@app.route('/plan', methods=['POST', 'GET'])
def plan():
    if session['logged_in'] is True:
        if request.method == 'POST':
            plan = request.form.get('plan')
            session['plan'] = plan
            data = {'email': session['email'], 'plan': session['plan']}
            update_plan(data)
            return redirect('payment')
        else:
            return render_template('plan.html')
    else:
        return redirect('subscribe')


@app.route('/payment', methods=['POST', 'GET'])
def payment():
    if session['logged_in'] is True:
        error = None
        if 'plan' in session:
            plan = session['plan']
            if plan == 'bronze':
                return redirect('account')
            return render_template('payment.html', plan=plan, error=error)
        else:
            plan = 'unknown'
            error = 'Please go back and reselect plan!'
            return render_template('payment.html', plan=plan, error=error)


@app.route('/api')
def api():
    if session['logged_in'] is True:
        if session['email'] == 'info@basexvi.com':
            return render_template('api.html', session=session)
        else:
            return redirect('/')
    else:
        return redirect('/')


@app.route('/logout')
def logout():
    session = {}
    session['logged_in'] = False
    return redirect('/')


@app.route('/mech')
def mech():
    if session['logged_in'] is True:
        if session['email'] == 'info@basexvi.com':
            data = get_mech()
            return render_template('mech.html', data=data)
        else:
            return redirect('login')
    else:
        return redirect('login')


if __name__ == '__main__':
    app.run(debug=True)
    # app.run()
