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
def generar_imagen_con_gemini(prompt_imagen):
    """Llama al modelo Imagen (image-001) para generar una imagen."""
    try:
        # Usamos el mismo cliente para ambos
        image_response = client.models.generate_content(
            model='image-001',
            contents=[prompt_imagen]
        )
        # image_response.images[0].image contiene el objeto PIL Image
        return image_response.images[0].image 
    except Exception as e:
        # st.error(f"No se pudo generar la imagen para: '{prompt_imagen}'. Error: {e}")
        return None

# --- 5. LÓGICA PRINCIPAL DE LA APLICACIÓN ---

if st.sidebar.button("¡Crear Cuento Ilustrado!"):
    
    if not intereses:
        st.error("Por favor, introduce los intereses y personajes del niño para empezar.")
    else:
        # 1. GENERACIÓN DEL CUENTO Y PROMPTS
        with st.spinner("Conectando con Gemini, creando la historia y las descripciones de imágenes..."):
            try:
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
                st.caption(f"🎨 `{escena['prompt_imagen']}`")

            with col2:
                with st.spinner(f"Generando ilustración para la escena {i+1}..."):
                    imagen_generada = generar_imagen_con_gemini(escena['prompt_imagen'])
                    if imagen_generada:
                        # st.image espera un objeto PIL Image
                        st.image(imagen_generada, caption=f"Ilustración para la Escena {i+1}", use_column_width=True)
                    else:
                        st.warning("No se pudo generar la imagen para esta escena (revisa los logs).")
            st.markdown("---") 
            
        st.markdown(f"**Moraleja:** *{datos_cuento['moraleja']}*")

st.sidebar.markdown("""
---
**Modelos de IA:** Gemini 1.5 Flash (texto) e Imagen (ilustraciones).
""")
