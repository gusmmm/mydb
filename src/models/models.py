from datetime import date
from enum import Enum
from typing import Optional

from pydantic import field_validator
from sqlmodel import Field, Relationship, SQLModel


class SexoEnum(str, Enum):
    M = "M"
    F = "F"


class DoenteBase(SQLModel):
    nome: str
    numero_processo: int
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
    internamentos: list["Internamento"] = Relationship(back_populates="doente")


class InternamentoBase(SQLModel):
    numero_internamento: int
    data_entrada: date | None = None
    data_alta: date | None = None
    doente_id: int | None = Field(foreign_key="doente.id")

    @field_validator('data_entrada', 'data_alta', mode='before')
    @classmethod
    def parse_dates(cls, v):
        if isinstance(v, str):
            return date.fromisoformat(v)
        return v


class InternamentoCreate(InternamentoBase):
    doente_id: Optional[int] = None  # Optional for creation, will be set by API


class Internamento(InternamentoBase, table=True):
    id: int = Field(default=None, primary_key=True)
    doente: Doente = Relationship(back_populates="internamentos")
