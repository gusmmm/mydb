# MyDB - Medical Database Management System

A full-stack web application for managing medical patient records with a FastAPI backend and Vue.js frontend.

## 🏥 Overview

MyDB is a comprehensive medical database management system that provides:
- **Backend API**: FastAPI-based REST API with SQLModel and SQLite
- **Frontend Web Interface**: Vue.js 3 application with PrimeVue UI components
- **Database Management**: Full CRUD operations for medical lookup tables
- **Interactive UI**: Data tables with inline editing, forms, and real-time updates

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI with async support
- **Database**: SQLite with SQLModel ORM
- **Validation**: Pydantic V2
- **Package Management**: uv
- **Testing**: pytest with coverage
- **Linting**: ruff
- **Debugging**: icecream
- **Migrations**: Alembic

### Frontend
- **Framework**: Vue.js 3 with Composition API
- **Build Tool**: Vite
- **Language**: TypeScript
- **UI Library**: PrimeVue 4
- **State Management**: Pinia
- **HTTP Client**: Axios
- **Icons**: PrimeIcons
- **Routing**: Vue Router

## 📁 Project Structure

```
mydb/
├── src/                    # Backend source code
│   ├── api.py             # FastAPI application and routes
│   ├── db.py              # Database connection and initialization
│   ├── models/            # SQLModel database models
│   └── schemas/           # Pydantic schemas
├── frontend/              # Vue.js frontend application
│   ├── src/
│   │   ├── components/    # Vue components
│   │   ├── stores/        # Pinia stores
│   │   ├── services/      # API service layer
│   │   ├── views/         # Page components
│   │   └── router/        # Vue Router configuration
│   ├── package.json       # Frontend dependencies
│   └── vite.config.ts     # Vite configuration
├── tests/                 # Backend tests
├── migrations/            # Alembic database migrations
├── .env                   # Environment variables
├── dbdesign               # Database design specification
└── pyproject.toml         # Backend dependencies and configuration
```

## 🚀 Quick Start

### Prerequisites
- **Python 3.13+** with uv package manager
- **Node.js 22.11+** with npm
- **Git** for version control

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd mydb
   ```

2. **Install backend dependencies:**
   ```bash
   uv sync
   ```

3. **Install frontend dependencies:**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

4. **Set up environment variables:**
   ```bash
   # Create .env file in project root
   echo 'DATABASE_URL="sqlite:///./mydb.db"' > .env
   ```

## 🖥️ Running the Application

### Start Backend Server (Port 8001)
```bash
# Option 1: Using predefined task
uv run task run

# Option 2: Direct uvicorn command
uv run uvicorn src.api:app --reload --port 8001
```

### Start Frontend Server (Port 5173/5174)
```bash
# Navigate to frontend directory
cd frontend

# Start development server
npm run dev
```

### Access the Application
- **Frontend Web Interface**: http://localhost:5173 (or 5174)
- **Backend API**: http://127.0.0.1:8001
- **API Documentation**: http://127.0.0.1:8001/docs
- **ReDoc Documentation**: http://127.0.0.1:8001/redoc

## 💻 Using the Web Interface

### Home Dashboard
- Overview statistics of database tables
- Quick navigation to different sections
- Clean, professional layout

### Infectious Agents Management
Navigate to the "Agentes Infecciosos" tab to:
- **View Data**: Sortable table with pagination
- **Add Records**: Click "Add New Agent" button
- **Edit Inline**: Click any cell to edit directly
- **Delete Records**: Use trash icon with confirmation
- **Real-time Updates**: Changes reflected immediately

### Features
- **Responsive Design**: Works on desktop and mobile
- **Toast Notifications**: User feedback for all operations
- **Error Handling**: Graceful error messages and recovery
- **Loading States**: Visual feedback during API calls
- **Confirmation Dialogs**: Prevent accidental deletions

## 🗄️ Database Schema

### Core Tables
- **doente** (Patients): Patient information and demographics
- **internamento** (Hospitalizations): Hospital admission records
- **agenteinfeccioso** (Infectious Agents): Bacterial, viral, and fungal pathogens

### Lookup Tables
- **tipoacidente** (Accident Types): Classification of accidents
- **agentequeimadura** (Burn Agents): Types of burn-causing agents  
- **mecanismoqueimadura** (Burn Mechanisms): Heat transfer mechanisms
- **origemdestino** (Origin/Destination): Patient transfer locations
- **queimadura** (Burns): Individual burn records
- **localanatomico** (Anatomical Locations): Body regions
- **And many more...**

## 🧪 Development Tasks

### Backend Tasks
```bash
# Run tests with coverage
uv run task test

# Linting and formatting
uv run task lint

# Database migrations
uv run alembic upgrade head

# Create new migration
uv run alembic revision -m "description"
```

### Frontend Tasks
```bash
cd frontend

# Development server
npm run dev

# Type checking
npm run type-check

# Build for production
npm run build

# Preview production build
npm run preview
```

## 📡 API Examples

### Get All Infectious Agents
```bash
curl -X GET "http://127.0.0.1:8001/agentes_infecciosos"
```

### Create New Infectious Agent
```bash
curl -X POST "http://127.0.0.1:8001/agentes_infecciosos" \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Staphylococcus aureus",
    "tipo_agente": "Bacteria",
    "codigo_snomedct": "3092008",
    "subtipo_agent": "Gram-positive cocci"
  }'
```

### Update Infectious Agent
```bash
curl -X PUT "http://127.0.0.1:8001/agentes_infecciosos/1" \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Updated Agent Name",
    "tipo_agente": "Updated Type"
  }'
```

### Delete Infectious Agent
```bash
curl -X DELETE "http://127.0.0.1:8001/agentes_infecciosos/1"
```

## 🔧 Development Features

### Backend Features
- **Automatic Database Creation**: Tables created on startup
- **CORS Configuration**: Frontend-backend communication enabled
- **Error Handling**: Comprehensive HTTP status codes
- **Type Safety**: SQLModel ensures type-safe database operations
- **Audit Fields**: Automatic created_at and updated_at timestamps
- **Validation**: Pydantic models for request/response validation

### Frontend Features
- **TypeScript Support**: Full type safety throughout the application
- **Reactive State Management**: Pinia stores with computed properties
- **Component Library**: PrimeVue components for consistent UI
- **Hot Module Replacement**: Instant updates during development
- **Vue DevTools**: Enhanced debugging capabilities
- **Route-based Code Splitting**: Optimized bundle sizes

## 📚 Additional Resources

- **Database Design**: See `dbdesign` file for complete schema specification
- **API Documentation**: Available at http://127.0.0.1:8001/docs when backend is running
- **Vue.js Documentation**: https://vuejs.org/
- **PrimeVue Components**: https://primevue.org/
- **FastAPI Documentation**: https://fastapi.tiangolo.com/

## 🚧 Future Enhancements

- **Additional Lookup Tables**: Extend frontend to manage all database tables
- **Advanced Filtering**: Search and filter capabilities across all tables
- **Data Export**: CSV/Excel export functionality
- **User Authentication**: Login and role-based access control
- **Bulk Operations**: Mass import/export of data
- **Audit Trail**: Track all data changes
- **Mobile App**: Native mobile application
- **Reporting**: Dashboard with charts and analytics

---

**Ready to use!** Start both servers and navigate to http://localhost:5173 to begin managing your medical database. 🎉