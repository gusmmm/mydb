# Database Models and Relationships - September 7, 2025

## SQLModel Implementation Details

### Model Hierarchy and Design Patterns

#### Base Model Pattern
The implementation uses SQLModel's recommended pattern with base classes for shared fields:

```python
class DoenteBase(SQLModel):
    # Shared fields between create/read operations
    nome: str
    numero_process: int
    data_nascimento: str
    sexo: SexoEnum
    morada: str

class DoenteCreate(DoenteBase):
    # Input schema with nested relationships
    internamentos: list["Internamento"] | None = None

class Doente(DoenteBase, table=True):
    # Database table with auto-generated ID and relationships
    id: int = Field(default=None, primary_key=True)
    internamentos: list["Internamento"] = Relationship(back_populates="doente")
```

### Database Schema Implementation

#### Doente Table
- **Primary Key**: `id` (auto-generated integer)
- **Unique Constraint**: `numero_processo` (enforced at application level)
- **Foreign Relations**: One-to-many with Internamento
- **Enum Field**: `sexo` using SexoEnum (M/F)

#### Internamento Table  
- **Primary Key**: `id` (auto-generated integer)
- **Foreign Key**: `doente_id` → `doente.id`
- **Optional Fields**: `data_entrada`, `data_alta` (nullable strings)
- **Relationship**: Many-to-one with Doente

### Relationship Configuration

#### SQLModel Relationship Mapping
```python
# In Doente model
internamentos: list["Internamento"] = Relationship(back_populates="doente")

# In Internamento model  
doente: Doente = Relationship(back_populates="internamentos")
```

#### Foreign Key Constraints
```python
# Internamento foreign key definition
doente_id: int | None = Field(foreign_key="doente.id")
```

### Data Type Decisions

#### String-based Dates
**Current Implementation**: All date fields are strings
- `data_nascimento: str`
- `data_entrada: str | None`
- `data_alta: str | None`

**Rationale**: Simplifies JSON serialization and client handling
**Future Consideration**: Convert to `datetime.date` or `datetime.datetime`

#### Enum Implementation
```python
class SexoEnum(str, Enum):
    M = "M" 
    F = "F"
```
**Benefits**: Type safety, automatic validation, clear API documentation

### Database Relationship Handling

#### Creation Pattern (Parent → Child)
```python
# 1. Create parent (Doente)
doente_bd = Doente(**doente_data)
session.add(doente_bd)

# 2. Flush to get auto-generated ID
session.flush()  # doente_bd.id now available

# 3. Create children with foreign key
internamento_bd = Internamento(
    doente_id=doente_bd.id,  # Use flushed ID
    **internamento_data
)
session.add(internamento_bd)

# 4. Final commit
session.commit()
```

#### Query Patterns

**Parent with Children (Lazy Loading)**
```python
doente = session.get(Doente, doente_id)
# doente.internamentos automatically loaded when accessed
```

**Filter by Relationship**
```python
# Get doentes with active internamentos
statement = select(Doente).join(Internamento).where(
    Internamento.data_alta.is_(None)
)
```

### Field Validation and Constraints

#### Automatic Pydantic Validation
- **Type Checking**: Automatic validation of field types
- **Enum Validation**: SexoEnum ensures valid gender values
- **Required Fields**: Non-nullable fields enforced by Pydantic

#### Database Constraints
- **Primary Keys**: Auto-incrementing integers
- **Foreign Keys**: Referential integrity enforced by SQLite
- **NOT NULL**: Enforced for required fields

### Migration Considerations

#### Current State
- **Table Creation**: Automatic via `SQLModel.metadata.create_all()`
- **Schema Changes**: Require manual database recreation
- **Data Persistence**: SQLite file-based storage

#### Future Migration Strategy
- **Alembic Integration**: For production schema versioning
- **Data Migration Scripts**: For transforming existing data
- **Backup Strategy**: Before schema modifications

### Performance and Optimization

#### Query Optimization
- **Select Statements**: Type-safe SQLModel queries
- **Lazy Loading**: Relationships loaded on-demand
- **Index Considerations**: Primary keys automatically indexed

#### Connection Management
- **Session Lifecycle**: FastAPI dependency injection
- **Connection Pooling**: SQLite default handling
- **Transaction Management**: Explicit commit/rollback

### Extensions and Future Schema

#### Database Design Alignment
The current implementation covers core tables from dbdesign:
- ✅ `doente` table (implemented)
- ✅ `internamento` table (basic fields implemented)
- ⏳ Extended internamento fields (medical burn data)
- ⏳ Lookup tables (tipoAcidente, agenteQueimadura, etc.)

#### Planned Model Extensions
Based on dbdesign specification:
1. **Extended Internamento Fields**:
   - Medical burn assessment data
   - Treatment details
   - Outcome metrics

2. **Lookup Tables**:
   - TipoAcidente
   - AgenteQueimadura  
   - Additional medical coding tables

3. **Audit Fields**:
   - created_at, last_modified timestamps
   - User tracking (when authentication added)

### Technical Debt and Considerations

#### Current Limitations
- **Date Types**: String format instead of proper date objects
- **Validation**: Limited business logic validation
- **Constraints**: Missing unique constraints on numero_processo
- **Relationships**: No cascade delete configuration

#### Improvement Opportunities
- **Custom Validators**: Pydantic validators for business rules
- **Computed Fields**: Derived fields for common calculations
- **Index Strategy**: Performance optimization for common queries
- **Soft Deletes**: Instead of hard deletes for audit trails
