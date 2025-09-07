from fastapi import FastAPI, HTTPException

from src.schemas.schemas import DoenteCreate, DoenteWithID, SexoEnum

app = FastAPI()

doentes = [
    {"id": 1, "nome": "Alice", "numero_processo": 30,
     "data_nascimento": "1990-01-01", "sexo": "F", "morada": "Rua A, 123"},
    {"id": 2, "nome": "Bob", "numero_processo": 45,
     "data_nascimento": "1985-05-12", "sexo": "M", "morada": "Rua B, 456"},
    {"id": 3, "nome": "Charlie", "numero_processo": 22,
     "data_nascimento": "1978-09-23", "sexo": "M", "morada": "Rua C, 789"},
    {"id": 4, "nome": "Diana", "numero_processo": 15,
     "data_nascimento": "1992-11-30", "sexo": "F", "morada": "Rua D, 101"},
    {"id": 5, "nome": "Eve", "numero_processo": 50,
     "data_nascimento": "1988-07-14", "sexo": "F", "morada": "Rua E, 202"},
]


@app.get("/")
async def index() -> dict[str, str]:
    return {"message": "Hello, World!"}


@app.get("/about")
async def about() -> dict[str, str]:
    return {"message": "Local database management system."}


@app.get("/doentes")
async def read_doentes(sexo: SexoEnum | None = None) -> list[DoenteWithID]:
    if sexo:
        result = [doente for doente in doentes
              if doente["sexo"].upper() == sexo.value.upper()]
        if not result:
            raise HTTPException(status_code=404,
                                detail="No doentes found with the specified sexo")
        return [DoenteWithID(**doente) for doente in result]
    return [
        DoenteWithID(**doente) for doente in doentes
    ]


@app.get("/doentes/{doente_id}")
async def read_doente(doente_id: int) -> DoenteWithID:
    for doente in doentes:
        if doente["id"] == doente_id:
            return DoenteWithID(**doente)
    raise HTTPException(status_code=404, detail="Doente not found")


@app.get("/doentes/numero_processo/{numero_processo}")
async def read_doente_by_numero_processo(numero_processo: int) -> DoenteWithID:
    for doente in doentes:
        if doente["numero_processo"] == numero_processo:
            return DoenteWithID(**doente)
    raise HTTPException(status_code=404, detail="Doente not found")


# @app.get("/doentes/sexo/{sexo}")
# async def read_doentes_by_sexo(sexo: SexoEnum) -> list[Doente]:
#     result = [doente for doente in doentes
#               if doente["sexo"].upper() == sexo.value.upper()]
#     if not result:
#         raise HTTPException(status_code=404,
#                             detail="No doentes found with the specified sexo")
#     return [Doente(**doente) for doente in result]

@app.post("/doentes", status_code=201)
async def create_doente(doente: DoenteCreate) -> DoenteWithID:
    new_id = max(doente["id"] for doente in doentes) + 1 if doentes else 1
    new_doente = DoenteWithID(id=new_id, **doente.model_dump()).model_dump()
    doentes.append(new_doente)
    return DoenteWithID(**new_doente)