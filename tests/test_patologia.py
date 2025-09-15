# ruff: noqa: PLR6301, PLR2004, E501
from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from src.api import app
from src.db import get_session
from src.models.models import (
    Doente,
    DoentePatologia,
    Patologia,
    SexoEnum,
)

# Test constants
HTTP_200_OK = 200
HTTP_404_NOT_FOUND = 404
HTTP_422_UNPROCESSABLE_ENTITY = 422


@pytest.fixture(name="session")
def session_fixture():
    """Create a test database session."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Create test client with database session."""
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="sample_doente")
def sample_doente_fixture(session: Session):
    """Create a sample patient for testing."""
    doente = Doente(
        nome="Test Patient",
        numero_processo=12345,
        data_nascimento=date(1990, 1, 1),
        sexo=SexoEnum.M,
        morada="Test Street"
    )
    session.add(doente)
    session.commit()
    session.refresh(doente)
    return doente


@pytest.fixture(name="sample_patologia")
def sample_patologia_fixture(session: Session):
    """Create a sample pathology for testing."""
    patologia = Patologia(
        nome_patologia="Diabetes",
        classe_patologia="Endócrino",
        codigo="E11.9"
    )
    session.add(patologia)
    session.commit()
    session.refresh(patologia)
    return patologia


class TestPatologia:
    """Test cases for Patologia model and API."""

    def test_create_patologia(self, client: TestClient):
        """Test creating a new patologia."""
        patologia_data = {
            "nome_patologia": "Hipertensão Arterial",
            "classe_patologia": "Cardiovascular",
            "codigo": "I10"
        }

        response = client.post("/patologias", json=patologia_data)

        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert data["nome_patologia"] == "Hipertensão Arterial"
        assert data["classe_patologia"] == "Cardiovascular"
        assert data["codigo"] == "I10"
        assert "id" in data

    def test_create_patologia_minimal(self, client: TestClient):
        """Test creating patologia with minimal required fields."""
        patologia_data = {
            "nome_patologia": "Asma"
        }

        response = client.post("/patologias", json=patologia_data)

        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert data["nome_patologia"] == "Asma"
        assert data["classe_patologia"] is None
        assert data["codigo"] is None

    def test_get_all_patologias(self, client: TestClient, sample_patologia: Patologia):
        """Test getting all patologias."""
        response = client.get("/patologias")

        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["nome_patologia"] == sample_patologia.nome_patologia

    def test_get_patologia_by_id(self, client: TestClient, sample_patologia: Patologia):
        """Test getting a specific patologia by ID."""
        response = client.get(f"/patologias/{sample_patologia.id}")

        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert data["nome_patologia"] == sample_patologia.nome_patologia
        assert data["classe_patologia"] == sample_patologia.classe_patologia
        assert data["codigo"] == sample_patologia.codigo
        assert data["id"] == sample_patologia.id

    def test_get_nonexistent_patologia(self, client: TestClient):
        """Test getting a non-existent patologia."""
        response = client.get("/patologias/999")

        assert response.status_code == HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Patologia not found"

    def test_patologia_required_fields(self, client: TestClient):
        """Test that nome_patologia is required."""
        patologia_data = {
            "classe_patologia": "Cardiovascular"
        }

        response = client.post("/patologias", json=patologia_data)

        assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY


class TestDoentePatologia:
    """Test cases for DoentePatologia model and API."""

    def test_create_doente_patologia(
        self,
        client: TestClient,
        sample_doente: Doente,
        sample_patologia: Patologia
    ):
        """Test creating a new doente-patologia relationship."""
        data = {
            "doente_id": sample_doente.id,
            "patologia": sample_patologia.id,
            "nota": "Diabetes controlada com medicação"
        }

        response = client.post("/doentes_patologia", json=data)

        assert response.status_code == HTTP_200_OK
        response_data = response.json()
        assert response_data["doente_id"] == sample_doente.id
        assert response_data["patologia"] == sample_patologia.id
        assert response_data["nota"] == "Diabetes controlada com medicação"
        assert "id" in response_data

    def test_create_doente_patologia_minimal(
        self,
        client: TestClient,
        sample_doente: Doente
    ):
        """Test creating doente-patologia with minimal fields."""
        data = {
            "doente_id": sample_doente.id
        }

        response = client.post("/doentes_patologia", json=data)

        assert response.status_code == HTTP_200_OK
        response_data = response.json()
        assert response_data["doente_id"] == sample_doente.id
        assert response_data["patologia"] is None
        assert response_data["nota"] is None

    def test_create_doente_patologia_invalid_doente(
        self,
        client: TestClient
    ):
        """Test creating doente-patologia with invalid doente."""
        data = {
            "doente_id": 999,
            "patologia": 1,
            "nota": "Test note"
        }

        response = client.post("/doentes_patologia", json=data)

        assert response.status_code == HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Doente not found"

    def test_create_doente_patologia_invalid_patologia(
        self,
        client: TestClient,
        sample_doente: Doente
    ):
        """Test creating doente-patologia with invalid patologia."""
        data = {
            "doente_id": sample_doente.id,
            "patologia": 999,
            "nota": "Test note"
        }

        response = client.post("/doentes_patologia", json=data)

        assert response.status_code == HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Patologia not found"

    def test_get_all_doentes_patologia(
        self,
        client: TestClient,
        sample_doente: Doente,
        sample_patologia: Patologia
    ):
        """Test getting all doente-patologia relationships."""
        # Create a relationship first
        data = {
            "doente_id": sample_doente.id,
            "patologia": sample_patologia.id,
            "nota": "Test relationship"
        }
        client.post("/doentes_patologia", json=data)

        response = client.get("/doentes_patologia")

        assert response.status_code == HTTP_200_OK
        response_data = response.json()
        assert isinstance(response_data, list)
        assert len(response_data) >= 1
        assert response_data[0]["doente_id"] == sample_doente.id

    def test_get_doente_patologia_by_id(
        self,
        client: TestClient,
        sample_doente: Doente,
        sample_patologia: Patologia
    ):
        """Test getting a specific doente-patologia by ID."""
        data = {
            "doente_id": sample_doente.id,
            "patologia": sample_patologia.id,
            "nota": "Test relationship"
        }
        create_response = client.post("/doentes_patologia", json=data)
        created_id = create_response.json()["id"]

        response = client.get(f"/doentes_patologia/{created_id}")

        assert response.status_code == HTTP_200_OK
        response_data = response.json()
        assert response_data["doente_id"] == sample_doente.id
        assert response_data["patologia"] == sample_patologia.id
        assert response_data["id"] == created_id

    def test_get_nonexistent_doente_patologia(self, client: TestClient):
        """Test getting a non-existent doente-patologia."""
        response = client.get("/doentes_patologia/999")

        assert response.status_code == HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Doente patologia not found"

    def test_get_patologias_by_doente(
        self,
        client: TestClient,
        sample_doente: Doente,
        sample_patologia: Patologia
    ):
        """Test getting patologias for a specific doente."""
        # Create a relationship first
        data = {
            "doente_id": sample_doente.id,
            "patologia": sample_patologia.id,
            "nota": "Test relationship"
        }
        client.post("/doentes_patologia", json=data)

        response = client.get(f"/doentes/{sample_doente.id}/patologias")

        assert response.status_code == HTTP_200_OK
        response_data = response.json()
        assert isinstance(response_data, list)
        assert len(response_data) >= 1
        assert response_data[0]["doente_id"] == sample_doente.id
        assert response_data[0]["patologia"] == sample_patologia.id

    def test_get_patologias_by_nonexistent_doente(self, client: TestClient):
        """Test getting patologias for non-existent doente."""
        response = client.get("/doentes/999/patologias")

        assert response.status_code == HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Doente not found"

    def test_doente_patologia_required_fields(self, client: TestClient):
        """Test that doente_id is required."""
        data = {
            "patologia": 1
        }

        response = client.post("/doentes_patologia", json=data)

        assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY


class TestDatabaseRelationships:
    """Test database relationships for patologia tables."""

    def test_patologia_doente_relationship(
        self,
        session: Session,
        sample_doente: Doente,
        sample_patologia: Patologia
    ):
        """Test the relationship between patologia and doente."""
        # Create a relationship
        doente_patologia = DoentePatologia(
            doente_id=sample_doente.id,
            patologia=sample_patologia.id,
            nota="Test relationship"
        )
        session.add(doente_patologia)
        session.commit()
        session.refresh(doente_patologia)

        # Test forward relationship
        assert doente_patologia.doente is not None
        assert doente_patologia.doente.id == sample_doente.id

        # Test patologia relationship
        assert doente_patologia.patologia_rel is not None
        assert doente_patologia.patologia_rel.id == sample_patologia.id

    def test_doente_has_patologias_relationship(
        self,
        session: Session,
        sample_doente: Doente,
        sample_patologia: Patologia
    ):
        """Test that doente can access its patologias."""
        # Create a relationship
        doente_patologia = DoentePatologia(
            doente_id=sample_doente.id,
            patologia=sample_patologia.id,
            nota="Test relationship"
        )
        session.add(doente_patologia)
        session.commit()

        # Refresh to load relationships
        session.refresh(sample_doente)

        # Test that doente has patologias
        assert len(sample_doente.doente_patologias) >= 1
        assert sample_doente.doente_patologias[0].patologia == sample_patologia.id

    def test_patologia_has_doentes_relationship(
        self,
        session: Session,
        sample_doente: Doente,
        sample_patologia: Patologia
    ):
        """Test that patologia can access its doentes."""
        # Create a relationship
        doente_patologia = DoentePatologia(
            doente_id=sample_doente.id,
            patologia=sample_patologia.id,
            nota="Test relationship"
        )
        session.add(doente_patologia)
        session.commit()

        # Refresh to load relationships
        session.refresh(sample_patologia)

        # Test that patologia has doente relationships
        assert len(sample_patologia.doente_patologias) >= 1
        assert sample_patologia.doente_patologias[0].doente_id == sample_doente.id
