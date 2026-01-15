#  5. RAG WORKFLOW

# Importación de librerias 
import uuid
import os
import inngest
from inngest.experimental import ai
from custom_types import RAGChunkAndSrc, RAGUpsertResult, RAGSearchResult
from functions import QdrantStorage, VectorProcessor, AuditLogger

class RAGWorkflow:
    def __init__(self, processor:VectorProcessor, storage:QdrantStorage, logger:AuditLogger):
        """
        processor: instancia de VectorProcessor
        storage: instancia de QdrantStorage
        """
        self.processor = processor
        self.storage = storage
        self.logger = logger

    # FUNCIÓN 1 (INGESTA) 
    
    async def _load(self, ctx: inngest.Context) -> RAGChunkAndSrc:
        pdf_path = ctx.event.data["pdf_path"]
        source_id = ctx.event.data.get("source_id", pdf_path)
        chunks = self.processor.load_and_chunk_pdf(pdf_path)
        return RAGChunkAndSrc(chunks=chunks, source_id=source_id)

    async def _upsert(self, chunks_and_src: RAGChunkAndSrc) -> RAGUpsertResult:
        """Mantiene la lógica exacta de tu función original"""
        chunks = chunks_and_src.chunks
        source_id = chunks_and_src.source_id
        
        if not chunks:
            print(f"AVISO: No se encontraron chunks para {source_id}. Cancelando upsert.")
            return RAGUpsertResult(ingested=0)
            
        vecs = self.processor.embed_texts(chunks)
        ids = [str(uuid.uuid5(uuid.NAMESPACE_URL, f"{source_id}:{i}")) for i in range(len(chunks))]
        payloads = [{"source": source_id, "text": chunks[i]} for i in range(len(chunks))]
        
        self.storage.upsert(ids, vecs, payloads)
        return RAGUpsertResult(ingested=len(chunks))

    # FUNCIÓN 2 (BÚSQUEDA) 

    async def _search(self, question: str, top_k: int = 5, source_id: str = None) -> RAGSearchResult:
        """
        Busca contexto filtrando opcionalmente por un PDF específico.
        """
        query_vec = self.processor.embed_texts([question])[0] # Convertimos la pregunta en un vector
        
        found = self.storage.search(query_vec, top_k=top_k, source_id=source_id) # Busca el almacenamiento en función de estos parámetros 

        return RAGSearchResult(contexts=found["contexts"], sources=found["sources"]) # Devuelve respuesta y la fuente

     # FUNCION 3

    async def _log_interaction(self, question: str, answer: str, source_id: str, sources: list):
        """
        Método asíncrono modificado para recibir el source_id (nombre del PDF)
        y pasárselo al motor de auditoría.
        """
        self.logger.save_log(
            question=question, 
            answer=answer, 
            source_id=source_id, # <--- Agregamos este cable
            sources=sources
        )
        return {"status": "logged"}