import os
import shlex, subprocess
from flask import Flask, flash, url_for, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug import secure_filename
from flask_caching import Cache


app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['UPLOAD_FOLDER'] = './upload'
db = SQLAlchemy(app)
ALLOWED_EXTENSIONS = set(['bib','ris'])
# change to "redis" and restart to cache again

# some time later

# change to "redis" and restart to cache again

# some time later

# All caching functions will simply call through
# to the wrapped function, with no caching
# (since NullCache does not cache).



class User(db.Model):
	""" Create user table"""
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(80), unique=True)
	password = db.Column(db.String(80))

	def __init__(self, username, password):
		self.username = username
		self.password = password


@app.route('/', methods=['GET', 'POST'])
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
def login():
	"""Login Form"""
	if request.method == 'GET':
		return render_template('login.html')
	else:
		name = request.form['username']
		passw = request.form['password']
		try:
			data = User.query.filter_by(username=name, password=passw).first()
			if data is not None:
				session['logged_in'] = True
				return redirect(url_for('home'))
			else:
				return redirect(url_for('home'))
		except:
			return "Dont Login"

@app.route('/register/', methods=['GET', 'POST'])
def register():
	"""Register Form"""
	if request.method == 'POST':
		new_user = User(username=request.form['username'], password=request.form['password'])
		db.session.add(new_user)
		db.session.commit()
		return render_template('login.html')
	return render_template('register.html')

@app.route("/logout")
def logout():
	"""Logout Form"""
	session['logged_in'] = False
	return redirect(url_for('home'))

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/upload", methods=['POST'])
def uploader():
	 if request.method == 'POST':
	 	if 'archivo' not in request.files:
	 		flash('no file part')
	 		return 
	 	file = request.files['archivo']
	 	if file.filename == '':
	 		flash('No selected file')
	 		return 
	 	if file and allowed_file(file.filename):
	 		filename = secure_filename(file.filename)
	 		file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
	 		#print("./upload/"+filename)
	 		archivo = "./upload/"+filename
	 		os.rename(archivo, "./static/upload/1.bib")
	 		#Aqui para ejecutar un comando de python 
	 		process = subprocess.Popen('python3 ./static/upload/BIB2CSV.py', shell=True, stdout=subprocess.PIPE)
	 		#process = subprocess.Popen('python3 bibtex2bibjson.py ../SASR/static/upload/1.bib > ../SASR/static/upload/1.json', shell=True, stdout=subprocess.PIPE)
	 		
	 	print (process.returncode)
	 	return render_template('index.html')

 #return cosole.log(filename);

#os.rename(a,a1)

if __name__ == '__main__':
	app.debug = True
	db.create_all()
	app.secret_key = "123"
	app.run(host='0.0.0.0')
	