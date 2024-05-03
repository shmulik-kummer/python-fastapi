import time
from fastapi import FastAPI, HTTPException, Response, status, Depends
import itertools
import psycopg
from psycopg.rows import dict_row
from sqlalchemy.orm import Session
from . import models
from .database import get_db, engine
from .schemas import PostCreate, PostResponse
from .models import Post


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


models.Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Welcome to my API"}


@app.get("/posts")
def get_posts(db: Session = Depends(get_db)):
    try:
        posts = db.query(models.Post).all()
        return posts
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/posts", status_code=status.HTTP_201_CREATED, response_model=PostResponse)
def create_post(post: PostCreate, db: Session = Depends(get_db)):
    new_post = Post(**post.dict())

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


@app.get("/posts/{post_id}")
def get_post_by_id(post_id: int, db: Session = Depends(get_db)):
    try:
        post = db.query(Post).filter(Post.id == post_id).first()
        if not post:
            raise_not_found_error(post_id)
        return post
    except HTTPException as e:
        raise e


@app.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise_not_found_error(post_id)

    # Delete the post
    db.delete(post)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put('/posts/{post_id}')
def update_post(post_id: int, updated_post: PostCreate, db: Session = Depends(get_db)):
    # Query for the existing post
    post_query = db.query(Post).filter(Post.id == post_id)
    post = post_query.first()

    if not post:
        raise_not_found_error(post_id)

    # Update the post using the data provided
    post_query.update(updated_post.dict(exclude_unset=True), synchronize_session='fetch')

    # Commit the changes to the database
    db.commit()

    # Refresh the instance to ensure it's updated
    db.refresh(post)

    # Return the updated post
    return post
