import streamlit as st
import asyncio
import json
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.team import Team
from agno.tools.reasoning import ReasoningTools
from agno.tools.calculator import CalculatorTools
import PyPDF2
import io
import zipfile
import tempfile
import os

load_dotenv()

# 🎨 Config
st.set_page_config(page_title="🧠 AGNO HR", layout="wide")
st.markdown("<h1 style='text-align: center;'>🧠 AGNO HR</h1>", unsafe_allow_html=True)

# 📄 Funciones
def extract_pdf_text(pdf_content):
    try:
        return "".join([page.extract_text() for page in PyPDF2.PdfReader(io.BytesIO(pdf_content)).pages])
    except:
        return ""

def process_zip(zip_file):
    cvs_data, names = [], []
    with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp:
        tmp.write(zip_file.read())
        tmp_path = tmp.name
    
    with zipfile.ZipFile(tmp_path, 'r') as zip_ref:
        for file_info in zip_ref.filelist:
            if file_info.filename.lower().endswith('.pdf') and not file_info.is_dir():
                try:
                    text = extract_pdf_text(zip_ref.read(file_info.filename))
                    if len(text.strip()) > 50:
                        cvs_data.append(text[:2000])
                        names.append(file_info.filename)
                except:
                    continue
    
    os.unlink(tmp_path)
    return cvs_data, names

# 🧠 Agentes
async def analyze_cv(content, role, mode="optimize"):
    if mode == "optimize":
        prompt = f"CV para {role}:\n{content[:2500]}\n\nAnaliza y sugiere 5 mejoras específicas, keywords faltantes y puntaje 1-10."
        agent = Agent(model=OpenAIChat(id="gpt-4o"), tools=[ReasoningTools()], 
                     instructions="Experto optimización CVs. Sé específico y práctico.", markdown=True)
    else:
        prompt = f"""
        Analiza estos CVs para: {role}
        
        {content}
        
        DEVUELVE JSON EXACTO:
        {{
          "candidatos": [
            {{
              "nombre": "Nombre extraído del CV",
              "archivo": "archivo.pdf", 
              "puntaje": 85,
              "experiencia_anos": 5,
              "skills": ["Python", "SQL"],
              "educacion": "Ingeniería de Sistemas",
              "recomendacion": "Excelente match para el cargo"
            }}
          ]
        }}
        """
        agent = Agent(model=OpenAIChat(id="gpt-4o"), tools=[ReasoningTools(), CalculatorTools()], 
                     instructions="Experto RRHH. SIEMPRE devuelve JSON válido con estructura exacta.", markdown=True)
    
    response = await agent.arun(prompt)
    return response.content

# 🎯 Interface
mode = st.radio("🎯 Modo:", ["📄 Optimizar CV", "📦 Selección Masiva", "📝 Generar Oferta"], horizontal=True)

if mode == "📄 Optimizar CV":
    # Modo individual
    uploaded_file = st.file_uploader("📄 CV:", type=["pdf", "txt"])
    target_role = st.text_input("🎯 Cargo objetivo:")
    
    if st.button("🔍 Analizar") and uploaded_file and target_role:
        with st.spinner("Analizando..."):
            content = extract_pdf_text(uploaded_file.read()) if uploaded_file.type == "application/pdf" else str(uploaded_file.read(), "utf-8")
            if content.strip():
                analysis = asyncio.run(analyze_cv(content, target_role, "optimize"))
                st.markdown("### 📊 Análisis:")
                st.markdown(analysis)
            else:
                st.error("❌ No se pudo extraer texto")

elif mode == "📝 Generar Oferta":
    # Generador de ofertas
    st.markdown("### 📝 Generador de Ofertas Laborales")
    col1, col2 = st.columns(2)
    with col1:
        job_title = st.text_input("🎯 Título del cargo:", placeholder="Desarrollador Senior Python")
        company_name = st.text_input("🏢 Empresa:", placeholder="Tech Solutions SA")
        job_desc = st.text_area("💼 Descripción del cargo:", height=70)
    with col2:
        location = st.text_input("📍 Ubicación:", placeholder="Bogotá, Colombia")
        salary_range = st.text_input("💰 Rango salarial:", placeholder="$3M - $5M COP")
        modality = st.selectbox("🏠 Modalidad:", ["Presencial", "Remoto", "Híbrido"])
    
    if st.button("📝 Generar Oferta") and job_title and company_name and job_desc:
        with st.spinner("Generando oferta profesional..."):
            offer_prompt = f"""
            Crea una oferta laboral profesional para: {job_title} en {company_name}
            
            Descripción: {job_desc}
            Ubicación: {location} | Modalidad: {modality} | Salario: {salary_range}
            
            GENERA OFERTA PROFESIONAL:
            
            🔸 TÍTULO ATRACTIVO (optimizado para búsquedas)
            🔸 SOBRE LA EMPRESA (2-3 líneas que generen interés)
            🔸 MISIÓN DEL CARGO (qué impacto tendrá)
            🔸 RESPONSABILIDADES CLAVE (5 principales, específicas)
            🔸 REQUISITOS OBLIGATORIOS (técnicos y experiencia)
            🔸 REQUISITOS DESEABLES (que marquen diferencia)  
            🔸 QUÉ OFRECEMOS (beneficios atractivos y competitivos)
            🔸 PROCESO DE SELECCIÓN (pasos claros)
            🔸 CALL TO ACTION (cómo aplicar)
            
            IMPORTANTE: 
            - Usa lenguaje profesional pero cercano
            - Incluye keywords para ATS (sistemas de tracking)
            - Que sea atractivo para candidatos top
            - Sin asteriscos, solo texto limpio y viñetas (•)
            """
            
            offer_agent = Agent(model=OpenAIChat(id="gpt-4o"), tools=[], 
                              instructions="Eres un experto en ofertas laborales. Devuelve ÚNICAMENTE el texto de la oferta, sin explicaciones adicionales.", markdown=False)
            offer = asyncio.run(offer_agent.arun(offer_prompt))
            
            # Limpiar respuesta si tiene metadata
            clean_offer = offer.content if hasattr(offer, 'content') else str(offer)
            # Extraer solo el texto principal si hay metadata
            if "based on the gathered information" in clean_offer or "ReasoningStep" in clean_offer:
                # Buscar el texto real de la oferta
                lines = clean_offer.split('\n')
                clean_lines = []
                for line in lines:
                    if not any(x in line.lower() for x in ['reasoning', 'metadata', 'confidence', 'next_action', 'based on']):
                        clean_lines.append(line)
                clean_offer = '\n'.join(clean_lines).strip()
            
            st.markdown("### 📋 Oferta Laboral Generada:")
            st.text_area("📄 Oferta completa:", value=clean_offer, height=400, disabled=True)
            
            # Botón para generar versión LinkedIn
            if st.button("🔗 Versión para LinkedIn"):
                linkedin_prompt = f"""
                Convierte esta oferta en post LinkedIn profesional pero atractivo:
                
                {offer[:1000]}
                
                ESTRUCTURA LINKEDIN:
                🚀 Hook inicial impactante
                📍 {location} | {modality} | {salary_range}
                
                Lo que harás:
                • [Responsabilidad top]
                • [Responsabilidad top]
                
                Buscamos:
                • [Requisito clave]
                • [Requisito clave]
                
                Ofrecemos:
                • [Beneficio atractivo]
                • [Beneficio atractivo]
                
                👥 Etiqueta a alguien que le interese
                🔗 Aplica en comentarios o DM
                
                [3-4 hashtags relevantes]
                
                MÁXIMO 280 caracteres. Solo texto plano, sin markdown.
                """
                linkedin_agent = Agent(model=OpenAIChat(id="gpt-4o"), tools=[ReasoningTools()], 
                                     instructions="Especialista LinkedIn. Posts virales de empleo, formato profesional.", markdown=False)
                linkedin_post = asyncio.run(linkedin_agent.arun(linkedin_prompt))
                
                st.markdown("### 🔗 Post para LinkedIn:")
                st.text_area("📱 Post LinkedIn:", value=linkedin_post, height=200, disabled=True)

else:
    # Modo masivo
    team_mode = st.radio("IA:", ["⚡ Single", "🤝 Team"], horizontal=True)
    zip_file = st.file_uploader("📦 ZIP:", type="zip")
    col1, col2 = st.columns(2)
    with col1:
        job_desc = st.text_area("💼 Cargo:", height=70)
        skills = st.text_input("🛠️ Skills:")
    with col2:
        exp = st.number_input("📅 Exp:", 0, 30, 2)
        location = st.text_input("📍 Ubicación:")

    # Session state
    if "results" not in st.session_state:
        st.session_state.results = None
    if "interviews" not in st.session_state:
        st.session_state.interviews = []

    if st.button("🚀 Analizar") and zip_file and job_desc:
        with st.spinner("Procesando..."):
            cvs_data, names = process_zip(zip_file)
            if cvs_data:
                content = "\n---\n".join([f"{n}: {cv}" for cv, n in zip(cvs_data, names)])
                
                if "Team" in team_mode:
                    team = Team(model=OpenAIChat(id="gpt-4o"), 
                               members=[Agent(name="A", tools=[ReasoningTools()], instructions="Analizar CVs y extraer información"),
                                       Agent(name="B", tools=[CalculatorTools()], instructions="Puntuar candidatos del 1-100")],
                               instructions="Trabajen juntos. DEVUELVAN JSON: {candidatos: [{nombre, archivo, puntaje, skills, educacion, recomendacion}]}", markdown=True)
                    response = asyncio.run(team.arun(f"Analicen para cargo: {job_desc}\nSkills requeridos: {skills}\nExperiencia: {exp}años\n\nCVs:\n{content}"))
                    result_text = response.content
                else:
                    result_text = asyncio.run(analyze_cv(content, f"{job_desc}. Skills: {skills}. Exp: {exp}años", "batch"))
                
                # Parsear JSON
                try:
                    if "```json" in result_text:
                        result_text = result_text.split("```json")[1].split("```")[0]
                    elif "```" in result_text:
                        result_text = result_text.split("```")[1].split("```")[0]
                    
                    results = json.loads(result_text)
                    st.session_state.results = results
                    
                    if "candidatos" in results:
                        df = pd.DataFrame(results["candidatos"]).sort_values("puntaje", ascending=False)
                        st.success(f"✅ {len(df)} candidatos analizados")
                        
                        # Mostrar tabla completa con todas las columnas
                        display_cols = ["nombre", "puntaje", "skills", "educacion", "recomendacion"]
                        available_cols = [col for col in display_cols if col in df.columns]
                        st.dataframe(df[available_cols], use_container_width=True)
                    else:
                        st.markdown("### 📊 Resultados:")
                        st.markdown(result_text)
                        
                except json.JSONDecodeError:
                    # Si falla JSON, mostrar resultado directo
                    st.markdown("### 📊 Análisis:")
                    st.markdown(result_text)
                    # Crear estructura básica para funcionalidades
                    st.session_state.results = {
                        "candidatos": [{"nombre": f"Candidato {i+1}", "puntaje": 75, "recomendacion": "Analizado"} 
                                     for i in range(len(names))]
                    }
            else:
                st.error("❌ No se encontraron CVs")

    # Extras para modo masivo
    if st.session_state.results and "candidatos" in st.session_state.results:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("❓ Preguntas para #1"):
                df = pd.DataFrame(st.session_state.results["candidatos"])
                if len(df) > 0:
                    top = df.sort_values("puntaje", ascending=False).iloc[0]
                    questions = asyncio.run(analyze_cv(f"Candidato: {top['nombre']}, Skills: {top.get('skills', [])}", job_desc, "optimize"))
                    st.markdown(f"### 🎤 Preguntas para {top['nombre']}:")
                    st.markdown(questions)
        
        with col2:
            candidates = [c["nombre"] for c in st.session_state.results["candidatos"]]
            if candidates:
                selected = st.selectbox("📅 Agendar:", candidates)
                if st.button("📅 Agendar"):
                    st.session_state.interviews.append({"candidato": selected, "fecha": datetime.now().strftime("%Y-%m-%d")})
                    st.success(f"✅ {selected} agendado")

        if st.session_state.interviews:
            st.dataframe(pd.DataFrame(st.session_state.interviews), use_container_width=True)
        
        # 💬 Chat
        st.markdown("### 💬 Consultas sobre Resultados")
        user_q = st.text_input("🤔 Pregunta:", placeholder="¿Por qué eligió este candidato?")
        
        if st.button("📤 Preguntar") and user_q:
            with st.spinner("Analizando..."):
                df_str = pd.DataFrame(st.session_state.results["candidatos"]).to_string()
                chat_prompt = f"Pregunta: {user_q}\nDatos candidatos: {df_str}\nCargo: {job_desc}\nResponde basándote solo en estos datos."
                
                agent = Agent(model=OpenAIChat(id="gpt-4o"), tools=[ReasoningTools()], 
                             instructions="Experto RRHH. Responde consultas sobre candidatos analizados.", markdown=True)
                answer = asyncio.run(agent.arun(chat_prompt))
                
                st.markdown(f"**🤖 Respuesta:** {answer.content}")

# Info
if mode == "📄 Optimizar CV" and (not uploaded_file or not target_role):
    st.info("📄 Sube CV y especifica cargo objetivo")
elif mode == "📦 Selección Masiva" and (not zip_file or not job_desc):
    st.info("📦 Sube ZIP con CVs y describe el cargo")
elif mode == "📝 Generar Oferta" and (not job_title or not company_name or not job_desc):
    st.info("📝 Completa título, empresa y descripción del cargo")