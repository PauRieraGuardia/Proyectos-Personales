# 2. ADMINISTRADOR BASE DE DATOS VECTORIZADA

# Lógica de Comportamiento: En este pipeline definimos la lógica de cómo se deben organizar, guardar y buscar los datos. 
# No creamos la base de datos aquí, sino que dictamos las "reglas de operación" (como el tamaño de los vectores y el método de comparación).
# Para ello, hacemos uso de DOCKER y de QDRANT
#   - QDRANT (Motor): Es el motor de base de datos vectorial. No es solo una librería, es el "cerebro" que procesa los vectores. 
#                     La librería que usamos en Python (qdrant-client) es el puente para enviarle órdenes a ese motor.
#   - DOCKER (Contenedor): Es el entorno donde vive y corre Qdrant. 

# PASO 1. IMPORTACIÓN DE LIBRERIAS 
from qdrant_client import QdrantClient           # Importa el "conector" principal para conectar con DOCKER
from qdrant_client.models import (VectorParams,  # Molde para configurar las reglas del estante (dimensión y medida).
                                Distance,        # Define la regla matemática (Coseno) para buscar similitudes.
                                PointStruct,     # Molde para crear el "paquete" de datos (ID + Vector + Texto).
                                Filter, 
                                FieldCondition, 
                                MatchValue, 
                                PointStruct)     

# PASO 2. CREACIÓN DE UN OBJETO CLASS
# Los objetos class sirven para agrupar codigo, en este caso, estamos agrupando todas las funciones relacionadas con el tratamiento que le daremos a los datos en la fase de almacenamiento.
# En este caso estamos creando una CLASS ADMINISTRADOR. Se caracteriza por la presencia de __init__, que establece una conexión con algo exterior.
# Cuando creamos un objeto class estamos creando nuestra "propia libreria" con sus funciones o sus conexiones __init__.
# Con esta función procesaremos los datos de los pdfs y los transformaremos a formato json,

class QdrantStorage: 
    def __init__( # Esta función establece la conexión entre el codigo y la base de datos QDRANT, que esta corriendo dentro de un contenedor DOCKER
                self,  # Hilo conductor de las distintas funciones, es el objeto que le aplicaremos  
                 url="http://localhost:6333", # Puerto del DOCKER 
                 collection="docs", # Nombre de una nueva colección
                 dim=3072): # Dimensión de los datos de entrada
        
        self.client = QdrantClient(url=url,timeout=30) # Establece conexión con el servidor QDRANT (DOCKER)
        self.collection = collection # Guardamos el nombre de la carpeta donde guardaremos los datos
        
        if not self.client.collection_exists(self.collection): # Si la collection no existe, la creamos 
            self.client.create_collection(
                collection_name = self.collection, # Nombre de la colección
                vectors_config = VectorParams(size=dim, distance=Distance.COSINE),) # Configuración téncica de los vectores en la colección 


    def upsert( self, ids, vectors, payloads): # Función que inserta los datos que puedan llegar con un formato determinado
        points = [PointStruct(id=ids[i], vector = vectors[i], payload = payloads[i]) for i in range(len(ids))]
        return self.client.upsert(self.collection, points=points)
    

    def search(self,query_vector, top_k: int=5, source_id: str = None): # Función que recibe una query convertida a vector y busca en la base de datos cual se parece más, similar a un senctence similarity
        
        # PASO A: CREACIÓN DEL FILTRO para que solo responda en función del pdf o pdfs adjuntados
        search_filter = None
        if source_id:
            search_filter = Filter(
                must=[
                    FieldCondition(
                        key="source", # Debe coincidir con la clave que pusimos en el payload del upsert
                        match=MatchValue(value=source_id)
                    )
                ]
            )
        
        # PASO B: Llamamos la función query_points incluyendo el filtro
        results = self.client.query_points( # Llamamos la funcion search del cliente QdrantClient, busqueda por similitud matemática
            collection_name = self.collection, # Le damos el nombre de la colección
            query = query_vector, # El vector de la query
            query_filter = search_filter, # El filtro de la query, el pdf o pdfs adjuntados
            limit = top_k).points # Define el número máximo de resultados

        contexts = [] # Creación lista vacia llamada contexts
        sources = set() # Creación de contenedor para las sourcers

        for r in results: 
            payload = getattr(r, "payload", None) or  {} # información de cada results
            text = payload.get("text", "") # el texto similar
            source = payload.get("source", "") # la fuente
            if text: # Si existe texto 
                contexts.append(text) # Lo añade en contexts
                sources.add(source)   # Lo añade en sources
        
        return {"contexts":contexts, "sources":list(sources)} # Imprime el texto y la fuente
    

    def clear_collection(self):
        """Borra la colección de documentos y la recrea vacía"""
        self.client.delete_collection(collection_name=self.collection)
        
        # La recreamos inmediatamente para que el sistema siga funcionando
        self.client.create_collection(
            collection_name=self.collection,
            vectors_config=VectorParams(size=3072, distance=Distance.COSINE),
        )
        print(f"DEBUG: Colección '{self.collection}' reiniciada.")

# 3. PROCESAMIENTO E INGESTA VECTORIAL

# En este pipeline vamos a transformar documentos PDF en vectores numéricos:
#   - LLAMAINDEX: No es un LLM, es un "Framework de Datos". Lo usamos para la INGESTA (leer el PDF) 
#     y el CHUNKING (dividir el texto en fragmentos lógicos para no superar el límite de memoria de la IA).
#   - OPENAI: Es nuestro "Embedding Model". Actúa como un traductor que convierte cada fragmento de 
#     texto en un vector (una lista de números) que representa su significado semántico.

from openai import OpenAI # Imporatmos la api de OPNEAI para poder acceder al modelo
from llama_index.readers.file import PDFReader # Extrae el texto de los PDFs limpio para que el LLM pueda entenderlo
from llama_index.core.node_parser import SentenceSplitter # Esta herramienta corta el texto en troxos (chunks) sin romper frases a la mitad

from dotenv import load_dotenv # Sirve para leer tu API KEY desde el archivo '.env'.

load_dotenv() # Carga las variables de entorno desde un archivo '.env' al sistema para proteger claves y credenciales.

class VectorProcessor:
    def __init__(self):
        # Aquí preparamos las herramientas (Se ejecuta al poner: procesador = VectorProcesor())
        self.client = OpenAI() # Llamamos a la Api de OpenAI
        self.splitter = SentenceSplitter(chunk_size=1000, chunk_overlap=200) # Definimos la herramienta sentencesplitter y los parámetros que queremos
        self.embed_model = "text-embedding-3-large" # Definimos el modelo
        self.embed_dim = 3072 # Definimos la dimensión, en función del modelo

    def load_and_chunk_pdf(self, path: str): # Funcion para leer y partir el pdf donde le facilitamos el parametro path
        docs = PDFReader().load_data(file=path) # Lee el documento, aplica PDFReader de LLamaIndex para que pueda ser procesado por el LLM
        texts = [d.text for d in docs if d.text and d.text.strip()]  # Va recorriendo cada texto de docs y los añade a texts
        chunks = [] # Creación de lista vacia 
        for t in texts: # Para cada fragmentod etexto
            split_results = self.splitter.split_text(t)
            chunks.extend([c for c in split_results if c and c.strip()]) # Aplica el splitter y lo añade a chunks 
        return chunks # Nos devuelve chunks, que es una lista con trozos de texto

    def embed_texts(self, texts: list[str]) -> list[list[float]]: # Recibe una lista de trozos de texto(texts, creada con la función anterior) y promete devolver una lista de listas de números (floats).
        # 1. VERIFICACIÓN: ¿Qué le estamos enviando a OpenAI?
        print(f"DEBUG: Enviando {len(texts)} fragmentos a OpenAI.")
    
        if not texts:
            print("ERROR: La lista de textos está VACÍA. No se puede llamar a OpenAI.")
            return [] # Evitamos que explote el código
    
        response = self.client.embeddings.create( # Creación de embeddings
            model=self.embed_model, # Modelo a usar
            input=texts, # Lista texts. 
        )
        return [item.embedding for item in response.data] # Lista de vectores del objeto response 


# 4. PROCESO PARA GUATRDAR TODAS LAS CONSULTAS Y OPUTPUS REALZIADOS 

import uuid
from datetime import datetime
from qdrant_client.models import PointStruct, VectorParams, Distance


class AuditLogger:
  
    def __init__(self, client: QdrantClient):
            self.client = client
            self.collection_name = "audit_logs"

    def save_log(self, question: str, answer: str, source_id: str, sources: list, chat_history: list = None): 
        

            # 1. Crear colección si no existe (se queda igual)
            if not self.client.collection_exists(self.collection_name):
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=3072, distance=Distance.COSINE),
                )

            # 2. Insertar el log con el PDF referenciado
            self.client.upsert(
                collection_name=self.collection_name,
                points=[
                    PointStruct(
                        id=str(uuid.uuid4()),
                        vector=[0.0] * 3072,
                        payload={
                            "timestamp": datetime.now().isoformat(),
                            "question": question,
                            "answer": answer,
                            "pdf_usado": source_id,  
                            "fragmentos_encontrados": sources,
                            "historial": chat_history
                        }
                    )
                ]
        )