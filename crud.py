from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv() 

class Article(BaseModel):
    title: str
    body: str

app = FastAPI()

import pymysql

timeout = 10
connection = pymysql.connect(
  charset="utf8mb4",
  connect_timeout=timeout,
  cursorclass=pymysql.cursors.DictCursor,
  db=os.getenv('MYSQL_DB'),
  host=os.getenv('MYSQL_HOST'),
  password=os.getenv('MYSQL_PW'),
  read_timeout=timeout,
  port=os.getenv('MYSQL_PORT'),
  user=os.getenv('MYSQL_USER'),
  write_timeout=timeout,
)
  
"""Basic connection example.
"""

import redis

r = redis.Redis(
    host=os.getenv('REDIS_HOST'),
    port=13863,
    decode_responses=True,
    username=os.getenv('REDIS_USER'),
    password=os.getenv('REDIS_PW'),
)

@app.get("/articles")
def read_articles():
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM articles")
        result = cursor.fetchall()
        print(result)
        return result
    finally:
        pass
 
@app.get("/articles/{id}")
def read_article(id):
    try:
        # TODO: read from cache (hint: result = r.get('foo'))
        cached = r.hgetall(id)
        print('c', cached)
        if cached == {}:
            print('first')
            cursor = connection.cursor()
            cursor.execute(f"SELECT * FROM articles WHERE id={id}")
            result = cursor.fetchall()[0]
            r.hmset(id, result)
            return result
        else:
            print('cached')
            return cached
    finally:
        pass

@app.put("/articles/{id}")
def update_article(id, article:Article):
    # DB
    title = article.title
    body = article.body
    print(title, body)
    try:
        cursor = connection.cursor()
        query = f"UPDATE articles SET title='{title}', body='{body}' WHERE id={id}"
        print(query)
        cursor.execute(query)
    finally:
        pass

    # Cache
    r.hmset(id, {'id': id, 'title': title, 'body': body})
