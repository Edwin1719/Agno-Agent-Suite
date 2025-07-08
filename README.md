# Suite de Agentes de IA con Agno

Este repositorio contiene una suite de agentes de IA construidos con el framework Agno, demostrando diversas capacidades y casos de uso.

## Agentes Disponibles

### 1. Agente Financiero (`financial_agent`)

Una aplicación web con Streamlit que funciona como un dashboard para análisis financiero. Utiliza un equipo de agentes para investigar y analizar datos de acciones, noticias y criptomonedas.

**Para ejecutar:**
```bash
streamlit run financial_agent/app.py
```

### 2. Agente de Recursos Humanos (`hr_agent`)

Una completa herramienta de Recursos Humanos, también construida con Streamlit. Puede analizar y optimizar CVs, seleccionar candidatos de forma masiva a partir de un archivo ZIP y generar ofertas de trabajo profesionales.

**Para ejecutar:**
```bash
streamlit run hr_agent/app.py
```

### 3. Agente de Mapas (`maps_agent`)

Un cliente de línea de comandos que demuestra cómo un agente de IA puede conectarse a un servidor MCP (en este caso, Google Maps) para responder a preguntas geográficas.

**Para ejecutar:**
```bash
python maps_agent/main.py
```

## Instalación

1. Clona este repositorio.
2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
3. Crea un archivo `.env` basado en `.env.example` y añade tus claves de API.

