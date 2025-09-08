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


class TipoAcidenteBase(BaseModel):
    acidente: str
    tipo_acidente: str


class TipoAcidenteCreate(TipoAcidenteBase):
    pass


class TipoAcidenteWithID(TipoAcidenteBase):
    id: int
