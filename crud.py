from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import redis
import pymysql

load_dotenv() 

app = FastAPI()

timeout = int(os.getenv('MYSQL_TIMEOUT'))
connection = pymysql.connect(
  charset="utf8mb4",
  connect_timeout=timeout,
  cursorclass=pymysql.cursors.DictCursor,
  db=os.getenv('MYSQL_DB'),
  host=os.getenv('MYSQL_HOST'),
  password=os.getenv('MYSQL_PW'),
  read_timeout=timeout,
  port=int(os.getenv('MYSQL_PORT')),
  user=os.getenv('MYSQL_USER'),
  write_timeout=timeout,
)

r = redis.Redis(
    host=os.getenv('REDIS_HOST'),
    port=int(os.getenv('REDIS_PORT')),
    decode_responses=True,
    username=os.getenv('REDIS_USER'),
    password=os.getenv('REDIS_PW'),
)

class Article(BaseModel):
    title: str
    body: str

@app.post("/articles")
def write_article(article:Article):
    try:
        cursor = connection.cursor()
        cursor.execute(f"INSERT INTO articles (title, body) VALUES('{article.title}', '{article.body}')")
    finally:
        pass

@app.get("/articles")
def read_articles():
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM articles")
        result = cursor.fetchall()
        return result
    finally:
        pass
 
@app.get("/articles/{id}")
def read_article(id):
    try:
        cached = r.hgetall(id)
        if cached == {}:
            cursor = connection.cursor()
            cursor.execute(f"SELECT * FROM articles WHERE id={id}")
            result = cursor.fetchall()[0]
            r.hmset(id, result)
            return result
        else:
            return cached
    finally:
        pass

@app.put("/articles/{id}")
def update_article(id, article:Article):
    title = article.title
    body = article.body
    try:
        cursor = connection.cursor()
        query = f"UPDATE articles SET title='{article.title}', body='{article.body}' WHERE id={id}"
        cursor.execute(query)
    finally:
        pass

    r.hmset(id, {'id': id, 'title': title, 'body': body})

@app.delete("/articles/{id}")
def delete_article(id):
    try:
        cursor = connection.cursor()
        query = f"DELETE FROM articles WHERE id={id}"
        cursor.execute(query)
    finally:
        pass

    # Cache
    r.delete(id)
