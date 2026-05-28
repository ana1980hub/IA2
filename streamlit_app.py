import streamlit as st
import pdfplumber
from docx import Document
import cohere
import io

# --- Configuración de página ---
st.set_page_config(page_title="LéeTuPóliza", page_icon="📄", layout="centered")

# --- Cliente Cohere ---
co = cohere.Client(st.secrets["COHERE_API_KEY"])

system_prompt = """Eres un asistente especializado en seguros. Analizás pólizas y respondés preguntas basándote exclusivamente en el texto proporcionado. Nunca inventás coberturas ni condiciones que no figuren en el documento. Si algo no está claro, lo indicás explícitamente. Usás siempre lenguaje simple, directo y sin tecnicismos innecesarios."""

if pregunta.strip():
    prompt_usuario = f"""Texto de la póliza:

{texto_poliza[:8000]}

Respondé únicamente esta pregunta basándote en el texto de la póliza: {pregunta}
No hagas resúmenes ni análisis adicionales. Solo respondé lo que se pregunta."""
else:
    prompt_usuario = f"""Texto de la póliza:

{texto_poliza[:8000]}

Realizá un análisis general con:
1. Resumen de 5 puntos clave (qué cubre y qué no cubre).
2. Glosario de términos técnicos explicados en lenguaje simple.
3. Exclusiones, franquicias y límites de cobertura más importantes."""

IMPORTANTE: No inventes coberturas ni condiciones que no figuren en el texto. Si algo no está claro en el documento, indícalo explícitamente. Usa siempre un lenguaje simple, directo y sin tecnicismos innecesarios."""

# --- UI ---
st.title("📄 LéeTuPóliza")
st.caption("Entendé tu póliza de seguro en segundos, sin tecnicismos.")

# --- Ingreso del texto ---
st.subheader("1. Cargá tu póliza")
modo = st.radio("¿Cómo querés ingresar el texto?", ["Subir archivo (PDF o Word)", "Pegar texto manualmente"])

texto_poliza = ""

if modo == "Subir archivo (PDF o Word)":
    archivo = st.file_uploader("Subí tu póliza", type=["pdf", "docx"])
    if archivo:
        if archivo.name.endswith(".pdf"):
            with pdfplumber.open(archivo) as pdf:
                texto_poliza = "\n".join(p.extract_text() or "" for p in pdf.pages)
        elif archivo.name.endswith(".docx"):
            doc = Document(io.BytesIO(archivo.read()))
            texto_poliza = "\n".join(p.text for p in doc.paragraphs)
        if texto_poliza.strip():
            st.success("Archivo cargado correctamente.")
        else:
            st.warning("No se pudo extraer texto. El archivo puede estar escaneado. Probá pegando el texto manualmente.")
else:
    texto_poliza = st.text_area("Pegá el texto de tu póliza aquí:", height=250)

# --- Pregunta del usuario ---
st.subheader("2. ¿Qué querés saber?")
pregunta = st.text_input("Escribí tu pregunta (o dejá vacío para un análisis general):")

# --- Botón de análisis ---
if st.button("Analizar póliza"):
    if not texto_poliza.strip():
        st.warning("Primero cargá o pegá el texto de tu póliza.")
    else:
        prompt_usuario = f"""Aquí está el texto de una póliza de seguro:

{texto_poliza[:8000]}

{"Pregunta del usuario: " + pregunta if pregunta.strip() else "Realizá un análisis general de la póliza siguiendo las instrucciones."}
"""
        try:
            with st.spinner("Analizando tu póliza..."):
                response = co.chat(
                    model="command-a-03-2025",
                    preamble=system_prompt,
                    message=prompt_usuario
                )
                resultado = response.text

            st.subheader("📋 Resultado del análisis")
            st.markdown(resultado)
            st.divider()
            st.caption("⚠️ LéeTuPóliza es una herramienta informativa. No almacena documentos ni datos del usuario. No reemplaza el asesoramiento de un profesional matriculado en seguros.")

        except Exception as e:
            st.error(f"Error al conectar con la IA: {e}")
