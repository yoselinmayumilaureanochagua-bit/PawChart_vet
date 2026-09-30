import streamlit as st
from openai import OpenAI
import base64
from PIL import Image
import io

# Configuración de la página
st.set_page_config(
    page_title="VetClinic AI - Historia Clínica y Radiología",
    page_icon="🐾",
    layout="wide"
)

# Estilos visuales personalizados
st.markdown("""
    <style>
    .stApp {
        background-color: #F8FAFC;
        font-family: 'Inter', sans-serif;
    }
    section[data-testid="stSidebar"] {
        background-color: #1E293B;
        color: #FFFFFF;
    }
    section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] label {
        color: #F1F5F9 !important;
    }
    h1, h2, h3 {
        color: #0F172A;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #E2E8F0;
        border-radius: 8px 8px 0px 0px;
        padding: 10px 20px;
        color: #0F172A;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #0E9F6E !important;
        color: #FFFFFF !important;
    }
    div.stButton > button:first-child {
        background-color: #0E9F6E;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 12px 24px;
        font-weight: bold;
        font-size: 16px;
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# Encabezado
st.markdown("<h1 style='color: #0E9F6E; text-align: center;'>🐾 VetClinic AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #64748B; font-size: 16px;'>Historia Clínica e Interpretación Radiológica con IA</p>", unsafe_allow_html=True)
st.divider()

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuración")
    api_key = st.text_input("OpenAI API Key", type="password", help="Clave de OpenAI para la IA")

if 'reporte' not in st.session_state:
    st.session_state.reporte = None

# Pestañas
tab1, tab2, tab3 = st.tabs(["📋 Historia Clínica", "🦴 Radiología IA", "📑 Informe"])

# TAB 1
with tab1:
    st.markdown("### 🐶 Datos del Paciente")
    tutor_nombre = st.text_input("Nombre del Tutor", "María García")
    tutor_tel = st.text_input("Teléfono", "+51 987 654 321")
    mascota_nombre = st.text_input("Mascota", "Rocko")
    especie = st.selectbox("Especie", ["Canino", "Felino", "Equino", "Exótico"])
    raza = st.text_input("Raza", "Bulldog Francés")
    
    col1, col2 = st.columns(2)
    with col1:
        edad = st.text_input("Edad", "3 años")
        peso = st.number_input("Peso (kg)", min_value=0.1, value=12.4)
    with col2:
        sexo = st.selectbox("Sexo", ["Macho Entero", "Macho Castrado", "Hembra Entera", "Hembra Esterilizada"])
        ecc = st.slider("Condición Corporal (1-9)", 1, 9, 5)

    st.markdown("### 🩺 Constantes Fisiológicas")
    temp = st.text_input("Temp (°C)", "38.8")
    fc = st.text_input("FC (ppm)", "120")
    fr = st.text_input("FR (rpm)", "32")
    motivo_consulta = st.text_area("Motivo de Consulta", "Tos persistente nocturna.")

# TAB 2
with tab2:
    st.markdown("### 📷 Carga de Placa Radiográfica")
    uploaded_file = st.file_uploader("Subir foto o archivo de la placa", type=["png", "jpg", "jpeg"])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Placa cargada", use_column_width=True)
        
    zona_anatomica = st.selectbox("Región Anatómica", ["Tórax", "Abdomen", "Miembro Anterior", "Miembro Posterior", "Columna/Cráneo"])
    proyeccion = st.selectbox("Proyección", ["Lateral Izquierda (LL)", "Lateral Derecha (RL)", "Ventrodorsal (VD)", "Dorsoventral (DV)"])
    sospecha = st.text_input("Sospecha Clínica", "Cardiomegalia / Colapso Traqueal")
    
    btn_analizar = st.button("✨ Generar Diagnóstico con IA")

    if btn_analizar:
        if not api_key:
            st.error("⚠️️ Ingresa tu API Key de OpenAI en el menú lateral.")
        elif uploaded_file is None:
            st.warning("⚠️ Subes una foto de la radiografía primero.")
        else:
            with st.spinner("Analizando radiografía con IA..."):
                try:
                    buffered = io.BytesIO()
                    image.save(buffered, format="JPEG")
                    base64_image = base64.b64encode(buffered.getvalue()).decode('utf-8')
                    
                    client = OpenAI(api_key=api_key)
                    
                    prompt_vet = f"""
                    Actúa como Especialista en Radiología Veterinaria.
                    Analiza la radiografía adjunta:
                    - Paciente: {mascota_nombre} ({especie}, {raza}, {edad}, {peso} kg).
                    - Región: {zona_anatomica} | Proyección: {proyeccion}.
                    - Motivo/Sospecha: {motivo_consulta} | {sospecha}.

                    Responde en formato Markdown:
                    1. **CALIDAD Y PROYECCIÓN**
                    2. **HALLAZGOS RADIOLÓGICOS DETALLADOS** (Si es tórax, estima el VHS).
                    3. **DIAGNÓSTICOS DIFERENCIALES Y CONCLUSIÓN**
                    4. **RECOMENDACIONES CLÍNICAS**

                    *Nota: Indicar que este reporte es sugerencia de IA y requiere validación veterinaria.*
                    """

                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": prompt_vet},
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:image/jpeg;base64,{base64_image}"
                                        }
                                    }
                                ]
                            }
                        ],
                        max_tokens=1000
                    )

                    st.session_state.reporte = response.choices[0].message.content
                    st.success("✅ ¡Análisis completado! Revisa la pestaña 'Informe'.")

                except Exception as e:
                    st.error(f"Error: {e}")

# TAB 3
with tab3:
    st.markdown("### 📄 Expediente e Informe")
    if st.session_state.reporte:
        st.info(f"**Paciente:** {mascota_nombre} | **Especie:** {especie} ({raza}) | **Tutor:** {tutor_nombre}")
        st.divider()
        st.markdown(st.session_state.reporte)
    else:
        st.warning("Aún no has analizado ninguna placa.")
