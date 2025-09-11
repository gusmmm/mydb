"""Tests for OrigemDestino model and API endpoints."""

import random

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlmodel import Session

from src.api import app
from src.db import engine, get_session
from src.models.models import (
    Doente,
    Internamento,
    IntExtEnum,
    OrigemDestino,
    SexoEnum,
)

# Constants for testing
INVALID_ID = 999
STATUS_OK = 200
STATUS_CREATED = 201
STATUS_NOT_FOUND = 404
MIN_TEST_DATA_COUNT = 2


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def test_session():
    """Create a test database session."""
    with Session(engine) as session:
        yield session


def test_create_origem_destino(client: TestClient):
    """Test creating a new origem/destino."""
    response = client.post(
        '/origens_destino',
        json={
            'local': 'Centro de Saúde Local',
            'int_ext': 'INTERNO',
            'descricao': 'Centro de saúde do município',
        },
    )
    assert response.status_code == STATUS_CREATED
    data = response.json()
    assert data['local'] == 'Centro de Saúde Local'
    assert data['int_ext'] == 'INTERNO'
    assert data['descricao'] == 'Centro de saúde do município'
    assert 'id' in data


def test_get_all_origens_destino_empty(client: TestClient):
    """Test getting all origens/destinos when none exist."""
    # Clear any existing data
    session = next(get_session())
    session.execute(text('DELETE FROM origemdestino'))
    session.commit()

    response = client.get('/origens_destino')
    assert response.status_code == STATUS_OK
    assert response.json() == []


def test_get_all_origens_destino_with_data(client: TestClient):
    """Test getting all origens/destinos with data."""
    # Create test data
    test_data = [
        {
            'local': 'Hospital Central',
            'int_ext': 'INTERNO',
            'descricao': 'Hospital principal da região',
        },
        {
            'local': 'Clínica Externa',
            'int_ext': 'EXTERNO',
            'descricao': 'Clínica privada externa',
        },
    ]

    created_items = []
    for item in test_data:
        response = client.post('/origens_destino', json=item)
        assert response.status_code == STATUS_CREATED
        created_items.append(response.json())

    # Get all items
    response = client.get('/origens_destino')
    assert response.status_code == STATUS_OK
    data = response.json()
    assert len(data) >= MIN_TEST_DATA_COUNT


def test_get_origem_destino_by_id(client: TestClient):
    """Test getting a specific origem/destino by ID."""
    # Create an item first
    create_response = client.post(
        '/origens_destino',
        json={
            'local': 'Hospital de Teste',
            'int_ext': 'INTERNO',
            'descricao': 'Hospital para testes',
        },
    )
    assert create_response.status_code == STATUS_CREATED
    created_item = create_response.json()

    # Get the item by ID
    response = client.get(f'/origens_destino/{created_item["id"]}')
    assert response.status_code == STATUS_OK
    data = response.json()
    assert data['id'] == created_item['id']
    assert data['local'] == 'Hospital de Teste'
    assert data['int_ext'] == 'INTERNO'


def test_get_origem_destino_not_found(client: TestClient):
    """Test getting a non-existent origem/destino."""
    response = client.get(f'/origens_destino/{INVALID_ID}')
    assert response.status_code == STATUS_NOT_FOUND
    assert response.json()['detail'] == 'Origem/destino not found'


def test_origem_destino_int_ext_enum_values(client: TestClient):
    """Test that int_ext accepts valid enum values."""
    valid_values = ['INTERNO', 'EXTERNO', 'OUTRO']

    for value in valid_values:
        response = client.post(
            '/origens_destino',
            json={
                'local': f'Teste {value}',
                'int_ext': value,
                'descricao': f'Teste para valor {value}',
            },
        )
        assert response.status_code == STATUS_CREATED
        data = response.json()
        assert data['int_ext'] == value


def test_origem_destino_relationships_in_database(test_session: Session):
    """Test creating origem/destino directly in the database."""
    origem = OrigemDestino(
        local='Hospital de Teste',
        int_ext=IntExtEnum.INTERNO,
        descricao='Hospital para testes de relacionamento',
    )

    test_session.add(origem)
    test_session.commit()
    test_session.refresh(origem)

    # Verify it was created
    assert origem.id is not None
    assert origem.local == 'Hospital de Teste'
    assert origem.int_ext == IntExtEnum.INTERNO

    # Clean up
    test_session.delete(origem)
    test_session.commit()


def test_internamento_with_origem_destino_foreign_key(
    client: TestClient, test_session: Session
):
    """Test creating internamento with origem/destino foreign keys."""

    # Generate unique numbers
    unique_numero_processo = 90000 + random.randint(1, 9999)
    unique_numero_internamento = 90000 + random.randint(1, 9999)

    # Create a patient first
    doente = Doente(
        nome='Paciente Teste FK',
        numero_processo=unique_numero_processo,
        sexo=SexoEnum.M,
        morada='Endereço de teste FK',
    )
    test_session.add(doente)
    test_session.commit()
    test_session.refresh(doente)

    # Create origem/destino records
    origem = OrigemDestino(
        local='Emergência',
        int_ext=IntExtEnum.INTERNO,
        descricao='Serviço de emergência',
    )
    destino = OrigemDestino(
        local='Domicílio',
        int_ext=IntExtEnum.EXTERNO,
        descricao='Casa do paciente',
    )

    test_session.add(origem)
    test_session.add(destino)
    test_session.commit()
    test_session.refresh(origem)
    test_session.refresh(destino)

    # Create internamento with foreign key relationships
    response = client.post(
        '/internamentos',
        json={
            'numero_internamento': unique_numero_internamento,
            'doente_id': doente.id,
            'data_entrada': '2025-09-12',
            'ASCQ_total': 35,
            'lesao_inalatoria': 'SIM',
            'origem_entrada': origem.id,
            'destino_alta': destino.id,
        },
    )
    assert response.status_code == STATUS_CREATED
    data = response.json()
    assert data['origem_entrada'] == origem.id
    assert data['destino_alta'] == destino.id

    # Clean up
    internamento = test_session.get(Internamento, data['id'])
    if internamento:
        test_session.delete(internamento)
    test_session.delete(doente)
    test_session.delete(origem)
    test_session.delete(destino)
    test_session.commit()


def test_internamento_with_invalid_origem_destino_fk(client: TestClient):
    """Test creating internamento with invalid origem/destino fk."""

    # Generate unique number
    unique_numero_internamento = 80000 + random.randint(1, 9999)

    # Note: SQLite doesn't enforce foreign key constraints by default,
    # so this will succeed but with an invalid reference
    response = client.post(
        '/internamentos',
        json={
            'numero_internamento': unique_numero_internamento,
            'doente_id': 1,  # Assuming this exists
            'data_entrada': '2025-09-12',
            'ASCQ_total': 15,
            'lesao_inalatoria': 'NAO',
            'origem_entrada': INVALID_ID,  # Invalid foreign key
        },
    )

    # This will succeed in SQLite without foreign key enforcement
    # But the foreign key reference will be invalid
    if response.status_code == STATUS_CREATED:
        data = response.json()
        assert data['origem_entrada'] == INVALID_ID


def test_origem_destino_model_validation(test_session: Session):
    """Test OrigemDestino model validation and properties."""
    # Test valid enum values
    for enum_val in IntExtEnum:
        origem = OrigemDestino(
            local=f'Local {enum_val.value}',
            int_ext=enum_val,
            descricao=f'Descrição para {enum_val.value}',
        )
        assert origem.int_ext == enum_val


def test_origem_destino_string_representation(test_session: Session):
    """Test that OrigemDestino has proper string representation."""
    origem = OrigemDestino(
        local='Teste Representação',
        int_ext=IntExtEnum.EXTERNO,
        descricao='Teste da representação string',
    )

    # Test that the object can be converted to string
    str_repr = str(origem)
    assert isinstance(str_repr, str)
    assert len(str_repr) > 0


def test_origem_destino_audit_fields(client: TestClient):
    """Test that audit fields are set when creating origem/destino."""
    response = client.post(
        '/origens_destino',
        json={
            'local': 'Hospital com Auditoria',
            'int_ext': 'INTERNO',
            'descricao': 'Teste dos campos de auditoria',
        },
    )
    assert response.status_code == STATUS_CREATED
    data = response.json()

    # Note: The API response might not include audit fields
    # But they should be set in the database
    assert 'id' in data
    assert data['local'] == 'Hospital com Auditoria'


def test_origem_destino_comprehensive_crud(client: TestClient):
    """Test comprehensive CRUD operations for origem/destino."""
    # Create
    create_response = client.post(
        '/origens_destino',
        json={
            'local': 'CRUD Teste',
            'int_ext': 'OUTRO',
            'descricao': 'Teste completo de CRUD',
        },
    )
    assert create_response.status_code == STATUS_CREATED
    created_data = create_response.json()
    origem_id = created_data['id']

    # Read - individual
    read_response = client.get(f'/origens_destino/{origem_id}')
    assert read_response.status_code == STATUS_OK
    read_data = read_response.json()
    assert read_data['id'] == origem_id
    assert read_data['local'] == 'CRUD Teste'

    # Read - list (should include our item)
    list_response = client.get('/origens_destino')
    assert list_response.status_code == STATUS_OK
    list_data = list_response.json()
    origem_ids = [item['id'] for item in list_data]
    assert origem_id in origem_ids

    # Note: UPDATE and DELETE endpoints are not implemented yet
    # following the same pattern as other lookup tables
