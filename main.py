from fastapi import Body, FastAPI
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Welcome to my API"}

@app.get("/posts")
def get_posts():
    return {"data": "These are your posts"}

@app.post("/createposts")
def create_posts(payLoad: dict = Body(...)):
    print(payLoad)
    return {"new_post": payLoad}