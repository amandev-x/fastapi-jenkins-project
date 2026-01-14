from fastapi.testclient import TestClient
from app.main import app 

# Create a test client
client = TestClient(app)

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
   
   