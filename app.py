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

# --- OBTENCIÓN DE COORDENADAS MEJORADA ---
st.subheader("📍 Ubicación")
col_gps, col_manual = st.columns([2, 1])

with col_gps:
    loc = streamlit_js_eval(js_expressions="str([coords.latitude, coords.longitude])", key="GPS_FIX")

lat, lon = None, None

if loc:
    try:
        lat_lon = eval(loc)
        lat, lon = lat_lon[0], lat_lon[1]
        st.success(f"GPS detectado: {lat}, {lon}")
    except:
        st.error("Error leyendo GPS.")

if not lat:
    with col_manual:
        manual_city = st.text_input("O escribe tu ciudad:")
        if manual_city:
            # Usamos una búsqueda rápida para obtener coordenadas de la ciudad
            geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={manual_city}&limit=1&appid={WEATHER_API_KEY}"
            geo_data = requests.get(geo_url).json()
            if geo_data:
                lat, lon = geo_data[0]['lat'], geo_data[0]['lon']
                st.success(f"Ubicación manual: {geo_data[0]['name']}")

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
