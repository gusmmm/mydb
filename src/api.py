from contextlib import asynccontextmanager
from datetime import date

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from icecream import ic
from sqlmodel import Session, select

from src.db import get_session, init_db
from src.models.models import (
    AgenteInfeccioso,
    AgenteInfecciosoCreate,
    AgenteQueimadura,
    AgenteQueimaduraCreate,
    Antibiotico,
    AntibioticoCreate,
    Doente,
    DoenteCreate,
    DoenteMedicacao,
    DoenteMedicacaoCreate,
    DoentePatologia,
    DoentePatologiaCreate,
    IndicacaoAntibiotico,
    IndicacaoAntibioticoCreate,
    Infecao,
    InfecaoCreate,
    Internamento,
    InternamentoAntibiotico,
    InternamentoAntibioticoCreate,
    InternamentoCreate,
    InternamentoProcedimento,
    InternamentoProcedimentoCreate,
    LocalAnatomico,
    LocalAnatomicoCreate,
    MecanismoQueimadura,
    MecanismoQueimaduraCreate,
    Medicacao,
    MedicacaoCreate,
    OrigemDestino,
    OrigemDestinoCreate,
    Patologia,
    PatologiaCreate,
    Procedimento,
    ProcedimentoCreate,
    Queimadura,
    QueimaduraCreate,
    SexoEnum,
    TipoAcidente,
    TipoAcidenteCreate,
    TipoInfecao,
    TipoInfecaoCreate,
    Trauma,
    TraumaCreate,
    TraumaTipo,
    TraumaTipoCreate,
)
from src.schemas.schemas import (
    AgenteInfecciosoUpdate,
    AgenteInfecciosoWithID,
    AntibioticoWithID,
    DoenteMedicacaoWithID,
    DoentePatch,
    DoentePatologiaWithID,
    DoenteUpdate,
    IndicacaoAntibioticoWithID,
    InfecaoWithID,
    InternamentoAntibioticoWithID,
    InternamentoProcedimentoWithID,
    LocalAnatomicoWithID,
    MedicacaoWithID,
    InternamentoPatch,
    PatologiaWithID,
    ProcedimentoWithID,
    QueimaduraUpdate,
    QueimaduraWithID,
    TipoInfecaoWithID,
    TraumaTipoWithID,
    TraumaWithID,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],  # Vite default ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/')
async def index() -> dict[str, str]:
    return {'message': 'Hello, World!'}


@app.get('/about')
async def about() -> dict[str, str]:
    return {'message': 'Local database management system.'}


@app.get('/doentes')
async def read_doentes(
    sexo: SexoEnum | None = None, session: Session = Depends(get_session)
) -> list[Doente]:
    statement = select(Doente)
    if sexo:
        statement = statement.where(Doente.sexo == sexo)
    doentes = session.exec(statement).all()
    return list(doentes)


@app.get('/doentes/numero_processo/{numero_processo}')
async def read_doente_by_numero_processo(
    numero_processo: int, session: Session = Depends(get_session)
) -> Doente:
    statement = select(Doente).where(Doente.numero_processo == numero_processo)
    doente = session.exec(statement).first()
    if not doente:
        raise HTTPException(status_code=404, detail='Doente not found')
    return doente


@app.get('/doentes/{doente_id}')
async def read_doente_by_id(
    doente_id: int, session: Session = Depends(get_session)
) -> Doente:
    """Get a specific doente by ID."""
    ic(f'Getting doente with id: {doente_id}')
    doente = session.get(Doente, doente_id)
    if not doente:
        ic(f'Doente {doente_id} not found')
        raise HTTPException(status_code=404, detail='Doente not found')
    ic(f'Found doente: {doente.nome}')
    return doente


@app.put('/doentes/{doente_id}')
async def update_doente(
    doente_id: int,
    doente_update: DoenteUpdate,
    session: Session = Depends(get_session),
) -> Doente:
    """Full update of a doente (PUT - replaces all fields)."""
    ic(f'Full update of doente with id: {doente_id}')
    ic('Update data:', doente_update.model_dump())

    # Get the existing doente
    doente = session.get(Doente, doente_id)
    if not doente:
        ic(f'Doente {doente_id} not found for update')
        raise HTTPException(status_code=404, detail='Doente not found')

    # Update all fields from the update model
    update_data = doente_update.model_dump()
    for field, field_value in update_data.items():
        # Handle date field conversion
        if field == 'data_nascimento' and isinstance(field_value, str):
            converted_value = date.fromisoformat(field_value)
            setattr(doente, field, converted_value)
        else:
            setattr(doente, field, field_value)

    ic('Updated doente fields')

    # Commit changes
    session.add(doente)
    session.commit()
    session.refresh(doente)

    ic(f'Successfully updated doente {doente_id}')
    return doente


@app.patch('/doentes/{doente_id}')
async def patch_doente(
    doente_id: int,
    doente_patch: DoentePatch,
    session: Session = Depends(get_session),
) -> Doente:
    """Partial update of a doente (PATCH - updates only provided fields)."""
    ic(f'Partial update of doente with id: {doente_id}')
    ic('Patch data:', doente_patch.model_dump(exclude_unset=True))

    # Get the existing doente
    doente = session.get(Doente, doente_id)
    if not doente:
        ic(f'Doente {doente_id} not found for patch')
        raise HTTPException(status_code=404, detail='Doente not found')

    # Update only the fields that were provided (exclude_unset=True)
    update_data = doente_patch.model_dump(exclude_unset=True)
    for field, field_value in update_data.items():
        # Handle date field conversion
        if field == 'data_nascimento' and isinstance(field_value, str):
            converted_value = date.fromisoformat(field_value)
            setattr(doente, field, converted_value)
        else:
            setattr(doente, field, field_value)

    ic(f'Updated {len(update_data)} fields')

    # Commit changes
    session.add(doente)
    session.commit()
    session.refresh(doente)

    ic(f'Successfully patched doente {doente_id}')
    return doente


@app.delete('/doentes/{doente_id}')
async def delete_doente(
    doente_id: int, session: Session = Depends(get_session)
) -> dict[str, str]:
    """Delete a doente."""
    ic(f'Deleting doente with id: {doente_id}')

    # Get the existing doente
    doente = session.get(Doente, doente_id)
    if not doente:
        ic(f'Doente {doente_id} not found for deletion')
        raise HTTPException(status_code=404, detail='Doente not found')

    ic(f'Found doente to delete: {doente.nome}')

    # Delete the doente (cascade will handle related internamentos
    # if configured)
    session.delete(doente)
    session.commit()

    ic(f'Successfully deleted doente {doente_id}')
    return {'message': f'Doente {doente_id} deleted successfully'}


@app.get('/internamentos')
async def read_internamentos(
    session: Session = Depends(get_session),
) -> list[Internamento]:
    statement = select(Internamento)
    internamentos = session.exec(statement).all()
    return list(internamentos)


@app.get('/internamentos/{numero_internamento}')
async def read_internamento_by_numero(
    numero_internamento: int, session: Session = Depends(get_session)
) -> Internamento:
    statement = select(Internamento).where(
        Internamento.numero_internamento == numero_internamento
    )
    internamento = session.exec(statement).first()
    if not internamento:
        raise HTTPException(status_code=404, detail='Internamento not found')
    return internamento


@app.post('/internamentos', status_code=201)
async def create_internamento(
    internamento: InternamentoCreate, session: Session = Depends(get_session)
) -> Internamento:
    ic('Starting internamento creation')
    ic(
        'Internamento numero:',
        internamento.numero_internamento,
        'doente_id:',
        internamento.doente_id,
    )

    # Validate that the doente exists if doente_id is provided
    if internamento.doente_id:
        doente = session.get(Doente, internamento.doente_id)
        if not doente:
            raise HTTPException(status_code=404, detail='Doente not found')

    # Convert the InternamentoCreate to dict
    internamento_data = internamento.model_dump()

    # Create the internamento instance
    internamento_bd = Internamento(**internamento_data)

    ic('Created internamento instance', internamento_bd.numero_internamento)

    # Add and commit
    session.add(internamento_bd)
    session.commit()
    session.refresh(internamento_bd)

    ic('Committed internamento successfully', internamento_bd.id)

    return internamento_bd


@app.put('/internamentos/{internamento_id}')
async def update_internamento(
    internamento_id: int,
    internamento_update: InternamentoCreate,
    session: Session = Depends(get_session),
) -> Internamento:
    """Full update of an internamento (PUT)."""
    ic(f'Full update of internamento with id: {internamento_id}')
    internamento = session.get(Internamento, internamento_id)
    if not internamento:
        raise HTTPException(status_code=404, detail='Internamento not found')

    # Replace all updatable fields
    data = internamento_update.model_dump()
    for field, value in data.items():
        if field in {'data_entrada', 'data_alta', 'data_queimadura'} and isinstance(value, str):
            setattr(internamento, field, date.fromisoformat(value))
        else:
            setattr(internamento, field, value)

    session.add(internamento)
    session.commit()
    session.refresh(internamento)
    ic(f'Successfully updated internamento {internamento_id}')
    return internamento


@app.patch('/internamentos/{internamento_id}')
async def patch_internamento(
    internamento_id: int,
    internamento_patch: InternamentoPatch,
    session: Session = Depends(get_session),
) -> Internamento:
    """Partial update of an internamento (PATCH)."""
    ic(f'Partial update of internamento with id: {internamento_id}')
    ic('Patch data:', internamento_patch.model_dump(exclude_unset=True))

    internamento = session.get(Internamento, internamento_id)
    if not internamento:
        raise HTTPException(status_code=404, detail='Internamento not found')

    update_data = internamento_patch.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        # Convert ISO date strings
        if field in {'data_entrada', 'data_alta', 'data_queimadura'} and isinstance(value, str):
            setattr(internamento, field, date.fromisoformat(value))
        else:
            setattr(internamento, field, value)

    session.add(internamento)
    session.commit()
    session.refresh(internamento)
    ic(f'Successfully patched internamento {internamento_id}')
    return internamento


@app.delete('/internamentos/{internamento_id}')
async def delete_internamento(
    internamento_id: int, session: Session = Depends(get_session)
) -> dict[str, str]:
    """Delete an internamento."""
    ic(f'Deleting internamento with id: {internamento_id}')
    internamento = session.get(Internamento, internamento_id)
    if not internamento:
        raise HTTPException(status_code=404, detail='Internamento not found')

    session.delete(internamento)
    session.commit()
    ic(f'Successfully deleted internamento {internamento_id}')
    return {'message': f'Internamento {internamento_id} deleted successfully'}


@app.post('/doentes', status_code=201)
async def create_doente(
    doente: DoenteCreate, session: Session = Depends(get_session)
) -> Doente:
    ic('Starting doente creation')
    ic(doente.nome, doente.numero_processo, doente.sexo)
    ic(
        'Date type check - data_nascimento:',
        type(doente.data_nascimento),
        doente.data_nascimento,
    )

    # Create the doente instance
    doente_bd = Doente(
        nome=doente.nome,
        numero_processo=doente.numero_processo,
        data_nascimento=doente.data_nascimento,
        sexo=doente.sexo,
        morada=doente.morada,
    )

    ic('Created doente instance', doente_bd)

    # Add and flush to get the ID, but don't commit yet
    session.add(doente_bd)
    ic('Added doente to session')

    session.flush()  # This assigns the ID to doente_bd
    ic('Flushed session - doente ID:', doente_bd.id)

    # Now create internamentos with the correct doente_id
    if doente.internamentos:
        ic('Processing internamentos', len(doente.internamentos))
        for i, internamento in enumerate(doente.internamentos):
            ic(
                f'Creating internamento {i + 1}',
                internamento.numero_internamento,
                internamento.data_entrada,
            )
            ic(
                f'Internamento {i + 1} date types:',
                type(internamento.data_entrada),
                type(internamento.data_alta),
            )

            # Convert the InternamentoCreate to dict and add doente_id
            internamento_data = internamento.model_dump()
            internamento_data['doente_id'] = doente_bd.id

            internamento_bd = Internamento(**internamento_data)
            ic(
                f'Created internamento {i + 1} with doente_id:',
                internamento_bd.doente_id,
            )
            session.add(internamento_bd)
            ic(f'Added internamento {i + 1} to session')
    else:
        ic('No internamentos to create')

    # Commit all changes
    ic('Committing changes')
    session.commit()
    ic('Committed successfully')

    session.refresh(doente_bd)
    ic('Refreshed doente', doente_bd.id)

    return doente_bd


# TipoAcidente endpoints
@app.get('/tipos_acidente')
def read_tipos_acidente(
    session: Session = Depends(get_session),
) -> list[TipoAcidente]:
    """Get all tipos de acidente."""
    ic('Getting all tipos de acidente')
    tipos = session.exec(select(TipoAcidente)).all()
    ic(f'Found {len(tipos)} tipos de acidente')
    return list(tipos)


@app.get('/tipos_acidente/{tipo_id}')
def read_tipo_acidente(
    tipo_id: int, session: Session = Depends(get_session)
) -> TipoAcidente:
    """Get a specific tipo de acidente by ID."""
    ic(f'Getting tipo de acidente with id: {tipo_id}')
    tipo = session.get(TipoAcidente, tipo_id)
    if not tipo:
        ic(f'Tipo de acidente {tipo_id} not found')
        raise HTTPException(
            status_code=404, detail='Tipo de acidente not found'
        )
    ic(f'Found tipo de acidente: {tipo.acidente}')
    return tipo


@app.post('/tipos_acidente', status_code=201)
def create_tipo_acidente(
    tipo: TipoAcidenteCreate, session: Session = Depends(get_session)
) -> TipoAcidente:
    """Create a new tipo de acidente."""
    ic(f'Creating new tipo de acidente: {tipo.acidente}')

    tipo_bd = TipoAcidente(**tipo.model_dump())
    session.add(tipo_bd)
    session.commit()
    session.refresh(tipo_bd)

    ic(f'Created tipo de acidente with id: {tipo_bd.id}')
    return tipo_bd


# AgenteQueimadura endpoints
@app.get('/agentes_queimadura')
def read_agentes_queimadura(
    session: Session = Depends(get_session),
) -> list[AgenteQueimadura]:
    """Get all agentes de queimadura."""
    ic('Getting all agentes de queimadura')
    agentes = session.exec(select(AgenteQueimadura)).all()
    ic(f'Found {len(agentes)} agentes de queimadura')
    return list(agentes)


@app.get('/agentes_queimadura/{agente_id}')
def read_agente_queimadura(
    agente_id: int, session: Session = Depends(get_session)
) -> AgenteQueimadura:
    """Get a specific agente de queimadura by ID."""
    ic(f'Getting agente de queimadura with id: {agente_id}')
    agente = session.get(AgenteQueimadura, agente_id)
    if not agente:
        ic(f'Agente de queimadura {agente_id} not found')
        raise HTTPException(
            status_code=404, detail='Agente de queimadura not found'
        )
    ic(f'Found agente de queimadura: {agente.agente_queimadura}')
    return agente


@app.post('/agentes_queimadura', status_code=201)
def create_agente_queimadura(
    agente: AgenteQueimaduraCreate, session: Session = Depends(get_session)
) -> AgenteQueimadura:
    """Create a new agente de queimadura."""
    ic(f'Creating new agente de queimadura: {agente.agente_queimadura}')

    agente_bd = AgenteQueimadura(**agente.model_dump())
    session.add(agente_bd)
    session.commit()
    session.refresh(agente_bd)

    ic(f'Created agente de queimadura with id: {agente_bd.id}')
    return agente_bd


# MecanismoQueimadura endpoints
@app.get('/mecanismos_queimadura')
def read_mecanismos_queimadura(
    session: Session = Depends(get_session),
) -> list[MecanismoQueimadura]:
    """Get all mecanismos de queimadura."""
    ic('Getting all mecanismos de queimadura')
    mecanismos = session.exec(select(MecanismoQueimadura)).all()
    ic(f'Found {len(mecanismos)} mecanismos de queimadura')
    return list(mecanismos)


@app.get('/mecanismos_queimadura/{mecanismo_id}')
def read_mecanismo_queimadura(
    mecanismo_id: int, session: Session = Depends(get_session)
) -> MecanismoQueimadura:
    """Get a specific mecanismo de queimadura by ID."""
    ic(f'Getting mecanismo de queimadura with id: {mecanismo_id}')
    mecanismo = session.get(MecanismoQueimadura, mecanismo_id)
    if not mecanismo:
        ic(f'Mecanismo de queimadura {mecanismo_id} not found')
        raise HTTPException(
            status_code=404, detail='Mecanismo de queimadura not found'
        )
    ic(f'Found mecanismo de queimadura: {mecanismo.mecanismo_queimadura}')
    return mecanismo


@app.post('/mecanismos_queimadura', status_code=201)
def create_mecanismo_queimadura(
    mecanismo: MecanismoQueimaduraCreate,
    session: Session = Depends(get_session),
) -> MecanismoQueimadura:
    """Create a new mecanismo de queimadura."""
    ic(
        f'Creating new mecanismo de queimadura: '
        f'{mecanismo.mecanismo_queimadura}'
    )

    mecanismo_bd = MecanismoQueimadura(**mecanismo.model_dump())
    session.add(mecanismo_bd)
    session.commit()
    session.refresh(mecanismo_bd)

    ic(f'Created mecanismo de queimadura with id: {mecanismo_bd.id}')
    return mecanismo_bd


# OrigemDestino endpoints
@app.get('/origens_destino')
def read_origens_destino(
    session: Session = Depends(get_session),
) -> list[OrigemDestino]:
    """Get all origens e destinos."""
    ic('Getting all origens e destinos')
    origens = session.exec(select(OrigemDestino)).all()
    ic(f'Found {len(origens)} origens e destinos')
    return list(origens)


@app.get('/origens_destino/{origem_id}')
def read_origem_destino(
    origem_id: int, session: Session = Depends(get_session)
) -> OrigemDestino:
    """Get a specific origem/destino by ID."""
    ic(f'Getting origem/destino with id: {origem_id}')
    origem = session.get(OrigemDestino, origem_id)
    if not origem:
        ic(f'Origem/destino {origem_id} not found')
        raise HTTPException(status_code=404, detail='Origem/destino not found')
    ic(f'Found origem/destino: {origem.local}')
    return origem


@app.post('/origens_destino', status_code=201)
def create_origem_destino(
    origem: OrigemDestinoCreate, session: Session = Depends(get_session)
) -> OrigemDestino:
    """Create a new origem/destino."""
    ic(f'Creating new origem/destino: {origem.local}')

    origem_bd = OrigemDestino(**origem.model_dump())
    session.add(origem_bd)
    session.commit()
    session.refresh(origem_bd)

    ic(f'Created origem/destino with id: {origem_bd.id}')
    return origem_bd


# Queimaduras endpoints
@app.get('/queimaduras')
def get_all_queimaduras(
    session: Session = Depends(get_session),
) -> list[Queimadura]:
    """Get all queimaduras."""
    ic('Getting all queimaduras')
    statement = select(Queimadura)
    queimaduras = session.exec(statement).all()
    ic(f'Found {len(queimaduras)} queimaduras')
    return queimaduras


@app.get('/queimaduras/{queimadura_id}')
def get_queimadura_by_id(
    queimadura_id: int, session: Session = Depends(get_session)
) -> Queimadura:
    """Get a specific queimadura by ID."""
    ic(f'Getting queimadura with id: {queimadura_id}')
    queimadura = session.get(Queimadura, queimadura_id)
    if not queimadura:
        ic(f'Queimadura {queimadura_id} not found')
        raise HTTPException(status_code=404, detail='Queimadura not found')
    ic(f'Found queimadura for internamento: {queimadura.internamento_id}')
    return queimadura


@app.get('/internamentos/{internamento_id}/queimaduras')
def get_queimaduras_by_internamento(
    internamento_id: int, session: Session = Depends(get_session)
) -> list[Queimadura]:
    """Get all queimaduras for a specific internamento."""
    ic(f'Getting queimaduras for internamento: {internamento_id}')

    # First check if internamento exists
    internamento = session.get(Internamento, internamento_id)
    if not internamento:
        ic(f'Internamento {internamento_id} not found')
        raise HTTPException(status_code=404, detail='Internamento not found')

    statement = select(Queimadura).where(
        Queimadura.internamento_id == internamento_id
    )
    queimaduras = session.exec(statement).all()
    ic(
        f'Found {len(queimaduras)} queimaduras for '
        f'internamento {internamento_id}'
    )
    return queimaduras


@app.post('/queimaduras', status_code=201)
def create_queimadura(
    queimadura: QueimaduraCreate, session: Session = Depends(get_session)
) -> Queimadura:
    """Create a new queimadura."""
    ic(
        'Creating new queimadura for internamento: '
        + f'{queimadura.internamento_id}'
    )

    # Check if internamento exists
    internamento = session.get(Internamento, queimadura.internamento_id)
    if not internamento:
        ic(f'Internamento {queimadura.internamento_id} not found')
        raise HTTPException(status_code=404, detail='Internamento not found')

    queimadura_bd = Queimadura(**queimadura.model_dump())
    session.add(queimadura_bd)
    session.commit()
    session.refresh(queimadura_bd)

    ic(f'Created queimadura with id: {queimadura_bd.id}')
    return queimadura_bd
    return QueimaduraWithID(**queimadura_bd.model_dump())


@app.put('/queimaduras/{queimadura_id}')
def update_queimadura(
    queimadura_id: int,
    queimadura_update: QueimaduraUpdate,
    session: Session = Depends(get_session),
) -> QueimaduraWithID:
    """Update a queimadura."""
    ic(f'Updating queimadura with id: {queimadura_id}')

    queimadura = session.get(Queimadura, queimadura_id)
    if not queimadura:
        ic(f'Queimadura {queimadura_id} not found')
        raise HTTPException(status_code=404, detail='Queimadura not found')

    # Update only the fields that are provided
    update_data = queimadura_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(queimadura, field, value)

    session.add(queimadura)
    session.commit()
    session.refresh(queimadura)

    ic(f'Updated queimadura with id: {queimadura.id}')
    return QueimaduraWithID(**queimadura.model_dump())


@app.delete('/queimaduras/{queimadura_id}')
def delete_queimadura(
    queimadura_id: int, session: Session = Depends(get_session)
) -> dict[str, str]:
    """Delete a queimadura."""
    ic(f'Deleting queimadura with id: {queimadura_id}')

    queimadura = session.get(Queimadura, queimadura_id)
    if not queimadura:
        ic(f'Queimadura {queimadura_id} not found')
        raise HTTPException(status_code=404, detail='Queimadura not found')

    session.delete(queimadura)
    session.commit()

    ic(f'Deleted queimadura with id: {queimadura_id}')
    return {'message': 'Queimadura deleted successfully'}


# LocalAnatomico endpoints
@app.get('/locais_anatomicos')
def get_all_locais_anatomicos(
    session: Session = Depends(get_session),
) -> list[LocalAnatomico]:
    """Get all locais anatómicos."""
    ic('Getting all locais anatómicos')
    statement = select(LocalAnatomico)
    locais = session.exec(statement).all()
    ic(f'Found {len(locais)} locais anatómicos')
    return locais


@app.get('/locais_anatomicos/{local_id}')
def get_local_anatomico_by_id(
    local_id: int, session: Session = Depends(get_session)
) -> LocalAnatomico:
    """Get a specific local anatómico by ID."""
    ic(f'Getting local anatómico with id: {local_id}')
    local = session.get(LocalAnatomico, local_id)
    if not local:
        ic(f'Local anatómico {local_id} not found')
        raise HTTPException(
            status_code=404, detail='Local anatómico not found'
        )
    ic(f'Found local anatómico: {local.local_anatomico}')
    return local


@app.post('/locais_anatomicos')
def create_local_anatomico(
    local: LocalAnatomicoCreate, session: Session = Depends(get_session)
) -> LocalAnatomicoWithID:
    """Create a new local anatómico."""
    ic(f'Creating new local anatómico: {local.local_anatomico}')

    local_bd = LocalAnatomico(**local.model_dump())
    session.add(local_bd)
    session.commit()
    session.refresh(local_bd)

    ic(f'Created local anatómico with id: {local_bd.id}')
    return local_bd


# ============================================================================
# TraumaTipo Endpoints (Lookup Table)
# ============================================================================


@app.get('/tipos_trauma')
def get_all_tipos_trauma(
    session: Session = Depends(get_session),
) -> list[TraumaTipoWithID]:
    """Get all tipos de trauma."""
    ic('Getting all tipos de trauma')
    tipos_trauma = session.exec(select(TraumaTipo)).all()
    ic(f'Found {len(tipos_trauma)} tipos de trauma')
    return tipos_trauma


@app.get('/tipos_trauma/{tipo_trauma_id}')
def get_tipo_trauma(
    tipo_trauma_id: int, session: Session = Depends(get_session)
) -> TraumaTipoWithID:
    """Get a specific tipo de trauma by ID."""
    ic(f'Getting tipo de trauma with id: {tipo_trauma_id}')
    tipo_trauma = session.get(TraumaTipo, tipo_trauma_id)
    if not tipo_trauma:
        ic(f'Tipo de trauma {tipo_trauma_id} not found')
        raise HTTPException(
            status_code=404, detail='Tipo de trauma not found'
        )
    ic(f'Found tipo de trauma: {tipo_trauma.local} - {tipo_trauma.tipo}')
    return tipo_trauma


@app.post('/tipos_trauma')
def create_tipo_trauma(
    tipo_trauma: TraumaTipoCreate, session: Session = Depends(get_session)
) -> TraumaTipoWithID:
    """Create a new tipo de trauma."""
    ic(f'Creating new tipo de trauma: {tipo_trauma.local} - '
       f'{tipo_trauma.tipo}')

    tipo_trauma_bd = TraumaTipo(**tipo_trauma.model_dump())
    session.add(tipo_trauma_bd)
    session.commit()
    session.refresh(tipo_trauma_bd)

    ic(f'Created tipo de trauma with id: {tipo_trauma_bd.id}')
    return tipo_trauma_bd


# ============================================================================
# Trauma Endpoints
# ============================================================================


@app.get('/traumas')
def get_all_traumas(
    session: Session = Depends(get_session),
) -> list[TraumaWithID]:
    """Get all traumas."""
    ic('Getting all traumas')
    traumas = session.exec(select(Trauma)).all()
    ic(f'Found {len(traumas)} traumas')
    return traumas


@app.get('/traumas/{trauma_id}')
def get_trauma(
    trauma_id: int, session: Session = Depends(get_session)
) -> TraumaWithID:
    """Get a specific trauma by ID."""
    ic(f'Getting trauma with id: {trauma_id}')
    trauma = session.get(Trauma, trauma_id)
    if not trauma:
        ic(f'Trauma {trauma_id} not found')
        raise HTTPException(status_code=404, detail='Trauma not found')
    ic(f'Found trauma for internamento: {trauma.internamento_id}')
    return trauma


@app.post('/traumas')
def create_trauma(
    trauma: TraumaCreate, session: Session = Depends(get_session)
) -> TraumaWithID:
    """Create a new trauma."""
    ic(f'Creating new trauma for internamento: {trauma.internamento_id}')

    # Validate that internamento exists
    internamento_db = session.exec(
        select(Internamento).where(Internamento.id == trauma.internamento_id)
    ).first()
    if not internamento_db:
        ic(f'Internamento {trauma.internamento_id} not found')
        raise HTTPException(status_code=404, detail='Internamento not found')

    # Validate that tipo_local exists if provided
    if trauma.tipo_local:
        tipo_trauma_db = session.get(TraumaTipo, trauma.tipo_local)
        if not tipo_trauma_db:
            ic(f'Tipo de trauma {trauma.tipo_local} not found')
            raise HTTPException(
                status_code=404, detail='Tipo de trauma not found'
            )

    trauma_bd = Trauma(**trauma.model_dump())
    session.add(trauma_bd)
    session.commit()
    session.refresh(trauma_bd)

    ic(f'Created trauma with id: {trauma_bd.id}')
    return trauma_bd


@app.get('/internamentos/{internamento_id}/traumas')
def get_traumas_for_internamento(
    internamento_id: int, session: Session = Depends(get_session)
) -> list[TraumaWithID]:
    """Get all traumas for a specific internamento."""
    ic(f'Getting traumas for internamento: {internamento_id}')

    # Validate that internamento exists
    internamento_db = session.exec(
        select(Internamento).where(Internamento.id == internamento_id)
    ).first()
    if not internamento_db:
        ic(f'Internamento {internamento_id} not found')
        raise HTTPException(status_code=404, detail='Internamento not found')

    traumas = session.exec(
        select(Trauma).where(Trauma.internamento_id == internamento_id)
    ).all()
    ic(f'Found {len(traumas)} traumas for internamento {internamento_id}')
    return traumas


# AgenteInfeccioso endpoints
@app.post('/agentes_infecciosos', response_model=AgenteInfecciosoWithID)
def create_agente_infeccioso(
    agente: AgenteInfecciosoCreate, session: Session = Depends(get_session)
):
    ic(
        f'Creating new agente infeccioso: {agente.nome} - {agente.tipo_agente}'
    )

    agente_bd = AgenteInfeccioso(**agente.model_dump())
    session.add(agente_bd)
    session.commit()
    session.refresh(agente_bd)

    ic(f'Created agente infeccioso with id: {agente_bd.id}')
    return agente_bd


@app.get('/agentes_infecciosos', response_model=list[AgenteInfecciosoWithID])
def get_all_agentes_infecciosos(session: Session = Depends(get_session)):
    ic('Getting all agentes infecciosos')
    agentes = session.exec(select(AgenteInfeccioso)).all()
    ic(f'Found {len(agentes)} agentes infecciosos')
    return agentes


@app.get(
    '/agentes_infecciosos/{agente_id}', response_model=AgenteInfecciosoWithID
)
def get_agente_infeccioso(
    agente_id: int, session: Session = Depends(get_session)
):
    ic(f'Getting agente infeccioso with id: {agente_id}')
    agente = session.get(AgenteInfeccioso, agente_id)
    if not agente:
        ic(f'Agente infeccioso {agente_id} not found')
        raise HTTPException(
            status_code=404, detail='Agente infeccioso not found'
        )
    ic(f'Found agente infeccioso: {agente.nome} - {agente.tipo_agente}')
    return agente


@app.patch(
    '/agentes_infecciosos/{agente_id}', response_model=AgenteInfecciosoWithID
)
def update_agente_infeccioso(
    agente_id: int,
    agente_update: AgenteInfecciosoUpdate,
    session: Session = Depends(get_session)
):
    ic(f'Updating agente infeccioso with id: {agente_id}')

    # Get the existing agente
    agente = session.get(AgenteInfeccioso, agente_id)
    if not agente:
        ic(f'Agente infeccioso {agente_id} not found')
        raise HTTPException(
            status_code=404, detail='Agente infeccioso not found'
        )

    # Update only the fields that were provided (not None)
    update_data = agente_update.model_dump(exclude_unset=True)
    ic(f'Updating agente {agente_id} with data: {update_data}')

    for key, value in update_data.items():
        if hasattr(agente, key):
            setattr(agente, key, value)

    session.add(agente)
    session.commit()
    session.refresh(agente)

    ic(
        f'Successfully updated agente infeccioso: {agente.nome} - '
        f'{agente.tipo_agente}'
    )
    return agente


@app.delete('/agentes_infecciosos/{agente_id}')
def delete_agente_infeccioso(
    agente_id: int, session: Session = Depends(get_session)
):
    ic(f'Deleting agente infeccioso with id: {agente_id}')

    # Get the existing agente
    agente = session.get(AgenteInfeccioso, agente_id)
    if not agente:
        ic(f'Agente infeccioso {agente_id} not found')
        raise HTTPException(
            status_code=404, detail='Agente infeccioso not found'
        )

    ic(f'Found agente to delete: {agente.nome} - {agente.tipo_agente}')

    session.delete(agente)
    session.commit()

    ic(f'Successfully deleted agente infeccioso: {agente.nome}')
    return {'message': 'Agente infeccioso deleted successfully'}


# TipoInfecao endpoints
@app.post('/tipos_infeccao', response_model=TipoInfecaoWithID)
def create_tipo_infeccao(
    tipo: TipoInfecaoCreate, session: Session = Depends(get_session)
):
    ic(f'Creating new tipo de infeccao: {tipo.tipo_infeccao} - {tipo.local}')

    tipo_bd = TipoInfecao(**tipo.model_dump())
    session.add(tipo_bd)
    session.commit()
    session.refresh(tipo_bd)

    ic(f'Created tipo de infeccao with id: {tipo_bd.id}')
    return tipo_bd


@app.get('/tipos_infeccao', response_model=list[TipoInfecaoWithID])
def get_all_tipos_infeccao(session: Session = Depends(get_session)):
    ic('Getting all tipos de infeccao')
    tipos = session.exec(select(TipoInfecao)).all()
    ic(f'Found {len(tipos)} tipos de infeccao')
    return tipos


@app.get('/tipos_infeccao/{tipo_id}', response_model=TipoInfecaoWithID)
def get_tipo_infeccao(tipo_id: int, session: Session = Depends(get_session)):
    ic(f'Getting tipo de infeccao with id: {tipo_id}')
    tipo = session.get(TipoInfecao, tipo_id)
    if not tipo:
        ic(f'Tipo de infeccao {tipo_id} not found')
        raise HTTPException(
            status_code=404, detail='Tipo de infeccao not found'
        )
    ic(f'Found tipo de infeccao: {tipo.tipo_infeccao} - {tipo.local}')
    return tipo


# Infecao endpoints
@app.post('/infeccoes', response_model=InfecaoWithID)
def create_infecao(
    infecao: InfecaoCreate, session: Session = Depends(get_session)
):
    ic(f'Creating new infeccao for internamento: {infecao.internamento_id}')

    # Validate internamento exists
    internamento = session.get(Internamento, infecao.internamento_id)
    if not internamento:
        ic(f'Internamento {infecao.internamento_id} not found')
        raise HTTPException(
            status_code=404, detail='Internamento not found'
        )

    # Validate agente infeccioso if provided
    if infecao.agente:
        agente = session.get(AgenteInfeccioso, infecao.agente)
        if not agente:
            ic(f'Agente infeccioso {infecao.agente} not found')
            raise HTTPException(
                status_code=404, detail='Agente infeccioso not found'
            )

    # Validate tipo infeccao if provided
    if infecao.local_tipo_infecao:
        tipo = session.get(TipoInfecao, infecao.local_tipo_infecao)
        if not tipo:
            ic(f'Tipo de infeccao {infecao.local_tipo_infecao} not found')
            raise HTTPException(
                status_code=404, detail='Tipo de infeccao not found'
            )

    infecao_bd = Infecao(**infecao.model_dump())
    session.add(infecao_bd)
    session.commit()
    session.refresh(infecao_bd)

    ic(f'Created infeccao with id: {infecao_bd.id}')
    return infecao_bd


@app.get('/infeccoes', response_model=list[InfecaoWithID])
def get_all_infeccoes(session: Session = Depends(get_session)):
    ic('Getting all infeccoes')
    infeccoes = session.exec(select(Infecao)).all()
    ic(f'Found {len(infeccoes)} infeccoes')
    return infeccoes


@app.get('/infeccoes/{infecao_id}', response_model=InfecaoWithID)
def get_infecao(infecao_id: int, session: Session = Depends(get_session)):
    ic(f'Getting infeccao with id: {infecao_id}')
    infecao = session.get(Infecao, infecao_id)
    if not infecao:
        ic(f'Infeccao {infecao_id} not found')
        raise HTTPException(status_code=404, detail='Infeccao not found')
    ic(f'Found infeccao for internamento: {infecao.internamento_id}')
    return infecao


@app.get(
    '/internamentos/{internamento_id}/infeccoes',
    response_model=list[InfecaoWithID],
)
def get_infeccoes_by_internamento(
    internamento_id: int, session: Session = Depends(get_session)
):
    ic(f'Getting infeccoes for internamento: {internamento_id}')

    # Validate internamento exists
    internamento = session.get(Internamento, internamento_id)
    if not internamento:
        ic(f'Internamento {internamento_id} not found')
        raise HTTPException(
            status_code=404, detail='Internamento not found'
        )

    infeccoes = session.exec(
        select(Infecao).where(Infecao.internamento_id == internamento_id)
    ).all()
    ic(f'Found {len(infeccoes)} infeccoes for internamento {internamento_id}')
    return infeccoes


# Antibiotico endpoints
@app.post('/antibioticos', response_model=AntibioticoWithID)
def create_antibiotico(
    antibiotico: AntibioticoCreate, session: Session = Depends(get_session)
):
    ic(f'Creating antibiotico: {antibiotico.nome_antibiotico}')
    antibiotico_bd = Antibiotico.model_validate(antibiotico)
    session.add(antibiotico_bd)
    session.commit()
    session.refresh(antibiotico_bd)
    ic(f'Created antibiotico with id: {antibiotico_bd.id}')
    return antibiotico_bd


@app.get('/antibioticos', response_model=list[AntibioticoWithID])
def get_all_antibioticos(session: Session = Depends(get_session)):
    ic('Getting all antibioticos')
    antibioticos = session.exec(select(Antibiotico)).all()
    ic(f'Found {len(antibioticos)} antibioticos')
    return antibioticos


@app.get('/antibioticos/{antibiotico_id}', response_model=AntibioticoWithID)
def get_antibiotico(
    antibiotico_id: int, session: Session = Depends(get_session)
):
    ic(f'Getting antibiotico with id: {antibiotico_id}')
    antibiotico = session.get(Antibiotico, antibiotico_id)
    if not antibiotico:
        ic(f'Antibiotico {antibiotico_id} not found')
        raise HTTPException(status_code=404, detail='Antibiotico not found')
    ic(f'Found antibiotico: {antibiotico.nome_antibiotico}')
    return antibiotico


# IndicacaoAntibiotico endpoints
@app.post('/indicacoes_antibiotico', response_model=IndicacaoAntibioticoWithID)
def create_indicacao_antibiotico(
    indicacao: IndicacaoAntibioticoCreate,
    session: Session = Depends(get_session),
):
    ic(f'Creating indicacao antibiotico: {indicacao.indicacao}')
    indicacao_bd = IndicacaoAntibiotico.model_validate(indicacao)
    session.add(indicacao_bd)
    session.commit()
    session.refresh(indicacao_bd)
    ic(f'Created indicacao antibiotico with id: {indicacao_bd.id}')
    return indicacao_bd


@app.get(
    '/indicacoes_antibiotico', response_model=list[IndicacaoAntibioticoWithID]
)
def get_all_indicacoes_antibiotico(session: Session = Depends(get_session)):
    ic('Getting all indicacoes antibiotico')
    indicacoes = session.exec(select(IndicacaoAntibiotico)).all()
    ic(f'Found {len(indicacoes)} indicacoes antibiotico')
    return indicacoes


@app.get(
    '/indicacoes_antibiotico/{indicacao_id}',
    response_model=IndicacaoAntibioticoWithID,
)
def get_indicacao_antibiotico(
    indicacao_id: int, session: Session = Depends(get_session)
):
    ic(f'Getting indicacao antibiotico with id: {indicacao_id}')
    indicacao = session.get(IndicacaoAntibiotico, indicacao_id)
    if not indicacao:
        ic(f'Indicacao antibiotico {indicacao_id} not found')
        raise HTTPException(
            status_code=404, detail='Indicacao antibiotico not found'
        )
    ic(f'Found indicacao: {indicacao.indicacao}')
    return indicacao


# InternamentoAntibiotico endpoints
@app.post(
    '/internamentos_antibiotico', response_model=InternamentoAntibioticoWithID
)
def create_internamento_antibiotico(
    internamento_antibiotico: InternamentoAntibioticoCreate,
    session: Session = Depends(get_session),
):
    ic(
        f'Creating internamento antibiotico for internamento: '
        f'{internamento_antibiotico.internamento_id}'
    )

    # Validate internamento exists
    internamento = session.get(
        Internamento, internamento_antibiotico.internamento_id
    )
    if not internamento:
        ic(
            f'Internamento {internamento_antibiotico.internamento_id} '
            f'not found'
        )
        raise HTTPException(
            status_code=404, detail='Internamento not found'
        )

    # Validate antibiotico exists if provided
    if internamento_antibiotico.antibiotico:
        antibiotico = session.get(
            Antibiotico, internamento_antibiotico.antibiotico
        )
        if not antibiotico:
            ic(f'Antibiotico {internamento_antibiotico.antibiotico} not found')
            raise HTTPException(
                status_code=404, detail='Antibiotico not found'
            )

    # Validate indicacao exists if provided
    if internamento_antibiotico.indicacao:
        indicacao = session.get(
            IndicacaoAntibiotico, internamento_antibiotico.indicacao
        )
        if not indicacao:
            ic(f'Indicacao {internamento_antibiotico.indicacao} not found')
            raise HTTPException(
                status_code=404, detail='Indicacao antibiotico not found'
            )

    internamento_antibiotico_bd = InternamentoAntibiotico.model_validate(
        internamento_antibiotico
    )
    session.add(internamento_antibiotico_bd)
    session.commit()
    session.refresh(internamento_antibiotico_bd)
    ic(
        f'Created internamento antibiotico with id: '
        f'{internamento_antibiotico_bd.id}'
    )
    return internamento_antibiotico_bd


@app.get(
    '/internamentos_antibiotico',
    response_model=list[InternamentoAntibioticoWithID],
)
def get_all_internamentos_antibiotico(
    session: Session = Depends(get_session)
):
    ic('Getting all internamentos antibiotico')
    internamentos_antibiotico = session.exec(
        select(InternamentoAntibiotico)
    ).all()
    ic(f'Found {len(internamentos_antibiotico)} internamentos antibiotico')
    return internamentos_antibiotico


@app.get(
    '/internamentos_antibiotico/{internamento_antibiotico_id}',
    response_model=InternamentoAntibioticoWithID,
)
def get_internamento_antibiotico(
    internamento_antibiotico_id: int, session: Session = Depends(get_session)
):
    ic(
        f'Getting internamento antibiotico with id: '
        f'{internamento_antibiotico_id}'
    )
    internamento_antibiotico = session.get(
        InternamentoAntibiotico, internamento_antibiotico_id
    )
    if not internamento_antibiotico:
        ic(f'Internamento antibiotico {internamento_antibiotico_id} not found')
        raise HTTPException(
            status_code=404, detail='Internamento antibiotico not found'
        )
    ic(f'Found internamento antibiotico for internamento: '
       f'{internamento_antibiotico.internamento_id}')
    return internamento_antibiotico


@app.get(
    '/internamentos/{internamento_id}/antibioticos',
    response_model=list[InternamentoAntibioticoWithID],
)
def get_antibioticos_by_internamento(
    internamento_id: int, session: Session = Depends(get_session)
):
    ic(f'Getting antibioticos for internamento: {internamento_id}')

    # Validate internamento exists
    internamento = session.get(Internamento, internamento_id)
    if not internamento:
        ic(f'Internamento {internamento_id} not found')
        raise HTTPException(
            status_code=404, detail='Internamento not found'
        )

    internamentos_antibiotico = session.exec(
        select(InternamentoAntibiotico).where(
            InternamentoAntibiotico.internamento_id == internamento_id
        )
    ).all()
    ic(
        f'Found {len(internamentos_antibiotico)} antibioticos for '
        f'internamento {internamento_id}'
    )
    return internamentos_antibiotico


# Procedimento endpoints
@app.post('/procedimentos', response_model=ProcedimentoWithID)
def create_procedimento(
    procedimento: ProcedimentoCreate, session: Session = Depends(get_session)
):
    ic(f'Creating procedimento: {procedimento.nome_procedimento}')
    db_procedimento = Procedimento.model_validate(procedimento)
    session.add(db_procedimento)
    session.commit()
    session.refresh(db_procedimento)
    ic(f'Created procedimento with id: {db_procedimento.id}')
    return db_procedimento


@app.get('/procedimentos', response_model=list[ProcedimentoWithID])
def get_procedimentos(session: Session = Depends(get_session)):
    ic('Getting all procedimentos')
    procedimentos = session.exec(select(Procedimento)).all()
    ic(f'Found {len(procedimentos)} procedimentos')
    return procedimentos


@app.get('/procedimentos/{procedimento_id}', response_model=ProcedimentoWithID)
def get_procedimento(
    procedimento_id: int, session: Session = Depends(get_session)
):
    ic(f'Getting procedimento with id: {procedimento_id}')
    procedimento = session.get(Procedimento, procedimento_id)
    if not procedimento:
        ic(f'Procedimento {procedimento_id} not found')
        raise HTTPException(status_code=404, detail='Procedimento not found')
    ic(f'Found procedimento: {procedimento.nome_procedimento}')
    return procedimento


# InternamentoProcedimento endpoints
@app.post(
    '/internamentos_procedimento',
    response_model=InternamentoProcedimentoWithID
)
def create_internamento_procedimento(
    internamento_procedimento: InternamentoProcedimentoCreate,
    session: Session = Depends(get_session),
):
    ic(
        f'Creating internamento procedimento for internamento: '
        f'{internamento_procedimento.internamento_id}'
    )

    # Validate internamento exists
    internamento = session.get(
        Internamento, internamento_procedimento.internamento_id
    )
    if not internamento:
        internamento_id = internamento_procedimento.internamento_id
        ic(f'Internamento {internamento_id} not found')
        raise HTTPException(
            status_code=404, detail='Internamento not found'
        )

    # Validate procedimento exists if provided
    if internamento_procedimento.procedimento:
        procedimento = session.get(
            Procedimento, internamento_procedimento.procedimento
        )
        if not procedimento:
            procedimento_id = internamento_procedimento.procedimento
            ic(f'Procedimento {procedimento_id} not found')
            raise HTTPException(
                status_code=404, detail='Procedimento not found'
            )

    db_internamento_procedimento = InternamentoProcedimento.model_validate(
        internamento_procedimento
    )
    session.add(db_internamento_procedimento)
    session.commit()
    session.refresh(db_internamento_procedimento)
    ic(f'Created internamento procedimento with id: '
       f'{db_internamento_procedimento.id}')
    return db_internamento_procedimento


@app.get(
    '/internamentos_procedimento',
    response_model=list[InternamentoProcedimentoWithID],
)
def get_internamentos_procedimento(session: Session = Depends(get_session)):
    ic('Getting all internamentos procedimento')
    internamentos_procedimento = session.exec(
        select(InternamentoProcedimento)
    ).all()
    ic(f'Found {len(internamentos_procedimento)} internamentos procedimento')
    return internamentos_procedimento


@app.get(
    '/internamentos_procedimento/{internamento_procedimento_id}',
    response_model=InternamentoProcedimentoWithID,
)
def get_internamento_procedimento(
    internamento_procedimento_id: int, session: Session = Depends(get_session)
):
    ic(
        f'Getting internamento procedimento with id: '
        f'{internamento_procedimento_id}'
    )
    internamento_procedimento = session.get(
        InternamentoProcedimento, internamento_procedimento_id
    )
    if not internamento_procedimento:
        item_id = internamento_procedimento_id
        msg = f'Internamento procedimento {item_id} not found'
        ic(msg)
        raise HTTPException(
            status_code=404, detail='Internamento procedimento not found'
        )
    ic(f'Found internamento procedimento for internamento: '
       f'{internamento_procedimento.internamento_id}')
    return internamento_procedimento


@app.get(
    '/internamentos/{internamento_id}/procedimentos',
    response_model=list[InternamentoProcedimentoWithID],
)
def get_procedimentos_by_internamento(
    internamento_id: int, session: Session = Depends(get_session)
):
    ic(f'Getting procedimentos for internamento: {internamento_id}')

    # Validate internamento exists
    internamento = session.get(Internamento, internamento_id)
    if not internamento:
        ic(f'Internamento {internamento_id} not found')
        raise HTTPException(
            status_code=404, detail='Internamento not found'
        )

    internamentos_procedimento = session.exec(
        select(InternamentoProcedimento).where(
            InternamentoProcedimento.internamento_id == internamento_id
        )
    ).all()
    ic(
        f'Found {len(internamentos_procedimento)} procedimentos for '
        f'internamento {internamento_id}'
    )
    return internamentos_procedimento


# Patologia endpoints
@app.post('/patologias', response_model=PatologiaWithID)
def create_patologia(
    patologia: PatologiaCreate, session: Session = Depends(get_session)
):
    """Create a new patologia."""
    ic(f'Creating new patologia: {patologia.nome_patologia}')

    patologia_bd = Patologia(**patologia.model_dump())
    session.add(patologia_bd)
    session.commit()
    session.refresh(patologia_bd)

    ic(f'Created patologia with id: {patologia_bd.id}')
    return patologia_bd


@app.get('/patologias', response_model=list[PatologiaWithID])
def get_all_patologias(session: Session = Depends(get_session)):
    """Get all patologias."""
    ic('Getting all patologias')

    patologias = session.exec(select(Patologia)).all()
    ic(f'Found {len(patologias)} patologias')
    return patologias


@app.get('/patologias/{patologia_id}', response_model=PatologiaWithID)
def get_patologia_by_id(
    patologia_id: int, session: Session = Depends(get_session)
):
    """Get a specific patologia by ID."""
    ic(f'Getting patologia with id: {patologia_id}')

    patologia = session.get(Patologia, patologia_id)
    if not patologia:
        ic(f'Patologia {patologia_id} not found')
        raise HTTPException(
            status_code=404, detail='Patologia not found'
        )

    ic(f'Found patologia: {patologia.nome_patologia}')
    return patologia


# DoentePatologia endpoints
@app.post(
    '/doentes_patologia',
    response_model=DoentePatologiaWithID
)
def create_doente_patologia(
    doente_patologia: DoentePatologiaCreate,
    session: Session = Depends(get_session)
):
    """Create a new doente-patologia relationship."""
    ic(f'Creating doente patologia for doente: {doente_patologia.doente_id}')

    # Validate doente exists
    doente = session.get(Doente, doente_patologia.doente_id)
    if not doente:
        doente_id = doente_patologia.doente_id
        ic(f'Doente {doente_id} not found')
        raise HTTPException(
            status_code=404, detail='Doente not found'
        )

    # Validate patologia exists if provided
    if doente_patologia.patologia:
        patologia = session.get(Patologia, doente_patologia.patologia)
        if not patologia:
            patologia_id = doente_patologia.patologia
            ic(f'Patologia {patologia_id} not found')
            raise HTTPException(
                status_code=404, detail='Patologia not found'
            )

    doente_patologia_bd = DoentePatologia(**doente_patologia.model_dump())
    session.add(doente_patologia_bd)
    session.commit()
    session.refresh(doente_patologia_bd)

    ic(f'Created doente patologia with id: {doente_patologia_bd.id}')
    return doente_patologia_bd


@app.get('/doentes_patologia', response_model=list[DoentePatologiaWithID])
def get_all_doentes_patologia(session: Session = Depends(get_session)):
    """Get all doente-patologia relationships."""
    ic('Getting all doente patologia relationships')

    doentes_patologia = session.exec(select(DoentePatologia)).all()
    ic(f'Found {len(doentes_patologia)} doente patologia relationships')
    return doentes_patologia


@app.get(
    '/doentes_patologia/{doente_patologia_id}',
    response_model=DoentePatologiaWithID
)
def get_doente_patologia_by_id(
    doente_patologia_id: int, session: Session = Depends(get_session)
):
    """Get a specific doente-patologia relationship by ID."""
    ic(f'Getting doente patologia with id: {doente_patologia_id}')

    doente_patologia = session.get(DoentePatologia, doente_patologia_id)
    if not doente_patologia:
        item_id = doente_patologia_id
        msg = f'Doente patologia {item_id} not found'
        ic(msg)
        raise HTTPException(
            status_code=404, detail='Doente patologia not found'
        )

    ic(f'Found doente patologia for doente: {doente_patologia.doente_id}')
    return doente_patologia


@app.get(
    '/doentes/{doente_id}/patologias',
    response_model=list[DoentePatologiaWithID]
)
def get_patologias_by_doente(
    doente_id: int, session: Session = Depends(get_session)
):
    """Get all patologias for a specific doente."""
    ic(f'Getting patologias for doente: {doente_id}')

    # Validate doente exists
    doente = session.get(Doente, doente_id)
    if not doente:
        ic(f'Doente {doente_id} not found')
        raise HTTPException(
            status_code=404, detail='Doente not found'
        )

    doentes_patologia = session.exec(
        select(DoentePatologia).where(
            DoentePatologia.doente_id == doente_id
        )
    ).all()
    ic(
        f'Found {len(doentes_patologia)} patologias for '
        f'doente {doente_id}'
    )
    return doentes_patologia


# Medicacao endpoints
@app.post('/medicacoes', response_model=MedicacaoWithID)
def create_medicacao(
    medicacao: MedicacaoCreate, session: Session = Depends(get_session)
):
    """Create a new medicacao."""
    ic(f'Creating new medicacao: {medicacao.nome_medicacao}')

    medicacao_bd = Medicacao(**medicacao.model_dump())
    session.add(medicacao_bd)
    session.commit()
    session.refresh(medicacao_bd)

    ic(f'Created medicacao with id: {medicacao_bd.id}')
    return medicacao_bd


@app.get('/medicacoes', response_model=list[MedicacaoWithID])
def get_all_medicacoes(session: Session = Depends(get_session)):
    """Get all medicacoes."""
    ic('Getting all medicacoes')

    medicacoes = session.exec(select(Medicacao)).all()
    ic(f'Found {len(medicacoes)} medicacoes')
    return medicacoes


@app.get('/medicacoes/{medicacao_id}', response_model=MedicacaoWithID)
def get_medicacao_by_id(
    medicacao_id: int, session: Session = Depends(get_session)
):
    """Get a specific medicacao by ID."""
    ic(f'Getting medicacao with id: {medicacao_id}')

    medicacao = session.get(Medicacao, medicacao_id)
    if not medicacao:
        item_id = medicacao_id
        ic(f'Medicacao {item_id} not found')
        raise HTTPException(
            status_code=404, detail='Medicacao not found'
        )

    ic(f'Found medicacao: {medicacao.nome_medicacao}')
    return medicacao


# DoenteMedicacao endpoints
@app.post(
    '/doentes_medicacao',
    response_model=DoenteMedicacaoWithID
)
def create_doente_medicacao(
    doente_medicacao: DoenteMedicacaoCreate,
    session: Session = Depends(get_session)
):
    """Create a new doente-medicacao relationship."""
    ic(f'Creating doente medicacao for doente: {doente_medicacao.doente_id}')

    # Validate doente exists
    doente = session.get(Doente, doente_medicacao.doente_id)
    if not doente:
        ic(f'Doente {doente_medicacao.doente_id} not found')
        raise HTTPException(
            status_code=404, detail='Doente not found'
        )

    # Validate medicacao exists (if provided)
    if doente_medicacao.medicacao is not None:
        medicacao = session.get(Medicacao, doente_medicacao.medicacao)
        if not medicacao:
            ic(f'Medicacao {doente_medicacao.medicacao} not found')
            raise HTTPException(
                status_code=404, detail='Medicacao not found'
            )

    doente_medicacao_bd = DoenteMedicacao(**doente_medicacao.model_dump())
    session.add(doente_medicacao_bd)
    session.commit()
    session.refresh(doente_medicacao_bd)

    ic(f'Created doente medicacao with id: {doente_medicacao_bd.id}')
    return doente_medicacao_bd


@app.get('/doentes_medicacao', response_model=list[DoenteMedicacaoWithID])
def get_all_doentes_medicacao(session: Session = Depends(get_session)):
    """Get all doente-medicacao relationships."""
    ic('Getting all doente medicacao relationships')

    doentes_medicacao = session.exec(select(DoenteMedicacao)).all()
    ic(f'Found {len(doentes_medicacao)} doente medicacao relationships')
    return doentes_medicacao


@app.get(
    '/doentes_medicacao/{doente_medicacao_id}',
    response_model=DoenteMedicacaoWithID
)
def get_doente_medicacao_by_id(
    doente_medicacao_id: int, session: Session = Depends(get_session)
):
    """Get a specific doente-medicacao relationship by ID."""
    ic(f'Getting doente medicacao with id: {doente_medicacao_id}')

    doente_medicacao = session.get(DoenteMedicacao, doente_medicacao_id)
    if not doente_medicacao:
        item_id = doente_medicacao_id
        ic(f'Doente medicacao {item_id} not found')
        raise HTTPException(
            status_code=404, detail='Doente medicacao not found'
        )

    ic(f'Found doente medicacao for doente: {doente_medicacao.doente_id}')
    return doente_medicacao


@app.get(
    '/doentes/{doente_id}/medicacoes',
    response_model=list[DoenteMedicacaoWithID]
)
def get_medicacoes_by_doente(
    doente_id: int, session: Session = Depends(get_session)
):
    """Get all medicacoes for a specific doente."""
    ic(f'Getting medicacoes for doente: {doente_id}')

    # Validate doente exists
    doente = session.get(Doente, doente_id)
    if not doente:
        ic(f'Doente {doente_id} not found')
        raise HTTPException(
            status_code=404, detail='Doente not found'
        )

    doentes_medicacao = session.exec(
        select(DoenteMedicacao).where(
            DoenteMedicacao.doente_id == doente_id
        )
    ).all()
    ic(
        f'Found {len(doentes_medicacao)} medicacoes for '
        f'doente {doente_id}'
    )
    return doentes_medicacao
