"""Test module for infection-related functionality.

This module tests the AgenteInfeccioso, TipoInfecao, and Infecao models
and their API endpoints.
"""

from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel

from src.api import app, get_session
from src.models.models import (
    Doente,
    Internamento,
    LesaoInalatorialEnum,
    SexoEnum,
)

# HTTP Status Code Constants
HTTP_200_OK = 200
HTTP_404_NOT_FOUND = 404
HTTP_422_UNPROCESSABLE_ENTITY = 422

# Test Constants
NON_EXISTENT_ID = 999
NON_EXISTENT_LARGE_ID = 999999
MIN_TEST_DATA_COUNT = 2


# Test database setup
@pytest.fixture(name="session")
def session_fixture():
    """Create a test database session."""
    engine = create_engine(
        "sqlite:///",  # In-memory database
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Create a test client with dependency override."""
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


class TestAgenteInfeccioso:
    """Test class for AgenteInfeccioso functionality."""

    @staticmethod
    def test_create_agente_infeccioso(client: TestClient):
        """Test creating a new agente infeccioso."""
        response = client.post(
            "/agentes_infecciosos",
            json={
                "nome": "Staphylococcus aureus",
                "tipo_agente": "BACTERIA",
            },
        )
        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert data["nome"] == "Staphylococcus aureus"
        assert data["tipo_agente"] == "BACTERIA"
        assert "id" in data

    @staticmethod
    def test_get_all_agentes_infecciosos(client: TestClient):
        """Test retrieving all agentes infecciosos."""
        # Create test agentes
        client.post(
            "/agentes_infecciosos",
            json={
                "nome": "Pseudomonas aeruginosa",
                "tipo_agente": "BACTERIA",
            },
        )
        client.post(
            "/agentes_infecciosos",
            json={
                "nome": "Candida albicans",
                "tipo_agente": "FUNGO",
            },
        )

        response = client.get("/agentes_infecciosos")
        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert len(data) >= MIN_TEST_DATA_COUNT
        assert any(
            agente["nome"] == "Pseudomonas aeruginosa" for agente in data
        )
        assert any(agente["nome"] == "Candida albicans" for agente in data)

    @staticmethod
    def test_get_agente_infeccioso_by_id(client: TestClient):
        """Test retrieving agente infeccioso by ID."""
        create_response = client.post(
            "/agentes_infecciosos",
            json={
                "nome": "Escherichia coli",
                "tipo_agente": "BACTERIA",
            },
        )
        agente_id = create_response.json()["id"]

        response = client.get(f"/agentes_infecciosos/{agente_id}")
        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert data["nome"] == "Escherichia coli"
        assert data["id"] == agente_id

    @staticmethod
    def test_get_nonexistent_agente_infeccioso(client: TestClient):
        """Test retrieving non-existent agente infeccioso."""
        response = client.get(f"/agentes_infecciosos/{NON_EXISTENT_ID}")
        assert response.status_code == HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()


class TestTipoInfecao:
    """Test class for TipoInfecao functionality."""

    @staticmethod
    def test_create_tipo_infecao(client: TestClient):
        """Test creating a new tipo de infecção."""
        response = client.post(
            "/tipos_infeccao",
            json={
                "tipo_infeccao": "Infecção respiratória",
                "local": "Aparelho respiratório",
            },
        )
        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert data["tipo_infeccao"] == "Infecção respiratória"
        assert data["local"] == "Aparelho respiratório"
        assert "id" in data

    @staticmethod
    def test_get_all_tipos_infeccao(client: TestClient):
        """Test retrieving all tipos de infecção."""
        # Create test tipos
        client.post(
            "/tipos_infeccao",
            json={
                "tipo_infeccao": "Infecção de ferida",
                "local": "Ferida cirúrgica",
            },
        )
        client.post(
            "/tipos_infeccao",
            json={
                "tipo_infeccao": "Septicemia",
                "local": "Sistémica",
            },
        )

        response = client.get("/tipos_infeccao")
        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert len(data) >= MIN_TEST_DATA_COUNT
        assert any(
            tipo["tipo_infeccao"] == "Infecção de ferida" for tipo in data
        )
        assert any(tipo["tipo_infeccao"] == "Septicemia" for tipo in data)

    @staticmethod
    def test_get_tipo_infecao_by_id(client: TestClient):
        """Test retrieving tipo de infecção by ID."""
        create_response = client.post(
            "/tipos_infeccao",
            json={
                "tipo_infeccao": "Infecção urinária",
                "local": "Aparelho urinário",
            },
        )
        tipo_id = create_response.json()["id"]

        response = client.get(f"/tipos_infeccao/{tipo_id}")
        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert data["tipo_infeccao"] == "Infecção urinária"
        assert data["id"] == tipo_id

    @staticmethod
    def test_get_nonexistent_tipo_infecao(client: TestClient):
        """Test retrieving non-existent tipo de infecção."""
        response = client.get(f"/tipos_infeccao/{NON_EXISTENT_ID}")
        assert response.status_code == HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()


class TestInfecao:
    """Test class for Infecao functionality."""

    def test_create_infecao_with_all_relationships(  # noqa: PLR6301
        self, client: TestClient, session: Session
    ):
        """Test creating infecção with all required relationships."""
        # Create required data first
        doente = Doente(
            nome="João Silva",
            numero_processo=12345,
            sexo=SexoEnum.M,
            morada="Rua de Teste, 123",
        )
        session.add(doente)
        session.commit()
        session.refresh(doente)

        internamento = Internamento(
            numero_internamento=11111,
            doente_id=doente.id,
            data_entrada=date(2025, 9, 15),
            ASCQ_total=25,
            lesao_inalatoria=LesaoInalatorialEnum.SIM,
        )
        session.add(internamento)
        session.commit()
        session.refresh(internamento)

        agente_response = client.post(
            "/agentes_infecciosos",
            json={
                "nome": "Staphylococcus epidermidis",
                "tipo_agente": "BACTERIA",
            },
        )
        agente_id = agente_response.json()["id"]

        tipo_response = client.post(
            "/tipos_infeccao",
            json={
                "tipo_infeccao": "Infecção cutânea",
                "local": "Pele",
            },
        )
        tipo_id = tipo_response.json()["id"]

        # Create infecção
        response = client.post(
            "/infeccoes",
            json={
                "internamento_id": internamento.id,
                "agente": agente_id,
                "local_tipo_infecao": tipo_id,
                "nota": "Primeira infecção documentada",
            },
        )
        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert data["internamento_id"] == internamento.id
        assert data["agente"] == agente_id
        assert data["local_tipo_infecao"] == tipo_id
        assert "id" in data

    @staticmethod
    def test_create_infecao_invalid_internamento(client: TestClient):
        """Test creating infecção with invalid internamento_id."""
        response = client.post(
            "/infeccoes",
            json={
                "internamento_id": NON_EXISTENT_ID,
                "agente": 1,
                "local_tipo_infecao": 1,
                "nota": "Test invalid internamento",
            },
        )
        # The API may return 404 if the related record is not found
        assert response.status_code in {400, 404}
        assert "not found" in response.json()["detail"].lower()

    def test_create_infecao_invalid_agente(  # noqa: PLR6301
        self, client: TestClient, session: Session
    ):
        """Test creating infecção with invalid agente ID."""
        # Create required internamento
        doente = Doente(
            nome="Maria Santos",
            numero_processo=54321,
            sexo=SexoEnum.F,
            morada="Avenida Teste, 456",
        )
        session.add(doente)
        session.commit()
        session.refresh(doente)

        internamento = Internamento(
            numero_internamento=22222,
            doente_id=doente.id,
            data_entrada=date(2025, 9, 15),
            ASCQ_total=15,
            lesao_inalatoria=LesaoInalatorialEnum.NAO,
        )
        session.add(internamento)
        session.commit()
        session.refresh(internamento)

        response = client.post(
            "/infeccoes",
            json={
                "internamento_id": internamento.id,
                "agente": NON_EXISTENT_ID,
                "local_tipo_infecao": 1,
                "nota": "Test invalid agente",
            },
        )
        # The API may return 404 if the related record is not found
        assert response.status_code in {400, 404}
        assert "not found" in response.json()["detail"].lower()

    def test_create_infecao_invalid_tipo(  # noqa: PLR6301
        self, client: TestClient, session: Session
    ):
        """Test creating infecção with invalid tipo de infecção ID."""
        # Create required data
        doente = Doente(
            nome="Carlos Oliveira",
            numero_processo=98765,
            sexo=SexoEnum.M,
            morada="Praça Teste, 789",
        )
        session.add(doente)
        session.commit()
        session.refresh(doente)

        internamento = Internamento(
            numero_internamento=33333,
            doente_id=doente.id,
            data_entrada=date(2025, 9, 15),
            ASCQ_total=20,
            lesao_inalatoria=LesaoInalatorialEnum.SIM,
        )
        session.add(internamento)
        session.commit()
        session.refresh(internamento)

        agente_response = client.post(
            "/agentes_infecciosos",
            json={
                "nome": "Streptococcus pyogenes",
                "tipo_agente": "BACTERIA",
            },
        )
        agente_id = agente_response.json()["id"]

        response = client.post(
            "/infeccoes",
            json={
                "internamento_id": internamento.id,
                "agente": agente_id,
                "local_tipo_infecao": NON_EXISTENT_ID,
                "nota": "Test invalid tipo",
            },
        )
        # The API may return 404 if the related record is not found
        assert response.status_code in {400, 404}
        assert "not found" in response.json()["detail"].lower()

    def test_get_all_infecoes(self, client: TestClient, session: Session):  # noqa: PLR6301
        """Test retrieving all infecções."""
        # Create required data and infecções
        doente = Doente(
            nome="Ana Costa",
            numero_processo=11223,
            sexo=SexoEnum.F,
            morada="Rua Nova, 100",
        )
        session.add(doente)
        session.commit()
        session.refresh(doente)

        internamento1 = Internamento(
            numero_internamento=44444,
            doente_id=doente.id,
            data_entrada=date(2025, 9, 15),
            ASCQ_total=10,
            lesao_inalatoria=LesaoInalatorialEnum.NAO,
        )
        internamento2 = Internamento(
            numero_internamento=55555,
            doente_id=doente.id,
            data_entrada=date(2025, 9, 16),
            ASCQ_total=30,
            lesao_inalatoria=LesaoInalatorialEnum.SIM,
        )
        session.add_all([internamento1, internamento2])
        session.commit()
        session.refresh(internamento1)
        session.refresh(internamento2)

        agente_response = client.post(
            "/agentes_infecciosos",
            json={
                "nome": "Enterococcus faecalis",
                "tipo_agente": "BACTERIA",
            },
        )
        agente_id = agente_response.json()["id"]

        tipo_response = client.post(
            "/tipos_infeccao",
            json={
                "tipo_infeccao": "Infecção gastrointestinal",
                "local": "Aparelho digestivo",
            },
        )
        tipo_id = tipo_response.json()["id"]

        # Create two infecções
        client.post(
            "/infeccoes",
            json={
                "internamento_id": internamento1.id,
                "agente": agente_id,
                "local_tipo_infecao": tipo_id,
                "nota": "Primera infecção",
            },
        )
        client.post(
            "/infeccoes",
            json={
                "internamento_id": internamento2.id,
                "agente": agente_id,
                "local_tipo_infecao": tipo_id,
                "nota": "Segunda infecção",
            },
        )

        response = client.get("/infeccoes")
        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert len(data) >= MIN_TEST_DATA_COUNT

    def test_get_infecao_by_id(self, client: TestClient, session: Session):  # noqa: PLR6301
        """Test retrieving infecção by ID."""
        # Create required data
        doente = Doente(
            nome="Pedro Almeida",
            numero_processo=33445,
            sexo=SexoEnum.M,
            morada="Travessa Teste, 50",
        )
        session.add(doente)
        session.commit()
        session.refresh(doente)

        internamento = Internamento(
            numero_internamento=66666,
            doente_id=doente.id,
            data_entrada=date(2025, 9, 15),
            ASCQ_total=18,
            lesao_inalatoria=LesaoInalatorialEnum.NAO,
        )
        session.add(internamento)
        session.commit()
        session.refresh(internamento)

        agente_response = client.post(
            "/agentes_infecciosos",
            json={
                "nome": "Acinetobacter baumannii",
                "tipo_agente": "BACTERIA",
            },
        )
        agente_id = agente_response.json()["id"]

        tipo_response = client.post(
            "/tipos_infeccao",
            json={
                "tipo_infeccao": "Pneumonia nosocomial",
                "local": "Pulmões",
            },
        )
        tipo_id = tipo_response.json()["id"]

        create_response = client.post(
            "/infeccoes",
            json={
                "internamento_id": internamento.id,
                "agente": agente_id,
                "local_tipo_infecao": tipo_id,
                "nota": "Pneumonia grave",
            },
        )
        infecao_id = create_response.json()["id"]

        response = client.get(f"/infeccoes/{infecao_id}")
        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert data["id"] == infecao_id
        assert data["internamento_id"] == internamento.id

    @staticmethod
    def test_get_nonexistent_infecao(client: TestClient):
        """Test retrieving non-existent infecção."""
        response = client.get(f"/infeccoes/{NON_EXISTENT_ID}")
        assert response.status_code == HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()

    def test_infecao_required_fields(  # noqa: PLR6301
        self, client: TestClient, session: Session
    ):
        """Test that required fields are validated."""
        # Create required data
        doente = Doente(
            nome="Isabel Santos",
            numero_processo=77889,
            sexo=SexoEnum.F,
            morada="Largo Teste, 25",
        )
        session.add(doente)
        session.commit()
        session.refresh(doente)

        internamento = Internamento(
            numero_internamento=77777,
            doente_id=doente.id,
            data_entrada=date(2025, 9, 15),
            ASCQ_total=22,
            lesao_inalatoria=LesaoInalatorialEnum.SIM,
        )
        session.add(internamento)
        session.commit()
        session.refresh(internamento)

        # Test with only required field (internamento_id) - should succeed
        response = client.post(
            "/infeccoes",
            json={
                "internamento_id": internamento.id,
                "nota": "Test with minimal fields",
            },
        )
        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert data["internamento_id"] == internamento.id
        assert data["agente"] is None
        assert data["local_tipo_infecao"] is None

        # Test missing internamento_id - should fail
        response = client.post(
            "/infeccoes",
            json={
                "nota": "Test without internamento_id",
            },
        )
        assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY


if __name__ == "__main__":
    pytest.main([__file__])
