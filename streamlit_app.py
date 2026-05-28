import streamlit as st
import pdfplumber
from docx import Document
import cohere
import io

# ─── Configuración de página ───────────────────────────────────────────────────
st.set_page_config(page_title="LéeTuPóliza", page_icon="📄", layout="wide")

# ─── Cliente Cohere ────────────────────────────────────────────────────────────
co = cohere.Client(st.secrets["COHERE_API_KEY"])

# ─── System Prompt ─────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """Eres un asistente especializado en seguros. Analizás pólizas y respondés preguntas basándote exclusivamente en el texto proporcionado. Nunca inventás coberturas ni condiciones que no figuren en el documento. Si algo no está claro, lo indicás explícitamente. Usás siempre lenguaje simple, directo y sin tecnicismos innecesarios."""

# ─── Funciones auxiliares ──────────────────────────────────────────────────────

def extraer_texto_pdf(archivo):
    """Extrae texto de un archivo PDF digital página por página."""
    with pdfplumber.open(archivo) as pdf:
        paginas = [p.extract_text() for p in pdf.pages if p.extract_text()]
    return "\n".join(paginas)

def extraer_texto_docx(archivo):
    """Extrae texto de un archivo Word (.docx)."""
    doc = Document(io.BytesIO(archivo.read()))
    return "\n".join(p.text for p in doc.paragraphs)

def construir_prompt(texto_poliza, pregunta):
    """Construye el prompt según si hay pregunta específica o análisis general."""
    base = "Texto de la poliza:\n\n" + texto_poliza[:8000] + "\n\n"
    if pregunta.strip():
        return (
            base
            + "Respondé únicamente esta pregunta basándote en el texto de la póliza: "
            + pregunta
            + "\nNo hagas resúmenes ni análisis adicionales. Solo respondé lo que se pregunta."
        )
    else:
        return (
            base
            + "Realizá un análisis general con:\n"
            + "1. Resumen de 5 puntos clave (qué cubre y qué no cubre).\n"
            + "2. Glosario de términos técnicos explicados en lenguaje simple.\n"
            + "3. Exclusiones, franquicias y límites de cobertura más importantes."
        )

def analizar_con_ia(prompt_usuario):
    """Envía el prompt a Cohere y retorna la respuesta."""
    response = co.chat(
        model="command-a-03-2025",
        preamble=SYSTEM_PROMPT,
        message=prompt_usuario
    )
    return response.text

# ─── Sidebar: Cómo funciona ────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ℹ️ Información")
    st.markdown("### ¿Cómo funciona?")
    st.markdown("**LéeTuPóliza** usa Inteligencia Artificial para analizar tu póliza de seguro y explicarla en lenguaje simple.")
    st.markdown("""
1. **Cargá tu póliza**: subí un PDF digital o Word, o pegá el texto directamente.
2. **Hacé una pregunta** *(opcional)*: por ejemplo, *¿Qué cubre en caso de robo?*
3. **Hacé clic en "Analizar póliza"**: la IA procesa el documento y te responde.
""")
    st.markdown("### ¿Qué obtenés?")
    st.markdown("""
- **Sin pregunta**: análisis completo con coberturas, glosario y exclusiones.
- **Con pregunta**: respuesta puntual basada en tu póliza.
""")
    st.markdown("### Limitaciones")
    st.markdown("""
- Solo funciona con PDFs digitales (no escaneados).
- Responde únicamente sobre lo que dice el documento.
""")
    st.divider()
    st.caption("⚠️ Herramienta informativa. No reemplaza el asesoramiento de un profesional matriculado en seguros.")

# ─── Área principal ────────────────────────────────────────────────────────────
st.title("📄 LéeTuPóliza")
st.caption("Entendé tu póliza de seguro en segundos, sin tecnicismos.")
st.divider()

# ─── Sección 1: Ingreso de la póliza ──────────────────────────────────────────
st.subheader("1. Cargá tu póliza")
modo = st.radio("¿Cómo querés ingresar el texto?", ["Subir archivo (PDF o Word)", "Pegar texto manualmente"])

texto_poliza = ""

if modo == "Subir archivo (PDF o Word)":
    archivo = st.file_uploader("Subí tu póliza", type=["pdf", "docx"])
    if archivo is not None:
        if archivo.name.endswith(".pdf"):
            texto_poliza = extraer_texto_pdf(archivo)
        elif archivo.name.endswith(".docx"):
            texto_poliza = extraer_texto_docx(archivo)

        if texto_poliza.strip():
            st.success("Archivo cargado correctamente.")
        else:
            st.warning("No se pudo extraer texto. El archivo puede estar escaneado. Probá pegando el texto manualmente.")
else:
    texto_poliza = st.text_area("Pegá el texto de tu póliza aquí:", height=250)

# ─── Sección 2: Pregunta del usuario ──────────────────────────────────────────
st.subheader("2. ¿Qué querés saber?")
pregunta = st.text_input("Escribí tu pregunta (o dejá vacío para un análisis general):")

# ─── Botón de acción ───────────────────────────────────────────────────────────
if st.button("🔍 Analizar póliza"):
    if not texto_poliza.strip():
        st.warning("Primero cargá o pegá el texto de tu póliza.")
    else:
        try:
            prompt_usuario = construir_prompt(texto_poliza, pregunta)
            with st.spinner("Analizando tu póliza..."):
                resultado = analizar_con_ia(prompt_usuario)

            st.divider()
            st.subheader("📋 Resultado del análisis")
            st.markdown(resultado)

        except Exception as e:
            st.error(f"Error al conectar con la IA: {e}")
