from typing import List
from fastapi import FastAPI, HTTPException, status
from .models import Todo, HealthCheckResponse, JenkinsResponse

app = FastAPI(
    title="FastAPI Jenkins Project"
)

# In memory database
todos = []
todo_id_counter = 1

@app.get("/")
async def root():
    return {"Message": "Welcome to FastAPI Jenkins Project"}

@app.get("/health", response_model=HealthCheckResponse)
async def healthcheck():
    return {"status": "OK"}

@app.get("/jenkins", response_model=JenkinsResponse)
async def get():
    return {"status": "Running in Jenkins"}

@app.get("/todos", response_model=List[Todo])
async def get_todos():
    return todos 

@app.post("/todos", response_model=Todo)
async def create_todo(todo: Todo):
    global todo_id_counter
    todo.id = todo_id_counter
    todo_id_counter += 1
    todos.append(todo)
    return todo

@app.get("/todos/{todo_id}", response_model=Todo)
async def get_todo(todo_id: int):
    for todo in todos:
       if todo.id == todo_id:
          return todo 
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Todo with the given ID {todo_id} not found"
        )

@app.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(todo_id: int):
    for index, todo in enumerate(todos):
        if todo.id == todo_id:
         todos.pop(index)
         return {"Message": "Todo deleted successfully"}
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Todo with the given ID {todo_id} not found"
        )