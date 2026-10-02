import pytest
import database

def test_app_creates(app):
    assert app.testing is True

def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200

def test_create_valid_task(client, app):
    response = client.post("/add", data={
        "title": "Valid Task",
        "description": "Desc",
        "priority": "High",
        "due_date": "2026-10-10"
    })
    assert response.status_code == 302
    
    with app.app_context():
        tasks = database.get_all_tasks(app.config["DATABASE"])
        assert len(tasks) == 1
        assert tasks[0]["title"] == "Valid Task"

def test_created_task_visible(client):
    client.post("/add", data={
        "title": "Visible Task",
        "priority": "Medium",
        "due_date": "2026-11-11"
    })
    response = client.get("/")
    assert b"Visible Task" in response.data

def test_complete_task(client, app):
    client.post("/add", data={
        "title": "To Complete",
        "priority": "Low",
        "due_date": "2026-12-12"
    })
    
    with app.app_context():
        tasks = database.get_all_tasks(app.config["DATABASE"])
        task_id = tasks[0]["id"]
    
    response = client.post(f"/complete/{task_id}")
    assert response.status_code == 302
    
    with app.app_context():
        task = database.get_task(app.config["DATABASE"], task_id)
        assert task["status"] == "Completed"

def test_empty_title_rejected(client, app):
    response = client.post("/add", data={
        "title": "",
        "priority": "High",
        "due_date": "2026-10-10"
    })
    assert response.status_code == 400
    
    with app.app_context():
        tasks = database.get_all_tasks(app.config["DATABASE"])
        assert len(tasks) == 0

def test_invalid_priority_rejected(client):
    response = client.post("/add", data={
        "title": "Bad Priority",
        "priority": "SuperHigh",
        "due_date": "2026-10-10"
    })
    assert response.status_code == 400

def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json == {"status": "ok"}
