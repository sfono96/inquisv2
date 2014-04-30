from flask import *
from functools import wraps
from db import *
from json import dumps

app = Flask(__name__)
app.secret_key = '5RD{Hd1CRSwCoqct4Y497&4Ar12t5V'

# login decorator
def login_required(test):
	@wraps(test)
	def wrap(*args, **kwargs):
		if 'logged_in' in session:
			return test(*args, **kwargs)
		else:
			flash('Please login first.')
			return redirect(url_for('log'))
	return wrap

##################### routes #####################

# logout session
@app.route('/logout')
def logout():
	session.pop('logged_in', None)
	flash('You were logged out')
	return redirect(url_for('log'))

# login
@app.route('/log',methods=['GET','POST'])
def log():
	error = None
	if request.method == 'POST':
		if request.form['uid'] != 'admin' or request.form['pwd'] != 'ponytracks':
			error = 'Invalid Credentials. Please try again.'
			flash(error)
			return redirect(url_for('log'))
		else:
			session['logged_in'] = True
			return redirect(url_for('index'))
	return render_template('log.html',error=error)

# main
@app.route('/')
@login_required
@app.route('/dash',methods=['GET','POST'])
def dash():
	return render_template('dash.html')

# julie test
@login_required
@app.route('/drill',methods=['GET','POST'])
def drill():
	return render_template('drill.html')


################ data API's ################


if __name__ == '__main__':
	app.run(debug=True)