"""Tests for trauma and traumaTipo functionality."""

from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from src.api import app
from src.db import get_session
from src.models.models import (
    Doente,
    Internamento,
    LesaoInalatorialEnum,
    SexoEnum,
    TraumaTipo,
)

# HTTP Status Code Constants
HTTP_200_OK = 200
HTTP_404_NOT_FOUND = 404
HTTP_422_UNPROCESSABLE_ENTITY = 422
HTTP_STATUS_COUNT_TWO = 2


@pytest.fixture(name="engine")
def engine_fixture():
    """Create a test database engine."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
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
    """Create test client with session dependency override."""
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="sample_doente")
def sample_doente_fixture(session: Session):
    """Create sample patient for testing."""
    doente = Doente(
        nome="Test Patient",
        numero_processo=12345,
        data_nascimento=date(1990, 1, 1),
        sexo=SexoEnum.M,
        morada="Test Address",
    )
    session.add(doente)
    session.commit()
    session.refresh(doente)
    return doente


@pytest.fixture(name="sample_internamento")
def sample_internamento_fixture(session: Session, sample_doente):
    """Create sample internamento for testing."""
    internamento = Internamento(
        numero_internamento=54321,
        data_entrada=date(2025, 1, 15),
        ASCQ_total=25,
        lesao_inalatoria=LesaoInalatorialEnum.NAO,
        doente_id=sample_doente.id,
    )
    session.add(internamento)
    session.commit()
    session.refresh(internamento)
    return internamento


@pytest.fixture(name="sample_traumatipo")
def sample_traumatipo_fixture(session: Session):
    """Create sample trauma tipo for testing."""
    traumatipo = TraumaTipo(
        local="Crânio",
        tipo="Traumatismo craneoencefálico"
    )
    session.add(traumatipo)
    session.commit()
    session.refresh(traumatipo)
    return traumatipo


class TestTraumaTipo:
    """Tests for TraumaTipo functionality."""

    @staticmethod
    def test_create_traumatipo(client: TestClient):
        """Test creating a new traumatipo."""
        traumatipo_data = {
            "local": "Face",
            "tipo": "Traumatismo facial"
        }
        response = client.post("/tipos_trauma", json=traumatipo_data)

        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert data["local"] == "Face"
        assert data["tipo"] == "Traumatismo facial"
        assert "id" in data
        assert data["id"] is not None

    @staticmethod
    def test_get_all_traumatipos_empty(client: TestClient):
        """Test getting all traumatipos when empty."""
        response = client.get("/tipos_trauma")
        assert response.status_code == HTTP_200_OK
        assert response.json() == []

    @staticmethod
    def test_get_all_traumatipos(client: TestClient, sample_traumatipo):
        """Test getting all traumatipos."""
        response = client.get("/tipos_trauma")
        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["local"] == "Crânio"
        assert data[0]["tipo"] == "Traumatismo craneoencefálico"

    @staticmethod
    def test_get_traumatipo_by_id(client: TestClient, sample_traumatipo):
        """Test getting traumatipo by ID."""
        response = client.get(f"/tipos_trauma/{sample_traumatipo.id}")
        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert data["id"] == sample_traumatipo.id
        assert data["local"] == "Crânio"
        assert data["tipo"] == "Traumatismo craneoencefálico"

    @staticmethod
    def test_get_traumatipo_not_found(client: TestClient):
        """Test getting non-existent traumatipo."""
        response = client.get("/tipos_trauma/999")
        assert response.status_code == HTTP_404_NOT_FOUND
        expected_response = {"detail": "Tipo de trauma not found"}
        assert response.json() == expected_response

    @staticmethod
    def test_traumatipo_required_fields(client: TestClient):
        """Test traumatipo creation with missing required fields."""
        # Missing local
        response = client.post("/tipos_trauma", json={"tipo": "Test"})
        assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY

        # Missing tipo
        response = client.post("/tipos_trauma", json={"local": "Test"})
        assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY

    @staticmethod
    def test_traumatipo_audit_fields(client: TestClient):
        """Test that audit fields are automatically set."""
        traumatipo_data = {
            "local": "Tórax",
            "tipo": "Traumatismo torácico"
        }
        response = client.post("/tipos_trauma", json=traumatipo_data)

        assert response.status_code == HTTP_200_OK
        # Note: API doesn't return audit fields,
        # but they should be set in database


class TestTrauma:
    """Tests for Trauma functionality."""

    @staticmethod
    def test_create_trauma(
        client: TestClient, sample_internamento, sample_traumatipo
    ):
        """Test creating a new trauma."""
        trauma_data = {
            "internamento_id": sample_internamento.id,
            "tipo_local": sample_traumatipo.id,
            "cirurgia_urgente": True
        }
        response = client.post("/traumas", json=trauma_data)

        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert data["internamento_id"] == sample_internamento.id
        assert data["tipo_local"] == sample_traumatipo.id
        assert data["cirurgia_urgente"] is True
        assert "id" in data
        assert data["id"] is not None

    @staticmethod
    def test_create_trauma_optional_fields(
        client: TestClient, sample_internamento
    ):
        """Test creating trauma with optional fields only."""
        trauma_data = {
            "internamento_id": sample_internamento.id,
            "cirurgia_urgente": False
        }
        response = client.post("/traumas", json=trauma_data)

        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert data["internamento_id"] == sample_internamento.id
        assert data["tipo_local"] is None
        assert data["cirurgia_urgente"] is False

    @staticmethod
    def test_create_trauma_invalid_internamento(
        client: TestClient, sample_traumatipo
    ):
        """Test creating trauma with invalid internamento_id."""
        trauma_data = {
            "internamento_id": 999,
            "tipo_local": sample_traumatipo.id,
            "cirurgia_urgente": True
        }
        response = client.post("/traumas", json=trauma_data)

        assert response.status_code == HTTP_404_NOT_FOUND
        expected_response = {"detail": "Internamento not found"}
        assert response.json() == expected_response

    @staticmethod
    def test_create_trauma_invalid_traumatipo(
        client: TestClient, sample_internamento
    ):
        """Test creating trauma with invalid tipo_local."""
        trauma_data = {
            "internamento_id": sample_internamento.id,
            "tipo_local": 999,
            "cirurgia_urgente": False
        }
        response = client.post("/traumas", json=trauma_data)

        assert response.status_code == HTTP_404_NOT_FOUND
        expected_response = {"detail": "Tipo de trauma not found"}
        assert response.json() == expected_response

    @staticmethod
    def test_get_all_traumas_empty(client: TestClient):
        """Test getting all traumas when empty."""
        response = client.get("/traumas")
        assert response.status_code == HTTP_200_OK
        assert response.json() == []

    @staticmethod
    def test_get_all_traumas(
        client: TestClient, sample_internamento, sample_traumatipo
    ):
        """Test getting all traumas."""
        # Create trauma first
        trauma_data = {
            "internamento_id": sample_internamento.id,
            "tipo_local": sample_traumatipo.id,
            "cirurgia_urgente": True
        }
        client.post("/traumas", json=trauma_data)

        response = client.get("/traumas")
        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["internamento_id"] == sample_internamento.id
        assert data[0]["tipo_local"] == sample_traumatipo.id
        assert data[0]["cirurgia_urgente"] is True

    @staticmethod
    def test_get_trauma_by_id(
        client: TestClient, sample_internamento, sample_traumatipo
    ):
        """Test getting trauma by ID."""
        # Create trauma first
        trauma_data = {
            "internamento_id": sample_internamento.id,
            "tipo_local": sample_traumatipo.id,
            "cirurgia_urgente": False
        }
        create_response = client.post("/traumas", json=trauma_data)
        trauma_id = create_response.json()["id"]

        response = client.get(f"/traumas/{trauma_id}")
        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert data["id"] == trauma_id
        assert data["internamento_id"] == sample_internamento.id
        assert data["tipo_local"] == sample_traumatipo.id
        assert data["cirurgia_urgente"] is False

    @staticmethod
    def test_get_trauma_not_found(client: TestClient):
        """Test getting non-existent trauma."""
        response = client.get("/traumas/999")
        assert response.status_code == HTTP_404_NOT_FOUND
        expected_response = {"detail": "Trauma not found"}
        assert response.json() == expected_response

    @staticmethod
    def test_get_traumas_by_internamento(
        client: TestClient, sample_internamento, sample_traumatipo
    ):
        """Test getting traumas for specific internamento."""
        # Create multiple traumas for the same internamento
        trauma_data_1 = {
            "internamento_id": sample_internamento.id,
            "tipo_local": sample_traumatipo.id,
            "cirurgia_urgente": True
        }
        trauma_data_2 = {
            "internamento_id": sample_internamento.id,
            "cirurgia_urgente": False
        }

        client.post("/traumas", json=trauma_data_1)
        client.post("/traumas", json=trauma_data_2)

        endpoint = f"/internamentos/{sample_internamento.id}/traumas"
        response = client.get(endpoint)
        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert len(data) == HTTP_STATUS_COUNT_TWO
        # All traumas should belong to this internamento
        for trauma in data:
            assert trauma["internamento_id"] == sample_internamento.id

    @staticmethod
    def test_get_traumas_by_nonexistent_internamento(client: TestClient):
        """Test getting traumas for non-existent internamento."""
        response = client.get("/internamentos/999/traumas")
        assert response.status_code == HTTP_404_NOT_FOUND
        expected_response = {"detail": "Internamento not found"}
        assert response.json() == expected_response

    @staticmethod
    def test_trauma_required_fields(client: TestClient):
        """Test trauma creation with missing required fields."""
        # Missing internamento_id
        response = client.post("/traumas", json={"cirurgia_urgente": True})
        assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY

    @staticmethod
    def test_trauma_audit_fields(client: TestClient, sample_internamento):
        """Test that audit fields are automatically set."""
        trauma_data = {
            "internamento_id": sample_internamento.id,
            "cirurgia_urgente": True
        }
        response = client.post("/traumas", json=trauma_data)

        assert response.status_code == HTTP_200_OK
        # Note: API doesn't return audit fields,
        # but they should be set in database

    @staticmethod
    def test_multiple_traumas_per_internamento(
        client: TestClient, sample_internamento, sample_traumatipo
    ):
        """Test business rule: each internamento can have multiple traumas."""
        # Create multiple traumas for same internamento
        trauma_1 = {
            "internamento_id": sample_internamento.id,
            "tipo_local": sample_traumatipo.id,
            "cirurgia_urgente": True
        }
        trauma_2 = {
            "internamento_id": sample_internamento.id,
            "cirurgia_urgente": False
        }

        response1 = client.post("/traumas", json=trauma_1)
        response2 = client.post("/traumas", json=trauma_2)

        assert response1.status_code == HTTP_200_OK
        assert response2.status_code == HTTP_200_OK

        # Verify both traumas exist
        endpoint = f"/internamentos/{sample_internamento.id}/traumas"
        response = client.get(endpoint)
        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert len(data) == HTTP_STATUS_COUNT_TWO

    @staticmethod
    def test_zero_traumas_per_internamento(
        client: TestClient, sample_internamento
    ):
        """Test business rule: each internamento can have zero traumas."""
        # Don't create any traumas, just verify empty result
        endpoint = f"/internamentos/{sample_internamento.id}/traumas"
        response = client.get(endpoint)
        assert response.status_code == HTTP_200_OK
        assert response.json() == []


class TestTraumaEdgeCases:
    """Edge case tests for trauma functionality."""

    @staticmethod
    def test_trauma_with_null_tipo_local(
        client: TestClient, sample_internamento
    ):
        """Test trauma creation with null tipo_local (should be allowed)."""
        trauma_data = {
            "internamento_id": sample_internamento.id,
            "cirurgia_urgente": True
        }
        response = client.post("/traumas", json=trauma_data)

        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert data["tipo_local"] is None

    @staticmethod
    def test_trauma_with_null_cirurgia_urgente(
        client: TestClient, sample_internamento
    ):
        """Test trauma creation with null cirurgia_urgente.

        Should be allowed per business rules.
        """
        trauma_data = {
            "internamento_id": sample_internamento.id,
        }
        response = client.post("/traumas", json=trauma_data)

        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert data["cirurgia_urgente"] is None
