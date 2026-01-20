import streamlit as st
import pandas as pd
from functions import QdrantStorage

st.set_page_config(page_title="Monitor Técnico RAG", layout="wide")

st.title("🛡️ Panel de Supervisión Técnica")

storage = QdrantStorage()

# 1. ESTADO DE LA INFRAESTRUCTURA
st.subheader("Estado de los Motores")
col1, col2 = st.columns(2)

try:
    # Intentamos conectar y pedir info de las colecciones
    coll_info = storage.client.get_collection("docs")
    audit_info = storage.client.get_collection("audit_logs")
    
    col1.metric("Vectores de Conocimiento", coll_info.points_count)
    col2.metric("Total Consultas Auditadas", audit_info.points_count)
except Exception as e:
    # Esta línea está movida a la derecha (4 espacios), así no da IndentationError
    st.error(f"Error conectando con Qdrant o colecciones no creadas: {e}")

st.divider()

# 2. TABLA DE MONITOREO EN TIEMPO REAL
st.subheader("Últimas interacciones")

try:
    # Intentamos traer los datos de auditoría
    logs, _ = storage.client.scroll(
        collection_name="audit_logs",
        limit=20,
        with_payload=True
    )

    if logs:
        # Convertimos la lista de logs en un DataFrame de Pandas
        data = [l.payload for l in logs]
        df = pd.DataFrame(data)
        
        # Filtro de seguridad para evitar el KeyError si falta alguna columna
        cols_deseadas = ['timestamp', 'question', 'source_id', 'answer']
        cols_finales = [c for c in cols_deseadas if c in df.columns]
        
        st.dataframe(df[cols_finales], use_container_width=True)
        
        # 3. ANALISIS DE CALIDAD
        if 'answer' in df.columns:
            st.subheader("Análisis de Calidad")
            # Buscamos patrones de respuestas donde el bot no encontró info
            terminos_fallidos = "no encuentro|no lo sé|no aparece|no tengo claro"
            no_info = df[df['answer'].str.contains(terminos_fallidos, case=False, na=False)].shape[0]
            
            if no_info > 0:
                st.warning(f"⚠️ Hay {no_info} consultas que el bot no supo responder.")
            else:
                st.success("✅ Todas las consultas fueron respondidas con éxito.")
    else:
        st.info("La colección de auditoría está vacía. El chat aún no ha guardado registros.")

except Exception as e:
    # Bloque except indentado correctamente para evitar errores
    st.warning(f"No se pudo cargar la tabla de interacciones: {e}")

# Espacio extra y botón de actualización
st.write("")
if st.button("🔄 Actualizar Datos"):
    st.rerun()
# Para correr el monitoreo: 
# uv run streamlit run admin_monitor.py