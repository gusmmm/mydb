from enum import Enum

from pydantic import BaseModel, Field


class SexoEnum(str, Enum):
    M = 'M'
    F = 'F'


class GrauMaximoEnum(str, Enum):
    PRIMEIRO = 'PRIMEIRO'
    SEGUNDO = 'SEGUNDO'
    TERCEIRO = 'TERCEIRO'
    QUARTO = 'QUARTO'


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


class MecanismoQueimaduraBase(BaseModel):
    mecanismo_queimadura: str
    nota: str


class MecanismoQueimaduraCreate(MecanismoQueimaduraBase):
    pass


class MecanismoQueimaduraWithID(MecanismoQueimaduraBase):
    id: int


class OrigemDestinoBase(BaseModel):
    local: str
    int_ext: str
    descricao: str


class OrigemDestinoCreate(OrigemDestinoBase):
    pass


class OrigemDestinoWithID(OrigemDestinoBase):
    id: int


class LocalAnatomicoBase(BaseModel):
    local_anatomico: str
    regiao_anatomica: str | None = None


class LocalAnatomicoCreate(LocalAnatomicoBase):
    pass


class LocalAnatomicoWithID(LocalAnatomicoBase):
    id: int


class QueimaduraBase(BaseModel):
    internamento_id: int
    local_anatomico: int | None = None
    grau_maximo: GrauMaximoEnum | None = None
    notas: str | None = None


class QueimaduraCreate(QueimaduraBase):
    pass


class QueimaduraWithID(QueimaduraBase):
    id: int


class QueimaduraUpdate(BaseModel):
    internamento_id: int | None = None
    local_anatomico: int | None = None
    grau_maximo: GrauMaximoEnum | None = None
    notas: str | None = None


# Internamento partial update schema (used by PATCH)
class InternamentoPatch(BaseModel):
    numero_internamento: int | None = None
    doente_id: int | None = None

    # Dates as YYYY-MM-DD strings (validated by pattern)
    data_entrada: str | None = Field(
        default=None, pattern=r"^\d{4}-\d{2}-\d{2}$"
    )
    data_alta: str | None = Field(
        default=None, pattern=r"^\d{4}-\d{2}-\d{2}$"
    )
    data_queimadura: str | None = Field(
        default=None, pattern=r"^\d{4}-\d{2}-\d{2}$"
    )

    origem_entrada: int | None = None
    destino_alta: int | None = None
    ASCQ_total: int | None = None

    # Enum-like fields are accepted as strings here and coerced in API
    lesao_inalatoria: str | None = None
    mecanismo_queimadura: int | None = None
    agente_queimadura: int | None = None
    tipo_acidente: int | None = None
    incendio_florestal: bool | None = None
    contexto_violento: str | None = None
    suicidio_tentativa: bool | None = None
    fogueira_queda: bool | None = None
    lareira_queda: bool | None = None
    escarotomias_entrada: bool | None = None
    intubacao_OT: str | None = None
    VMI_dias: int | None = None
    VNI: bool | None = None


# TraumaTipo Schemas
class TraumaTipoBase(BaseModel):
    local: str
    tipo: str


class TraumaTipoCreate(TraumaTipoBase):
    pass


class TraumaTipoWithID(TraumaTipoBase):
    id: int


# Trauma Schemas
class TraumaBase(BaseModel):
    internamento_id: int
    tipo_local: int | None = None
    cirurgia_urgente: bool | None = None


class TraumaCreate(TraumaBase):
    pass


class TraumaWithID(TraumaBase):
    id: int


class TraumaUpdate(BaseModel):
    internamento_id: int | None = None
    tipo_local: int | None = None
    cirurgia_urgente: bool | None = None


# AgenteInfeccioso Schemas
class AgenteInfecciosoBase(BaseModel):
    nome: str
    tipo_agente: str
    codigo_snomedct: str | None = None
    subtipo_agent: str | None = None


class AgenteInfecciosoCreate(AgenteInfecciosoBase):
    pass


class AgenteInfecciosoUpdate(BaseModel):
    nome: str | None = None
    tipo_agente: str | None = None
    codigo_snomedct: str | None = None
    subtipo_agent: str | None = None


class AgenteInfecciosoWithID(AgenteInfecciosoBase):
    id: int


# TipoInfecao Schemas
class TipoInfecaoBase(BaseModel):
    tipo_infeccao: str
    local: str


class TipoInfecaoCreate(TipoInfecaoBase):
    pass


class TipoInfecaoWithID(TipoInfecaoBase):
    id: int


# Infecao Schemas
class InfecaoBase(BaseModel):
    internamento_id: int
    agente: int | None = None
    local_tipo_infecao: int | None = None
    nota: str | None = None


class InfecaoCreate(InfecaoBase):
    pass


class InfecaoWithID(InfecaoBase):
    id: int


# Antibiotico Schemas
class AntibioticoBase(BaseModel):
    nome_antibiotico: str
    classe_antibiotico: str | None = None
    codigo: str | None = None


class AntibioticoCreate(AntibioticoBase):
    pass


class AntibioticoWithID(AntibioticoBase):
    id: int


# IndicacaoAntibiotico Schemas
class IndicacaoAntibioticoBase(BaseModel):
    indicacao: str


class IndicacaoAntibioticoCreate(IndicacaoAntibioticoBase):
    pass


class IndicacaoAntibioticoWithID(IndicacaoAntibioticoBase):
    id: int


# InternamentoAntibiotico Schemas
class InternamentoAntibioticoBase(BaseModel):
    internamento_id: int
    antibiotico: int | None = None
    indicacao: int | None = None


class InternamentoAntibioticoCreate(InternamentoAntibioticoBase):
    pass


class InternamentoAntibioticoWithID(InternamentoAntibioticoBase):
    id: int


# Procedimento Schemas
class ProcedimentoBase(BaseModel):
    nome_procedimento: str
    tipo_procedimento: str | None = None


class ProcedimentoCreate(ProcedimentoBase):
    pass


class ProcedimentoWithID(ProcedimentoBase):
    id: int


# InternamentoProcedimento Schemas
class InternamentoProcedimentoBase(BaseModel):
    internamento_id: int
    procedimento: int | None = None


class InternamentoProcedimentoCreate(InternamentoProcedimentoBase):
    pass


class InternamentoProcedimentoWithID(InternamentoProcedimentoBase):
    id: int


# Patologia Schemas
class PatologiaBase(BaseModel):
    nome_patologia: str
    classe_patologia: str | None = None
    codigo: str | None = None


class PatologiaCreate(PatologiaBase):
    pass


class PatologiaWithID(PatologiaBase):
    id: int


# DoentePatologia Schemas
class DoentePatologiaBase(BaseModel):
    doente_id: int
    patologia: int | None = None
    nota: str | None = None


class DoentePatologiaCreate(DoentePatologiaBase):
    pass


class DoentePatologiaWithID(DoentePatologiaBase):
    id: int


# Medicacao Schemas
class MedicacaoBase(BaseModel):
    nome_medicacao: str
    classe_terapeutica: str | None = None
    codigo: str | None = None


class MedicacaoCreate(MedicacaoBase):
    pass


class MedicacaoWithID(MedicacaoBase):
    id: int


# DoenteMedicacao Schemas
class DoenteMedicacaoBase(BaseModel):
    doente_id: int
    medicacao: int | None = None
    nota: str | None = None


class DoenteMedicacaoCreate(DoenteMedicacaoBase):
    pass


class DoenteMedicacaoWithID(DoenteMedicacaoBase):
    id: int
