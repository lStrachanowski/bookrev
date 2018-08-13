from flask import Flask, session
from flask import render_template
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask import request
import hashlib
import json
import urllib

app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
db_uri = 'postgres://mkpywnlvmhnhpf:90f16e461037e56efb35077fb3ebe4d491939728cf1650fa4f0d689c67f6abb8@ec2-54-228-251-254.eu-west-1.compute.amazonaws.com:5432/d6je9s4ur9vhgm'
engine = create_engine(db_uri)
db = scoped_session(sessionmaker(bind=engine))
usernamedisplay = ''

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        uname = request.form.get('username')
        upass = request.form.get('userpass')
        if uname and upass:
            check = db.execute("SELECT username,password FROM users WHERE username=:unameval",{'unameval': uname}).first()
            if check is None:
                return render_template('invalid.html', message="Check credentials, user don`t exist")
            else:
                if hashlib.md5(upass.encode()).hexdigest() == check[1] and uname == check[0]:
                    global usernamedisplay
                    session[uname] = uname
                    usernamedisplay = check['username']
                    return render_template('search.html',usernamedisplay=usernamedisplay)
                else:
                    return render_template('invalid.html', message="Wrong user name or password")
        else:
            return render_template('invalid.html', message="All fields has to be filled in.")
    else:
        return render_template('login.html')

@app.route('/join', methods=['GET', 'POST'])
def join():
    if request.method == 'POST':
        uname = request.form.get('username')
        uemail = request.form.get('useremail')
        upass = request.form.get('userpass')
        check = db.execute("SELECT username,email FROM users WHERE username=:unameval OR email=:uemailval",{'unameval':uname, 'uemailval':uemail} )
        if uname and uemail and upass:
            if check.first() is None:
                db.execute("INSERT INTO users(username,email,password) VALUES (:username,:email,:password)",
                           {"username": uname, "email": uemail, "password": hashlib.md5(upass.encode()).hexdigest()})
                db.commit()
                return render_template('invalid.html', message="Account created.Log in with credentials")
            else:
                return render_template('invalid.html',
                                       message="Email or user name is already in use. Please check new credentials.")
        else:
            return render_template('invalid.html',message="All fields has to be filled in.")
    else:
        return render_template('join.html')


@app.route('/search', methods=['GET','POST'])
def search():
    if usernamedisplay in session:
        if request.method == 'GET':
            return render_template('search.html')
        else:
            formval = request.form.get('searchfield')
            fval = '%'+formval+'%'
            sr = db.execute("SELECT * FROM books WHERE title LIKE :searchtitle",{'searchtitle':fval}).fetchall()
            return render_template('results.html', loopvalues=sr)
    else:
        return render_template('invalid.html', message="Log in first")


@app.route('/results')
def results():
    if usernamedisplay in session:
        return render_template('results.html',usernamedisplay=usernamedisplay)
    else:
        return render_template('invalid.html', message="Log in first")

@app.route('/book')
def book():
    if usernamedisplay in session:
        return render_template('book.html',usernamedisplay=usernamedisplay)
    else:
        return render_template('invalid.html',message="Log in first")

@app.route('/logout')
def logout():
    global usernamedisplay
    session.pop(usernamedisplay,None)
    return render_template('index.html')

@app.route('/book/<isbn>')
def book_route(isbn):
    if usernamedisplay in session:
        api_request = 'https://www.goodreads.com/book/review_counts.json?isbns='+isbn+'&key=oVeYIluiDTM5qYO74SzGUA'
        data = urllib.request.urlopen(api_request).read().decode()
        goodreads_data = json.loads(data)
        rating_data = goodreads_data["books"][0]
        sr = db.execute("SELECT * FROM books WHERE isbn=:searchisbn", {'searchisbn': isbn}).fetchall()
        return render_template('book.html',title=sr[0].title, year=sr[0].year, author=sr[0].author, bookisbn=sr[0].isbn, rating=rating_data['average_rating'],
                               total=rating_data['work_reviews_count'])
