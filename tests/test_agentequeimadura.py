"""
Tests for AgenteQueimadura functionality.
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

# Start tracemalloc to track memory allocations
tracemalloc.start()


@pytest.fixture(name='engine')
def engine_fixture():
    """Create a test database engine."""
    engine = create_engine(
        'sqlite://',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    yield engine
    # Ensure engine is properly disposed
    engine.dispose()


@pytest.fixture(name='session')
def session_fixture(engine):
    """Create a test database session."""
    with Session(engine) as session:
        yield session
        # Session is automatically closed by context manager


@pytest.fixture(name='client')
def client_fixture(session: Session):
    """Create a test client with the test database session."""

    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    with TestClient(app) as client:
        yield client

    # Clean up
    app.dependency_overrides.clear()


def test_create_agente_queimadura(client: TestClient):
    """Test creating a new agente queimadura."""
    response = client.post(
        '/agentes_queimadura',
        json={'agente_queimadura': 'Test Agente', 'nota': 'Test nota'},
    )
    assert response.status_code == HTTP_201_CREATED
    data = response.json()
    assert data['agente_queimadura'] == 'Test Agente'
    assert data['nota'] == 'Test nota'
    assert 'id' in data


def test_get_all_agentes_queimadura(client: TestClient):
    """Test getting all agentes queimadura."""
    # First create some agentes
    client.post(
        '/agentes_queimadura',
        json={'agente_queimadura': 'Agente 1', 'nota': 'Nota 1'},
    )
    client.post(
        '/agentes_queimadura',
        json={'agente_queimadura': 'Agente 2', 'nota': 'Nota 2'},
    )

    response = client.get('/agentes_queimadura')
    assert response.status_code == HTTP_200_OK
    data = response.json()
    expected_count = 2
    assert len(data) == expected_count
    assert data[0]['agente_queimadura'] == 'Agente 1'
    assert data[1]['agente_queimadura'] == 'Agente 2'


def test_get_agente_queimadura_by_id(client: TestClient):
    """Test getting a specific agente queimadura by ID."""
    # Create an agente
    create_response = client.post(
        '/agentes_queimadura',
        json={'agente_queimadura': 'Specific Agente', 'nota': 'Specific nota'},
    )
    agente_id = create_response.json()['id']

    response = client.get(f'/agentes_queimadura/{agente_id}')
    assert response.status_code == HTTP_200_OK
    data = response.json()
    assert data['agente_queimadura'] == 'Specific Agente'
    assert data['nota'] == 'Specific nota'
    assert data['id'] == agente_id


def test_get_agente_queimadura_not_found(client: TestClient):
    """Test getting a non-existent agente queimadura."""
    response = client.get('/agentes_queimadura/999')
    assert response.status_code == HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Agente de queimadura not found'}


def test_internamento_with_agente_queimadura_foreign_key(client: TestClient):
    """Test creating an internamento with agente queimadura foreign key."""
    # First create a patient
    patient_response = client.post(
        '/doentes/',
        json={
            'nome': 'Test Patient',
            'numero_processo': 12345,
            'sexo': 'M',
            'morada': 'Test Address',
            'data_nascimento': '1990-01-01',
        },
    )
    patient_id = patient_response.json()['id']

    # Create an agente queimadura
    agente_response = client.post(
        '/agentes_queimadura',
        json={'agente_queimadura': 'Test Agente FK', 'nota': 'Test FK nota'},
    )
    agente_id = agente_response.json()['id']

    # Create internamento with foreign key
    internamento_response = client.post(
        '/internamentos',
        json={
            'numero_internamento': 98765,
            'doente_id': patient_id,
            'data_entrada': '2025-09-09',
            'ASCQ_total': 25,
            'lesao_inalatoria': 'SIM',
            'agente_queimadura': agente_id,
        },
    )
    assert internamento_response.status_code == HTTP_201_CREATED
    data = internamento_response.json()
    assert data['agente_queimadura'] == agente_id
    assert data['doente_id'] == patient_id


def test_agente_queimadura_validation(client: TestClient):
    """Test validation for agente queimadura creation."""
    # Test missing required fields
    response = client.post(
        '/agentes_queimadura', json={'agente_queimadura': 'Test without nota'}
    )
    assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY

    response = client.post(
        '/agentes_queimadura', json={'nota': 'Test without agente'}
    )
    assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY


def test_agente_queimadura_empty_fields(client: TestClient):
    """Test agente queimadura with empty fields."""
    response = client.post(
        '/agentes_queimadura', json={'agente_queimadura': '', 'nota': ''}
    )
    # Empty strings are allowed
    assert response.status_code == HTTP_201_CREATED
    data = response.json()
    assert not data['agente_queimadura']
    assert not data['nota']
