---
applyTo: '**'
---

# AgenteQueimadura Lookup Table Implementation

## Overview
Successfully implemented the `AgenteQueimadura` lookup table following the same pattern as `TipoAcidente`. This table stores information about different types of burning agents and their associated notes.

## Database Design
The `AgenteQueimadura` table includes:
- `id`: Primary key (auto-increment)
- `agente_queimadura`: String field for the agent name
- `nota`: String field for additional notes/descriptions

## Implementation Details

### Models (src/models/models.py)
- `AgenteQueimaduraBase`: Base schema with `agente_queimadura` and `nota` fields
- `AgenteQueimaduraCreate`: Inherits from base for creation operations
- `AgenteQueimadura`: Database table model with relationships

### Foreign Key Relationship
Updated `Internamento` model to include proper foreign key relationship:
- Field: `agente_queimadura: int | None = Field(default=None, foreign_key="agentequeimadura.id")`
- Relationship: `agente_queimadura_ref: AgenteQueimadura | None = Relationship(back_populates="internamentos")`

### API Endpoints (src/api.py)
Implemented full CRUD operations:
- `GET /agentes_queimadura` - List all agents
- `GET /agentes_queimadura/{agente_id}` - Get specific agent by ID
- `POST /agentes_queimadura` - Create new agent

### Schemas (src/schemas/schemas.py)
Added Pydantic schemas:
- `AgenteQueimaduraBase`: Base validation schema
- `AgenteQueimaduraCreate`: For creation operations
- `AgenteQueimaduraWithID`: Response schema with ID

### Database Migration
- Migration file: `24b1412cf938_add_agentequeimadura_table_and_foreign_.py`
- SQLModel auto-creates the table structure
- Foreign key relationship properly established

## Testing
Comprehensive test suite in `tests/test_agentequeimadura.py`:
- Create agent functionality
- Get all agents
- Get agent by ID
- 404 error handling for non-existent agents
- Foreign key relationship testing with internamentos
- Validation testing

## Sample Data Created
1. "Fogo direto" - "Exposição direta ao fogo"
2. "Líquido quente" - "Água fervente, óleo quente, etc."
3. "Electricidade" - "Queimadura eléctrica por contacto"

## Integration
The AgenteQueimadura table is fully integrated with the Internamento system:
- Internamentos can reference AgenteQueimadura via foreign key
- Proper relationships established for data integrity
- API endpoints tested and working correctly

## Pattern for Future Lookup Tables
This implementation establishes the standard pattern for creating lookup tables:
1. Create Base/Create/Table models in models.py
2. Add foreign key field to related tables
3. Establish SQLModel relationships
4. Create API endpoints (GET list, GET by ID, POST create)
5. Add Pydantic schemas for validation
6. Create database migration
7. Write comprehensive tests
8. Populate with sample data

All functionality tested and working correctly as of September 9, 2025.

## Code Quality
- All linting errors have been resolved
- Code follows project style guidelines with proper:
  - Import organization (imports at top-level)
  - Line length compliance (≤79 characters)
  - No variable overwrites in for loops
  - Proper trailing whitespace handling
  - Use of constants for HTTP status codes in tests
