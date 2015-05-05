from flask import Flask, redirect, request, session, g, render_template, abort, send_from_directory
from werkzeug.utils import secure_filename
import os
import sqlite3
import time

app = Flask(__name__)
app.config.from_object(__name__)
# Load default config and override config from an environment variable
app.config.update(dict(
	DATABASE=os.path.join(app.root_path, 'codiyapa.db'),
	DEBUG=True,
	SECRET_KEY='development key',
	USERNAME='admin',
	PASSWORD='#app2py9c&go',
	UPLOAD_FOLDER='/home/sourya/VProgramming/codiyapa/uploads/',
	ALLOWED_EXTENSIONS = set(['txt', 'c', 'cpp', 'java', 'py'])
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

userkeys = {'supersourya'	: '#brainf#ck'}# add all usernames and passwords in this dict

def connect_db():
	rv = sqlite3.connect(app.config['DATABASE'])
	rv.row_factory = sqlite3.Row
	return rv

def get_db():
	if not hasattr(g, 'sqlite_db'):
		g.sqlite_db = connect_db()
	return g.sqlite_db

def allowed_file(filename):
	return ('.' in filename and filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']) or ('.' not in filename)

@app.route('/')
def home():
	username = None
	if 'loggedin' in session:
		loggedin = session['loggedin']
		username = session['username']
	else:
		loggedin = False
	var = {'loggedin': loggedin, 'error': None, 'username': username}
	return render_template('home.html', var=var)
	
@app.route('/login', methods=['POST'])
def login():
	error = None
	loggedin = False
	username = None
	if request.method == "POST":
		username = request.form['username']
		password = request.form['password']
		if username not in userkeys:
			error = "Invalid Username"
		elif username in userkeys and userkeys[username] != password:
			error = "Invalid password"
		else:
			loggedin = True
			session['loggedin'] = True
			session['username'] = username
	return redirect('/')

@app.route('/logout')
def logout():
	if 'username' in session:
		session.pop('username')
		session.pop('loggedin')
	
	return redirect('/')

@app.route('/problems/<question>')
def problem_show(question):
	username = None
	if 'loggedin' in session:
		loggedin = session['loggedin']
		username = session['username']
	else:
		loggedin = False
	if (question in ['prob1', 'prob2', 'prob3']):
		ques = question + '.html'
		var = {'loggedin': loggedin, 'error': None, 'username': username}
		return render_template(ques, var=var)
	else:
		abort(404)

@app.route('/ranklist')
def rank_show():
	db = get_db()
	username = None
	if 'loggedin' in session:
		loggedin = session['loggedin']
		username = session['username']
	else:
		loggedin = False
	ranks = db.execute('select username, score, prob1, prob2, prob3 from coders order by score desc').fetchall()
	var = {'loggedin': loggedin, 'ranks': ranks, 'username': username}
	return render_template('ranklist.html', var=var)

@app.route('/submit/<question>')
def submit(question):
	username = None
	if 'loggedin' in session:
		loggedin = session['loggedin']
		username = session['username']
	else:
		loggedin = False
	
	if (question in ['prob1', 'prob2', 'prob3']):
		var = {'loggedin': loggedin, 'error': None, 'prob_code': question, 'username': username}
		return render_template('submit.html', var=var)
	else:
		abort(404)

@app.route('/result', methods=['POST'])
def result():
	username = None
	if 'loggedin' in session:
		loggedin = session['loggedin']
		username = session['username']
	else:
		loggedin = False
	error = None
	var = {'loggedin': loggedin, 'error': error, 'username': username}
	
	if request.method == "POST":
		usercode = request.files['usercode']
		useroutput = request.files['useroutput']
	
		if (usercode and allowed_file(usercode.filename)) and (useroutput and allowed_file(useroutput.filename)):
			codefilename = session['username']+request.form['prob_code']+'code'
			usercode.save(os.path.join(app.config['UPLOAD_FOLDER'], codefilename))
		
			outfilename = session['username']+request.form['prob_code']+'out'
			useroutput.save(os.path.join(app.config['UPLOAD_FOLDER'], outfilename))
			
			var['code_error'] = check(request.form['prob_code'])
			
			if var['code_error']:
				write_to_db(-1, request.form['prob_code'])
			else:
				write_to_db(1, request.form['prob_code'])
			
			return render_template('results.html', var=var)
			
		else:
			var['error'] = "Submit both your code file and your output file."
			return render_template('submit.html', var=var)
	else:
		return render_template('submit.html', var=var)


def check(prob_code):
	correct = open('./outfile/%s'%prob_code).readlines()
	userout = open(app.config['UPLOAD_FOLDER'] + session['username'] + prob_code + 'out').readlines()
	if len(correct) != len(userout):
		return "Wrong answer"

	i = 0
	while i < len(correct):
		if correct[i] != userout[i]:
			return "Wrong answer"
		i += 1

	if i >= len(correct):
		return None

@app.route('/inputfile/<number>')
def input_file(number):
	return send_from_directory('infile', str(number))

def write_to_db(code, prob_code):
	db = get_db()
	prob_code = str(prob_code)
	
	#print "Yo!", db.execute('select score from coders where username = ?', [session['username']]).fetchone()[0]
	score = int(db.execute('select score from coders where username = ?', [session['username']]).fetchone()[0])
	print score
	#print db.execute('select ? from coders where username = ?', [prob_code, session['username']]).fetchone()
	if (prob_code == 'prob1'):
		mytime = str(db.execute('select prob1 from coders where username = ?', [session['username']]).fetchone()[0])
	elif (prob_code == 'prob2'):
		mytime = str(db.execute('select prob2 from coders where username = ?', [session['username']]).fetchone()[0])
	elif (prob_code == 'prob3'):
		mytime = str(db.execute('select prob3 from coders where username = ?', [session['username']]).fetchone()[0])
	
	print mytime
	#print "mytime = ", mytime
	if code == 1:
		if str(mytime) == '0':
			score += 100
			print score
			if (prob_code == 'prob1'):
				db.execute('update coders set prob1 = ? where username = ?', [str(time.time()), session['username']])
			elif (prob_code == 'prob2'):
				db.execute('update coders set prob2 = ? where username = ?', [str(time.time()), session['username']])
			elif (prob_code == 'prob3'):
				db.execute('update coders set prob3 = ? where username = ?', [str(time.time()), session['username']])
	else:
		score -= 10
	db.execute('update coders set score = ? where username = ?', [score, session['username']])
	db.commit()

from base import app

if __name__ == '__main__':
	app.run('0.0.0.0')
