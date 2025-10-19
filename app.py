import streamlit as st
# Usamos la importación directa y completa para evitar el conflicto
import google.generativeai as genai 
import json
from PIL import Image

# --- 1. CONFIGURACIÓN E INICIALIZACIÓN ---
# Recuperar la clave API de forma segura desde Streamlit Secrets
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except KeyError:
    st.error("Error: La clave API (GEMINI_API_KEY) no está configurada.")
    st.stop()

# Inicializar el cliente de Gemini
# Usamos el nombre del paquete completo en lugar de 'genai'
client = genai.Client(api_key=API_KEY)

# Configuración de la interfaz
st.set_page_config(
    page_title="Generador de Cuentos Ilustrados con Gemini",
    layout="wide"
)
st.title("Generador de Cuentos Ilustrados 🎨✨")
st.subheader("Tu propia biblioteca de cuentos personalizados con imágenes de IA")

# --- 2. ENTRADAS DEL USUARIO ---
st.sidebar.header("Parámetros del Cuento")

intereses = st.sidebar.text_input(
    "1. Intereses y personajes principales:",
    placeholder="Ej: Un gatito valiente que explora el espacio y un ratoncito genio"
)

edad = st.sidebar.slider(
    "2. Edad del niño (vocabulario y complejidad):",
    min_value=3, max_value=12, value=6
)

tematica = st.sidebar.selectbox(
    "3. Valor principal a enseñar:",
    ["Amistad", "Valentía", "Empatía", "Generosidad", "Curiosidad"]
)

estilo_ilustracion = st.sidebar.selectbox(
    "4. Estilo de las ilustraciones:",
    ["Acuarela infantil", "Dibujo animado 2D", "Estilo Pixar 3D", "Lápices de colores", "Pastel suave"]
)

st.sidebar.markdown("---")

# --- 3. FUNCIÓN GENERADORA DEL PROMPT (Texto a JSON) ---

def generar_prompt_cuento(intereses, edad, tematica, estilo_ilustracion):
    """Genera el prompt estructurado para el modelo Gemini, incluyendo el estilo de imagen."""
    
    prompt = f"""
    Eres un escritor experto en cuentos infantiles. Tu tarea es crear una historia de 4 escenas y 
    generar, para cada escena, una descripción de la imagen que la acompaña (el 'prompt_imagen').
    
    Historia: Para un niño de {edad} años. Debe ser divertido y promover el valor de la {tematica}.
    Personajes: {intereses}.
    
    Las descripciones de imagen deben ser para un generador de imágenes y tener el estilo '{estilo_ilustracion}'.
    
    Devuelve la respuesta estrictamente en formato JSON con la siguiente estructura:
    
    {{
      "titulo": "Título atractivo del cuento",
      "escenas": [
        {{
          "texto": "Párrafo del cuento para la Escena 1.",
          "prompt_imagen": "Descripción detallada y artística (estilo {estilo_ilustracion} para niños) de la escena 1, lista para un generador de imágenes."
        }},
        {{
          "texto": "Párrafo del cuento para la Escena 2.",
          "prompt_imagen": "Descripción detallada y artística (estilo {estilo_ilustracion} para niños) de la escena 2, lista para un generador de imágenes."
        }},
        {{
          "texto": "Párrafo del cuento para la Escena 3.",
          "prompt_imagen": "Descripción detallada y artística (estilo {estilo_ilustracion} para niños) de la escena 3, lista para un generador de imágenes."
        }},
        {{
          "texto": "Párrafo del cuento para la Escena 4.",
          "prompt_imagen": "Descripción detallada y artística (estilo {estilo_ilustracion} para niños) de la escena 4, lista para un generador de imágenes."
        }}
      ],
      "moraleja": "Moraleja simple al final del cuento."
    }}
    """
    return prompt

# --- 4. FUNCIÓN PARA GENERAR UNA SOLA IMAGEN (Text-to-Image) ---
@st.cache_data(show_spinner=False)
