from sqlmodel import SQLModel, Field

class Ingressos(SQLModel, table = True):
    cod_regua: str = Field(primary_key=True)
    cod_empreendimento: str
    data_ingresso: str
    valor_ingressado: float

class Registros(SQLModel, table = True):
    cod_regua: str = Field(primary_key=True)
    cod_empreendimento: str
    data_ingresso: str
    valor_ingressado: float