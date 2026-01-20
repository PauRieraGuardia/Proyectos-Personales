 
# 1. CONECTIVIDAD DE LOS DISTINTOS ENTORNOS Y PIPELINES

# En el main tratamos de realizar la conexión entre los distintos entornos a usar y los pipelines creados 
# Para este proyecto usaremos varias plataformas y aplicaciones
#   - INNGEST: plataforma necesaria para monitorear la actividad de nuestra app
#   - QDRANT: Base de datos vectorial, donde almacenaremos todos los embeddings de los PDFs facilitadps 
#   - LLAMAINXEX: libreria que lee los archivos y los "transfomra" para que el LLM sea capaz de usarlo.
#   - OPEN AI API: LLM que utilizaremos, motor de nuestro modelo
#   - DOCKER DESKTOP: Contenedor (almacen) donde guardamos todas las instalaciones necesarias para que corra el codigo. Es una instalación local (ya lo tenemos)


# PASO 1. IMPROTACIÓN DE LIBRERIAS
import logging # Para registrar eventos y errores en la consola (Logs).
import os  # Para interactuar con el sistema (rutas de archivos, variables).
import datetime #Para manejar fechas, horas y cálculos de tiempo.
from fastapi import FastAPI # El framework principal para crear tu API web.
import inngest # Librería base para gestionar flujos de trabajo (workflows).
import inngest.fast_api # El "conector" que permite a Inngest trabajar dentro de FastAPI.
from inngest.experimental import ai # Herramientas avanzadas para flujos de trabajo con IA/LLMs.
from dotenv import load_dotenv # Para leer tus credenciales secretas desde un archivo .env.

# Importamos nuestras hojas de pipeline
from custom_types import RAGChunkAndSrc, RAGUpsertResult, RAGSearchResult, RAGQueryResult
from functions import QdrantStorage, VectorProcessor, AuditLogger
from workflow import RAGWorkflow

# PASO 2. 
# Necesario para activar las claves de la api al haber creado el archivo .env
load_dotenv() # Carga las variables de entorno desde un archivo '.env' al sistema para proteger claves y credenciales.

# PASO 8. INICIALIZACIÓN DE MOTORES (Singletons)
# Creamos las instancias una sola vez aquí para reutilizarlas
storage_engine = QdrantStorage()
processor_engine = VectorProcessor()
audit_engine = AuditLogger(storage_engine.client)

# PASO 9. INICIALIZACIÓN DEL WORKFLOW (Inyección de dependencias)
workflow = RAGWorkflow(processor=processor_engine, storage=storage_engine, logger=audit_engine)

# PASO 3. CEREBRO DE INNGEST, necesario para establecer conexión con la api de inngest
inngest_client = inngest.Inngest( # Crea la instancia del cliente principal para gestionar eventos y flujos. Es decir, aquello que conecta el código con la paltaforma de Inngest
    app_id = "rag_app", # Define el identificador único de tu aplicación en el panel de Inngest. Es decir, como se verá en el panel de inngest el proyecto a monitorizar
    logger = logging.getLogger("uvicorn"),  # Vincula los mensajes de Inngest con los logs del servidor web (Uvicorn).
    is_production = False, # Indica que estás en modo desarrollo, mientras se mantenga False se abre la plataforma de inngest en local
    serializer = inngest.PydanticSerializer()) # Permite enviar objetos complejos (modelos Pydantic) como datos de eventos.

# PASO 4. FUNCIONES CLIENTE, necesario, pues sino no funciona nuestra conexión

# FUNCIÓN 1, para la ingesto del pdf
@inngest_client.create_function( # Crea un apartado donde le dira a inngest que la siguiente función se activará con el siguiente trigger.
    fn_id = "RAG: Ingest PDF", # Identificador único de la función para monitorearla en el panel de Inngest.
    trigger = inngest.TriggerEvent(event="rag/ingest_pdf") # Define qué evento específico "despierta" a esta siguiente función.
) 

async def rag_ingest_pdf(ctx: inngest.Context): # Define la función lógica asíncrona (que no se bloquea) con el nombre de la función y los elementos de esta
    
    # Aqui es donde introducimos lo que hará nuestro sistema, las funciones definidas, PODEMOS INCLUSO DEFINIR OTRO PIPELINE CON ESTA ESTRUCTURA
    chunks_and_src = await ctx.step.run("load-and-chunk", lambda: workflow._load(ctx), output_type=RAGChunkAndSrc)  
    ingested = await ctx.step.run("embd-and-upsert", lambda: workflow._upsert(chunks_and_src), output_type=RAGUpsertResult)
    return ingested.model_dump()

# FUNCIÓN 2, para la query 
@inngest_client.create_function( # Crea un apartado donde le dira a inngest que la siguiente función se activará con el siguiente trigger.
    fn_id = "RAG: Query PDF", # Identificador único de la función para monitorearla en el panel de Inngest.
    trigger = inngest.TriggerEvent(event="rag/query_pdf_ai") # Define qué evento específico "despierta" a esta siguiente función.
) 

async def rag_query_pdf_ai(ctx: inngest.Context):

    # 1. CONFIGURACIÓN DEL PROMPT 
    # Aqui es donde le damos contexto al LLM para que responda de una formad determinada

    NOMBRE_EMPRESA = "Empresa S.L"
    PERSONALIDAD = "un asistente técnico profesional, atento y preciso"

    MI_PROMPT = f"""
    [ROL]: Eres {PERSONALIDAD} de la empresa {NOMBRE_EMPRESA}. Tu objetivo es ayudar a los usuarios basándote exclusivamente en la documentación proporcionada.

    [DIRECTRICES DE RESPUESTA]:
    1. FIDELIDAD: Responde ÚNICAMENTE utilizando la información del contexto suministrado. 
    2. HONESTIDAD: Si la respuesta no está en los documentos o no estás seguro, di: "Lo siento, no encuentro esa información en la documentación de {NOMBRE_EMPRESA}, ¿puedo ayudarte con otra consulta?". NO inventes datos.
    3. IDIOMA: Responde siempre en el mismo idioma en el que el usuario te pregunte.
    4. TONO: Mantén un tono corporativo, educado y servicial.

    [FORMATO]:
    - Utiliza negritas para resaltar términos importantes.
    - Si la información contiene pasos o listas, utiliza viñetas o numeración para mayor claridad.
    """


    # 2. RECUPERACIÓN DE DATOS DEL EVENTO

    question = ctx.event.data["question"]
    source_id = ctx.event.data.get("source_id")
    top_k = int(ctx.event.data.get("top_k", 5))
    chat_history = ctx.event.data.get("chat_history", [])

    # 3. GENERACIÓN DEL SYSTEM PROMPT DINÁMICO USANDO EL WORKFLOW
    # Llamamos a la Función 6 del workflow para combinar el prompt con la base RAG
    system_content = await workflow._get_system_prompt(MI_PROMPT)

    # 4. CONDENSACIÓN DE LA PREGUNTA 
    search_query = await ctx.step.run("condense-question", lambda: workflow._condense_question(question, chat_history))
    
    # 5. BÚSQUEDA SEMÁNTICA EN QDRANT 
    found = await ctx.step.run("embedn-and-search", lambda: workflow._search(search_query, top_k, source_id=source_id), output_type = RAGSearchResult)

    # 6. PREPARACIÓN DE LOS MENSAJES PARA EL LLM
    messages = [{"role": "system", "content": system_content}]
    
    # Añadimos a messages el historial de mensajes 
    for msg in (chat_history or [])[-6:]: # Pasamos los últimos 6 mensajes para dar fluidez
        messages.append(msg) # Añadimos cada mensaje a messages

    # 7. EL CONTENIDO DEL USUARIO
    context_block = "\n\n".join(f"- {c}" for c in found.contexts)
    
    user_content = (
        f"Context:\n{context_block}\n\n"
        f"Question: {question}\n"
        )
    
    # 8. CONFIGURACIÓN DE IA E INFERENCIA 
    # Configuración IA
    adapter = ai.openai.Adapter(
        auth_key= os.getenv("OPENAI_API_KEY"), # Activamos la api key personal
        model = "gpt-4o-mini" # Modelo que queremos utilizar 
    )

    # Inferencia del LLM
    res = await ctx.step.ai.infer(
        "llm-asnwer",
        adapter = adapter,
        body = {
            "max_tokens": 1024,
            "temperature":0.2, # Nivel de "creatividad" de la IA
            "messages": messages + [{"role": "user", "content": user_content}]
        }
    )

    answer = res["choices"][0]["message"]["content"].strip()

    # 9. AUDITORIA Y REGISTRO (CAJA NEGRA) 
    await ctx.step.run(
        "audit-log-interaction",
        lambda: workflow._log_interaction(
            question=question,
            answer=answer,
            source_id=source_id, # Enviamos el PDF usado
            sources=found.sources,
            chat_history=chat_history
        )
    )

    return {"answer": answer, "sources": found.sources, "num_contexts": len(found.contexts)}



# PASO 5. API PROPIA, 
app = FastAPI() # Inicializa la aplicación web que recibirá las peticiones HTTP.


# PASO 6. CONEXIÓN API PROPIA - CEREBRO INNGEST
inngest.fast_api.serve( # Registra el punto de acceso (endpoint) para que Inngest pueda comunicarse con tu API.
                        app, # Servidor que aloja la comunicación, api propia
                       inngest_client,  # El cerebro que gestiona los eventos 
                       functions=[rag_ingest_pdf,rag_query_pdf_ai])  # El catálogo de tareas disponibles, aqui añadiremos las funciones 

# PASO 7: Para luego activar por un lado el local host y por el otro el portal de monitoreo de inngest debemos hacer los sigueintes pasos:
# 5.1- Abrir un terminal y ejecutar lo siguiente: uv run uvicorn main:app
# 5.2- Se nos ejecutará un código y se nos abrirá un nuevo local_host (Añadir local_host terminal anterior)
# 5.3- Abrimos otro nuevo terminal, sin cerrar el anterior, y ejecutamos lo siguiente: npx inngest-cli@latest dev -u (Añadir local_host terminal anterior)/api/inngest
# 5.4- Se nos abríra un nuevo local_host donde se mostrara el monitoreo desde el SaaS INNGEST
# 5.5- Ahora, si vamos al primer terminal uv, veremos que inngest ha intentado establecer conexión con nuestra api en varios portales hastat conseguirlo
# 5.6- Si abrimos el porta de inngest, veremos disponible nuestras distintas funciones
# 5.7- Una vez tenemos la conexión entre INNGEST y mi propia API, deberemos crear la base de datos. Para ello creamos una nueva carpeta QDRANT (puesto que la bade de datos es vectorizada)
# 5.8- El siguiente paso es conectar DOCKER con mi carpeta QDRANT y darle formato QDRANT, para ello abrimos el terminal y insteramos: docker run -d --name (nombre del contenedor) -p 6333:6333 (puerto por defecto) -v "$(pwd)/(Nombre de la carpeta):/qdrant/storage" qdrant/qdrant ()
#      Mismo proceso si queremos otro tipo de base de datos pero cambiano puerto nombre imagen y volumenes.
#      Si el contenedor ya esta creado, debemos usar esta función en el terminal para inicializarlo otra vez docker start (nombre_de_tu_contenedor) o desde la aplicaicón de docker
# 5.9- Una vez hemos enlazado DOKCER con nuestra carpeta qdrant, creamos un nuevo archivo py donde almacenaremos la base de datos PASAMOS A ESE ARCHIVO