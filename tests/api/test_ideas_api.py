def test_ideas_crud(client, user_headers):
    # 1. List empty ideas
    get_res = client.get("/api/ideas", headers=user_headers)
    assert get_res.status_code == 200
    assert get_res.json() == []

    # 2. Create Idea
    payload = {
        "title": "Post sobre FastAPI e AsyncIO",
        "description": "Explicar como o loop assíncrono melhora a concorrência no Python",
        "channel": "bluesky"
    }
    create_res = client.post("/api/ideas", json=payload, headers=user_headers)
    assert create_res.status_code == 200
    idea_id = create_res.json()["id"]
    assert create_res.json()["title"] == "Post sobre FastAPI e AsyncIO"

    # 3. Update Idea
    update_res = client.put(f"/api/ideas/{idea_id}", json={"status": "drafted"}, headers=user_headers)
    assert update_res.status_code == 200
    assert update_res.json()["status"] == "drafted"

    # 4. Delete Idea
    del_res = client.delete(f"/api/ideas/{idea_id}", headers=user_headers)
    assert del_res.status_code == 200
    assert del_res.json()["status"] == "success"
