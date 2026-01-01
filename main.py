from fastapi import FastAPI, Depends, HTTPException
from models import UserCreate, TaskCreate, TaskUpdate
from database import users_collection, tasks_collection
from auth import hash_password, verify_password, create_token, get_current_user
from bson import ObjectId

app = FastAPI(title="Smart ToDo API")

# ---------- AUTH ----------
@app.post("/register")
def register(user: UserCreate):
    if users_collection.find_one({"username": user.username}):
        raise HTTPException(status_code=400, detail="User exists")
    users_collection.insert_one({
        "username": user.username,
        "password": hash_password(user.password)
    })
    return {"message": "User registered"}

@app.post("/login")
def login(user: UserCreate):
    db_user = users_collection.find_one({"username": user.username})
    if not db_user or not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}

# ---------- TASKS ----------
@app.post("/tasks")
def create_task(task: TaskCreate, user=Depends(get_current_user)):
    tasks_collection.insert_one({
        "title": task.title,
        "description": task.description,
        "is_completed": task.is_completed,
        "user": user["username"]
    })
    return {"message": "Task created"}

@app.get("/tasks")
def get_tasks(user=Depends(get_current_user)):
    tasks = tasks_collection.find({"user": user["username"]})
    return [{"id": str(t["_id"]), "title": t["title"], "description": t.get("description"), "is_completed": t.get("is_completed", False)} for t in tasks]

@app.put("/tasks/{task_id}")
def update_task(task_id: str, task: TaskUpdate, user=Depends(get_current_user)):
    update_data = {k: v for k, v in task.dict().items() if v is not None}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No data provided for update")

    result = tasks_collection.update_one(
        {"_id": ObjectId(task_id), "user": user["username"]},
        {"$set": update_data}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404)
    return {"message": "Task updated"}

@app.delete("/tasks/{task_id}")
def delete_task(task_id: str, user=Depends(get_current_user)):
    result = tasks_collection.delete_one(
        {"_id": ObjectId(task_id), "user": user["username"]}
    )
    if result.deleted_count == 0:
        raise HTTPException(status_code=404)
    return {"message": "Task deleted"}

@app.get("/")
def root():
    return {"message": "Smart ToDo API is running"}
