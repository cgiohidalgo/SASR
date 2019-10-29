import sys, os
import shlex, subprocess
from flask import Flask, flash, url_for, render_template, request, redirect, session, make_response
from flask_sqlalchemy import SQLAlchemy
from werkzeug import secure_filename
from flask_caching import Cache
from functools import wraps, update_wrapper
from datetime import datetime


app = Flask(__name__, static_url_path='/static')
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
#cache = Cache(app, config={'CACHE_TYPE': 'simple'})
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['UPLOAD_FOLDER'] = os.getcwd()+"/{}/{}/".format("static","upload")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
ALLOWED_EXTENSIONS = set(['bib','ris'])
# change to "redis" and restart to cache again

# some time later

# change to "redis" and restart to cache again

# some time later

# All caching functions will simply call through
# to the wrapped function, with no caching
# (since NullCache does not cache).

def nocache(view):
    @wraps(view)
    def no_cache(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers['Last-Modified'] = datetime.now()
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response
        
    return update_wrapper(no_cache, view)

class User(db.Model):
	""" Create user table"""
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(80), unique=True)
	password = db.Column(db.String(80))

	def __init__(self, username, password):
		self.username = username
		self.password = password


@app.route('/', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
@nocache
def home():
	""" Session control"""
	if not session.get('logged_in'):
		return render_template('login.html')
	else:
		if request.method == 'POST':
			username = getname(request.form['username'])
			return render_template('index.html', data=getfollowedby(username))
		return render_template('index.html')

@app.route('/access', methods=['GET', 'POST'])
@nocache
def graphs():
	""" Session control"""
	if not session.get('logged_in'):
		return render_template('login.html')
	else:
		if request.method == 'POST':
			username = getname(request.form['username'])
			return render_template('access.html', data=getfollowedby(username))
		return render_template('access.html')

@app.route('/coauthor', methods=['GET', 'POST'])
@nocache
def graphs1():
	""" Session control"""
	if not session.get('logged_in'):
		return render_template('login.html')
	else:
		if request.method == 'POST':
			username = getname(request.form['username'])
			return render_template('coauthor.html', data=getfollowedby(username))
		return render_template('coauthor.html')

@app.route('/tree', methods=['GET', 'POST'])
@nocache
def graphs2():
	""" Session control"""
	if not session.get('logged_in'):
		return render_template('login.html')
	else:
		if request.method == 'POST':
			username = getname(request.form['username'])
			return render_template('tree.html', data=getfollowedby(username))
		return render_template('tree.html')

@app.route('/treemap', methods=['GET', 'POST'])
@nocache
def graphs3():
	""" Session control"""
	if not session.get('logged_in'):
		return render_template('login.html')
	else:
		if request.method == 'POST':
			username = getname(request.form['username'])
			return render_template('treemap.html', data=getfollowedby(username))
		return render_template('treemap.html')

@app.route('/data', methods=['GET', 'POST'])
@nocache
def data():
	""" Session control"""
	if not session.get('logged_in'):
		return render_template('login.html')
	else:
		if request.method == 'POST':
			username = getname(request.form['username'])
			return render_template('data.html', data=getfollowedby(username))
		return render_template('data.html')


@app.route('/login', methods=['GET', 'POST'])
@nocache
def login():
	"""Login Form"""
	if request.method == 'GET':
		return render_template('login.html')
	else:
		name = request.form['username']
		passw = request.form['password']
		#try:
		data = User.query.filter_by(username=name, password=passw).first()
		if data is not None:
			session['logged_in'] = True
			return redirect(url_for('home'))
		else:
			return redirect(url_for('home'))
		#except:
		#	return "Dont Login"

@app.route('/register/', methods=['GET', 'POST'])
@nocache
def register():
	"""Register Form"""
	if request.method == 'POST':
		new_user = User(username=request.form['username'], password=request.form['password'])
		db.session.add(new_user)
		db.session.commit()
		return render_template('login.html')
	return render_template('register.html')

@app.route("/logout")
@nocache
def logout():
	"""Logout Form"""
	session['logged_in'] = False
	return redirect(url_for('home'))

@nocache
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/upload", methods=['POST'])
@nocache
def uploader():
	if request.method == 'POST':	 	
		if 'archivo' in request.files:
			file = request.files['archivo']
			file_path = os.path.join(app.config['UPLOAD_FOLDER'], "1.bib")
			file.save(file_path)
			process = subprocess.Popen('python3 ./static/upload/BIB2CSV.py', shell=True, stdout=subprocess.PIPE)
			print (process.returncode)
			flash('File upload completly! :)')
			return render_template('index.html', data=None)
		else:
			flash('File not found:)')
			process = subprocess.Popen('python3 /static/upload/BIB2CSV.py', shell=True, stdout=subprocess.PIPE)
		print (process.returncode)
			#file = request.files['archivo']
		return render_template('index.html', data=None)
	 	
	 	# if file.filename == '':
	 	# 	flash('No selected file')
	 	# 	return 
	 	# if file and allowed_file(file.filename):
	 	# 	filename = secure_filename(file.filename)
	 	# 	file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
	 	# 	print("./upload/"+filename)
	 	# 	archivo = "./upload/"+filename
	 	# 	os.rename(archivo, './static/upload/1.bib')

	 	
	 		#Aqui para ejecutar un comando de python 
	 		#process = subprocess.Popen('python3 ./static/upload/BIB2CSV.py', shell=True, stdout=subprocess.PIPE)
	 		#process = subprocess.Popen('python3 bibtex2bibjson.py ../SASR/static/upload/1.bib > ../SASR/static/upload/1.json', shell=True, stdout=subprocess.PIPE)
	 	#print (process.returncode)
	 	#return render_template('index.html')

 #return cosole.log(filename);

#os.rename(a,a1)

if __name__ == '__main__':
	app.debug = True
	db.create_all()
	app.secret_key = "xtjsuA38383"
	app.run(host='0.0.0.0', port='80')
