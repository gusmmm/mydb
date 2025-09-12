"""Tests for antibiotic-related functionality."""

import random
from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from src.api import app
from src.db import engine
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


@pytest.fixture(name='client')
def client_fixture():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture(name='session')
def session_fixture():
    """Create a test database session."""
    with Session(engine) as session:
        yield session


class TestAntibiotico:
    """Test class for Antibiotico functionality."""

    @staticmethod
    def test_create_antibiotico(client: TestClient):
        """Test creating a new antibiotico."""
        response = client.post(
            '/antibioticos',
            json={
                'nome_antibiotico': 'Penicilina G',
                'classe_antibiotico': 'Beta-lactâmico',
                'codigo': 'PEN001',
            },
        )
        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert data['nome_antibiotico'] == 'Penicilina G'
        assert data['classe_antibiotico'] == 'Beta-lactâmico'
        assert data['codigo'] == 'PEN001'
        assert 'id' in data

    @staticmethod
    def test_get_all_antibioticos(client: TestClient):
        """Test retrieving all antibioticos."""
        response = client.get('/antibioticos')
        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    @staticmethod
    def test_get_antibiotico_by_id(client: TestClient):
        """Test retrieving antibiotico by ID."""
        create_response = client.post(
            '/antibioticos',
            json={'nome_antibiotico': 'Ciprofloxacina'},
        )
        antibiotico_id = create_response.json()['id']

        response = client.get(f'/antibioticos/{antibiotico_id}')
        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert data['nome_antibiotico'] == 'Ciprofloxacina'

    @staticmethod
    def test_get_nonexistent_antibiotico(client: TestClient):
        """Test retrieving non-existent antibiotico."""
        response = client.get(f'/antibioticos/{NON_EXISTENT_ID}')
        assert response.status_code == HTTP_404_NOT_FOUND


class TestIndicacaoAntibiotico:
    """Test class for IndicacaoAntibiotico functionality."""

    @staticmethod
    def test_create_indicacao_antibiotico(client: TestClient):
        """Test creating a new indicacao antibiotico."""
        response = client.post(
            '/indicacoes_antibiotico',
            json={'indicacao': 'Profilaxia cirúrgica'},
        )
        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert data['indicacao'] == 'Profilaxia cirúrgica'
        assert 'id' in data

    @staticmethod
    def test_get_all_indicacoes_antibiotico(client: TestClient):
        """Test retrieving all indicacoes antibiotico."""
        response = client.get('/indicacoes_antibiotico')
        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    @staticmethod
    def test_get_indicacao_antibiotico_by_id(client: TestClient):
        """Test retrieving indicacao antibiotico by ID."""
        create_response = client.post(
            '/indicacoes_antibiotico',
            json={'indicacao': 'Profilaxia de endocardite'},
        )
        indicacao_id = create_response.json()['id']

        response = client.get(f'/indicacoes_antibiotico/{indicacao_id}')
        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert data['indicacao'] == 'Profilaxia de endocardite'

    @staticmethod
    def test_get_nonexistent_indicacao_antibiotico(client: TestClient):
        """Test retrieving non-existent indicacao antibiotico."""
        response = client.get(f'/indicacoes_antibiotico/{NON_EXISTENT_ID}')
        assert response.status_code == HTTP_404_NOT_FOUND


class TestInternamentoAntibiotico:
    """Test class for InternamentoAntibiotico functionality."""

    def test_create_internamento_antibiotico_with_relationships(  # noqa: PLR6301
        self, client: TestClient, session: Session
    ):
        """Test creating internamento antibiotico with relationships."""
        # Create required data
        # Generate a random unique patient number to avoid conflicts
        random_num = random.randint(10000000, 99999999)
        doente = Doente(
            nome='Test Patient for Antibiotico',
            numero_processo=random_num,
            sexo=SexoEnum.M,
            morada='Test Address',
        )
        session.add(doente)
        session.commit()
        session.refresh(doente)

        internamento = Internamento(
            numero_internamento=random_num + 1,  # Use different number
            doente_id=doente.id,
            data_entrada=date(2025, 9, 12),
            ASCQ_total=20,
            lesao_inalatoria=LesaoInalatorialEnum.NAO,
        )
        session.add(internamento)
        session.commit()
        session.refresh(internamento)

        # Create antibiotico
        antibiotico_response = client.post(
            '/antibioticos',
            json={'nome_antibiotico': 'Meropenem'},
        )
        antibiotico_id = antibiotico_response.json()['id']

        # Create indicacao
        indicacao_response = client.post(
            '/indicacoes_antibiotico',
            json={'indicacao': 'Sepse grave'},
        )
        indicacao_id = indicacao_response.json()['id']

        # Create internamento antibiotico
        response = client.post(
            '/internamentos_antibiotico',
            json={
                'internamento_id': internamento.id,
                'antibiotico': antibiotico_id,
                'indicacao': indicacao_id,
            },
        )
        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert data['internamento_id'] == internamento.id
        assert data['antibiotico'] == antibiotico_id
        assert data['indicacao'] == indicacao_id
        assert 'id' in data

    def test_create_internamento_antibiotico_minimal(  # noqa: PLR6301
        self, client: TestClient, session: Session
    ):
        """Test creating internamento antibiotico with minimal data."""
        # Create required data
        # Generate a random unique patient number to avoid conflicts
        random_num = random.randint(10000000, 99999999)
        doente = Doente(
            nome='Minimal Test Patient',
            numero_processo=random_num,
            sexo=SexoEnum.F,
            morada='Minimal Address',
        )
        session.add(doente)
        session.commit()
        session.refresh(doente)

        internamento = Internamento(
            numero_internamento=random_num + 1,  # Use different number
            doente_id=doente.id,
            data_entrada=date(2025, 9, 12),
            ASCQ_total=15,
            lesao_inalatoria=LesaoInalatorialEnum.SIM,
        )
        session.add(internamento)
        session.commit()
        session.refresh(internamento)

        # Create internamento antibiotico with just internamento_id
        response = client.post(
            '/internamentos_antibiotico',
            json={'internamento_id': internamento.id},
        )
        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert data['internamento_id'] == internamento.id
        assert data['antibiotico'] is None
        assert data['indicacao'] is None
        assert 'id' in data

    @staticmethod
    def test_create_internamento_antibiotico_invalid_internamento(
        client: TestClient
    ):
        """Test creating internamento antibiotico with invalid internamento."""
        response = client.post(
            '/internamentos_antibiotico',
            json={'internamento_id': NON_EXISTENT_LARGE_ID},
        )
        assert response.status_code == HTTP_404_NOT_FOUND

    @staticmethod
    def test_get_all_internamentos_antibiotico(client: TestClient):
        """Test retrieving all internamentos antibiotico."""
        response = client.get('/internamentos_antibiotico')
        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    @staticmethod
    def test_get_nonexistent_internamento_antibiotico(
        client: TestClient
    ):
        """Test retrieving non-existent internamento antibiotico."""
        response = client.get(f'/internamentos_antibiotico/{NON_EXISTENT_ID}')
        assert response.status_code == HTTP_404_NOT_FOUND

    @staticmethod
    def test_get_antibioticos_by_nonexistent_internamento(
        client: TestClient
    ):
        """Test retrieving antibioticos for non-existent internamento."""
        response = client.get(
            f'/internamentos/{NON_EXISTENT_LARGE_ID}/antibioticos'
        )
        assert response.status_code == HTTP_404_NOT_FOUND

    @staticmethod
    def test_internamento_antibiotico_validation_error(
        client: TestClient
    ):
        """Test validation error for missing required fields."""
        response = client.post(
            '/internamentos_antibiotico',
            json={'antibiotico': 1},
        )
        assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY
