from fastapi.testclient import TestClient
from app.main import app, todos

# Create a test client
client = TestClient(app)

def clear_todos():
   """ Helper function to clear todos before each test """
   todos.clear()


def test_create_todo():
   response = client.post("/todos", json={
      "title": "FastAPI Todo Project",
      "description": "Building FastAPI Todo Project and automating CI/CD via Jenkins",
      "completed": False
   })

   assert response.status_code == 201
   data = response.json()
   assert data["title"] == "FastAPI Todo Project"
   assert data["id"] is not None
   clear_todos()


def create_todo_empty_title():
   response = client.post("/todos", json={
      "title": " ",
      "description": "Test empty title",
      "completed": False 
   })
   assert response.status_code == 400
   assert response.json()["detail"] == "Title cannot be empty"
   clear_todos()


def test_get_todos():
   client.post("/todos", json={
      "title": "First Todo",
      "description": "This is the first todo",
      "completed": False
   })

   client.post("/todos", json={
      "title": "Second Todo",
      "completed": True
   })

   response = client.get("/todos")
   assert response.status_code == 200
   assert len(response.json()) == 2
   clear_todos()

def test_get_todos_filtered():
   client.post("/todos", json={"title": "Todo 1", "completed": False})
   client.post("/todos", json={"title": "Todo 2", "completed": True})

   response = client.get("/todos?completed=true")
   assert response.status_code == 200
   assert len(response.json()) == 1
   clear_todos()

def test_update_todo():
   # Create a todo
   response = client.post("/todos", json={"title": "Old Title", "completed": False})
   todo_id = response.json()["id"]

   # Update it
   response = client.put(f"/todos/{todo_id}", json={"title": "New Title", "completed": True})
   assert response.status_code == 200
   assert response.json()["title"] == "New Title"
   assert response.json()["completed"] is True
   clear_todos()

def test_delete_todo():
   # Create a todo
   response = client.post("/todos", json={"title": "To be deleted", "completed": False})
   assert response.status_code == 201
   todo_id = response.json()["id"]

   # Delete it
   delete_response = client.delete(f"/todos/{todo_id}")
   assert delete_response.status_code == 204

   # Verify deletion
   get_response = client.get(f"/todos/{todo_id}")
   assert get_response.status_code == 404
   clear_todos()

def test_stats():
   client.post("/todos", json={"title": "Todo 1", "completed": True})
   client.post("/todos", json={"title": "Todo 2", "completed": False})
   client.post("/todos", json={"title": "Todo 3", "completed": True})

   response = client.get("/stats")
   assert response.status_code == 200
   data = response.json()
   assert data["total_todos"] == 3
   assert data["completed_todos"] == 2
   assert data["pending_todos"] == 1
   clear_todos()
   

def test_root():
   response = client.get("/")
   assert response.status_code == 200
   assert response.json()["Message"] == "Welcome to FastAPI Jenkins Project"

def test_healthcheck():
   response = client.get("/health")
   assert response.status_code == 200
   assert response.json()["status"] == "OK"

def test_jenkins():
   response = client.get("/jenkins")
   assert response.status_code == 200
   assert response.json()["status"] == "Running in Jenkins"

def test_create_and_get_todo():
   # Create a new todo
   todo_data = {"title": "Test Todo", "description": "This is a test todo", "completed": False}
   response = client.post("/todos", json=todo_data)
   assert response.status_code == 200
   todo_id = response.json()["id"]

   # Get the todo by ID
   response = client.get(f"/todos/{todo_id}")
   assert response.status_code == 200
   assert response.json()["title"] == "Test Todo"
   clear_todos()
   
   