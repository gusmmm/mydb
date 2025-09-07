from enum import Enum

from sqlmodel import Field, Relationship, SQLModel


class SexoEnum(str, Enum):
    M = "M"
    F = "F"


class DoenteBase(SQLModel):
    nome: str
    numero_processo: int
    data_nascimento: str
    sexo: SexoEnum
    morada: str

class DoenteCreate(DoenteBase):
    internamentos: list["Internamento"] | None = None

class Doente(DoenteBase, table=True):
    id: int = Field(default=None, primary_key=True)
    internamentos: list["Internamento"] = Relationship(back_populates="doente")


class InternamentoBase(SQLModel):
    numero_internamento: int
    data_entrada: str | None = None
    data_alta: str | None = None
    doente_id: int | None = Field(foreign_key="doente.id")


class Internamento(InternamentoBase, table=True):
    id: int = Field(default=None, primary_key=True)
    doente: Doente = Relationship(back_populates="internamentos")
