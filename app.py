import streamlit as st
import google.generativeai as genai
import json # Asegúrate de que json está importado

# --- 1. CONFIGURACIÓN E INICIALIZACIÓN ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except KeyError:
    st.error("Error: La clave API (GEMINI_API_KEY) no está configurada. Consulta la sección 3.")
    st.stop()

# Inicializar el cliente de Gemini para texto
client = genai.Client(api_key=API_KEY)

# Inicializar el cliente para generación de imágenes (esto es lo nuevo)
# Usaremos 'image-001' que es el modelo de Imagen para texto a imagen
image_client = genai.Client(api_key=API_KEY, client_options={"api_version": "v1beta"}) # A veces necesita v1beta

# Configuración de la interfaz
st.set_page_config(
    page_title="Generador de Cuentos Ilustrados con Gemini",
    layout="wide" # Cambiamos a wide para tener más espacio para las imágenes
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

# --- 3. FUNCIÓN GENERADORA DEL PROMPT ---
# (Esta función es la misma que ya tienes, pero la incluimos para contexto)
def generar_prompt_cuento(intereses, edad, tematica, estilo_ilustracion):
    """Genera el prompt estructurado para el modelo Gemini, incluyendo el estilo de imagen."""
    
    prompt = f"""
    Eres un escritor experto en cuentos infantiles. Tu tarea es crear una historia de 4 escenas y 
    generar, para cada escena, una descripción de la imagen que la acompaña (el 'prompt de imagen').
    
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


# --- 4. FUNCIÓN PARA GENERAR UNA SOLA IMAGEN ---
@st.cache_data(show_spinner=False) # Cacha las imágenes para no regenerarlas en cada recarga
def generar_imagen_con_gemini(prompt_imagen):
    """Llama al modelo de Imagen de Google para generar una imagen."""
    try:
        # Usamos el cliente image_client y el modelo de generación de imágenes 'image-001'
        image_response = image_client.models.generate_content(
            model='image-001',
            contents=[prompt_imagen] # El contenido es el prompt para la imagen
        )
        # El resultado es un objeto que contiene los datos de la imagen
        return image_response.images[0] # Tomamos la primera imagen generada
    except Exception as e:
        st.error(f"No se pudo generar la imagen para: '{prompt_imagen}'. Error: {e}")
        return None

# --- 5. LÓGICA PRINCIPAL DE LA APLICACIÓN ---

if st.sidebar.button("¡Crear Cuento Ilustrado!"):
    
    if not intereses:
        st.error("Por favor, introduce los intereses y personajes del niño para empezar.")
    else:
        with st.spinner("Conectando con Gemini para la historia..."):
            try:
                # 1. Generar el cuento y los prompts de imagen (texto a texto)
                response = client.models.generate_content(
                    model='gemini-1.5-flash', # Usamos 1.5-flash por su rapidez y capacidad JSON
                    contents=generar_prompt_cuento(intereses, edad, tematica, estilo_ilustracion),
                    config={"response_mime_type": "application/json"}
                )
                
                datos_cuento = json.loads(response.text)
                
                st.success(f"¡Cuento Generado: {datos_cuento['titulo']}!")
                st.header(datos_cuento['titulo'])
                
                # 2. Generar y mostrar las imágenes para cada escena
                for i, escena in enumerate(datos_cuento['escenas']):
                    col1, col2 = st.columns([1, 2]) # Dividimos la pantalla en 2 columnas

                    with col1:
                        st.markdown(f"**Escena {i+1}**")
                        st.markdown(escena['texto'])
                        st.caption(f"🎨 `{escena['prompt_imagen']}`") # Mostrar el prompt de imagen

                    with col2:
                        # Llamar a la función para generar la imagen
                        with st.spinner(f"Generando ilustración para la escena {i+1}..."):
                            imagen_generada = generar_imagen_con_gemini(escena['prompt_imagen'])
                            if imagen_generada:
                                # st.image espera un objeto PIL Image o bytes
                                st.image(imagen_generada.data, caption=f"Ilustración para la Escena {i+1}", use_column_width=True)
                            else:
                                st.warning("No se pudo generar la imagen para esta escena.")
                    st.markdown("---") # Separador entre escenas
                    
                st.markdown(f"**Moraleja:** *{datos_cuento['moraleja']}*")

            except Exception as e:
                st.error(f"Ocurrió un error al generar el cuento o las imágenes.")
                st.exception(e)

st.sidebar.markdown("""
---
**Modelos de IA:** Gemini 1.5 Flash (texto) e Imagen (ilustraciones).
**Ventaja:** Historias completas con imágenes generadas automáticamente.
""")
