import asyncio
import os
from pathlib import Path
from textwrap import dedent

from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.mcp import MCPTools
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Cargar las variables del archivo .env
load_dotenv()

async def create_maps_agent(session):
    """Crear un agente que use Google Maps via MCP."""
    mcp_tools = MCPTools(session=session)
    await mcp_tools.initialize()

    return Agent(
        model=OpenAIChat(
            id="gpt-4o-mini",
            api_key=os.getenv("OPENAI_API_KEY")
        ),
        tools=[mcp_tools],
        instructions=dedent("""\
            Eres un asistente geográfico experto. Ayudas a los usuarios a obtener información sobre ubicaciones, rutas y lugares de interés.

            - Usa Google Maps para encontrar ubicaciones relevantes
            - Da respuestas claras, organizadas y en markdown
            - Ofrece contexto útil sin rodeos
        """),
        markdown=True,
        show_tool_calls=True,
    )

async def run_agent(message: str) -> None:
    """Ejecuta el agente con Google Maps MCP y un mensaje dado."""

    if not os.getenv("GOOGLE_MAPS_API_KEY") or not os.getenv("OPENAI_API_KEY"):
        raise EnvironmentError("Faltan las variables OPENAI_API_KEY o GOOGLE_MAPS_API_KEY en .env")

    # Preparar el servidor MCP para Google Maps
    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-google-maps"],
        env={"GOOGLE_MAPS_API_KEY": os.getenv("GOOGLE_MAPS_API_KEY")},
    )

    # Crear sesión con el servidor
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            agent = await create_maps_agent(session)
            await agent.aprint_response(message, stream=True)

if __name__ == "__main__":
    # Ejemplo de pregunta
    asyncio.run(run_agent("¿Busca los 5 mejores restaurantes que hay cerca de La Plaza de Bolivar de Pereira Colombia?"))