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
    Internamento,
    InternamentoProcedimento,
    LesaoInalatorialEnum,
    Procedimento,
    SexoEnum,
)

# Test database engine (in memory)
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


def get_test_session():
    """Create test database session."""
    with Session(engine) as session:
        yield session


@pytest.fixture
def session():
    """Create database tables and yield test session."""
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    # Clean up
    try:
        SQLModel.metadata.drop_all(engine)
    except Exception:
        pass  # Ignore cleanup errors


@pytest.fixture
def client(session):
    """Create test client with overridden dependencies."""
    def get_test_session():
        return session

    app.dependency_overrides[get_session] = get_test_session

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def sample_doente(session: Session):
    """Create a sample patient for testing."""
    doente = Doente(
        nome="Test Patient Procedimento",
        numero_processo=123456,
        sexo=SexoEnum.M,
        morada="Test Street"
    )
    session.add(doente)
    session.commit()
    session.refresh(doente)
    return doente


@pytest.fixture
def sample_internamento(session: Session, sample_doente: Doente):
    """Create a sample internamento for testing."""
    internamento = Internamento(
        doente_id=sample_doente.id,
        numero_internamento=789012,
        data_entrada=date(2025, 9, 15),
        ASCQ_total=20,
        lesao_inalatoria=LesaoInalatorialEnum.NAO
    )
    session.add(internamento)
    session.commit()
    session.refresh(internamento)
    return internamento


@pytest.fixture
def sample_procedimento(session: Session):
    """Create a sample procedimento for testing."""
    procedimento = Procedimento(
        nome_procedimento="Test Procedimento",
        tipo_procedimento="Cirúrgico"
    )
    session.add(procedimento)
    session.commit()
    session.refresh(procedimento)
    return procedimento


class TestProcedimento:
    """Test cases for Procedimento model and API."""

    def test_create_procedimento(self, client: TestClient):
        """Test creating a new procedimento."""
        procedimento_data = {
            "nome_procedimento": "Enxerto de pele",
            "tipo_procedimento": "Cirúrgico"
        }

        response = client.post("/procedimentos", json=procedimento_data)

        assert response.status_code == 200
        data = response.json()
        assert data["nome_procedimento"] == "Enxerto de pele"
        assert data["tipo_procedimento"] == "Cirúrgico"
        assert "id" in data

    def test_create_procedimento_minimal(self, client: TestClient):
        """Test creating procedimento with minimal required fields."""
        procedimento_data = {
            "nome_procedimento": "Debridamento"
        }

        response = client.post("/procedimentos", json=procedimento_data)

        assert response.status_code == 200
        data = response.json()
        assert data["nome_procedimento"] == "Debridamento"
        assert data["tipo_procedimento"] is None

    def test_get_all_procedimentos(self, client: TestClient, sample_procedimento: Procedimento):
        """Test getting all procedimentos."""
        response = client.get("/procedimentos")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["nome_procedimento"] == sample_procedimento.nome_procedimento

    def test_get_procedimento_by_id(self, client: TestClient, sample_procedimento: Procedimento):
        """Test getting a specific procedimento by ID."""
        response = client.get(f"/procedimentos/{sample_procedimento.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["nome_procedimento"] == sample_procedimento.nome_procedimento
        assert data["tipo_procedimento"] == sample_procedimento.tipo_procedimento
        assert data["id"] == sample_procedimento.id

    def test_get_nonexistent_procedimento(self, client: TestClient):
        """Test getting a non-existent procedimento."""
        response = client.get("/procedimentos/999")

        assert response.status_code == 404
        assert response.json()["detail"] == "Procedimento not found"

    def test_procedimento_required_fields(self, client: TestClient):
        """Test that nome_procedimento is required."""
        procedimento_data = {
            "tipo_procedimento": "Cirúrgico"
        }

        response = client.post("/procedimentos", json=procedimento_data)

        assert response.status_code == 422


class TestInternamentoProcedimento:
    """Test cases for InternamentoProcedimento model and API."""

    def test_create_internamento_procedimento(
        self,
        client: TestClient,
        sample_internamento: Internamento,
        sample_procedimento: Procedimento
    ):
        """Test creating a new internamento-procedimento relationship."""
        data = {
            "internamento_id": sample_internamento.id,
            "procedimento": sample_procedimento.id
        }

        response = client.post("/internamentos_procedimento", json=data)

        assert response.status_code == 200
        response_data = response.json()
        assert response_data["internamento_id"] == sample_internamento.id
        assert response_data["procedimento"] == sample_procedimento.id
        assert "id" in response_data

    def test_create_internamento_procedimento_minimal(
        self,
        client: TestClient,
        sample_internamento: Internamento
    ):
        """Test creating internamento-procedimento with minimal data."""
        data = {
            "internamento_id": sample_internamento.id
        }

        response = client.post("/internamentos_procedimento", json=data)

        assert response.status_code == 200
        response_data = response.json()
        assert response_data["internamento_id"] == sample_internamento.id
        assert response_data["procedimento"] is None

    def test_create_internamento_procedimento_invalid_internamento(
        self,
        client: TestClient
    ):
        """Test creating relationship with non-existent internamento."""
        data = {
            "internamento_id": 999,
            "procedimento": 1
        }

        response = client.post("/internamentos_procedimento", json=data)

        assert response.status_code == 404
        assert response.json()["detail"] == "Internamento not found"

    def test_create_internamento_procedimento_invalid_procedimento(
        self,
        client: TestClient,
        sample_internamento: Internamento
    ):
        """Test creating relationship with non-existent procedimento."""
        data = {
            "internamento_id": sample_internamento.id,
            "procedimento": 999
        }

        response = client.post("/internamentos_procedimento", json=data)

        assert response.status_code == 404
        assert response.json()["detail"] == "Procedimento not found"

    def test_get_all_internamentos_procedimento(
        self,
        client: TestClient,
        sample_internamento: Internamento,
        sample_procedimento: Procedimento
    ):
        """Test getting all internamento-procedimento relationships."""
        # Create a relationship first
        data = {
            "internamento_id": sample_internamento.id,
            "procedimento": sample_procedimento.id
        }
        client.post("/internamentos_procedimento", json=data)

        response = client.get("/internamentos_procedimento")

        assert response.status_code == 200
        response_data = response.json()
        assert isinstance(response_data, list)
        assert len(response_data) >= 1
        assert response_data[0]["internamento_id"] == sample_internamento.id

    def test_get_internamento_procedimento_by_id(
        self,
        client: TestClient,
        sample_internamento: Internamento,
        sample_procedimento: Procedimento
    ):
        """Test getting a specific internamento-procedimento by ID."""
        # Create a relationship first
        data = {
            "internamento_id": sample_internamento.id,
            "procedimento": sample_procedimento.id
        }
        create_response = client.post("/internamentos_procedimento", json=data)
        created_id = create_response.json()["id"]

        response = client.get(f"/internamentos_procedimento/{created_id}")

        assert response.status_code == 200
        response_data = response.json()
        assert response_data["internamento_id"] == sample_internamento.id
        assert response_data["procedimento"] == sample_procedimento.id
        assert response_data["id"] == created_id

    def test_get_nonexistent_internamento_procedimento(self, client: TestClient):
        """Test getting a non-existent internamento-procedimento."""
        response = client.get("/internamentos_procedimento/999")

        assert response.status_code == 404
        assert response.json()["detail"] == "Internamento procedimento not found"

    def test_get_procedimentos_by_internamento(
        self,
        client: TestClient,
        sample_internamento: Internamento,
        sample_procedimento: Procedimento
    ):
        """Test getting procedimentos for a specific internamento."""
        # Create a relationship first
        data = {
            "internamento_id": sample_internamento.id,
            "procedimento": sample_procedimento.id
        }
        client.post("/internamentos_procedimento", json=data)

        response = client.get(f"/internamentos/{sample_internamento.id}/procedimentos")

        assert response.status_code == 200
        response_data = response.json()
        assert isinstance(response_data, list)
        assert len(response_data) >= 1
        assert response_data[0]["internamento_id"] == sample_internamento.id
        assert response_data[0]["procedimento"] == sample_procedimento.id

    def test_get_procedimentos_by_nonexistent_internamento(self, client: TestClient):
        """Test getting procedimentos for non-existent internamento."""
        response = client.get("/internamentos/999/procedimentos")

        assert response.status_code == 404
        assert response.json()["detail"] == "Internamento not found"

    def test_internamento_procedimento_required_fields(self, client: TestClient):
        """Test that internamento_id is required."""
        data = {
            "procedimento": 1
        }

        response = client.post("/internamentos_procedimento", json=data)

        assert response.status_code == 422


class TestDatabaseRelationships:
    """Test database relationships for procedimento tables."""

    def test_procedimento_internamento_relationship(
        self,
        session: Session,
        sample_internamento: Internamento,
        sample_procedimento: Procedimento
    ):
        """Test the relationship between procedimento and internamento."""
        # Create the relationship
        internamento_procedimento = InternamentoProcedimento(
            internamento_id=sample_internamento.id,
            procedimento=sample_procedimento.id
        )
        session.add(internamento_procedimento)
        session.commit()
        session.refresh(internamento_procedimento)

        # Test forward relationship
        assert internamento_procedimento.internamento is not None
        assert internamento_procedimento.internamento.id == sample_internamento.id

        # Test procedure relationship
        assert internamento_procedimento.procedimento_rel is not None
        assert internamento_procedimento.procedimento_rel.id == sample_procedimento.id

    def test_internamento_has_procedimentos_relationship(
        self,
        session: Session,
        sample_internamento: Internamento,
        sample_procedimento: Procedimento
    ):
        """Test that internamento can access its procedimentos."""
        # Create the relationship
        internamento_procedimento = InternamentoProcedimento(
            internamento_id=sample_internamento.id,
            procedimento=sample_procedimento.id
        )
        session.add(internamento_procedimento)
        session.commit()

        # Refresh to load relationships
        session.refresh(sample_internamento)

        # Test that internamento has procedimentos
        assert len(sample_internamento.internamento_procedimentos) >= 1
        assert sample_internamento.internamento_procedimentos[0].procedimento == sample_procedimento.id

    def test_procedimento_has_internamentos_relationship(
        self,
        session: Session,
        sample_internamento: Internamento,
        sample_procedimento: Procedimento
    ):
        """Test that procedimento can access its internamentos."""
        # Create the relationship
        internamento_procedimento = InternamentoProcedimento(
            internamento_id=sample_internamento.id,
            procedimento=sample_procedimento.id
        )
        session.add(internamento_procedimento)
        session.commit()

        # Refresh to load relationships
        session.refresh(sample_procedimento)

        # Test that procedimento has internamentos
        assert len(sample_procedimento.internamento_procedimentos) >= 1
        assert sample_procedimento.internamento_procedimentos[0].internamento_id == sample_internamento.id
