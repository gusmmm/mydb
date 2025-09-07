# MyDB - Local Database Management System

A FastAPI-based REST API for managing medical patient records (doentes) and hospitalizations (internamentos) using SQLModel and SQLite.

## Overview

This project implements a medical database management system with the following core entities:
- **Doentes** (Patients): Basic patient information including name, process number, birth date, gender, and address
- **Internamentos** (Hospitalizations): Hospitalization records linked to patients

## Technology Stack

- **Backend**: FastAPI with async support
- **Database**: SQLite with SQLModel ORM
- **Validation**: Pydantic V2
- **Environment**: Python 3.13+ with uv package management
- **Debugging**: icecream for enhanced logging
- **Testing**: pytest with coverage
- **Linting**: ruff

## Project Structure

```
mydb/
├── src/
│   ├── api.py              # FastAPI application and routes
│   ├── db.py               # Database connection and initialization
│   ├── models/
│   │   └── models.py       # SQLModel database models
│   └── schemas/
│       └── schemas.py      # Pydantic schemas (future)
├── tests/                  # Test files
├── migrations/             # Alembic database migrations
├── .env                    # Environment variables
├── dbdesign                # Database design specification
└── pyproject.toml          # Project configuration
```

## Current Implementation

### Database Models

**Doente (Patient)**
- `id`: Primary key (auto-generated)
- `nome`: Patient name
- `numero_processo`: Unique process number
- `data_nascimento`: Birth date (string format)
- `sexo`: Gender enum (M/F)
- `morada`: Address
- Relationship: One-to-many with Internamento

**Internamento (Hospitalization)**
- `id`: Primary key (auto-generated)
- `numero_internamento`: Hospitalization number
- `data_entrada`: Entry date (optional)
- `data_alta`: Discharge date (optional)
- `doente_id`: Foreign key to Doente
- Relationship: Many-to-one with Doente

### API Endpoints

#### Basic Endpoints
- `GET /` - Welcome message
- `GET /about` - API description

#### Doente (Patient) Endpoints
- `GET /doentes` - List all patients (with optional gender filter)
  - Query parameter: `sexo` (M/F)
- `GET /doentes/numero_processo/{numero_processo}` - Get patient by process number
- `POST /doentes` - Create new patient (with optional internamentos)

## Setup and Usage

### Prerequisites
- Python 3.13+
- uv package manager

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   uv sync
   ```

3. Set up environment variables in `.env`:
   ```
   DATABASE_URL="sqlite:///./mydb.db"
   ```

### Running the Application

```bash
# Start the development server
uv run task run

# The API will be available at http://localhost:8088
```

### API Documentation
- Swagger UI: http://localhost:8088/docs
- ReDoc: http://localhost:8088/redoc

### Development Tasks

```bash
# Linting
uv run task lint

# Formatting
uv run task format

# Testing
uv run task test

# Run all (lint + test + coverage)
uv run task test
```

### Example Usage

**Create a Patient:**
```bash
POST http://localhost:8088/doentes
Content-Type: application/json

{
    "nome": "João Silva",
    "numero_processo": 12345,
    "data_nascimento": "1990-01-01",
    "sexo": "M",
    "morada": "Rua Example, 123"
}
```

**Get All Patients:**
```bash
GET http://localhost:8088/doentes
```

**Get Patient by Process Number:**
```bash
GET http://localhost:8088/doentes/numero_processo/12345
```

**Filter Patients by Gender:**
```bash
GET http://localhost:8088/doentes?sexo=F
```

## Database Design

The database follows the specification in the `dbdesign` file, implementing a medical records system with patients and hospitalizations. The current implementation covers the core `doente` and `internamento` tables with their basic relationships.

## Development Notes

- Database tables are automatically created on application startup
- The API uses icecream for enhanced debugging output
- All endpoints include proper error handling and HTTP status codes
- The system uses SQLModel for type-safe database operations
- Foreign key relationships are properly established between entities

## Future Enhancements

Based on the database design, future implementations may include:
- Additional hospitalization fields (burn-related medical data)
- Lookup tables (tipoAcidente, agenteQueimadura, etc.)
- Update and delete operations
- Advanced filtering and pagination
- Alembic migrations for schema changes