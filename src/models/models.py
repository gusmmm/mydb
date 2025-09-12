from datetime import date, datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import field_validator
from sqlalchemy import func
from sqlmodel import Field, Relationship, SQLModel


class SexoEnum(str, Enum):
    M = 'M'
    F = 'F'


class LesaoInalatorialEnum(str, Enum):
    SIM = 'SIM'
    NAO = 'NAO'
    SUSPEITA = 'SUSPEITA'


class ContextoViolentoEnum(str, Enum):
    SIM = 'SIM'
    NAO = 'NAO'
    SUSPEITA = 'SUSPEITA'


class IntubacaoOTEnum(str, Enum):
    SIM = 'SIM'
    NAO = 'NAO'
    OUTRO = 'OUTRO'


class GrauMaximoEnum(str, Enum):
    PRIMEIRO = 'PRIMEIRO'
    SEGUNDO = 'SEGUNDO'
    TERCEIRO = 'TERCEIRO'
    QUARTO = 'QUARTO'


class TipoAcidenteBase(SQLModel):
    acidente: str
    tipo_acidente: str


class TipoAcidenteCreate(TipoAcidenteBase):
    pass


class TipoAcidente(TipoAcidenteBase, table=True):
    id: int = Field(default=None, primary_key=True)

    # Relationships
    internamentos: list['Internamento'] = Relationship(
        back_populates='tipo_acidente_ref'
    )


class AgenteQueimaduraBase(SQLModel):
    agente_queimadura: str
    nota: str


class AgenteQueimaduraCreate(AgenteQueimaduraBase):
    pass


class AgenteQueimadura(AgenteQueimaduraBase, table=True):
    id: int = Field(default=None, primary_key=True)

    # Relationships
    internamentos: list['Internamento'] = Relationship(
        back_populates='agente_queimadura_ref'
    )


class MecanismoQueimaduraBase(SQLModel):
    mecanismo_queimadura: str
    nota: str


class MecanismoQueimaduraCreate(MecanismoQueimaduraBase):
    pass


class MecanismoQueimadura(MecanismoQueimaduraBase, table=True):
    id: int = Field(default=None, primary_key=True)

    # Relationships
    internamentos: list['Internamento'] = Relationship(
        back_populates='mecanismo_queimadura_ref'
    )


class IntExtEnum(str, Enum):
    INTERNO = 'INTERNO'
    EXTERNO = 'EXTERNO'
    OUTRO = 'OUTRO'


class OrigemDestinoBase(SQLModel):
    local: str
    int_ext: IntExtEnum
    descricao: str


class OrigemDestinoCreate(OrigemDestinoBase):
    pass


class OrigemDestino(OrigemDestinoBase, table=True):
    id: int = Field(default=None, primary_key=True)

    # Relationships for origem_entrada
    internamentos_origem: list['Internamento'] = Relationship(
        back_populates='origem_entrada_ref',
        sa_relationship_kwargs={
            'foreign_keys': '[Internamento.origem_entrada]'
        },
    )

    # Relationships for destino_alta
    internamentos_destino: list['Internamento'] = Relationship(
        back_populates='destino_alta_ref',
        sa_relationship_kwargs={'foreign_keys': '[Internamento.destino_alta]'},
    )


class DoenteBase(SQLModel):
    nome: str
    numero_processo: int = Field(unique=True)
    data_nascimento: date | None = None
    sexo: SexoEnum
    morada: str

    @field_validator('data_nascimento', mode='before')
    @classmethod
    def parse_date_nascimento(cls, v):
        if isinstance(v, str):
            return date.fromisoformat(v)
        return v


class DoenteCreate(DoenteBase):
    internamentos: list['InternamentoCreate'] | None = None


class Doente(DoenteBase, table=True):
    id: int = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={'server_default': func.now()},
    )
    last_modified: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={
            'server_default': func.now(),
            'onupdate': func.now(),
        },
    )
    internamentos: list['Internamento'] = Relationship(back_populates='doente')


class InternamentoBase(SQLModel):
    numero_internamento: int = Field(unique=True)
    data_entrada: date | None = None
    data_alta: date | None = None
    data_queimadura: date | None = None
    origem_entrada: int | None = Field(
        default=None, foreign_key='origemdestino.id'
    )
    destino_alta: int | None = Field(
        default=None, foreign_key='origemdestino.id'
    )
    ASCQ_total: int | None = None
    lesao_inalatoria: LesaoInalatorialEnum | None = None
    mecanismo_queimadura: int | None = Field(
        default=None, foreign_key='mecanismoqueimadura.id'
    )
    agente_queimadura: int | None = Field(
        default=None, foreign_key='agentequeimadura.id'
    )
    tipo_acidente: int | None = Field(
        default=None, foreign_key='tipoacidente.id'
    )
    incendio_florestal: bool | None = None
    contexto_violento: ContextoViolentoEnum | None = None
    suicidio_tentativa: bool | None = None
    fogueira_queda: bool | None = None
    lareira_queda: bool | None = None
    escarotomias_entrada: bool | None = None
    intubacao_OT: IntubacaoOTEnum | None = None
    VMI_dias: int | None = None
    VNI: bool | None = None
    doente_id: int | None = Field(foreign_key='doente.id')

    @field_validator(
        'data_entrada', 'data_alta', 'data_queimadura', mode='before'
    )
    @classmethod
    def parse_dates(cls, v):
        if isinstance(v, str):
            return date.fromisoformat(v)
        return v


class InternamentoCreate(InternamentoBase):
    # Optional for creation, will be set by API
    doente_id: Optional[int] = None


class Internamento(InternamentoBase, table=True):
    id: int = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={'server_default': func.now()},
    )
    last_modified: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={
            'server_default': func.now(),
            'onupdate': func.now(),
        },
    )

    # Relationships
    doente: Doente = Relationship(back_populates='internamentos')
    tipo_acidente_ref: TipoAcidente | None = Relationship(
        back_populates='internamentos'
    )
    agente_queimadura_ref: AgenteQueimadura | None = Relationship(
        back_populates='internamentos'
    )
    mecanismo_queimadura_ref: MecanismoQueimadura | None = Relationship(
        back_populates='internamentos'
    )
    origem_entrada_ref: OrigemDestino | None = Relationship(
        back_populates='internamentos_origem',
        sa_relationship_kwargs={
            'foreign_keys': '[Internamento.origem_entrada]'
        },
    )
    destino_alta_ref: OrigemDestino | None = Relationship(
        back_populates='internamentos_destino',
        sa_relationship_kwargs={'foreign_keys': '[Internamento.destino_alta]'},
    )
    queimaduras: list['Queimadura'] = Relationship(
        back_populates='internamento'
    )
    traumas: list['Trauma'] = Relationship(back_populates='internamento')


class LocalAnatomicoBase(SQLModel):
    local_anatomico: str
    regiao_anatomica: str | None = None


class LocalAnatomicoCreate(LocalAnatomicoBase):
    pass


class LocalAnatomico(LocalAnatomicoBase, table=True):
    id: int = Field(default=None, primary_key=True)

    # Relationships
    queimaduras: list['Queimadura'] = Relationship(
        back_populates='local_anatomico_ref'
    )


class QueimaduraBase(SQLModel):
    internamento_id: int = Field(foreign_key='internamento.id')
    local_anatomico: int | None = Field(
        default=None, foreign_key='localanatomico.id'
    )
    grau_maximo: GrauMaximoEnum | None = None
    notas: str | None = None


class QueimaduraCreate(QueimaduraBase):
    pass


class Queimadura(QueimaduraBase, table=True):
    id: int = Field(default=None, primary_key=True)

    # Relationships
    internamento: Internamento = Relationship(back_populates='queimaduras')
    local_anatomico_ref: LocalAnatomico | None = Relationship(
        back_populates='queimaduras'
    )


# TraumaTipo Model (Lookup Table)
class TraumaTipoBase(SQLModel):
    local: str
    tipo: str


class TraumaTipoCreate(TraumaTipoBase):
    pass


class TraumaTipo(TraumaTipoBase, table=True):
    id: int = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    last_updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={'onupdate': func.now()},
    )

    # Relationships
    traumas: list['Trauma'] = Relationship(back_populates='trauma_tipo')


# Trauma Model
class TraumaBase(SQLModel):
    internamento_id: int = Field(foreign_key='internamento.id')
    tipo_local: int | None = Field(default=None, foreign_key='traumatipo.id')
    cirurgia_urgente: bool | None = None


class TraumaCreate(TraumaBase):
    pass


class Trauma(TraumaBase, table=True):
    id: int = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    last_updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={'onupdate': func.now()},
    )

    # Relationships
    internamento: Internamento = Relationship(back_populates='traumas')
    trauma_tipo: TraumaTipo | None = Relationship(back_populates='traumas')
