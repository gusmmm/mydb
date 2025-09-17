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
    doente_patologias: list['DoentePatologia'] = Relationship(
        back_populates='doente'
    )
    doente_medicacoes: list['DoenteMedicacao'] = Relationship(
        back_populates='doente'
    )


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
    infecoes: list['Infecao'] = Relationship(back_populates='internamento')
    internamento_antibioticos: list['InternamentoAntibiotico'] = Relationship(
        back_populates='internamento'
    )
    internamento_procedimentos: list[
        'InternamentoProcedimento'
    ] = Relationship(back_populates='internamento')


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


# AgenteInfeccioso tables
class AgenteInfecciosoBase(SQLModel):
    nome: str
    tipo_agente: str
    codigo_snomedct: str | None = None
    subtipo_agent: str | None = None


class AgenteInfecciosoCreate(AgenteInfecciosoBase):
    pass


class AgenteInfeccioso(AgenteInfecciosoBase, table=True):
    id: int = Field(default=None, primary_key=True)

    # Relationships
    infecoes: list['Infecao'] = Relationship(
        back_populates='agente_infeccioso'
    )


# TipoInfecao tables
class TipoInfecaoBase(SQLModel):
    tipo_infeccao: str
    local: str


class TipoInfecaoCreate(TipoInfecaoBase):
    pass


class TipoInfecao(TipoInfecaoBase, table=True):
    id: int = Field(default=None, primary_key=True)

    # Relationships
    infecoes: list['Infecao'] = Relationship(back_populates='tipo_infecao')


# Infecao tables
class InfecaoBase(SQLModel):
    internamento_id: int
    agente: int | None = None
    local_tipo_infecao: int | None = None
    nota: str | None = None


class InfecaoCreate(InfecaoBase):
    pass


class Infecao(InfecaoBase, table=True):
    id: int = Field(default=None, primary_key=True)
    internamento_id: int = Field(foreign_key='internamento.id')
    agente: int | None = Field(default=None, foreign_key='agenteinfeccioso.id')
    local_tipo_infecao: int | None = Field(
        default=None, foreign_key='tipoinfecao.id'
    )

    # Relationships
    internamento: Internamento = Relationship(back_populates='infecoes')
    agente_infeccioso: AgenteInfeccioso | None = Relationship(
        back_populates='infecoes'
    )
    tipo_infecao: TipoInfecao | None = Relationship(back_populates='infecoes')


# Antibiotic tables
class AntibioticoBase(SQLModel):
    nome_antibiotico: str
    classe_antibiotico: str | None = None
    codigo: str | None = None


class AntibioticoCreate(AntibioticoBase):
    pass


class Antibiotico(AntibioticoBase, table=True):
    id: int = Field(default=None, primary_key=True)

    # Relationships
    internamento_antibioticos: list['InternamentoAntibiotico'] = Relationship(
        back_populates='antibiotico_rel'
    )


class IndicacaoAntibioticoBase(SQLModel):
    indicacao: str


class IndicacaoAntibioticoCreate(IndicacaoAntibioticoBase):
    pass


class IndicacaoAntibiotico(IndicacaoAntibioticoBase, table=True):
    id: int = Field(default=None, primary_key=True)

    # Relationships
    internamento_antibioticos: list['InternamentoAntibiotico'] = Relationship(
        back_populates='indicacao_antibiotico_rel'
    )


class InternamentoAntibioticoBase(SQLModel):
    internamento_id: int
    antibiotico: int | None = None
    indicacao: int | None = None


class InternamentoAntibioticoCreate(InternamentoAntibioticoBase):
    pass


class InternamentoAntibiotico(InternamentoAntibioticoBase, table=True):
    id: int = Field(default=None, primary_key=True)
    internamento_id: int = Field(foreign_key='internamento.id')
    antibiotico: int | None = Field(
        default=None, foreign_key='antibiotico.id'
    )
    indicacao: int | None = Field(
        default=None, foreign_key='indicacaoantibiotico.id'
    )

    # Relationships
    internamento: Internamento = Relationship(
        back_populates='internamento_antibioticos'
    )
    antibiotico_rel: Antibiotico | None = Relationship(
        back_populates='internamento_antibioticos'
    )
    indicacao_antibiotico_rel: IndicacaoAntibiotico | None = Relationship(
        back_populates='internamento_antibioticos'
    )


# Procedimento models
class ProcedimentoBase(SQLModel):
    nome_procedimento: str
    tipo_procedimento: str | None = None


class ProcedimentoCreate(ProcedimentoBase):
    pass


class Procedimento(ProcedimentoBase, table=True):
    id: int = Field(default=None, primary_key=True)

    # Relationships
    internamento_procedimentos: list[
        'InternamentoProcedimento'
    ] = Relationship(back_populates='procedimento_rel')


# InternamentoProcedimento models
class InternamentoProcedimentoBase(SQLModel):
    internamento_id: int
    procedimento: int | None = None


class InternamentoProcedimentoCreate(InternamentoProcedimentoBase):
    pass


class InternamentoProcedimento(InternamentoProcedimentoBase, table=True):
    id: int = Field(default=None, primary_key=True)
    internamento_id: int = Field(foreign_key='internamento.id')
    procedimento: int | None = Field(
        default=None, foreign_key='procedimento.id'
    )

    # Relationships
    internamento: Internamento = Relationship(
        back_populates='internamento_procedimentos'
    )
    procedimento_rel: Procedimento | None = Relationship(
        back_populates='internamento_procedimentos'
    )


# Patologia models
class PatologiaBase(SQLModel):
    nome_patologia: str
    classe_patologia: str | None = None
    codigo: str | None = None


class PatologiaCreate(PatologiaBase):
    pass


class Patologia(PatologiaBase, table=True):
    id: int = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    last_modified: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={'onupdate': func.now()}
    )

    # Relationships
    doente_patologias: list['DoentePatologia'] = Relationship(
        back_populates='patologia_rel'
    )


# DoentePatologia models
class DoentePatologiaBase(SQLModel):
    doente_id: int
    patologia: int | None = None
    nota: str | None = None


class DoentePatologiaCreate(DoentePatologiaBase):
    pass


class DoentePatologia(DoentePatologiaBase, table=True):
    id: int = Field(default=None, primary_key=True)
    doente_id: int = Field(foreign_key='doente.id')
    patologia: int | None = Field(
        default=None, foreign_key='patologia.id'
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    last_modified: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={'onupdate': func.now()}
    )

    # Relationships
    doente: 'Doente' = Relationship(back_populates='doente_patologias')
    patologia_rel: Patologia | None = Relationship(
        back_populates='doente_patologias'
    )


# Medicacao models
class MedicacaoBase(SQLModel):
    nome_medicacao: str
    classe_terapeutica: str | None = None
    codigo: str | None = None


class MedicacaoCreate(MedicacaoBase):
    pass


class Medicacao(MedicacaoBase, table=True):
    id: int = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    last_modified: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={'onupdate': func.now()}
    )

    # Relationships
    doente_medicacoes: list['DoenteMedicacao'] = Relationship(
        back_populates='medicacao_rel'
    )


# DoenteMedicacao models
class DoenteMedicacaoBase(SQLModel):
    doente_id: int
    medicacao: int | None = None
    nota: str | None = None


class DoenteMedicacaoCreate(DoenteMedicacaoBase):
    pass


class DoenteMedicacao(DoenteMedicacaoBase, table=True):
    id: int = Field(default=None, primary_key=True)
    doente_id: int = Field(foreign_key='doente.id')
    medicacao: int | None = Field(
        default=None, foreign_key='medicacao.id'
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    last_modified: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={'onupdate': func.now()}
    )

    # Relationships
    doente: 'Doente' = Relationship(back_populates='doente_medicacoes')
    medicacao_rel: Medicacao | None = Relationship(
        back_populates='doente_medicacoes'
    )
