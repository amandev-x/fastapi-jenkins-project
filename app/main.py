from typing import List
from fastapi import FastAPI, HTTPException, status
from .models import Todo, TodoCreate, TodoUpdate, HealthCheckResponse, JenkinsResponse
from .config import settings

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    debug=settings.debug
)

# In memory database
todos = []
todo_id_counter = 1

@app.get("/")
async def root():
    return {
         "Message": settings.app_name,
         "version": settings.version,
         "docs": "/docs"
         }

@app.get("/health", response_model=HealthCheckResponse)
async def healthcheck():
    return {"status": "healthy",
            "total_todos": len(todos)}

@app.get("/jenkins", response_model=JenkinsResponse)
async def get():
    return {"status": "Running in Jenkins"}

@app.get("/todos", response_model=List[Todo])
async def get_todos(completed: bool = None):
    if completed is None:
        return todos 
    return [todo for todo in todos if todo.completed == completed]

@app.post("/todos", response_model=Todo, status_code=201)
async def create_todo(todo: TodoCreate):
    global todo_id_counter

    if len(todo.title.strip()) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title cannot be empty"
        )
    new_todo = Todo (
        id = todo_id_counter,
        title = todo.title,
        description = todo.description,
        completed = todo.completed
    )
    todo_id_counter += 1
    todos.append(new_todo)
    return new_todo

@app.get("/todos/{todo_id}", response_model=Todo)
async def get_todo(todo_id: int):
    for todo in todos:
       if todo.id == todo_id:
          return todo 
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Todo with the given ID {todo_id} not found"
        )

@app.put("/todos/{todo_id}", response_model=Todo)
async def update_todo(todo_id: int, todo_update: TodoUpdate):
    for i, todo in enumerate(todos):
        if todo.id == todo_id:
            updated_todo = todo.model_copy(
                update=todo_update.model_dump(exclude_unset=True)
            )
            todos[i] = updated_todo
            return updated_todo
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Todo with id {todo_id} not found. Please enter valid ID"
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

@app.get("/stats")
async def stats():
    total_todos = len(todos)
    completed_todos = len([todo for todo in todos if todo.completed])
    pending_todos = total_todos - completed_todos

    return {
        "total_todos": total_todos,
        "completed_todos": completed_todos,
        "pending_todos": pending_todos
    }