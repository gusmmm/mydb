from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from icecream import ic
from sqlmodel import Session, select

from src.db import get_session, init_db
from src.models.models import Doente, DoenteCreate, Internamento, InternamentoCreate, SexoEnum


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def index() -> dict[str, str]:
    return {"message": "Hello, World!"}


@app.get("/about")
async def about() -> dict[str, str]:
    return {"message": "Local database management system."}


@app.get("/doentes")
async def read_doentes(
    sexo: SexoEnum | None = None,
    session: Session = Depends(get_session)
) -> list[Doente]:
    statement = select(Doente)
    if sexo:
        statement = statement.where(Doente.sexo == sexo)
    doentes = session.exec(statement).all()
    return list(doentes)


@app.get("/doentes/numero_processo/{numero_processo}")
async def read_doente_by_numero_processo(
    numero_processo: int,
    session: Session = Depends(get_session)
) -> Doente:
    statement = select(Doente).where(Doente.numero_processo == numero_processo)
    doente = session.exec(statement).first()
    if not doente:
        raise HTTPException(status_code=404, detail="Doente not found")
    return doente


@app.get("/internamentos")
async def read_internamentos(
    session: Session = Depends(get_session)
) -> list[Internamento]:
    statement = select(Internamento)
    internamentos = session.exec(statement).all()
    return list(internamentos)


@app.get("/internamentos/{numero_internamento}")
async def read_internamento_by_numero(
    numero_internamento: int,
    session: Session = Depends(get_session)
) -> Internamento:
    statement = select(Internamento).where(Internamento.numero_internamento == numero_internamento)
    internamento = session.exec(statement).first()
    if not internamento:
        raise HTTPException(status_code=404, detail="Internamento not found")
    return internamento


@app.post("/internamentos", status_code=201)
async def create_internamento(
    internamento: InternamentoCreate,
    session: Session = Depends(get_session)
) -> Internamento:
    ic("Starting internamento creation")
    ic("Internamento numero:", internamento.numero_internamento, "doente_id:", internamento.doente_id)
    
    # Validate that the doente exists if doente_id is provided
    if internamento.doente_id:
        doente = session.get(Doente, internamento.doente_id)
        if not doente:
            raise HTTPException(status_code=404, detail="Doente not found")
    
    # Convert the InternamentoCreate to dict
    internamento_data = internamento.model_dump()
    
    # Create the internamento instance
    internamento_bd = Internamento(**internamento_data)
    
    ic("Created internamento instance", internamento_bd.numero_internamento)
    
    # Add and commit
    session.add(internamento_bd)
    session.commit()
    session.refresh(internamento_bd)
    
    ic("Committed internamento successfully", internamento_bd.id)
    
    return internamento_bd


@app.post("/doentes", status_code=201)
async def create_doente(
    doente: DoenteCreate,
    session: Session = Depends(get_session)
) -> Doente:
    ic("Starting doente creation")
    ic(doente.nome, doente.numero_processo, doente.sexo)
    ic("Date type check - data_nascimento:", type(doente.data_nascimento), doente.data_nascimento)
    
    # Create the doente instance
    doente_bd = Doente(
        nome=doente.nome,
        numero_processo=doente.numero_processo,
        data_nascimento=doente.data_nascimento,
        sexo=doente.sexo,
        morada=doente.morada
    )
    
    ic("Created doente instance", doente_bd)

    # Add and flush to get the ID, but don't commit yet
    session.add(doente_bd)
    ic("Added doente to session")

    session.flush()  # This assigns the ID to doente_bd
    ic("Flushed session - doente ID:", doente_bd.id)

    # Now create internamentos with the correct doente_id
    if doente.internamentos:
        ic("Processing internamentos", len(doente.internamentos))
        for i, internamento in enumerate(doente.internamentos):
            ic(f"Creating internamento {i + 1}",
               internamento.numero_internamento, internamento.data_entrada)
            ic(f"Internamento {i + 1} date types:", 
               type(internamento.data_entrada), type(internamento.data_alta))
            
            # Convert the InternamentoCreate to dict and add doente_id
            internamento_data = internamento.model_dump()
            internamento_data['doente_id'] = doente_bd.id
            
            internamento_bd = Internamento(**internamento_data)
            ic(f"Created internamento {i + 1} with doente_id:",
               internamento_bd.doente_id)
            session.add(internamento_bd)
            ic(f"Added internamento {i + 1} to session")
    else:
        ic("No internamentos to create")

    # Commit all changes
    ic("Committing changes")
    session.commit()
    ic("Committed successfully")

    session.refresh(doente_bd)
    ic("Refreshed doente", doente_bd.id)

    return doente_bd
