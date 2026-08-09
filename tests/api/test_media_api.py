import io
import pytest

def test_upload_media_success(client, user_headers):
    file_content = b"fake image byte content png"
    files = {
        "file": ("test_foto.png", io.BytesIO(file_content), "image/png")
    }
    response = client.post("/api/media/upload", files=files, headers=user_headers)
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["original_name"] == "test_foto.png"
    assert data["mime_type"] == "image/png"
    assert "url" in data
    assert "/uploads/user_" in data["url"]

def test_upload_media_invalid_type(client, user_headers):
    file_content = b"%PDF-1.4 fake pdf file content"
    files = {
        "file": ("documento.pdf", io.BytesIO(file_content), "application/pdf")
    }
    response = client.post("/api/media/upload", files=files, headers=user_headers)
    assert response.status_code == 400
    assert "Formato de arquivo não suportado" in response.json()["detail"]

def test_get_user_media_list(client, user_headers):
    # Upload one file
    file_content = b"fake image byte content jpg"
    files = {
        "file": ("foto2.jpg", io.BytesIO(file_content), "image/jpeg")
    }
    client.post("/api/media/upload", files=files, headers=user_headers)

    response = client.get("/api/media", headers=user_headers)
    assert response.status_code == 200
    media_list = response.json()
    assert isinstance(media_list, list)
    assert len(media_list) >= 1
    assert any(m["original_name"] == "foto2.jpg" for m in media_list)

def test_attach_media_to_calendar_item(client, user_headers):
    # 1. Upload media
    files = {
        "file": ("banner.png", io.BytesIO(b"banner bytes"), "image/png")
    }
    upload_res = client.post("/api/media/upload", files=files, headers=user_headers)
    media_id = upload_res.json()["id"]

    # 2. Create scheduled item
    cal_payload = {
        "theme": "Post com Mídia",
        "scheduled_date": "2028-10-10T15:00:00Z",
        "is_manual": True,
        "manual_content": "Legenda do post com foto de mídia anexada."
    }
    cal_res = client.post("/api/calendar", json=cal_payload, headers=user_headers)
    item_id = cal_res.json()["id"]

    # 3. Attach media to existing item
    attach_res = client.post(f"/api/calendar/{item_id}/media", json={"media_id": media_id}, headers=user_headers)
    assert attach_res.status_code == 200
    item_data = attach_res.json()
    assert item_data["media_id"] == media_id
    assert item_data["media"]["id"] == media_id

def test_user_media_isolation(client, user_headers, admin_headers):
    # User A uploads media
    files = {
        "file": ("privado.png", io.BytesIO(b"private data"), "image/png")
    }
    upload_res = client.post("/api/media/upload", files=files, headers=user_headers)
    media_id = upload_res.json()["id"]

    # Admin (User B) tries to delete User A's media
    del_res = client.delete(f"/api/media/{media_id}", headers=admin_headers)
    assert del_res.status_code == 404
    assert "Arquivo de mídia não encontrado" in del_res.json()["detail"]

def test_delete_media_success(client, user_headers):
    files = {
        "file": ("deletar.png", io.BytesIO(b"to delete"), "image/png")
    }
    upload_res = client.post("/api/media/upload", files=files, headers=user_headers)
    media_id = upload_res.json()["id"]

    # Delete
    del_res = client.delete(f"/api/media/{media_id}", headers=user_headers)
    assert del_res.status_code == 200
    assert del_res.json()["status"] == "success"

    # Confirm list is empty of this asset
    list_res = client.get("/api/media", headers=user_headers)
    assert not any(m["id"] == media_id for m in list_res.json())
