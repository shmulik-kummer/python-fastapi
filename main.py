from fastapi import FastAPI, HTTPException, Response,status
from pydantic import BaseModel
import itertools

# Generator for unique IDs
def id_generator():
    return itertools.count(1)
get_next_id = id_generator()

def raise_not_found_error(post_id: int):
    error_message = f"Post with ID {post_id} not found"
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_message)

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

@app.post("/posts", status_code=201)
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
    raise_not_found_error(post_id)

@app.get("/posts/{post_id}")
def get_post_by_id(post_id: int):
    try:
        post = find_post(post_id)
        return post
    except HTTPException as e:
        raise e


def find_index_post(post_id: int):
    for index, post in enumerate(my_posts):
        if post['id'] == post_id:
            return index
    raise_not_found_error(post_id)


@app.delete("/posts/{post_id}")
def delete_post(post_id: int):
    index = find_index_post(post_id)
    my_posts.pop(index)
    return Response(status_code = status.HTTP_204_NO_CONTENT)


@app.put('/posts/{post_id}')
def update_post(post_id: int, post: Post):
    index = find_index_post(post_id)
    post_dict = post.model_dump()
    post_dict['id'] = post_id
    my_posts[index] = post_dict
    return post_dict