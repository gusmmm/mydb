import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel

from src.api import app
from src.db import engine

HTTP_OK = 200


# Setup a test session dependency override
@pytest.fixture(name="session")
def session_fixture():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    # (Optional) Do not drop to keep other tests intact


@app.dependency_overrides.get
def override_get_session():  # type: ignore
    with Session(engine) as session:
        yield session


client = TestClient(app)


def test_create_agente_infeccioso_without_codigo():
    payload = {"nome": "Staphylococcus aureus", "tipo_agente": "Bacteria"}
    resp = client.post("/agentes_infecciosos", json=payload)
    assert resp.status_code == HTTP_OK, resp.text
    data = resp.json()
    assert data["nome"] == payload["nome"]
    assert data["tipo_agente"] == payload["tipo_agente"]
    assert data.get("codigo_snomedct") is None
    assert data.get("subtipo_agent") is None


def test_create_agente_infeccioso_with_codigo():
    payload = {
        "nome": "Escherichia coli",
        "tipo_agente": "Bacteria",
        "codigo_snomedct": "112283007",  # Example SNOMED CT ID
    }
    resp = client.post("/agentes_infecciosos", json=payload)
    assert resp.status_code == HTTP_OK, resp.text
    data = resp.json()
    assert data["codigo_snomedct"] == payload["codigo_snomedct"]
    assert data.get("subtipo_agent") is None


def test_create_agente_infeccioso_with_subtipo_agent():
    payload = {
        "nome": "Candida albicans",
        "tipo_agente": "Fungus",
        "codigo_snomedct": "20748006",
        "subtipo_agent": "Opportunistic pathogen"
    }
    resp = client.post("/agentes_infecciosos", json=payload)
    assert resp.status_code == HTTP_OK, resp.text
    data = resp.json()
    assert data["nome"] == payload["nome"]
    assert data["tipo_agente"] == payload["tipo_agente"]
    assert data["codigo_snomedct"] == payload["codigo_snomedct"]
    assert data["subtipo_agent"] == payload["subtipo_agent"]


def test_list_agentes_infecciosos_contains_codigo_field():
    resp = client.get("/agentes_infecciosos")
    assert resp.status_code == HTTP_OK
    data = resp.json()
    assert isinstance(data, list)
    assert any("codigo_snomedct" in item for item in data)
    assert any("subtipo_agent" in item for item in data)


def test_get_single_agente_infeccioso():
    # Create one with code and subtipo_agent
    payload = {
        "nome": "Pseudomonas aeruginosa",
        "tipo_agente": "Bacteria",
        "codigo_snomedct": "267036007",
        "subtipo_agent": "Gram-negative rod"
    }
    create_resp = client.post("/agentes_infecciosos", json=payload)
    assert create_resp.status_code == HTTP_OK
    agente_id = create_resp.json()["id"]

    get_resp = client.get(f"/agentes_infecciosos/{agente_id}")
    assert get_resp.status_code == HTTP_OK
    data = get_resp.json()
    assert data["codigo_snomedct"] == payload["codigo_snomedct"]
    assert data["subtipo_agent"] == payload["subtipo_agent"]


def test_patch_agente_infeccioso():
    # First create an agent
    create_payload = {
        "nome": "Test Agent",
        "tipo_agente": "Bacteria"
    }
    create_resp = client.post("/agentes_infecciosos", json=create_payload)
    assert create_resp.status_code == HTTP_OK
    agente_id = create_resp.json()["id"]
    
    # Test partial update
    update_payload = {
        "subtipo_agent": "Updated Subtype",
        "codigo_snomedct": "123456789"
    }
    patch_resp = client.patch(f"/agentes_infecciosos/{agente_id}", json=update_payload)
    assert patch_resp.status_code == HTTP_OK, patch_resp.text
    
    data = patch_resp.json()
    assert data["nome"] == create_payload["nome"]  # Unchanged
    assert data["tipo_agente"] == create_payload["tipo_agente"]  # Unchanged
    assert data["subtipo_agent"] == update_payload["subtipo_agent"]  # Updated
    assert data["codigo_snomedct"] == update_payload["codigo_snomedct"]  # Updated
    

def test_patch_agente_infeccioso_single_field():
    # First create an agent
    create_payload = {
        "nome": "Another Test Agent",
        "tipo_agente": "Fungus",
        "subtipo_agent": "Original Subtype"
    }
    create_resp = client.post("/agentes_infecciosos", json=create_payload)
    assert create_resp.status_code == HTTP_OK
    agente_id = create_resp.json()["id"]
    
    # Test updating only one field
    update_payload = {
        "codigo_snomedct": "987654321"
    }
    patch_resp = client.patch(f"/agentes_infecciosos/{agente_id}", json=update_payload)
    assert patch_resp.status_code == HTTP_OK, patch_resp.text
    
    data = patch_resp.json()
    assert data["nome"] == create_payload["nome"]  # Unchanged
    assert data["tipo_agente"] == create_payload["tipo_agente"]  # Unchanged
    assert data["subtipo_agent"] == create_payload["subtipo_agent"]  # Unchanged
    assert data["codigo_snomedct"] == update_payload["codigo_snomedct"]  # Updated


def test_patch_agente_infeccioso_not_found():
    # Test updating non-existent agent
    update_payload = {
        "subtipo_agent": "Should Fail"
    }
    patch_resp = client.patch("/agentes_infecciosos/999999", json=update_payload)
    assert patch_resp.status_code == 404
    assert "not found" in patch_resp.json()["detail"].lower()


def test_patch_agente_infeccioso_empty_update():
    # First create an agent
    create_payload = {
        "nome": "Empty Update Test",
        "tipo_agente": "Virus"
    }
    create_resp = client.post("/agentes_infecciosos", json=create_payload)
    assert create_resp.status_code == HTTP_OK
    agente_id = create_resp.json()["id"]
    
    # Test empty update (should return unchanged)
    update_payload = {}
    patch_resp = client.patch(f"/agentes_infecciosos/{agente_id}", json=update_payload)
    assert patch_resp.status_code == HTTP_OK, patch_resp.text
    
    data = patch_resp.json()
    assert data["nome"] == create_payload["nome"]
    assert data["tipo_agente"] == create_payload["tipo_agente"]
