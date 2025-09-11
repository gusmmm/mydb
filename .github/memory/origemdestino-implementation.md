---
applyTo: '**'
---

# OrigemDestino Implementation - Complete Lookup Table

## Overview
Successfully implemented the complete **OrigemDestino** lookup table following the same pattern as TipoAcidente, AgenteQueimadura, and MecanismoQueimadura.

## Database Schema
- **Table Name**: `origemdestino`
- **Fields**:
  - `id` (Integer, Primary Key, Auto-increment)
  - `local` (VARCHAR) - Location name/identifier
  - `int_ext` (ENUM: 'INTERNO', 'EXTERNO', 'OUTRO') - Internal/External/Other classification
  - `descricao` (VARCHAR, Optional) - Description field
  - `created_at` (DateTime) - Audit field for creation timestamp
  - `last_modified` (DateTime) - Audit field for last modification timestamp

## Relationships
- **Foreign Key References in Internamento Table**:
  - `origem_entrada` → `origemdestino.id` (Origin of admission)
  - `destino_alta` → `origemdestino.id` (Destination on discharge)
- **Bidirectional Relationships**: OrigemDestino has back-references to Internamento records

## IntExtEnum Implementation
Created a new enum `IntExtEnum` with values:
- `INTERNO` = "INTERNO"
- `EXTERNO` = "EXTERNO"  
- `OUTRO` = "OUTRO"

## API Endpoints
- `GET /origens_destino` - List all origem/destino records
- `GET /origens_destino/{id}` - Get specific origem/destino by ID
- `POST /origens_destino` - Create new origem/destino record
- Returns 404 for non-existent records with proper error messages

## Implementation Components

### 1. Models (`src/models/models.py`)
- `IntExtEnum` class extending `str, Enum`
- `OrigemDestinoBase` with validation
- `OrigemDestino` table model with relationships
- Foreign key fields added to `InternamentoBase`

### 2. Schemas (`src/schemas/schemas.py`)
- `OrigemDestinoBase` - Base schema with validation
- `OrigemDestinoCreate` - For creation requests  
- `OrigemDestinoWithID` - For responses including ID

### 3. API (`src/api.py`)
- Full CRUD endpoints following established patterns
- Proper error handling with 404 responses
- Foreign key relationship support in Internamento endpoints

### 4. Database Migration (`migrations/`)
- Alembic migration created and applied
- Foreign key constraints properly established
- Enum type constraints implemented

## Testing (`tests/test_origemdestino.py`)
**13 comprehensive test cases covering**:
1. Basic CRUD operations
2. Enum value validation
3. Foreign key relationships
4. Database model validation
5. Error handling (404 responses)
6. Audit field functionality
7. String representation
8. Integration with Internamento table

**All tests passing**: ✅ 13/13 tests successful

## Code Quality
- **Linting**: All ruff linting issues resolved
- **Constants**: Magic numbers replaced with named constants
- **Import Organization**: Proper import structure
- **Type Hints**: Full type annotation coverage

## Usage Examples

### Creating OrigemDestino Records
```json
{
    "local": "Hospital Central",
    "int_ext": "INTERNO", 
    "descricao": "Hospital principal da região"
}
```

### Internamento with Foreign Keys
```json
{
    "numero_internamento": 12345,
    "doente_id": 1,
    "origem_entrada": 1,  // References origemdestino.id
    "destino_alta": 2     // References origemdestino.id  
}
```

## Integration Points
- **Internamento Table**: Two foreign key relationships established
- **Database Constraints**: Proper referential integrity
- **API Consistency**: Follows same patterns as other lookup tables
- **Test Coverage**: Comprehensive validation of all functionality

## Status: ✅ COMPLETE
All functionality implemented, tested, and documented. The OrigemDestino table is fully operational and integrated with the existing system architecture.
