from flask import Flask, url_for
from flask import render_template
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask import request
import hashlib

app = Flask(__name__)

db_uri = 'postgres://mkpywnlvmhnhpf:90f16e461037e56efb35077fb3ebe4d491939728cf1650fa4f0d689c67f6abb8@ec2-54-228-251-254.eu-west-1.compute.amazonaws.com:5432/d6je9s4ur9vhgm'
engine = create_engine(db_uri)
db = scoped_session(sessionmaker(bind=engine))


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/join', methods=['GET', 'POST'])
def join():
    if request.method == 'POST':
        uname = request.form.get('username')
        uemail = request.form.get('useremail')
        upass = request.form.get('userpass')
        check = db.execute("SELECT username,email FROM users WHERE username=:unameval OR email=:uemailval",{'unameval':uname, 'uemailval':uemail} )
        if check.first() is None:
            db.execute("INSERT INTO users(username,email,password) VALUES (:username,:email,:password)",
                  {"username":uname, "email":uemail,"password":hashlib.md5(upass.encode()).hexdigest()})
            db.commit()
            return uname + ' ' + uemail + ' ' + upass
        else:
            return "User or email in use please use new credentials"
    else:
        return render_template('join.html')


@app.route('/search')
def search():
    return render_template('search.html')

@app.route('/results')
def results():
    return render_template('results.html')

@app.route('/book')
def book():
    return render_template('book.html')