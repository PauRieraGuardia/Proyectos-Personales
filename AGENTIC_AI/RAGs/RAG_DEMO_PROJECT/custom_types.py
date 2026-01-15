# 4. FORMATO DE LOS DATOS

# En este pipeline encontramos los distintos formatos que le daremos a los datos  de entrada usando la libreria pydantic 

import pydantic # Pydantic sirve para que tu programa no se rompa cuando recibe datos de fuera. Su función principal es la Validación de Datos.
from typing import List, Optional

class RAGChunkAndSrc(pydantic.BaseModel):
    chunks: List[str]
    source_id: Optional[str] =None


class RAGUpsertResult(pydantic.BaseModel):
    ingested:int


class RAGSearchResult(pydantic.BaseModel):
    contexts: List[str]
    sources: List[str]


class RAGQueryResult(pydantic.BaseModel):
    answer: str
    sources: List[str]
    num_contexts : int


