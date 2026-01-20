
# 6.FRONTEND 

import asyncio
from pathlib import Path
import time
import streamlit as st
import inngest
from dotenv import load_dotenv
import os
import requests
from functions import QdrantStorage


storage_engine = QdrantStorage()

load_dotenv()

st.set_page_config(page_title="Asistente RAG Profesional", page_icon="📄", layout="centered")


# INICIALIZACIÓN DE LA MEMORIA DE SESIÓN ---
if "messages" not in st.session_state:
    st.session_state.messages = []

@st.cache_resource
def get_inngest_client() -> inngest.Inngest:
    return inngest.Inngest(app_id="rag_app", is_production=False)


def save_uploaded_pdf(file) -> Path:
    uploads_dir = Path("uploads")
    uploads_dir.mkdir(parents=True, exist_ok=True)
    file_path = uploads_dir / file.name
    file_bytes = file.getbuffer()
    file_path.write_bytes(file_bytes)
    return file_path


async def send_rag_ingest_event(pdf_path: Path) -> None:
    client = get_inngest_client()
    await client.send(
        inngest.Event(
            name="rag/ingest_pdf",
            data={
                "pdf_path": str(pdf_path.resolve()),
                "source_id": pdf_path.name,
            },
        )
    )

# --- BOTÓN DE LIMPIEZA EN LA BARRA LATERAL ---
with st.sidebar:
    st.header("Administración")
    if st.button("🗑️ Limpiar Base de Datos"):
        with st.spinner("Borrando conocimiento..."):
            storage_engine.clear_collection()
            st.success("¡Base de datos vacía!")
            time.sleep(1)
            st.rerun()
    
    # NUEVO: Botón para resetear solo el chat sin borrar la DB
    if st.button("💬 Limpiar Chat"):
        st.session_state.messages = []
        st.rerun()


st.title("📂 Cargar Documentos")
uploaded = st.file_uploader("Sube un PDF para alimentar al asistente", type=["pdf"], accept_multiple_files=False)

if uploaded is not None:
    with st.spinner("Procesando documento..."):
        path = save_uploaded_pdf(uploaded)
        # Kick off the event and block until the send completes
        asyncio.run(send_rag_ingest_event(path))
        # Small pause for user feedback continuity
        time.sleep(0.3)
    st.success(f"Documento listo: {path.name}")
    st.caption("Puedes subir otro archivo si deseas actualizar el contexto.")

st.divider()

async def send_rag_query_event(question: str, top_k: int, chat_history: list, source_id: str = None) -> None:
    client = get_inngest_client()
    result = await client.send(
        inngest.Event(
            name="rag/query_pdf_ai",
            data={
                "question": question,
                "top_k": top_k,
                "source_id": source_id,
                "chat_history": chat_history, # <-- ENVIAMOS LA MEMORIA
            },
        )
    )
    return result[0]


def _inngest_api_base() -> str:
    # Local dev server default; configurable via env
    return os.getenv("INNGEST_API_BASE", "http://127.0.0.1:8288/v1")


def fetch_runs(event_id: str) -> list[dict]:
    url = f"{_inngest_api_base()}/events/{event_id}/runs"
    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.json()
    return data.get("data", [])


def wait_for_run_output(event_id: str, timeout_s: float = 120.0, poll_interval_s: float = 0.5) -> dict:
    start = time.time()
    last_status = None
    while True:
        runs = fetch_runs(event_id)
        if runs:
            run = runs[0]
            status = run.get("status")
            last_status = status or last_status
            if status in ("Completed", "Succeeded", "Success", "Finished"):
                return run.get("output") or {}
            if status in ("Failed", "Cancelled"):
                raise RuntimeError(f"Function run {status}")
        if time.time() - start > timeout_s:
            raise TimeoutError(f"Timed out waiting for run output (last status: {last_status})")
        time.sleep(poll_interval_s)


# INTERFAZ DE CHAT ---
st.title("Chat con tus PDFs")

# Dibujamos el historial de la conversación
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input de chat (Reemplaza al st.form anterior)
if prompt := st.chat_input("Escribe tu pregunta..."):
    
    # 1. Mostrar y guardar pregunta del usuario
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Generar respuesta
    with st.chat_message("assistant"):
        with st.spinner("Consultando documentos..."):
            current_file_name = uploaded.name if uploaded else None
            
            # Pasamos el historial previo (sin la pregunta actual que acabamos de añadir)
            event_id = asyncio.run(send_rag_query_event(
                prompt.strip(), 
                5, 
                st.session_state.messages[:-1], # <-- PASAMOS EL PASADO
                current_file_name
            ))
            
            output = wait_for_run_output(event_id)
            answer = output.get("answer", "No se obtuvo respuesta.")
            sources = output.get("sources", [])
            
            st.markdown(answer)
            
            if sources:
                with st.expander("Ver fuentes de esta respuesta"):
                    for s in sources:
                        st.write(f"- {s}")
            
            # 3. Guardar respuesta del asistente en memoria
            st.session_state.messages.append({"role": "assistant", "content": answer})
            st.rerun()

# Para correr el siguiente codigo y abrir la aplicación (nuestra API) debo correr el siguinte comando en el terminal uv run streamlit run .\(nombre de la pagina)