import csv
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session,sessionmaker

db_uri = 'postgres://mkpywnlvmhnhpf:90f16e461037e56efb35077fb3ebe4d491939728cf1650fa4f0d689c67f6abb8@ec2-54-228-251-254.eu-west-1.compute.amazonaws.com:5432/d6je9s4ur9vhgm'
engine = create_engine(db_uri)
# engine.execute('CREATE TABLE "books" ('
#                'isbn VARCHAR NOT NULL,'
#                'title VARCHAR NOT NULL, '
#                'author VARCHAR NOT NULL,'
#                'year INTEGER NOT NULL);')

# engine.execute('CREATE TABLE "users" ('
#                'id SERIAL PRIMARY KEY,'
#                'username VARCHAR NOT NULL,'
#                'email VARCHAR NOT NULL,'
#                'password VARCHAR NOT NULL);')
#
# engine.execute('DROP TABLE users')

db = scoped_session(sessionmaker(bind=engine))
us = db.execute("SELECT * FROM reviews").fetchall()
for val in us:
    print(val)
# db.commit()
# with open('C:/Users/Tomasy/Desktop/project1/project1/books.csv', newline='') as csvfile:
#     freader = csv.DictReader(csvfile, delimiter=',')
#     for row in freader:
#         db.execute("INSERT INTO books(isbn,title,author,year) VALUES (:isbn, :title, :author,:year)",
#                    {"isbn": row['isbn'], "title": row['title'], "author": row['author'], "year": row['year']})
#         print(row['isbn'], row['title'], row['author'], row['year'])
#         db.commit()
#
# engine.execute('CREATE TABLE "reviews" ('
#                'isbn VARCHAR,'
#                'userid VARCHAR ,'
#                'comment VARCHAR,'
#                'rating INTEGER,'
#                'username VARCHAR,'
#                'timestamp TIMESTAMP )')

# engine.execute('DROP TABLE reviews')