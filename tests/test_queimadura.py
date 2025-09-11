"""Tests for Queimadura API endpoints with proper foreign key relationships."""

import random
from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from src.api import app
from src.db import get_session
from src.models.models import (
    Doente,
    Internamento,
    LesaoInalatorialEnum,
    LocalAnatomico,
    SexoEnum,
)

# HTTP Status Code Constants
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_404_NOT_FOUND = 404
HTTP_422_UNPROCESSABLE_ENTITY = 422
MIN_EXPECTED_RECORDS = 2


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def session():
    """Create test database session."""
    return next(get_session())


@pytest.fixture
def setup_test_data(session: Session):
    """Set up test data for queimadura tests."""
    # Generate unique numbers to avoid conflicts
    unique_processo = random.randint(100000, 999999)
    unique_internamento = random.randint(100000, 999999)

    # Create a patient
    doente = Doente(
        nome='Test Patient',
        numero_processo=unique_processo,
        sexo=SexoEnum.M,
        morada='Test Street',
    )
    session.add(doente)
    session.commit()
    session.refresh(doente)

    # Create an internamento
    internamento = Internamento(
        numero_internamento=unique_internamento,
        doente_id=doente.id,
        data_entrada=date(2025, 9, 11),
        ASCQ_total=20,
        lesao_inalatoria=LesaoInalatorialEnum.SIM,
    )
    session.add(internamento)
    session.commit()
    session.refresh(internamento)

    # Create local anatómicos
    local1 = LocalAnatomico(
        local_anatomico='Braço', regiao_anatomica='Membro superior'
    )
    local2 = LocalAnatomico(
        local_anatomico='Perna', regiao_anatomica='Membro inferior'
    )
    session.add(local1)
    session.add(local2)
    session.commit()
    session.refresh(local1)
    session.refresh(local2)

    return {
        'doente': doente,
        'internamento': internamento,
        'local1': local1,
        'local2': local2,
    }


def test_create_queimadura(client: TestClient, setup_test_data):
    """Test creating a new queimadura."""
    data = setup_test_data

    response = client.post(
        '/queimaduras',
        json={
            'internamento_id': data['internamento'].id,
            'local_anatomico': data['local1'].id,
            'grau_maximo': 'SEGUNDO',
            'notas': 'Test queimadura',
        },
    )
    assert response.status_code == HTTP_201_CREATED
    result = response.json()
    assert result['internamento_id'] == data['internamento'].id
    assert result['local_anatomico'] == data['local1'].id
    assert result['grau_maximo'] == 'SEGUNDO'
    assert result['notas'] == 'Test queimadura'
    assert 'id' in result


def test_create_queimadura_invalid_internamento(
    client: TestClient, setup_test_data
):
    """Test creating queimadura with invalid internamento."""
    data = setup_test_data

    response = client.post(
        '/queimaduras',
        json={
            'internamento_id': 999,  # Invalid internamento
            'local_anatomico': data['local1'].id,
            'grau_maximo': 'SEGUNDO',
            'notas': 'Test queimadura',
        },
    )
    assert response.status_code == HTTP_404_NOT_FOUND
    assert 'Internamento not found' in response.json()['detail']


def test_get_all_queimaduras(client: TestClient, setup_test_data):
    """Test getting all queimaduras."""
    data = setup_test_data

    # Create some queimaduras
    client.post(
        '/queimaduras',
        json={
            'internamento_id': data['internamento'].id,
            'local_anatomico': data['local1'].id,
            'grau_maximo': 'PRIMEIRO',
            'notas': 'Queimadura 1',
        },
    )
    client.post(
        '/queimaduras',
        json={
            'internamento_id': data['internamento'].id,
            'local_anatomico': data['local2'].id,
            'grau_maximo': 'TERCEIRO',
            'notas': 'Queimadura 2',
        },
    )

    response = client.get('/queimaduras')
    assert response.status_code == HTTP_200_OK
    result = response.json()
    assert len(result) >= MIN_EXPECTED_RECORDS
    assert all('internamento_id' in item for item in result)


def test_get_queimadura_by_id(client: TestClient, setup_test_data):
    """Test getting a specific queimadura by ID."""
    data = setup_test_data

    # Create a queimadura
    create_response = client.post(
        '/queimaduras',
        json={
            'internamento_id': data['internamento'].id,
            'local_anatomico': data['local1'].id,
            'grau_maximo': 'SEGUNDO',
            'notas': 'Test queimadura ID',
        },
    )
    queimadura_id = create_response.json()['id']

    # Get it by ID
    response = client.get(f'/queimaduras/{queimadura_id}')
    assert response.status_code == HTTP_200_OK
    result = response.json()
    assert result['notas'] == 'Test queimadura ID'


def test_queimadura_grau_maximo_enum(client: TestClient, setup_test_data):
    """Test all valid grau maximo enum values."""
    data = setup_test_data

    for grau in ['PRIMEIRO', 'SEGUNDO', 'TERCEIRO', 'QUARTO']:
        response = client.post(
            '/queimaduras',
            json={
                'internamento_id': data['internamento'].id,
                'local_anatomico': data['local1'].id,
                'grau_maximo': grau,
                'notas': f'Queimadura {grau}',
            },
        )
        assert response.status_code == HTTP_201_CREATED
        assert response.json()['grau_maximo'] == grau


def test_queimadura_optional_fields(client: TestClient, setup_test_data):
    """Test queimadura with optional fields."""
    data = setup_test_data

    # Test with minimal required fields
    response = client.post(
        '/queimaduras', json={'internamento_id': data['internamento'].id}
    )
    assert response.status_code == HTTP_201_CREATED
    result = response.json()
    assert result['local_anatomico'] is None
    assert result['grau_maximo'] is None
    assert result['notas'] is None


def test_queimadura_required_internamento_id(client: TestClient):
    """Test that internamento_id is required."""
    response = client.post(
        '/queimaduras',
        json={'local_anatomico': 1, 'grau_maximo': 'SEGUNDO', 'notas': 'Test'},
    )
    assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY


def test_get_queimaduras_for_internamento(client: TestClient, setup_test_data):
    """Test getting queimaduras for a specific internamento."""
    data = setup_test_data

    # Create queimaduras for this internamento
    client.post(
        '/queimaduras',
        json={
            'internamento_id': data['internamento'].id,
            'local_anatomico': data['local1'].id,
            'grau_maximo': 'PRIMEIRO',
            'notas': 'Queimadura 1',
        },
    )
    client.post(
        '/queimaduras',
        json={
            'internamento_id': data['internamento'].id,
            'local_anatomico': data['local2'].id,
            'grau_maximo': 'SEGUNDO',
            'notas': 'Queimadura 2',
        },
    )

    internamento_id = data['internamento'].id
    response = client.get(f'/internamentos/{internamento_id}/queimaduras')
    assert response.status_code == HTTP_200_OK
    result = response.json()
    assert len(result) >= MIN_EXPECTED_RECORDS
    assert all(
        item['internamento_id'] == data['internamento'].id for item in result
    )
