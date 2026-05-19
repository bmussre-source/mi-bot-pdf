import streamlit as st
import os
from pypdf import PdfReader
from streamlit_mic_recorder import speech_to_text

# Configuración de la página web (Debe ser la primera instrucción de Streamlit)
st.set_page_config(
    page_title="Bot de PDFs Accesible",
    page_icon="🤖",
    layout="centered"
)

# Estilos visuales personalizados para mejorar la legibilidad
st.markdown("""
    <style>
    .main { background-color: #f7f9fc; }
    h1 { color: #1e3a8a; }
    .stButton>button {
        width: 100%;
        background-color: #2563eb;
        color: white;
        border-radius: 8px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🤖 Mi Bot de Consulta PDF Accesible")
st.write("Bienvenido. Puedes añadir PDFs a la carpeta del proyecto, hacer preguntas por escrito o dictarlas usando tu voz.")

# ==========================================================
# PASO 1: CONEXIÓN Y LECTURA DE DATOS DESDE LA CARPETA
# ==========================================================
FOLDER_PATH = "documentos"

def cargar_textos_pdf(carpeta):
    """Escanea la carpeta local y extrae el texto de todos los archivos PDF."""
    texto_total = ""
    # Si la carpeta no existe, el programa la crea automáticamente
    if not os.path.exists(carpeta):
        os.makedirs(carpeta)
    
    # Recorrer todos los archivos dentro de la carpeta 'documentos'
    for archivo in os.listdir(carpeta):
        if archivo.endswith(".pdf"):
            ruta_completa = os.path.join(carpeta, archivo)
            try:
                lector = PdfReader(ruta_completa)
                for pagina in lector.pages:
                    texto_extraido = pagina.extract_text()
                    if texto_extraido:
                        texto_total += texto_extraido + "\n"
            except Exception as e:
                st.error(f"Error al leer el archivo {archivo}: {e}")
    return texto_total

# Inicializar y cargar el contenido de los PDFs en la memoria del servidor
base_conocimiento = cargar_textos_pdf(FOLDER_PATH)

# Mostrar el estado de tus documentos cargados en la barra lateral izquierda
with st.sidebar:
    st.header("📂 Documentos Fuente")
    archivos_encontrados = [f for f in os.listdir(FOLDER_PATH) if f.endswith('.pdf')]
    if archivos_encontrados:
        st.success(f"¡{len(archivos_encontrados)} PDF(s) detectado(s)!")
        for archivo in archivos_encontrados:
            st.text(f"📄 {archivo}")
    else:
        st.warning("La carpeta 'documentos/' está vacía. Añade PDFs para entrenar al bot.")

# ==========================================================
# PASO 2: HISTORIAL DEL CHAT (Para no perder la conversación)
# ==========================================================
if "messages" not in st.session_state:
    st.session_state.messages = []

# Dibujar los mensajes guardados anteriormente en la pantalla
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ==========================================================
# PASO 3: CAPTURA DE PREGUNTAS (Voz / Teclado)
# ==========================================================
pregunta = None

st.write("---")
st.write("🎙️ **¿Prefieres hablar?** Presiona el botón para dictar tu duda:")

# Componente de Accesibilidad: Graba audio y lo convierte a texto en tiempo real
pregunta_dictada = speech_to_text(
    start_prompt="🎤 Iniciar grabación de voz",
    stop_prompt="🛑 Detener y procesar",
    language='es',
    key='dictado_voz'
)

# Si el usuario dictó, esa es la pregunta activa
if pregunta_dictada:
    pregunta = pregunta_dictada

# Entrada clásica por teclado (si no se usó el micrófono)
pregunta_escrita = st.chat_input("O escribe aquí tu pregunta sobre los documentos...")
if pregunta_escrita:
    pregunta = pregunta_escrita

# ==========================================================
# PASO 4: PROCESAMIENTO, ANIMACIÓN DE ONDAS Y AUDIO (TTS)
# ==========================================================
if pregunta:
    # 1. Mostrar la pregunta del usuario en el chat
    with st.chat_message("user"):
        st.markdown(pregunta)
    st.session_state.messages.append({"role": "user", "content": pregunta})
    
    # 2. Lógica de respuesta del bot
    if not base_conocimiento:
        respuesta_bot = "Actualmente no tengo documentos PDFs cargados en la carpeta 'documentos'. Por favor, añade archivos para que pueda ayudarte."
    else:
        # En el futuro, aquí conectarás la variable 'base_conocimiento' con OpenAI/Gemini
        respuesta_bot = f"He analizado los documentos guardados. En respuesta a tu consulta sobre '{pregunta}', los archivos indican que los protocolos estipulados deben seguirse bajo las normativas vigentes."

    # 3. Mostrar la respuesta en texto para los usuarios visuales
    with st.chat_message("assistant"):
        st.markdown(respuesta_bot)
    st.session_state.messages.append({"role": "assistant", "content": respuesta_bot})
    
    # 4. Inyección interactiva de Ondas Animadas (CSS) y Lectura en voz alta (JS)
    componente_accesible = f"""
    <div id="contenedor-ondas" style="display: flex; align-items: center; gap: 6px; margin-top: 15px; padding: 10px; background-color: #eff6ff; border-radius: 8px; border-left: 4px solid #2563eb; font-family: sans-serif;">
        <span style="color: #1e40af; font-size: 14px; font-weight: bold; margin-right: 10px;">🔊 Reproduciendo audio:</span>
        <div class="barra-onda" style="width: 4px; height: 12px; background-color: #2563eb; animation: rebote 0.5s ease-in-out infinite alternate;"></div>
        <div class="barra-onda" style="width: 4px; height: 24px; background-color: #2563eb; animation: rebote 0.4s ease-in-out infinite alternate 0.1s;"></div>
        <div class="barra-onda" style="width: 4px; height: 32px; background-color: #2563eb; animation: rebote 0.6s ease-in-out infinite alternate 0.2s;"></div>
        <div class="barra-onda" style="width: 4px; height: 20px; background-color: #2563eb; animation: rebote 0.3s ease-in-out infinite alternate 0.3s;"></div>
        <div class="barra-onda" style="width: 4px; height: 10px; background-color: #2563eb; animation: rebote 0.5s ease-in-out infinite alternate 0.4s;"></div>
    </div>

    <style>
        @keyframes rebote {{
            0% {{ transform: scaleY(0.2); }}
            100% {{ transform: scaleY(1); }}
        }}
        .barra-onda {{
            transform-origin: bottom;
        }}
    </style>

    <script>
        var mensajeVoz = new SpeechSynthesisUtterance("{respuesta_bot}");
        mensajeVoz.lang = 'es-ES';

        // Cuando la voz del navegador termine, las ondas desaparecen automáticamente
        mensajeVoz.onend = function(event) {{
            document.getElementById("contenedor-ondas").style.display = "none";
        }};

        window.speechSynthesis.speak(mensajeVoz);
    </script>
    """
    
    # Pintar las ondas y ejecutar el audio en el navegador
    st.components.v1.html(componente_accesible, height=75)