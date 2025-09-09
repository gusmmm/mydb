from enum import Enum

from pydantic import BaseModel, Field


class SexoEnum(str, Enum):
    M = "M"
    F = "F"


class DoenteBase(BaseModel):
    nome: str
    numero_processo: int
    data_nascimento: str = Field(pattern=r'^\d{4}-\d{2}-\d{2}$')
    sexo: SexoEnum
    morada: str


class DoenteCreate(DoenteBase):
    pass


class DoenteWithID(DoenteBase):
    id: int


class DoenteUpdate(BaseModel):
    nome: str
    numero_processo: int
    data_nascimento: str = Field(pattern=r'^\d{4}-\d{2}-\d{2}$')
    sexo: SexoEnum
    morada: str


class DoentePatch(BaseModel):
    nome: str | None = None
    numero_processo: int | None = None
    data_nascimento: str | None = Field(
        default=None, pattern=r'^\d{4}-\d{2}-\d{2}$'
    )
    sexo: SexoEnum | None = None
    morada: str | None = None


class TipoAcidenteBase(BaseModel):
    acidente: str
    tipo_acidente: str


class TipoAcidenteCreate(TipoAcidenteBase):
    pass


class TipoAcidenteWithID(TipoAcidenteBase):
    id: int


class AgenteQueimaduraBase(BaseModel):
    agente_queimadura: str
    nota: str


class AgenteQueimaduraCreate(AgenteQueimaduraBase):
    pass


class AgenteQueimaduraWithID(AgenteQueimaduraBase):
    id: int
