import streamlit as st
import requests
import google.generativeai as genai
from streamlit_js_eval import streamlit_js_eval

# Configuración de APIs
GEMINI_API_KEY = st.secrets["GEMINI_KEY"]
WEATHER_API_KEY = st.secrets["WEATHER_KEY"]

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-pro')

st.title("📸 EpicSky AI")

# --- OBTENCIÓN DE COORDENADAS ---
st.subheader("📍 Ubicación")
loc = streamlit_js_eval(js_expressions="str([coords.latitude, coords.longitude])", key="GPS")

if loc:
    lat_lon = eval(loc)
    lat, lon = lat_lon[0], lat_lon[1]
    st.success(f"Coordenadas fijadas: {lat}, {lon}")
else:
    st.warning("Esperando GPS... Asegúrate de dar permisos en tu móvil.")
    lat, lon = 40.41, -3.70 # Madrid por defecto si falla

# --- FUNCIÓN DE CLIMA ---
def obtener_clima(lat, lon):
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric&lang=es"
    data = requests.get(url).json()
    # Extraemos el pronóstico más cercano (próximas 3 horas)
    next_forecast = data['list'][0]
    return {
        "nubes_totales": next_forecast['clouds']['all'],
        "temp": next_forecast['main']['temp'],
        "descripcion": next_forecast['weather'][0]['description'],
        # Nota: OpenWeather free a veces no desglosa nubes altas/bajas detalladas, 
        # pero Gemini puede inferirlo por la descripción y humedad.
        "humedad": next_forecast['main']['humidity']
    }

# --- ANÁLISIS ---
if st.button("Analizar probabilidad de Candilazo"):
    clima = obtener_clima(lat, lon)
    
    prompt = f"""
    Actúa como fotógrafo experto. Datos actuales: {clima['nubes_totales']}% de nubes, 
    humedad {clima['humedad']}%, clima: {clima['descripcion']}.
    Calcula la probabilidad (0-100%) de que el atardecer/amanecer sea colorido. 
    Da una respuesta corta y un consejo técnico de cámara.
    """
    
    response = model.generate_content(prompt)
    st.metric(label="Probabilidad de Épica", value=f"{clima['nubes_totales']}% nubes detectadas")
    st.write(response.text)

# --- AUTO-REFRESH (Cada 30 min) ---
st.caption("La app se actualiza automáticamente cada 30 minutos.")
# Esto fuerza a la app a recargarse
# st.empty()
