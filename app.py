import streamlit as st
import os
from pypdf import PdfReader
from streamlit_mic_recorder import speech_to_text
import google.generativeai as genai

# Configuración de la página web (Debe ser la primera instrucción de Streamlit)
st.set_page_config(
    page_title="Bot de PDFs Accesible Inteligente",
    page_icon="🤖",
    layout="centered"
)

# ==========================================================
# CONFIGURACIÓN SEGURA DE LA INTELIGENCIA ARTIFICIAL (GEMINI)
# ==========================================================
# CIBERSEGURIDAD: La clave ya no se escribe aquí. Se lee encriptada desde el servidor.
if "GEMINI_API_KEY" in st.secrets:
    # .strip() elimina espacios invisibles accidentales al inicio o final de la clave
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"].strip())
else:
    st.error("⚠️ Configuración de seguridad ausente. Por favor, añade la variable 'GEMINI_API_KEY' en la sección de Secrets de Streamlit.")
    st.stop() # Detiene la ejecución para evitar que la app intente conectar sin clave

# Estilos visuales personalizados para mejorar la legibilidad y estética
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

st.title("🤖 Mi Bot de Consulta PDF Accesible Real")
st.write("Bienvenido. Puedes añadir PDFs a la carpeta del proyecto, hacer preguntas por escrito o dictarlas usando tu voz.")

# ==========================================================
# PASO 1: CONEXIÓN Y LECTURA DE DATOS DESDE LA CARPETA
# ==========================================================
FOLDER_PATH = "documentos"

def cargar_textos_pdf(carpeta):
    """Escanea la carpeta local y extrae el texto de todos los archivos PDF."""
    texto_total = ""
    if not os.path.exists(carpeta):
        os.makedirs(carpeta)
    
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

# Inicializar y cargar el contenido de los PDFs en la memoria
base_conocimiento = cargar_textos_pdf(FOLDER_PATH)

# Mostrar el estado de tus documentos cargados en la barra lateral izquierda
with st.sidebar:
    st.header("📂 Documentos Fuente")
    archivos_encontrados = [f for f in os.listdir(FOLDER_PATH) if f.endswith('.pdf')]
    if archivos_encontrados:
        st.success(f"¡{len(archivos_encontrados)} PDF(s) detectado(s) con éxito!")
        for archivo in archivos_encontrados:
            st.text(f"📄 {archivo}")
    else:
        st.warning("La carpeta 'documentos/' está vacía. Añade PDFs para que el bot pueda responder.")

# ==========================================================
# PASO 2: HISTORIAL DEL CHAT (Para mantener el contexto)
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

if pregunta_dictada:
    pregunta = pregunta_dictada

# Entrada clásica por teclado (si no se usó el micrófono)
pregunta_escrita = st.chat_input("O escribe aquí tu pregunta sobre los documentos...")
if pregunta_escrita:
    pregunta = pregunta_escrita

# ==========================================================
# PASO 4: PROCESAMIENTO REAL CON IA, AUDIO Y ONDAS SONORAS
# ==========================================================
if pregunta:
    # 1. Mostrar la pregunta del usuario en el chat
    with st.chat_message("user"):
        st.markdown(pregunta)
    st.session_state.messages.append({"role": "user", "content": pregunta})
    
    # 2. Lógica de respuesta del bot conectada a la IA
    if not base_conocimiento:
        respuesta_bot = "Actualmente no encuentro documentos PDFs cargados en la carpeta 'documentos'. Por favor, añade archivos para que pueda extraer la información y responderte."
    else:
        # Optimizamos el prompt recortando la base de conocimiento a los primeros 15,000 caracteres
        instruccion_ia = f"""
        Actúas como un asistente de lectura experto y accesible. Tu tarea es responder la pregunta del usuario utilizando exclusivamente la base de conocimientos proporcionada a continuación, la cual fue extraída de sus documentos PDF. 
        Si la respuesta no se encuentra en el texto proporcionado, di de manera muy amable que no encontraste esa información específica en los documentos actuales.
        Sé claro, directo y conciso en tu respuesta para facilitar su lectura en voz alta.

        Base de conocimientos de los PDFs:
        {base_conocimiento[:15000]}

        Pregunta del usuario:
        {pregunta}
        """
        
        try:
            # Llamamos al modelo de Google Gemini para procesar la información de manera rápida
            with st.spinner("Buscando y analizando en tus documentos..."):
                model = genai.GenerativeModel('gemini-2.5-flash') 
                
                # Forzamos una baja temperatura para respuestas lógicas, precisas y veloces
                resultado = model.generate_content(
                    instruccion_ia,
                    generation_config={"temperature": 0.3}
                )
                respuesta_bot = resultado.text
        except Exception as e:
            respuesta_bot = f"Lo siento, ocurrió un problema técnico al conectar con el cerebro de IA: {e}"

    # 3. Mostrar la respuesta en texto para los usuarios visuales
    with st.chat_message("assistant"):
        st.markdown(respuesta_bot)
    st.session_state.messages.append({"role": "assistant", "content": respuesta_bot})
    
    # Limpiar el texto de comillas o saltos extraños para evitar errores en JavaScript
    respuesta_limpia = respuesta_bot.replace('"', '\\"').replace('\n', ' ')

    # 4. Inyección interactiva de Ondas Animadas (CSS) y Lectura en voz alta (JS)
    componente_accesible = f"""
    <div id="contenedor-ondas" style="display: flex; align-items: center; gap: 6px; margin-top: 15px; padding: 10px; background-color: #eff6ff; border-radius: 8px; border-left: 4px solid #2563eb; font-family: sans-serif;">
        <span style="color: #1e40af; font-size: 14px; font-weight: bold; margin-right: 10px;">🔊 Leyendo en voz alta:</span>
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
        // Cancelar lecturas previas pendientes
        window.speechSynthesis.cancel();

        var mensajeVoz = new SpeechSynthesisUtterance("{respuesta_limpia}");
        mensajeVoz.lang = 'es-ES';

        // Ocultar las ondas dinámicas en la pantalla al finalizar el audio
        mensajeVoz.onend = function(event) {{
            document.getElementById("contenedor-ondas").style.display = "none";
        }};

        window.speechSynthesis.speak(mensajeVoz);
    </script>
    """
    
    st.components.v1.html(componente_accesible, height=75)