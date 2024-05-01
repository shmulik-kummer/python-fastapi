import time
from typing import Optional

from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel, Field
import itertools
import psycopg
from psycopg.rows import dict_row
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_db_connection(dbname, user, password, host, port):
    while True:
        try:
            conn = psycopg.connect(dbname=dbname, user=user, password=password, host=host, port=port,
                                   row_factory=dict_row, autocommit=True)
            print("Database connection was successful")
            return conn.cursor()

        except Exception as error:
            print("connecting to DB failed")
            print("Error: ", error)
            time.sleep(2)


# Create connection to Postgres
cursor = create_db_connection("fastapi", "postgres", "1234", "localhost", 5432)


# Generator for unique IDs
def id_generator():
    return itertools.count(1)


get_next_id = id_generator()


def raise_not_found_error(post_id: int):
    error_message = f"Post with ID {post_id} not found"
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_message)


app = FastAPI()


class Post(BaseModel):
    id: int = Field(default_factory=lambda: next(get_next_id))
    title: str
    content: str
    published: Optional[bool] = True


@app.get("/")
async def root():
    return {"message": "Welcome to my API"}


@app.get("/posts")
def get_posts():
    cursor.execute('''SELECT * from posts''')
    posts = cursor.fetchall()
    return {"data": posts}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(post: Post):
    cursor.execute(''' INSERT into posts (title, content, published) VALUES (%s, %s, %s) RETURNING * ''',
                   (post.title, post.content, post.published))
    new_post = cursor.fetchone()
    return {"data": new_post}


@app.get("/posts/{post_id}")
def get_post_by_id(post_id: int):
    try:
        cursor.execute("SELECT * FROM posts WHERE id = %s", (post_id,))
        post = cursor.fetchone()
        if not post:
            raise_not_found_error(post_id)
        return {"data": post}
    except HTTPException as e:
        raise e


@app.delete("/posts/{post_id}")
def delete_post(post_id: int):
    try:
        # Check if the post exists
        get_post_by_id(post_id)
        cursor.execute('''DELETE FROM posts WHERE id = %s returning *''', (post_id,))
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except HTTPException as e:
        raise e


@app.put('/posts/{post_id}')
def update_post(post_id: int, updated_post: Post):
    try:
        # Check if the post exists
        get_post_by_id(post_id)
        cursor.execute('''UPDATE posts SET title = %s, content = %s, published = %s RETURNING * ''',
                       (updated_post.title, updated_post.content, updated_post.published))
        updated_post = cursor.fetchone()
        return {"data": updated_post}

    except HTTPException as e:
        raise e
