import streamlit as st
from google import genai

# --- 1. CONFIGURACIÓN E INICIALIZACIÓN ---
# Recuperar la clave API de forma segura desde Streamlit Secrets
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except KeyError:
    st.error("Error: La clave API (GEMINI_API_KEY) no está configurada. Consulta la sección 3.")
    st.stop()

# Inicializar el cliente de Gemini
client = genai.Client(api_key=API_KEY)

# Configuración de la interfaz
st.set_page_config(
    page_title="Generador de Cuentos en la Nube con Gemini",
    layout="centered"
)
st.title("Generador de Cuentos Ilustrados ☁️✨")
st.subheader("Usa la potencia de Gemini para crear historias y descripciones de imágenes")

# --- 2. ENTRADAS DEL USUARIO ---
st.sidebar.header("Parámetros del Cuento")

intereses = st.sidebar.text_input(
    "1. Intereses y personajes:",
    placeholder="Ej: Un perro salchicha detective y un loro sabio"
)

edad = st.sidebar.slider(
    "2. Edad del niño (para ajustar vocabulario):",
    min_value=3, max_value=12, value=6
)

tematica = st.sidebar.selectbox(
    "3. Valor principal a enseñar:",
    ["Amistad", "Valentía", "Empatía", "Generosidad"]
)
st.sidebar.markdown("---")

# --- 3. FUNCIÓN GENERADORA DEL PROMPT ---

def generar_prompt_cuento(intereses, edad, tematica):
    """Genera el prompt estructurado para el modelo Gemini."""
    
    # Se usa JSON para asegurar que el modelo devuelve una estructura fácil de parsear
    prompt = f"""
    Eres un escritor experto en cuentos infantiles. Tu tarea es crear una historia de 4 escenas y 
    generar, para cada escena, una descripción de la imagen que la acompaña (el 'prompt de imagen').
    
    Historia: Para un niño de {edad} años. Debe ser divertido y promover el valor de la {tematica}.
    Personajes: {intereses}.
    
    Devuelve la respuesta estrictamente en formato JSON con la siguiente estructura:
    
    {{
      "titulo": "Título atractivo del cuento",
      "escenas": [
        {{
          "texto": "Párrafo del cuento para la Escena 1.",
          "prompt_imagen": "Descripción detallada y artística (estilo acuarela para niños) de la escena 1, lista para un generador de imágenes."
        }},
        // ... (otras 3 escenas más)
      ],
      "moraleja": "Moraleja simple al final del cuento."
    }}
    """
    return prompt

# --- 4. LÓGICA DE LA APLICACIÓN ---

if st.sidebar.button("¡Crear Cuento Ilustrado!"):
    
    if not intereses:
        st.error("Por favor, introduce los intereses del niño para empezar.")
    else:
        with st.spinner("Conectando con Gemini, creando la historia y los prompts de imágenes..."):
            try:
                # 1. Llamada a la API de Gemini
                response = client.models.generate_content(
                    model='gemini-2.5-flash', # Un modelo rápido y potente
                    contents=generar_prompt_cuento(intereses, edad, tematica),
                    config={"response_mime_type": "application/json"} # Pedir JSON
                )
                
                # 2. Procesar la respuesta JSON
                import json
                datos_cuento = json.loads(response.text)
                
                # 3. Mostrar el cuento estructurado
                st.success(f"¡Cuento Generado: {datos_cuento['titulo']}!")
                st.header(datos_cuento['titulo'])
                
                for i, escena in enumerate(datos_cuento['escenas']):
                    st.markdown(f"**Escena {i+1}**")
                    st.markdown(escena['texto'])
                    st.info(f"💡 **Sugerencia de Ilustración:** {escena['prompt_imagen']}")
                    st.markdown("---")
                    
                st.markdown(f"**Moraleja:** *{datos_cuento['moraleja']}*")

            except Exception as e:
                st.error(f"Error al generar el cuento. ¿Está correcta la clave API?")
                st.exception(e)

st.sidebar.markdown("""
---
**Modelo de IA:** Gemini 2.5 Flash (Google)
**Ventaja:** Permite solicitar prompts de imagen para ilustraciones.
""")
