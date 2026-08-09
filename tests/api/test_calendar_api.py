from datetime import datetime, timedelta

def test_get_calendar_empty(client, user_headers):
    response = client.get("/api/calendar", headers=user_headers)
    assert response.status_code == 200
    assert response.json() == []

def test_create_calendar_item_future(client, user_headers):
    future_date = (datetime.utcnow() + timedelta(days=2)).isoformat() + "Z"
    payload = {
        "theme": "Inteligência Artificial na Prática",
        "scheduled_date": future_date,
        "objective": "Engajar a comunidade",
        "cta": "Deixe sua opinião nos comentários",
        "channel": "bluesky",
        "is_manual": False
    }
    response = client.post("/api/calendar", json=payload, headers=user_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["theme"] == "Inteligência Artificial na Prática"
    assert data["channel"] == "bluesky"

def test_create_calendar_item_past_error(client, user_headers):
    past_date = (datetime.utcnow() - timedelta(days=1)).isoformat() + "Z"
    payload = {
        "theme": "Post no Passado",
        "scheduled_date": past_date,
        "channel": "bluesky"
    }
    response = client.post("/api/calendar", json=payload, headers=user_headers)
    assert response.status_code == 400
    assert "no passado" in response.json()["detail"]

def test_calendar_item_crud(client, user_headers):
    future_date = (datetime.utcnow() + timedelta(days=3)).isoformat() + "Z"
    
    # 1. Create
    payload = {
        "theme": "Dica de Python",
        "scheduled_date": future_date,
        "channel": "bluesky"
    }
    create_res = client.post("/api/calendar", json=payload, headers=user_headers)
    assert create_res.status_code == 200
    item_id = create_res.json()["id"]

    # 2. Update
    new_date = (datetime.utcnow() + timedelta(days=4)).isoformat() + "Z"
    update_payload = {
        "theme": "Dica de Python Atualizada",
        "scheduled_date": new_date,
        "channel": "twitter"
    }
    update_res = client.put(f"/api/calendar/{item_id}", json=update_payload, headers=user_headers)
    assert update_res.status_code == 200
    assert update_res.json()["theme"] == "Dica de Python Atualizada"
    assert update_res.json()["channel"] == "twitter"

    # 3. Delete
    del_res = client.delete(f"/api/calendar/{item_id}", headers=user_headers)
    assert del_res.status_code == 200
    assert del_res.json()["status"] == "success"
