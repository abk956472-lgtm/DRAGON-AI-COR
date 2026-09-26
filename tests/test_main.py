import pytest
from fastapi.testclient import TestClient
from dragon_core.main import app

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "Dragon Core API"
    assert data["status"] == "online"

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_chat_completions_endpoint():
    payload = {
        "messages": [
            {"role": "user", "content": "Hello Dragon Core"}
        ]
    }
    response = client.post("/v1/chat/completions", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "choices" in data
    assert len(data["choices"]) > 0
    assert data["choices"][0]["message"]["role"] == "assistant"

def test_chat_completions_empty_messages():
    payload = {"messages": []}
    response = client.post("/v1/chat/completions", json=payload)
    assert response.status_code == 400
