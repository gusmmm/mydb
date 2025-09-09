from datetime import date, datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import field_validator
from sqlalchemy import func
from sqlmodel import Field, Relationship, SQLModel


class SexoEnum(str, Enum):
    M = "M"
    F = "F"


class LesaoInalatorialEnum(str, Enum):
    SIM = "SIM"
    NAO = "NAO"
    SUSPEITA = "SUSPEITA"


class ContextoViolentoEnum(str, Enum):
    SIM = "SIM"
    NAO = "NAO"
    SUSPEITA = "SUSPEITA"


class IntubacaoOTEnum(str, Enum):
    SIM = "SIM"
    NAO = "NAO"
    OUTRO = "OUTRO"


class TipoAcidenteBase(SQLModel):
    acidente: str
    tipo_acidente: str


class TipoAcidenteCreate(TipoAcidenteBase):
    pass


class TipoAcidente(TipoAcidenteBase, table=True):
    id: int = Field(default=None, primary_key=True)
    
    # Relationships
    internamentos: list["Internamento"] = Relationship(back_populates="tipo_acidente_ref")


class AgenteQueimaduraBase(SQLModel):
    agente_queimadura: str
    nota: str


class AgenteQueimaduraCreate(AgenteQueimaduraBase):
    pass


class AgenteQueimadura(AgenteQueimaduraBase, table=True):
    id: int = Field(default=None, primary_key=True)
    
    # Relationships
    internamentos: list["Internamento"] = Relationship(back_populates="agente_queimadura_ref")


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
    internamentos: list["InternamentoCreate"] | None = None


class Doente(DoenteBase, table=True):
    id: int = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), sa_column_kwargs={"server_default": func.now()})
    last_modified: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), sa_column_kwargs={"server_default": func.now(), "onupdate": func.now()})
    internamentos: list["Internamento"] = Relationship(back_populates="doente")


class InternamentoBase(SQLModel):
    numero_internamento: int = Field(unique=True)
    data_entrada: date | None = None
    data_alta: date | None = None
    data_queimadura: date | None = None
    origem_entrada: int | None = None
    destino_alta: int | None = None
    ASCQ_total: int | None = None
    lesao_inalatoria: LesaoInalatorialEnum | None = None
    mecanismo_queimadura: int | None = None
    agente_queimadura: int | None = Field(default=None, foreign_key="agentequeimadura.id")
    tipo_acidente: int | None = Field(default=None, foreign_key="tipoacidente.id")
    incendio_florestal: bool | None = None
    contexto_violento: ContextoViolentoEnum | None = None
    suicidio_tentativa: bool | None = None
    fogueira_queda: bool | None = None
    lareira_queda: bool | None = None
    escarotomias_entrada: bool | None = None
    intubacao_OT: IntubacaoOTEnum | None = None
    VMI_dias: int | None = None
    VNI: bool | None = None
    doente_id: int | None = Field(foreign_key="doente.id")

    @field_validator('data_entrada', 'data_alta', 'data_queimadura', mode='before')
    @classmethod
    def parse_dates(cls, v):
        if isinstance(v, str):
            return date.fromisoformat(v)
        return v


class InternamentoCreate(InternamentoBase):
    doente_id: Optional[int] = None  # Optional for creation, will be set by API


class Internamento(InternamentoBase, table=True):
    id: int = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), sa_column_kwargs={"server_default": func.now()})
    last_modified: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), sa_column_kwargs={"server_default": func.now(), "onupdate": func.now()})
    
    # Relationships
    doente: Doente = Relationship(back_populates="internamentos")
    tipo_acidente_ref: TipoAcidente | None = Relationship(back_populates="internamentos")
    agente_queimadura_ref: AgenteQueimadura | None = Relationship(back_populates="internamentos")
