from fastapi import FastAPI
from pydantic import BaseModel
import itertools

# Generator for unique IDs
def id_generator():
    return itertools.count(1)
get_next_id = id_generator()

app = FastAPI()

class Post(BaseModel):
    title: str
    content: str

# Pre-populated list of posts
my_posts = [{"id": next(get_next_id), "title": "title 1", "content": "My first post"}]


@app.get("/")
async def root():
    return {"message": "Welcome to my API"}

@app.get("/posts")
def get_posts():
    return {"data": my_posts}

@app.post("/posts")  # Corrected the route and method
def create_post(new_post: Post):
    post_dict = new_post.model_dump()
    post_dict['id'] = next(get_next_id)
    my_posts.append(post_dict)
    return {"data": post_dict}


def find_post(post_id: int):
    """Utility function to find a post by ID."""
    for post in my_posts:
        if post['id'] == post_id:
            return post
    return None

@app.get("/posts/{post_id}")
def get_post_by_id(post_id: int):
    post = find_post(post_id)
    if post is None:
        return {"error": f"Post with ID {post_id} not found"}
    else:
        return post

    