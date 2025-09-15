---
applyTo: '**'
---

# Patologia and DoentePatologia Implementation

## Overview
Successfully implemented the `patologia` and `doentepatologia` tables following the database design specification in `dbdesign`.

## Implementation Details

### 1. Database Models (`src/models/models.py`)
- **PatologiaBase**: Core fields including `nome_patologia` (required), optional `classe_patologia` and `codigo`
- **PatologiaCreate**: Creation schema inheriting from PatologiaBase
- **Patologia**: Full model with audit fields (`created_at`, `last_modified`) and ID
- **DoentePatologiaBase**: Core relationship fields with `doente_id` (required), optional `patologia` and `nota`
- **DoentePatologiaCreate**: Creation schema inheriting from DoentePatologiaBase
- **DoentePatologia**: Full model with audit fields and bidirectional relationships

### 2. Database Relationships
- **Foreign Keys**: 
  - `doentepatologia.doente_id` → `doente.id` (required)
  - `doentepatologia.patologia` → `patologia.id` (optional)
- **Bidirectional Relationships**:
  - `Doente.doente_patologias` ← one-to-many → `DoentePatologia.doente`
  - `Patologia.doente_patologias` ← one-to-many → `DoentePatologia.patologia_rel`

### 3. Pydantic Schemas (`src/schemas/schemas.py`)
- **PatologiaBase**: Base validation schema
- **PatologiaCreate**: Creation schema
- **PatologiaWithID**: Response schema including ID and audit fields
- **DoentePatologiaBase**: Base validation schema  
- **DoentePatologiaCreate**: Creation schema
- **DoentePatologiaWithID**: Response schema including ID and audit fields

### 4. API Endpoints (`src/api.py`)
#### Patologia Endpoints:
- `POST /patologias` - Create new patologia
- `GET /patologias` - Get all patologias
- `GET /patologias/{patologia_id}` - Get specific patologia by ID

#### DoentePatologia Endpoints:
- `POST /doentes_patologia` - Create new doente-patologia relationship
- `GET /doentes_patologia` - Get all doente-patologia relationships
- `GET /doentes_patologia/{doente_patologia_id}` - Get specific relationship by ID
- `GET /doentes/{doente_id}/patologias` - Get all patologias for a specific doente

### 5. Comprehensive Testing (`tests/test_patologia.py`)
- **TestPatologia**: 6 test cases covering CRUD operations, validation, error handling
- **TestDoentePatologia**: 10 test cases covering relationship creation, validation, foreign key constraints
- **TestDatabaseRelationships**: 3 test cases verifying bidirectional relationships work correctly

## Key Features
1. **Foreign Key Validation**: API validates that referenced `doente` and `patologia` records exist
2. **Audit Fields**: Automatic `created_at` and `last_modified` timestamps on all records
3. **Optional Relationships**: DoentePatologia can exist with only doente_id, patologia is optional
4. **Comprehensive Error Handling**: Proper HTTP status codes (404, 422) with descriptive messages
5. **Bidirectional Navigation**: Can query from doente → patologias and patologia → doentes

## Database Tables Status
- Tables already existed in database (auto-created by SQLModel)
- Migration marked as complete using `alembic stamp head`
- Schema verified to match DBML specification

## Testing Results
- **All 19 tests passing** (6 Patologia + 10 DoentePatologia + 3 Database Relationships)
- **No linting errors** after cleanup
- **Full test coverage** with comprehensive test suite following established patterns
- **88% overall project coverage** maintained

## Usage Examples
```python
# Create a patologia
POST /patologias
{
    "nome_patologia": "Diabetes Mellitus",
    "classe_patologia": "Endócrino", 
    "codigo": "E11.9"
}

# Create doente-patologia relationship
POST /doentes_patologia  
{
    "doente_id": 1,
    "patologia": 1,
    "nota": "Diabetes controlada com medicação"
}

# Get all patologias for a patient
GET /doentes/1/patologias
```

This implementation follows the established patterns from other lookup tables (TipoAcidente, AgenteQueimadura, etc.) and provides a complete foundation for managing patient pathology relationships.