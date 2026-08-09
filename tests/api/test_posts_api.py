from unittest.mock import patch

def test_get_history_empty(client, user_headers):
    response = client.get("/api/history", headers=user_headers)
    assert response.status_code == 200
    assert response.json() == []

@patch("app.agent.generate_post_content")
def test_generate_draft(mock_gen, client, user_headers):
    mock_gen.return_value = "Este é um post de teste gerado pela IA."
    
    payload = {
        "theme": "Python & FastAPI",
        "tone": "informativo"
    }
    response = client.post("/api/generate-draft", json=payload, headers=user_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["content"] == "Este é um post de teste gerado pela IA."
    assert data["theme"] == "Python & FastAPI"
