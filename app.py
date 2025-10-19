import streamlit as st
# Importación directa y completa. Usaremos el alias 'genai' para simplicidad.
import google.generativeai as genai 
import json
from PIL import Image

# --- 1. CONFIGURACIÓN E INICIALIZACIÓN ---
# Recuperar la clave API de forma segura desde Streamlit Secrets
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except KeyError:
    st.error("Error: La clave API (GEMINI_API_KEY) no está configurada. Consulta la guía de configuración de Secrets.")
    st.stop()

# Inicializar el cliente de Gemini (CORRECCIÓN: La sintaxis de inicialización es correcta con la versión forzada)
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
    
    # Hemos añadido la variable estilo_ilustracion a la descripción del prompt_imagen
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
def generar_imagen_con_gemini(prompt_imagen):
    """Llama al modelo Imagen (image-001) para generar una imagen."""
    try:
        image_response = client.models.generate_content(
            model='image-001',
            contents=[prompt_imagen]
        )
        # image_response.images[0].image contiene el objeto PIL Image que st.image espera
        return image_response.images[0].image 
    except Exception as e:
        # Aquí se captura el error si la generación de imagen falla
        st.warning(f"Error al intentar generar imagen: {e}. Saltando esta escena.")
        return None

# --- 5. LÓGICA PRINCIPAL DE LA APLICACIÓN ---

if st.sidebar.button("¡Crear Cuento Ilustrado!"):
    
    if not intereses:
        st.error("Por favor, introduce los intereses y personajes del niño para empezar.")
    else:
        # 1. GENERACIÓN DEL CUENTO Y PROMPTS
        with st.spinner("Conectando con Gemini para la historia..."):
            try:
                # Usamos el modelo más rápido y potente en JSON
                response = client.models.generate_content(
                    model='gemini-1.5-flash',
                    contents=generar_prompt_cuento(intereses, edad, tematica, estilo_ilustracion),
                    config={"response_mime_type": "application/json"}
                )
                
                datos_cuento = json.loads(response.text)
                
                st.success(f"¡Cuento Generado: {datos_cuento['titulo']}!")
                st.header(datos_cuento['titulo'])
                
            except Exception as e:
                st.error("Ocurrió un error al generar el cuento (fase de texto).")
                st.exception(e)
                st.stop()
        
        # 2. GENERACIÓN DE IMÁGENES POR ESCENA
        st.markdown("---")
        for i, escena in enumerate(datos_cuento['escenas']):
            col1, col2 = st.columns([1, 2]) # Dividimos la pantalla

            with col1:
                st.markdown(f"**Escena {i+1}**")
                st.markdown(escena['texto'])
                st.caption(f"🎨 Prompt para la IA: `{escena['prompt_imagen']}`")

            with col2:
                with st.spinner(f"Generando ilustración para la escena {i+1} (puede tardar unos segundos)..."):
                    imagen_generada = generar_imagen_con_gemini(escena['prompt_imagen'])
                    if imagen_generada:
                        st.image(imagen_generada, caption=f"Ilustración para la Escena {i+1}", use_column_width=True)
                    else:
                        st.error("No se pudo generar la ilustración de esta escena.")
            st.markdown("---") 
            
        st.markdown(f"**Moraleja:** *{datos_cuento['moraleja']}*")

st.sidebar.markdown("""
---
**Modelos de IA:** Gemini 1.5 Flash (texto) e Imagen (ilustraciones).
""")
