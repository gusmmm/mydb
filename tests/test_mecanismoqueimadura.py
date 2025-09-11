"""
Tests for MecanismoQueimadura functionality.
"""

import tracemalloc

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from src.api import app, get_session

# HTTP status codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_404_NOT_FOUND = 404
HTTP_422_UNPROCESSABLE_ENTITY = 422

# Test constants
INVALID_ID = 999  # Non-existent ID for testing invalid foreign keys

# Start tracemalloc to track memory allocations
tracemalloc.start()


@pytest.fixture(name="engine")
def engine_fixture():
    """Create a test database engine."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    yield engine
    # Ensure engine is properly disposed
    engine.dispose()


@pytest.fixture(name="session")
def session_fixture(engine):
    """Create a test database session."""
    with Session(engine) as session:
        yield session
        # Session is automatically closed by context manager


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Create a test client with the test database session."""
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    with TestClient(app) as client:
        yield client

    # Clean up
    app.dependency_overrides.clear()


def test_create_mecanismo_queimadura(client: TestClient):
    """Test creating a new mecanismo queimadura."""
    response = client.post(
        "/mecanismos_queimadura",
        json={
            "mecanismo_queimadura": "Test Mecanismo",
            "nota": "Test nota"
        }
    )
    assert response.status_code == HTTP_201_CREATED
    data = response.json()
    assert data["mecanismo_queimadura"] == "Test Mecanismo"
    assert data["nota"] == "Test nota"
    assert "id" in data


def test_get_all_mecanismos_queimadura(client: TestClient):
    """Test getting all mecanismos queimadura."""
    # First create some mecanismos
    client.post(
        "/mecanismos_queimadura",
        json={
            "mecanismo_queimadura": "Condução",
            "nota": "Transmissão por contacto directo"
        }
    )
    client.post(
        "/mecanismos_queimadura",
        json={
            "mecanismo_queimadura": "Convecção",
            "nota": "Transmissão através de fluidos"
        }
    )

    response = client.get("/mecanismos_queimadura")
    assert response.status_code == HTTP_200_OK
    data = response.json()
    expected_count = 2
    assert len(data) == expected_count
    assert data[0]["mecanismo_queimadura"] == "Condução"
    assert data[1]["mecanismo_queimadura"] == "Convecção"


def test_get_mecanismo_queimadura_by_id(client: TestClient):
    """Test getting a specific mecanismo queimadura by ID."""
    # Create a mecanismo
    create_response = client.post(
        "/mecanismos_queimadura",
        json={
            "mecanismo_queimadura": "Radiação",
            "nota": "Transmissão através de ondas electromagnéticas"
        }
    )
    mecanismo_id = create_response.json()["id"]

    response = client.get(f"/mecanismos_queimadura/{mecanismo_id}")
    assert response.status_code == HTTP_200_OK
    data = response.json()
    assert data["mecanismo_queimadura"] == "Radiação"
    assert data["nota"] == "Transmissão através de ondas electromagnéticas"
    assert data["id"] == mecanismo_id


def test_get_mecanismo_queimadura_not_found(client: TestClient):
    """Test getting a non-existent mecanismo queimadura."""
    response = client.get(f"/mecanismos_queimadura/{INVALID_ID}")
    assert response.status_code == HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Mecanismo de queimadura not found"}


def test_internamento_with_mecanismo_queimadura_foreign_key(
    client: TestClient
):
    """Test creating an internamento with mecanismo queimadura foreign key."""
    # First create a patient
    patient_response = client.post(
        "/doentes/",
        json={
            "nome": "Test Patient for Mecanismo",
            "numero_processo": 54321,
            "sexo": "F",
            "morada": "Test Mecanismo Address",
            "data_nascimento": "1985-05-15"
        }
    )
    patient_id = patient_response.json()["id"]

    # Create a mecanismo queimadura
    mecanismo_response = client.post(
        "/mecanismos_queimadura",
        json={
            "mecanismo_queimadura": "Test Mecanismo FK",
            "nota": "Test FK nota"
        }
    )
    mecanismo_id = mecanismo_response.json()["id"]

    # Create internamento with foreign key
    internamento_response = client.post(
        "/internamentos",
        json={
            "numero_internamento": 56789,
            "doente_id": patient_id,
            "data_entrada": "2025-09-11",
            "ASCQ_total": 30,
            "lesao_inalatoria": "NAO",
            "mecanismo_queimadura": mecanismo_id
        }
    )
    assert internamento_response.status_code == HTTP_201_CREATED
    data = internamento_response.json()
    assert data["mecanismo_queimadura"] == mecanismo_id
    assert data["doente_id"] == patient_id


def test_internamento_with_multiple_foreign_keys(client: TestClient):
    """Test creating internamento with agente and mecanismo foreign keys."""
    # Create a patient
    patient_response = client.post(
        "/doentes/",
        json={
            "nome": "Multi FK Patient",
            "numero_processo": 11111,
            "sexo": "M",
            "morada": "Multi FK Address",
            "data_nascimento": "1992-03-10"
        }
    )
    patient_id = patient_response.json()["id"]

    # Create tipo acidente
    tipo_response = client.post(
        "/tipos_acidente",
        json={"acidente": "Test Accident", "tipo_acidente": "Test Type"}
    )
    tipo_id = tipo_response.json()["id"]

    # Create agente queimadura
    agente_response = client.post(
        "/agentes_queimadura",
        json={"agente_queimadura": "Test Agent", "nota": "Agent note"}
    )
    agente_id = agente_response.json()["id"]

    # Create mecanismo queimadura
    mecanismo_response = client.post(
        "/mecanismos_queimadura",
        json={
            "mecanismo_queimadura": "Test Mechanism",
            "nota": "Mechanism note"
        }
    )
    mecanismo_id = mecanismo_response.json()["id"]

    # Create internamento with all foreign keys
    internamento_response = client.post(
        "/internamentos",
        json={
            "numero_internamento": 77777,
            "doente_id": patient_id,
            "data_entrada": "2025-09-11",
            "ASCQ_total": 35,
            "lesao_inalatoria": "SIM",
            "tipo_acidente": tipo_id,
            "agente_queimadura": agente_id,
            "mecanismo_queimadura": mecanismo_id
        }
    )
    assert internamento_response.status_code == HTTP_201_CREATED
    data = internamento_response.json()
    assert data["mecanismo_queimadura"] == mecanismo_id
    assert data["agente_queimadura"] == agente_id
    assert data["tipo_acidente"] == tipo_id
    assert data["doente_id"] == patient_id


def test_mecanismo_queimadura_validation(client: TestClient):
    """Test validation for mecanismo queimadura creation."""
    # Test missing required fields
    response = client.post(
        "/mecanismos_queimadura",
        json={"mecanismo_queimadura": "Test without nota"}
    )
    assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY

    response = client.post(
        "/mecanismos_queimadura",
        json={"nota": "Test without mecanismo"}
    )
    assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY


def test_mecanismo_queimadura_empty_fields(client: TestClient):
    """Test mecanismo queimadura with empty fields."""
    response = client.post(
        "/mecanismos_queimadura",
        json={"mecanismo_queimadura": "", "nota": ""}
    )
    # Empty strings are allowed
    assert response.status_code == HTTP_201_CREATED
    data = response.json()
    assert not data["mecanismo_queimadura"]
    assert not data["nota"]


def test_mecanismo_queimadura_special_characters(client: TestClient):
    """Test mecanismo queimadura with special characters."""
    response = client.post(
        "/mecanismos_queimadura",
        json={
            "mecanismo_queimadura": "Radiação Térmica (>100°C)",
            "nota": (
                "Transmissão através de ondas electromagnéticas "
                "com temperatura elevada"
            )
        }
    )
    assert response.status_code == HTTP_201_CREATED
    data = response.json()
    assert data["mecanismo_queimadura"] == "Radiação Térmica (>100°C)"
    assert "electromagnéticas" in data["nota"]


def test_mecanismo_queimadura_long_text(client: TestClient):
    """Test mecanismo queimadura with long text fields."""
    long_mecanismo = "A" * 255  # Test with long string
    long_nota = "B" * 500  # Test with very long note

    response = client.post(
        "/mecanismos_queimadura",
        json={
            "mecanismo_queimadura": long_mecanismo,
            "nota": long_nota
        }
    )
    assert response.status_code == HTTP_201_CREATED
    data = response.json()
    assert data["mecanismo_queimadura"] == long_mecanismo
    assert data["nota"] == long_nota


def test_internamento_with_invalid_mecanismo_queimadura_fk(
    client: TestClient
):
    """Test creating internamento with invalid mecanismo queimadura FK."""
    # Create a patient first
    patient_response = client.post(
        "/doentes/",
        json={
            "nome": "Invalid FK Patient",
            "numero_processo": 99999,
            "sexo": "M",
            "morada": "Invalid FK Address",
            "data_nascimento": "1990-01-01"
        }
    )
    patient_id = patient_response.json()["id"]

    # Try to create internamento with non-existent mecanismo queimadura FK
    # SQLite doesn't enforce foreign key constraints by default in testing
    # but the API should still accept the request and store the value
    internamento_response = client.post(
        "/internamentos",
        json={
            "numero_internamento": 88888,
            "doente_id": patient_id,
            "data_entrada": "2025-09-11",
            "ASCQ_total": 20,
            "lesao_inalatoria": "NAO",
            "mecanismo_queimadura": INVALID_ID  # Non-existent ID
        }
    )
    assert internamento_response.status_code == HTTP_201_CREATED
    data = internamento_response.json()
    # Value should be stored even if invalid
    assert data["mecanismo_queimadura"] == INVALID_ID


def test_get_empty_mecanismos_queimadura_list(client: TestClient):
    """Test getting mecanismos queimadura when none exist."""
    response = client.get("/mecanismos_queimadura")
    assert response.status_code == HTTP_200_OK
    data = response.json()
    assert len(data) == 0
    assert data == []


def test_create_multiple_identical_mecanismos_queimadura(client: TestClient):
    """Test creating multiple mecanismos queimadura with identical content."""
    # Create first mecanismo
    response1 = client.post(
        "/mecanismos_queimadura",
        json={"mecanismo_queimadura": "Identical", "nota": "Same note"}
    )
    assert response1.status_code == HTTP_201_CREATED

    # Create second identical mecanismo (should be allowed)
    response2 = client.post(
        "/mecanismos_queimadura",
        json={"mecanismo_queimadura": "Identical", "nota": "Same note"}
    )
    assert response2.status_code == HTTP_201_CREATED

    # They should have different IDs
    assert response1.json()["id"] != response2.json()["id"]
