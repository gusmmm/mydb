from contextlib import asynccontextmanager
from datetime import date

from fastapi import Depends, FastAPI, HTTPException
from icecream import ic
from sqlmodel import Session, select

from src.db import get_session, init_db
from src.models.models import (
    AgenteQueimadura,
    AgenteQueimaduraCreate,
    Doente,
    DoenteCreate,
    Internamento,
    InternamentoCreate,
    LocalAnatomico,
    LocalAnatomicoCreate,
    MecanismoQueimadura,
    MecanismoQueimaduraCreate,
    OrigemDestino,
    OrigemDestinoCreate,
    Queimadura,
    QueimaduraCreate,
    SexoEnum,
    TipoAcidente,
    TipoAcidenteCreate,
    Trauma,
    TraumaCreate,
    TraumaTipo,
    TraumaTipoCreate,
)
from src.schemas.schemas import (
    DoentePatch,
    DoenteUpdate,
    LocalAnatomicoWithID,
    QueimaduraUpdate,
    QueimaduraWithID,
    TraumaTipoWithID,
    TraumaWithID,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)


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
