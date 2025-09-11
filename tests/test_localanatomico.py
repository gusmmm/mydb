"""Tests for LocalAnatomico API endpoints."""

import pytest
from fastapi.testclient import TestClient

from src.api import app
from src.db import get_session

# HTTP Status Code Constants
HTTP_200_OK = 200
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


def test_create_local_anatomico(client: TestClient):
    """Test creating a new local anatómico."""
    response = client.post(
        '/locais_anatomicos',
        json={
            'local_anatomico': 'Braço direito',
            'regiao_anatomica': 'Membro superior',
        },
    )
    assert response.status_code == HTTP_200_OK
    data = response.json()
    assert data['local_anatomico'] == 'Braço direito'
    assert data['regiao_anatomica'] == 'Membro superior'
    assert 'id' in data


def test_get_all_locais_anatomicos(client: TestClient):
    """Test getting all locais anatómicos."""
    # First create some data
    client.post(
        '/locais_anatomicos',
        json={'local_anatomico': 'Tórax', 'regiao_anatomica': 'Tronco'},
    )
    client.post(
        '/locais_anatomicos',
        json={
            'local_anatomico': 'Perna',
            'regiao_anatomica': 'Membro inferior',
        },
    )

    response = client.get('/locais_anatomicos')
    assert response.status_code == HTTP_200_OK
    data = response.json()
    assert len(data) >= MIN_EXPECTED_RECORDS
    assert all('local_anatomico' in item for item in data)


def test_get_local_anatomico_by_id(client: TestClient):
    """Test getting a specific local anatómico by ID."""
    # Create a local anatómico
    create_response = client.post(
        '/locais_anatomicos',
        json={'local_anatomico': 'Cabeça', 'regiao_anatomica': 'Crânio'},
    )
    local_id = create_response.json()['id']

    # Get it by ID
    response = client.get(f'/locais_anatomicos/{local_id}')
    assert response.status_code == HTTP_200_OK
    data = response.json()
    assert data['local_anatomico'] == 'Cabeça'
    assert data['regiao_anatomica'] == 'Crânio'


def test_get_local_anatomico_not_found(client: TestClient):
    """Test getting a non-existent local anatómico."""
    response = client.get('/locais_anatomicos/999')
    assert response.status_code == HTTP_404_NOT_FOUND
    assert 'not found' in response.json()['detail'].lower()


def test_local_anatomico_required_fields(client: TestClient):
    """Test that local_anatomico field is required."""
    response = client.post(
        '/locais_anatomicos',
        json={'regiao_anatomica': 'Tronco'},  # Missing local_anatomico
    )
    assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY


def test_local_anatomico_optional_regiao(client: TestClient):
    """Test that regiao_anatomica field is optional."""
    response = client.post(
        '/locais_anatomicos',
        json={'local_anatomico': 'Joelho'},  # No regiao_anatomica
    )
    assert response.status_code == HTTP_200_OK
    data = response.json()
    assert data['local_anatomico'] == 'Joelho'
    assert data['regiao_anatomica'] is None
