# API Implementation and Design Patterns - September 7, 2025

## FastAPI Application Architecture

### Application Lifecycle Management

#### Lifespan Context Manager
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()  # Initialize database tables on startup
    yield       # Application runs here
    # Cleanup code would go here (currently none needed)

app = FastAPI(lifespan=lifespan)
```

**Benefits**:
- Automatic database initialization
- Clean startup/shutdown hooks
- Async context management for resources

### Dependency Injection Pattern

#### Database Session Management
```python
def get_session():
    with Session(engine) as session:
        yield session

# Usage in endpoints
async def endpoint(session: Session = Depends(get_session)):
    # session automatically provided and closed
```

**Advantages**:
- Automatic session lifecycle management
- Testability (can override dependencies)
- Clean separation of concerns
- Exception safety (auto-rollback on errors)

### RESTful API Design

#### Endpoint Naming Conventions
Following CRUD patterns as specified in project guidelines:

**Resource**: `/doentes` (Patients)
- `GET /doentes` → `read_doentes` (list)
- `GET /doentes/{id}` → `read_doente_by_id` (get by ID)  
- `GET /doentes/numero_processo/{id}` → `read_doente_by_numero_processo` (get by process number)
- `POST /doentes` → `create_doente` (create)
- `PUT /doentes/{id}` → `update_doente` (full update)
- `PATCH /doentes/{id}` → `patch_doente` (partial update)
- `DELETE /doentes/{id}` → `delete_doente` (delete)

#### HTTP Status Codes
- **200 OK**: Successful GET operations
- **201 Created**: Successful POST operations (explicit status_code=201)
- **404 Not Found**: Resource not found
- **422 Unprocessable Entity**: Validation errors (automatic)
- **500 Internal Server Error**: Database constraint violations

### Query Implementation Patterns

#### List with Optional Filtering
```python
async def read_doentes(
    sexo: SexoEnum | None = None,
    session: Session = Depends(get_session)
) -> list[Doente]:
    statement = select(Doente)
    if sexo:
        statement = statement.where(Doente.sexo == sexo)
    doentes = session.exec(statement).all()
    return list(doentes)
```

**Features**:
- Optional query parameters
- Type-safe filtering
- Proper return type conversion

#### Single Resource by Unique Field
```python
async def read_doente_by_numero_processo(
    numero_processo: int,
    session: Session = Depends(get_session)
) -> Doente:
    statement = select(Doente).where(Doente.numero_processo == numero_processo)
    doente = session.exec(statement).first()
    if not doente:
        raise HTTPException(status_code=404, detail="Doente not found")
    return doente
```

**Key Points**:
- Uses field-based lookup (not primary key)
- Explicit 404 handling
- Type-safe query construction

### Complex Creation Pattern

#### Nested Object Creation
```python
async def create_doente(
    doente: DoenteCreate,
    session: Session = Depends(get_session)
) -> Doente:
    # 1. Create parent object
    doente_bd = Doente(**parent_fields)
    session.add(doente_bd)
    
    # 2. Flush to get auto-generated ID
    session.flush()
    
    # 3. Create child objects with foreign key
    if doente.internamentos:
        for internamento in doente.internamentos:
            internamento_bd = Internamento(
                doente_id=doente_bd.id,  # Use flushed ID
                **internamento_fields
            )
            session.add(internamento_bd)
    
    # 4. Final commit
    session.commit()
    session.refresh(doente_bd)
    return doente_bd
```

**Technical Pattern**:
- **Flush before foreign key**: Ensures parent ID is available
- **Explicit transaction management**: Clear commit boundaries
- **Refresh after commit**: Loads final state with relationships

### Error Handling Strategy

#### HTTP Exception Pattern
```python
if not doente:
    raise HTTPException(status_code=404, detail="Doente not found")
```

#### Automatic Validation Errors
- **Pydantic Validation**: Automatic 422 for invalid input
- **Type Errors**: Caught by FastAPI and converted to 422
- **Database Constraints**: Propagated as 500 errors

#### Debug Integration
```python
ic("Starting doente creation")
ic(doente.nome, doente.numero_processo, doente.sexo)
ic("Created doente instance", doente_bd)
ic("Flushed session - doente ID:", doente_bd.id)
```

**icecream Benefits**:
- Rich debugging output
- Variable name and value display
- Transaction state tracking
- Development troubleshooting

### API Documentation

#### Automatic OpenAPI Generation
FastAPI automatically generates:
- **Swagger UI**: Interactive API documentation at `/docs`
- **ReDoc**: Alternative documentation at `/redoc`
- **OpenAPI Schema**: JSON schema at `/openapi.json`

#### Type-driven Documentation
- **Request/Response Models**: Automatically documented from Pydantic models
- **Parameter Types**: Path and query parameters with types
- **Status Codes**: Documented from endpoint definitions
- **Error Responses**: HTTPException details included

### Request/Response Patterns

#### Input Validation
```python
# Automatic validation from Pydantic model
doente: DoenteCreate  # Validates all fields and nested objects
```

#### Response Serialization  
```python
-> list[Doente]  # Automatic JSON serialization
-> Doente        # SQLModel → JSON conversion
```

#### Nested Object Support
```python
# DoenteCreate accepts nested internamentos
{
    "nome": "Patient Name",
    "numero_processo": 12345,
    "internamentos": [
        {
            "numero_internamento": 1,
            "data_entrada": "2023-01-01"
        }
    ]
}
```

### Performance Considerations

#### Query Optimization
- **Select Statements**: Explicit column selection capability
- **Relationship Loading**: Lazy loading by default
- **Batch Operations**: Single transaction for multiple inserts

#### Connection Efficiency
- **Session Scope**: Request-scoped sessions
- **Connection Pooling**: SQLite default handling
- **Transaction Boundaries**: Explicit commit/rollback

### Security Patterns

#### SQL Injection Prevention
- **Parameterized Queries**: SQLModel/SQLAlchemy automatic protection
- **Type Safety**: Compile-time type checking

#### Input Sanitization
- **Pydantic Validation**: Automatic type and format validation
- **Enum Constraints**: Limited value sets for fields like sexo

### Testing Considerations

#### Dependency Override Pattern
```python
# For testing - can override get_session dependency
def override_get_session():
    # Return test database session
    pass

app.dependency_overrides[get_session] = override_get_session
```

#### Database State Management
- **Test Isolation**: Each test can use separate database
- **Transaction Rollback**: Test transactions can be rolled back
- **Fixture Support**: Setup/teardown for test data

### Future API Enhancements

#### Planned Features
1. **Pagination**: For large result sets
2. **Sorting**: Query parameter-based sorting
3. **Advanced Filtering**: Multiple field filters
4. **Bulk Operations**: Batch create/update/delete
5. **Authentication**: JWT or session-based auth
6. **Rate Limiting**: API usage controls
7. **Versioning**: API version management

#### Extension Points
- **Middleware**: Cross-cutting concerns (logging, auth)
- **Background Tasks**: Async processing
- **WebSocket Support**: Real-time updates
- **File Upload**: Document/image handling
- **Export Functions**: Data export in various formats

### Development Workflow Integration

#### Task Integration
- **Development Server**: `uv run task run` (port 8088)
- **Auto-reload**: FastAPI development mode with file watching
- **API Testing**: Built-in documentation for manual testing

#### Debugging Support
- **Verbose Logging**: Database queries logged (echo=True)
- **icecream Integration**: Rich debug output
- **Exception Details**: Full traceback in development mode
