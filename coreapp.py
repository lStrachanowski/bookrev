from flask import Flask, session, redirect,url_for
from flask import render_template
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask import request
import hashlib
import json
import urllib
import time


app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
db_uri = 'postgres://mkpywnlvmhnhpf:90f16e461037e56efb35077fb3ebe4d491939728cf1650fa4f0d689c67f6abb8@ec2-54-228-251-254.eu-west-1.compute.amazonaws.com:5432/d6je9s4ur9vhgm'
engine = create_engine(db_uri)
db = scoped_session(sessionmaker(bind=engine))
usernamedisplay = ''
searchvalues = ''

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
            db.commmit()
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
    global searchvalues
    if usernamedisplay in session:
        if request.method == 'GET':
            return render_template('search.html',usernamedisplay=usernamedisplay)
        else:
            formval = request.form.get('searchfield')
            fval = '%'+formval+'%'
            sr = db.execute("SELECT * FROM books WHERE title LIKE :searchtitle",{'searchtitle':fval}).fetchall()
            searchvalues = sr
            return render_template('results.html', loopvalues=sr, usernamedisplay=usernamedisplay)
    else:
        return render_template('invalid.html', message="Log in first")


@app.route('/results')
def results():
    if usernamedisplay in session:
        return render_template('results.html',usernamedisplay=usernamedisplay, loopvalues=searchvalues)
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

@app.route('/rating/<rating>/<isbn>', methods=['GET','POST'])
def rating(rating=None,isbn=None):
    global usernamedisplay
    sr = db.execute("SELECT * FROM reviews WHERE isbn=:searchisbn", {'searchisbn':isbn}).fetchall()
    user_id = db.execute("SELECT id FROM users WHERE username=:unameval",{'unameval': usernamedisplay}).first()
    if sr:
        for value in sr:
            if(value[1] == str(user_id[0])):
                db.execute("UPDATE reviews SET rating=:rating_val WHERE userid=:uid AND isbn=:isbn_val",{'rating_val':rating, 'uid':str(user_id[0]), 'isbn_val':isbn})
                db.commit()
                return redirect(url_for('book_route',isbn=isbn))
        else:
            db.execute("INSERT INTO reviews(isbn,rating,userid) VALUES(:isbn,:rating,:userid)",{"isbn":isbn, "rating":rating,"userid":user_id[0]})
            db.commit()
            return redirect(url_for('book_route',isbn=isbn))     
    else:
        db.execute("INSERT INTO reviews(isbn,rating,userid) VALUES(:isbn,:rating,:userid)",{"isbn":isbn, "rating":rating,"userid":user_id[0]})
        db.commit()
        return redirect(url_for('book_route',isbn=isbn))


@app.route('/book/<isbn>', methods=['GET','POST'])
def book_route(isbn):
    if usernamedisplay in session:
        if request.method == 'GET':
            api_request = 'https://www.goodreads.com/book/review_counts.json?isbns=' + isbn + '&key=oVeYIluiDTM5qYO74SzGUA'
            data = urllib.request.urlopen(api_request).read().decode()
            goodreads_data = json.loads(data)
            rating_data = goodreads_data["books"][0]
            u_score = None
            sr = db.execute("SELECT * FROM books WHERE isbn=:searchisbn", {'searchisbn': isbn}).fetchall()
            ur = db.execute("SELECT * FROM reviews WHERE isbn=:searchisbn", {'searchisbn':isbn}).fetchall()
            user_id = db.execute("SELECT id FROM users WHERE username=:unameval",{'unameval': usernamedisplay}).first()
            if ur:
                for value in ur:
                    if value[1] == str(user_id[0]):
                        u_score = value[3]
            return render_template('book.html', title=sr[0].title, year=sr[0].year, author=sr[0].author,
                                   bookisbn=sr[0].isbn, rating=rating_data['average_rating'],
                                   total=rating_data['work_reviews_count'], usernamedisplay=usernamedisplay,user_score=u_score)

        else:
            post_time = time.asctime(time.localtime(time.time()))
            comment_text = request.form.get('textfield')
            # rating_value =

            # db.execute("INSERT INTO reviews(isbn,userid,comment,rating,timestamp) VALUES (:isbn,:userid,:comment,:rating,:timestamp)",
            # {'isbn': 123,'userid':id,'comment':comment_text, 'rating':5,'timestamp':post_time})
            return 'comment added'

@app.route('/api/<isbn>')
def api(isbn):
    sr = db.execute("SELECT * FROM books WHERE isbn LIKE :searchisbn", {'searchisbn': isbn}).fetchall()
    if sr:
        api_request = 'https://www.goodreads.com/book/review_counts.json?isbns=' + isbn + '&key=oVeYIluiDTM5qYO74SzGUA'
        data = urllib.request.urlopen(api_request).read().decode()
        goodreads_data = json.loads(data)
        rating_data = goodreads_data["books"][0]
        api_data = {'title': sr[0].title,'author': sr[0].author, 'year':sr[0].year, 'isbn': sr[0].isbn,'reviev_count': rating_data['work_reviews_count'], 'avrage_score': rating_data['average_rating']}
        return json.dumps(api_data)
    else:
        return render_template('invalid.html', message="No such book in database")
