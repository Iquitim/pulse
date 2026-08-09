def test_get_config(client, user_headers):
    response = client.get("/api/config", headers=user_headers)
    assert response.status_code == 200
    data = response.json()
    assert "themes" in data
    assert "tone" in data
    assert "interval_hours" in data

def test_save_config_within_limits(client, user_headers):
    payload = {
        "themes": ["Tecnologia", "Inteligência Artificial"],
        "tone": "Informativo e direto",
        "interval_hours": 4,
        "is_active": True,
        "system_prompt": "Escreva posts objetivos.",
        "persona_description": "Desenvolvedor especialista em Python",
        "requires_approval": False
    }
    response = client.post("/api/config", json=payload, headers=user_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["tone"] == "Informativo e direto"
    assert len(data["themes"]) == 2


def test_save_config_exceeding_theme_limit(client, user_headers):
    # Free tier user max_themes limit is 3
    payload = {
        "themes": ["Tema 1", "Tema 2", "Tema 3", "Tema 4", "Tema 5"],
        "tone": "Descontraído",
        "interval_hours": 6,
        "is_active": True,
        "system_prompt": "Escreva posts.",
        "requires_approval": False
    }
    response = client.post("/api/config", json=payload, headers=user_headers)
    assert response.status_code == 400
    assert "Limite de temas excedido" in response.json()["detail"]


def test_llm_servers_crud(client, user_headers):
    # 1. Create LLM Server
    create_payload = {
        "name": "Ollama Local",
        "provider": "ollama",
        "model": "llama3",
        "base_url": "http://localhost:11434/v1",
        "api_key": "ollama"
    }
    create_res = client.post("/api/llm-servers", json=create_payload, headers=user_headers)
    assert create_res.status_code == 200
    server_data = create_res.json()
    assert server_data["name"] == "Ollama Local"
    server_id = server_data["id"]

    # 2. List LLM Servers
    list_res = client.get("/api/llm-servers", headers=user_headers)
    assert list_res.status_code == 200
    servers = list_res.json()
    assert any(s["id"] == server_id for s in servers)

    # 3. Update LLM Server
    update_payload = {
        "name": "Ollama Local Updated",
        "provider": "ollama",
        "model": "mistral",
        "base_url": "http://localhost:11434/v1",
        "api_key": "ollama"
    }
    update_res = client.put(f"/api/llm-servers/{server_id}", json=update_payload, headers=user_headers)
    assert update_res.status_code == 200
    assert update_res.json()["name"] == "Ollama Local Updated"
    assert update_res.json()["model"] == "mistral"

    # 4. Activate LLM Server
    act_res = client.post(f"/api/llm-servers/{server_id}/activate", headers=user_headers)
    assert act_res.status_code == 200
    assert act_res.json()["is_active"] is True

    # 5. Delete LLM Server
    del_res = client.delete(f"/api/llm-servers/{server_id}", headers=user_headers)
    assert del_res.status_code == 200
    assert del_res.json()["status"] == "success"
