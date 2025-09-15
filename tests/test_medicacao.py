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
    DoenteMedicacao,
    Medicacao,
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


@pytest.fixture(name="sample_medicacao")
def sample_medicacao_fixture(session: Session):
    """Create a sample medication for testing."""
    medicacao = Medicacao(
        nome_medicacao="Paracetamol",
        classe_terapeutica="Analgésico",
        codigo="N02BE01"
    )
    session.add(medicacao)
    session.commit()
    session.refresh(medicacao)
    return medicacao


class TestMedicacao:
    """Test cases for Medicacao model and API."""

    def test_create_medicacao(self, client: TestClient):
        """Test creating a new medicacao."""
        medicacao_data = {
            "nome_medicacao": "Ibuprofeno",
            "classe_terapeutica": "Anti-inflamatório",
            "codigo": "M01AE01"
        }

        response = client.post("/medicacoes", json=medicacao_data)

        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert data["nome_medicacao"] == "Ibuprofeno"
        assert data["classe_terapeutica"] == "Anti-inflamatório"
        assert data["codigo"] == "M01AE01"
        assert "id" in data

    def test_create_medicacao_minimal(self, client: TestClient):
        """Test creating medicacao with minimal required fields."""
        medicacao_data = {
            "nome_medicacao": "Aspirina"
        }

        response = client.post("/medicacoes", json=medicacao_data)

        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert data["nome_medicacao"] == "Aspirina"
        assert data["classe_terapeutica"] is None
        assert data["codigo"] is None

    def test_get_all_medicacoes(self, client: TestClient, sample_medicacao: Medicacao):
        """Test getting all medicacoes."""
        response = client.get("/medicacoes")

        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["nome_medicacao"] == sample_medicacao.nome_medicacao

    def test_get_medicacao_by_id(self, client: TestClient, sample_medicacao: Medicacao):
        """Test getting a specific medicacao by ID."""
        response = client.get(f"/medicacoes/{sample_medicacao.id}")

        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert data["nome_medicacao"] == sample_medicacao.nome_medicacao
        assert data["classe_terapeutica"] == sample_medicacao.classe_terapeutica
        assert data["codigo"] == sample_medicacao.codigo
        assert data["id"] == sample_medicacao.id

    def test_get_nonexistent_medicacao(self, client: TestClient):
        """Test getting a non-existent medicacao."""
        response = client.get("/medicacoes/999")

        assert response.status_code == HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Medicacao not found"

    def test_medicacao_required_fields(self, client: TestClient):
        """Test that nome_medicacao is required."""
        medicacao_data = {
            "classe_terapeutica": "Antibiótico"
        }

        response = client.post("/medicacoes", json=medicacao_data)

        assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY


class TestDoenteMedicacao:
    """Test cases for DoenteMedicacao model and API."""

    def test_create_doente_medicacao(
        self,
        client: TestClient,
        sample_doente: Doente,
        sample_medicacao: Medicacao
    ):
        """Test creating a new doente-medicacao relationship."""
        data = {
            "doente_id": sample_doente.id,
            "medicacao": sample_medicacao.id,
            "nota": "Tomar 500mg de 8 em 8 horas"
        }

        response = client.post("/doentes_medicacao", json=data)

        assert response.status_code == HTTP_200_OK
        response_data = response.json()
        assert response_data["doente_id"] == sample_doente.id
        assert response_data["medicacao"] == sample_medicacao.id
        assert response_data["nota"] == "Tomar 500mg de 8 em 8 horas"
        assert "id" in response_data

    def test_create_doente_medicacao_minimal(
        self,
        client: TestClient,
        sample_doente: Doente
    ):
        """Test creating doente-medicacao with minimal fields."""
        data = {
            "doente_id": sample_doente.id
        }

        response = client.post("/doentes_medicacao", json=data)

        assert response.status_code == HTTP_200_OK
        response_data = response.json()
        assert response_data["doente_id"] == sample_doente.id
        assert response_data["medicacao"] is None
        assert response_data["nota"] is None

    def test_create_doente_medicacao_invalid_doente(
        self,
        client: TestClient
    ):
        """Test creating doente-medicacao with invalid doente."""
        data = {
            "doente_id": 999,
            "medicacao": 1,
            "nota": "Test note"
        }

        response = client.post("/doentes_medicacao", json=data)

        assert response.status_code == HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Doente not found"

    def test_create_doente_medicacao_invalid_medicacao(
        self,
        client: TestClient,
        sample_doente: Doente
    ):
        """Test creating doente-medicacao with invalid medicacao."""
        data = {
            "doente_id": sample_doente.id,
            "medicacao": 999,
            "nota": "Test note"
        }

        response = client.post("/doentes_medicacao", json=data)

        assert response.status_code == HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Medicacao not found"

    def test_get_all_doentes_medicacao(
        self,
        client: TestClient,
        sample_doente: Doente,
        sample_medicacao: Medicacao
    ):
        """Test getting all doente-medicacao relationships."""
        # Create a relationship first
        data = {
            "doente_id": sample_doente.id,
            "medicacao": sample_medicacao.id,
            "nota": "Test relationship"
        }
        client.post("/doentes_medicacao", json=data)

        response = client.get("/doentes_medicacao")

        assert response.status_code == HTTP_200_OK
        response_data = response.json()
        assert isinstance(response_data, list)
        assert len(response_data) >= 1
        assert response_data[0]["doente_id"] == sample_doente.id

    def test_get_doente_medicacao_by_id(
        self,
        client: TestClient,
        sample_doente: Doente,
        sample_medicacao: Medicacao
    ):
        """Test getting a specific doente-medicacao by ID."""
        data = {
            "doente_id": sample_doente.id,
            "medicacao": sample_medicacao.id,
            "nota": "Test relationship"
        }
        create_response = client.post("/doentes_medicacao", json=data)
        created_id = create_response.json()["id"]

        response = client.get(f"/doentes_medicacao/{created_id}")

        assert response.status_code == HTTP_200_OK
        response_data = response.json()
        assert response_data["doente_id"] == sample_doente.id
        assert response_data["medicacao"] == sample_medicacao.id
        assert response_data["id"] == created_id

    def test_get_nonexistent_doente_medicacao(self, client: TestClient):
        """Test getting a non-existent doente-medicacao."""
        response = client.get("/doentes_medicacao/999")

        assert response.status_code == HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Doente medicacao not found"

    def test_get_medicacoes_by_doente(
        self,
        client: TestClient,
        sample_doente: Doente,
        sample_medicacao: Medicacao
    ):
        """Test getting medicacoes for a specific doente."""
        # Create a relationship first
        data = {
            "doente_id": sample_doente.id,
            "medicacao": sample_medicacao.id,
            "nota": "Test relationship"
        }
        client.post("/doentes_medicacao", json=data)

        response = client.get(f"/doentes/{sample_doente.id}/medicacoes")

        assert response.status_code == HTTP_200_OK
        response_data = response.json()
        assert isinstance(response_data, list)
        assert len(response_data) >= 1
        assert response_data[0]["doente_id"] == sample_doente.id
        assert response_data[0]["medicacao"] == sample_medicacao.id

    def test_get_medicacoes_by_nonexistent_doente(self, client: TestClient):
        """Test getting medicacoes for non-existent doente."""
        response = client.get("/doentes/999/medicacoes")

        assert response.status_code == HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Doente not found"

    def test_doente_medicacao_required_fields(self, client: TestClient):
        """Test that doente_id is required."""
        data = {
            "medicacao": 1
        }

        response = client.post("/doentes_medicacao", json=data)

        assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY


class TestDatabaseRelationships:
    """Test database relationships for medicacao tables."""

    def test_medicacao_doente_relationship(
        self,
        session: Session,
        sample_doente: Doente,
        sample_medicacao: Medicacao
    ):
        """Test the relationship between medicacao and doente."""
        # Create a relationship
        doente_medicacao = DoenteMedicacao(
            doente_id=sample_doente.id,
            medicacao=sample_medicacao.id,
            nota="Test relationship"
        )
        session.add(doente_medicacao)
        session.commit()
        session.refresh(doente_medicacao)

        # Test forward relationship
        assert doente_medicacao.doente is not None
        assert doente_medicacao.doente.id == sample_doente.id

        # Test medicacao relationship
        assert doente_medicacao.medicacao_rel is not None
        assert doente_medicacao.medicacao_rel.id == sample_medicacao.id

    def test_doente_has_medicacoes_relationship(
        self,
        session: Session,
        sample_doente: Doente,
        sample_medicacao: Medicacao
    ):
        """Test that doente can access its medicacoes."""
        # Create a relationship
        doente_medicacao = DoenteMedicacao(
            doente_id=sample_doente.id,
            medicacao=sample_medicacao.id,
            nota="Test relationship"
        )
        session.add(doente_medicacao)
        session.commit()

        # Refresh to load relationships
        session.refresh(sample_doente)

        # Test that doente has medicacoes
        assert len(sample_doente.doente_medicacoes) >= 1
        assert sample_doente.doente_medicacoes[0].medicacao == sample_medicacao.id

    def test_medicacao_has_doentes_relationship(
        self,
        session: Session,
        sample_doente: Doente,
        sample_medicacao: Medicacao
    ):
        """Test that medicacao can access its doentes."""
        # Create a relationship
        doente_medicacao = DoenteMedicacao(
            doente_id=sample_doente.id,
            medicacao=sample_medicacao.id,
            nota="Test relationship"
        )
        session.add(doente_medicacao)
        session.commit()

        # Refresh to load relationships
        session.refresh(sample_medicacao)

        # Test that medicacao has doente relationships
        assert len(sample_medicacao.doente_medicacoes) >= 1
        assert sample_medicacao.doente_medicacoes[0].doente_id == sample_doente.id
