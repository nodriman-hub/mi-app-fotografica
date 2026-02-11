import streamlit as st
import requests
import google.generativeai as genai

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="EpicSky - Predictor de Candilazos", layout="centered")

# Aquí introduciremos tus llaves en el siguiente paso de seguridad
GEMINI_API_KEY = st.secrets["GEMINI_KEY"]
WEATHER_API_KEY = st.secrets["WEATHER_KEY"]

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-pro')

st.title("📸 EpicSky AI")
st.subheader("Tu predictor de cielos épicos")

# --- LOCALIZACIÓN ---
loc_method = st.radio("Método de ubicación:", ["Automática (GPS)", "Manual"])

lat, lon = None, None

if loc_method == "Manual":
    city = st.text_input("Introduce tu ciudad o coordenadas:")
    if city:
        # Simplificación para el prototipo
        st.info("Buscando datos para: " + city)
        # Aquí iría la lógica de geocodificación
else:
    st.write("📍 Usando ubicación de red...")
    # El GPS automático se activa al desplegar en Streamlit Cloud

# --- LÓGICA DE CLIMA ---
if st.button("Analizar cielo ahora"):
    # Simulación de llamada a API cada 30 min
    st.write("🔄 Consultando satélites y capas de nubes...")
    
    # Aquí la app conecta con OpenWeather y envía los datos a Gemini
    prompt = f"Analiza estos datos meteorológicos (Nubes altas: 50%, Medias: 20%, Bajas: 5%) y dime la probabilidad de candilazo en un % y un consejo."
    response = model.generate_content(prompt)
    
    st.success(f"### Resultado: {response.text}")

# --- SECCIÓN DE APRENDIZAJE (FEEDBACK) ---
st.divider()
st.write("¿Acertó la predicción anterior?")
col1, col2 = st.columns(2)
with col1:
    if st.button("✅ ¡Fue épico!"):
        st.write("¡Genial! Guardo estos datos para mejorar.")
with col2:
    if st.button("❌ Fue un fiasco"):
        st.write("Vaya... analizaré qué falló en la capa de nubes.")
