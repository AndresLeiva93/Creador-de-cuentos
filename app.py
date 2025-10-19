import streamlit as st
import google.generativeai as genai 
import json
from PIL import Image

# --- 1. CONFIGURACIÓN E INICIALIZACIÓN ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except KeyError:
    st.error("Error: La clave API (GEMINI_API_KEY) no está configurada.")
    st.stop()

# --- CORRECCIÓN CRÍTICA DE CLIENTE ---
# Configura el SDK de manera global, eliminando el error 'has no attribute Client'.
genai.configure(api_key=API_KEY)

# Definimos 'client' como el propio módulo genai para que el código posterior funcione.
client = genai 

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

# ... (EL CÓDIGO RESTANTE ES EL MISMO)
# El resto del código que usa:
# client.models.generate_content
# funcionará porque ahora 'client' es un alias del módulo 'genai', 
# y la configuración de la API ya está hecha.

# ... (Continúa el resto del código)
# Por favor, usa el resto del código que te proporcioné anteriormente a partir de aquí.
