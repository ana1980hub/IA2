import streamlit as st
import pdfplumber
from docx import Document
import io

# --- Configuración de página ---
st.set_page_config(page_title="LéeTuPóliza", page_icon="📄", layout="centered")

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
        st.success("Archivo cargado correctamente.")
else:
    texto_poliza = st.text_area("Pegá el texto de tu póliza aquí:", height=250)

# --- Pregunta del usuario ---
st.subheader("2. ¿Qué querés saber?")
pregunta = st.text_input("Escribí tu pregunta (o dejá vacío para un análisis general):")

# --- Botón de análisis ---
if st.button("Analizar póliza") and texto_poliza.strip():
    import anthropic
    client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])

    prompt_usuario = f"""Aquí está el texto de una póliza de seguro:

{texto_poliza[:8000]}

{"Pregunta del usuario: " + pregunta if pregunta else "Realizá un análisis general de la póliza."}
"""

    system_prompt = """Eres un asistente especializado en seguros. Tu función es analizar pólizas de seguro y explicarlas en lenguaje claro y accesible para personas sin conocimientos técnicos.

Cuando el usuario te proporcione el texto de una póliza:
1. Genera un resumen de no más de 5 puntos clave que indiquen QUÉ CUBRE y QUÉ NO CUBRE la póliza.
2. Identifica y explica en lenguaje simple los términos técnicos o legales presentes.
3. Destaca las exclusiones, franquicias y límites de cobertura más importantes.
4. Responde solo con información que esté explícitamente en el texto proporcionado.
5. Si el usuario hace preguntas, respóndelas basándote exclusivamente en el documento cargado.

IMPORTANTE: No inventes coberturas ni condiciones que no figuren en el texto. Si algo no está claro en el documento, indícalo explícitamente. Usa siempre un lenguaje simple, directo y sin tecnicismos innecesarios."""

    with st.spinner("Analizando tu póliza..."):
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            system=system_prompt,
            messages=[{"role": "user", "content": prompt_usuario}]
        )
        resultado = response.content[0].text

    st.subheader("📋 Resultado del análisis")
    st.markdown(resultado)
    st.divider()
    st.caption("⚠️ LéeTuPóliza es una herramienta informativa. No reemplaza el asesoramiento de un profesional matriculado en seguros.")

elif st.button and not texto_poliza.strip():
    st.warning("Primero cargá o pegá el texto de tu póliza.")
