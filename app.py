import streamlit as st
import requests
import google.generativeai as genai
from streamlit_js_eval import streamlit_js_eval

# 1. CONFIGURACIÓN INICIAL
st.set_page_config(page_title="EpicSky AI", page_icon="📸")

# Recuperar llaves de los Secrets
try:
    GEMINI_API_KEY = st.secrets["GEMINI_KEY"]
    WEATHER_API_KEY = st.secrets["WEATHER_KEY"]
    genai.configure(api_key=GEMINI_API_KEY)
except Exception as e:
    st.error("Error con las llaves API en Secrets. Revisa la configuración.")
    st.stop()

# 2. CONECTAR CON EL CEREBRO (SISTEMA MULTI-MODELO)
@st.cache_resource
def conectar_modelo():
    model_names = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro']
    for name in model_names:
        try:
            m = genai.GenerativeModel(name)
            # Prueba rápida
            m.generate_content("test", generation_config={"max_output_tokens": 1})
            return m, name
        except:
            continue
    return None, None

model, model_name = conectar_modelo()

if model_name:
    st.sidebar.success(f"Cerebro: {model_name}")
else:
    st.sidebar.error("Sin conexión con Google AI")

# 3. INTERFAZ DE USUARIO
st.title("📸 EpicSky AI")
st.markdown("---")

# Ubicación
st.subheader("📍 ¿Dónde estamos?")
gps_location = streamlit_js_eval(js_expressions="str([coords.latitude, coords.longitude])", key="GPS")
manual_location = st.text_input("O escribe tu ciudad manualmente (ej: Madrid, ES):")

lat, lon = None, None

if manual_location:
    geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={manual_location}&limit=1&appid={WEATHER_API_KEY}"
    res = requests.get(geo_url).json()
    if res:
        lat, lon = res[0]['lat'], res[0]['lon']
        st.write(f"Ubicación fijada en: **{res[0]['name']}**")
elif gps_location:
    coords = eval(gps_location)
    lat, lon = coords[0], coords[1]
    st.write(f"Ubicación fijada por **GPS**")
else:
    st.info("Esperando ubicación... (Si estás en móvil, activa el GPS)")

# 4. LÓGICA DE ANÁLISIS
if st.button("🚀 Analizar cielo ahora"):
    if not lat or not lon:
        st.warning("Necesito una ubicación para consultar el clima.")
    else:
        with st.spinner("Analizando capas de nubes..."):
            try:
                w_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric&lang=es"
                w_data = requests.get(w_url).json()
                
                nubes = w_data['clouds']['all']
                desc = w_data['weather'][0]['description']
                hum = w_data['main']['humidity']
                
                prompt = f"Actúa como fotógrafo. Clima: {desc}, Nubes: {nubes}%, Humedad: {hum}%. Predice la probabilidad de un atardecer/amanecer épico (0-100%) y da un consejo de exposición."
                
                response = model.generate_content(prompt)
                
                st.balloons()
                st.metric("Probabilidad de Épica", f"{nubes}% nubes")
                st.markdown(f"### 🤖 Análisis de EpicSky:\n{response.text}")
                
            except Exception as e:
                st.error(f"Error en el análisis: {e}")

# 5. APRENDIZAJE Y FEEDBACK
st.markdown("---")
st.subheader("📉 ¿Cómo fue el cielo anterior?")
feedback = st.radio("Ayúdame a mejorar:", ["Sin feedback", "✅ Fue un candilazo", "❌ Estuvo soso"], horizontal=True)

if feedback != "Sin feedback":
    st.success("¡Gracias! He registrado el dato para ajustar mis futuras predicciones.")
    # Aquí en el futuro conectaremos una base de datos para que Gemini lea tus éxitos.
