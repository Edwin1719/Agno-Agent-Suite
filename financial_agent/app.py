import streamlit as st
import asyncio
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.team import Team
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.yfinance import YFinanceTools
from agno.tools.reasoning import ReasoningTools
from agno.tools.calculator import CalculatorTools
from agno.tools.newspaper4k import Newspaper4kTools

load_dotenv()

# 🎨 Config + Título centrado
st.set_page_config(page_title="🚀 AGNO FINANCE", layout="wide")
st.markdown("""
<div style="text-align: center;">
<h1>🚀 AGNO FINANCE</h1>
<h3>⚡ <em>Análisis Financiero Inteligente</em></h3>
</div>
""", unsafe_allow_html=True)

# 🧠 Orquestador único
async def orchestrate(query, mode="team"):
    if mode == "team":
        # Team: 3 agentes especializados colaboran automáticamente
        team = Team(
            mode="coordinate",
            model=OpenAIChat(id="gpt-4o-mini"),
            members=[
                Agent(name="Web Researcher", tools=[DuckDuckGoTools(), Newspaper4kTools()]),
                Agent(name="Financial Analyst", tools=[YFinanceTools(), CalculatorTools()]),
                Agent(name="AI Synthesizer", tools=[ReasoningTools()])
            ],
            instructions="Colaboren para análisis completos usando sus herramientas especializadas",
            markdown=True
        )
        response = await team.arun(query)
    else:
        # Single: Un super agente con todas las herramientas
        agent = Agent(
            model=OpenAIChat(id="gpt-4o-mini"),
            tools=[DuckDuckGoTools(), Newspaper4kTools(), YFinanceTools(), 
                   CalculatorTools(), ReasoningTools()],
            instructions="Usa herramientas en secuencia inteligente para análisis completos",
            markdown=True
        )
        response = await agent.arun(query)
    return response.content

# 🎯 Configuración
col1, col2 = st.columns([1, 2])
with col1:
    mode = st.radio("🎯 Modo:", ["🤝 Team", "⚡ Single"], horizontal=True)
with col2:
    st.selectbox("🛠️ Herramientas Disponibles:", [
        "🔍 DuckDuckGo - Búsqueda web instantánea",
        "📰 Newspaper4k - Lee artículos completos",
        "💰 YFinance - Datos financieros en tiempo real", 
        "🧮 Calculator - Cálculos matemáticos avanzados",
        "🧠 Reasoning - Análisis y síntesis inteligente"
    ])
    
    st.selectbox("💡 Ejemplos de Consultas:", [
        "💰 Analiza acciones de Apple + noticias recientes",
        "🔍 Bitcoin: precio actual + tendencias + cálculo ROI",
        "📊 Compara Tesla vs Ford: finanzas + noticias",
        "🏦 Bancolombia: análisis completo + impacto económico",
        "🚀 Microsoft: rendimiento + perspectivas futuras",
        "⚡ Nvidia vs AMD: comparación técnica + financiera"
    ])

# 📝 Input principal - LO MÁS IMPORTANTE
st.markdown("### 💬 **Tu Consulta:**")
query = st.text_area(
    "",
    value=st.session_state.get('query', ''),
    height=100,
    placeholder="Ejemplo: Busca noticias de Apple, analiza su precio y calcula el ROI de una inversión de $1000..."
)

# 🚀 Botón de ejecución
if st.button("🚀 Ejecutar") and query:
    with st.spinner("🤖 Orquestando..."):
        try:
            mode_key = "team" if "Team" in mode else "single"
            response = asyncio.run(orchestrate(query, mode_key))
            st.success("✅ Completado!")
            st.markdown(response)
        except Exception as e:
            st.error(f"❌ {e}")

# 🔧 Init
if 'query' not in st.session_state: 
    st.session_state.query = ""