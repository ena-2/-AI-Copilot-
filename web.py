import streamlit as st
import os
from dotenv import load_dotenv

# 🚨 SOLUCIÓN CRÍTICA: Añadir el path del proyecto al sistema (Corrige ImportError) 🚨
import sys
# Obtiene la ruta de la carpeta principal (Reto_Grupo_Carso)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# Importaciones Simples: Confían en el parche de sys.path
from core.conversation import handle_conversation
from services.llm import INFERENCE_PARAMS, get_llm_response

load_dotenv()

# --- Configuración de la App ---
st.set_page_config(page_title="AI Copilot MVP", layout="wide")

st.title("🤖 AI Copilot MVP")
st.caption("🚀 Producto Mínimo Viable para demostrar Integración LLM Robusta")

# Inicialización de estados de sesión
if "history" not in st.session_state:
    st.session_state.history = []
if "turn_count" not in st.session_state:
    st.session_state.turn_count = 0
if "metrics" not in st.session_state:
    st.session_state.metrics = {"latency": [], "tokens_in": [], "tokens_out": [], "fallbacks": 0, "retries": 0}

# Función para reiniciar la conversación
def reset_conversation():
    st.session_state.history = []
    st.session_state.turn_count = 0
    st.session_state.metrics = {"latency": [], "tokens_in": [], "tokens_out": [], "fallbacks": 0, "retries": 0}

# Sidebar con Métricas y Configuración
with st.sidebar:
    st.header("⚙️ Configuración y Métricas")
    st.button("Reiniciar Sesión", on_click=reset_conversation)

    st.subheader("Parámetros de Inferencia")
    st.json(INFERENCE_PARAMS) 
    st.caption(f"Modelo: {os.getenv('MODEL_NAME')}")
    st.caption(f"Contexto (Truncado): {os.getenv('MAX_HISTORY_TURNS')} turnos recientes")

    st.subheader("Métricas de Sesión")
    st.write(f"Turnos Actuales: **{st.session_state.turn_count} / 20**")
    
    st.write(f"Fallbacks: {st.session_state.metrics['fallbacks']}")
    st.write(f"Reintentos Total: {st.session_state.metrics['retries']}")
    
    if st.session_state.metrics["latency"]:
        avg_latency = sum(st.session_state.metrics["latency"]) / len(st.session_state.metrics["latency"])
        st.write(f"Latencia Promedio: {avg_latency:.2f} s")

# --- Área de Conversación ---
for message in st.session_state.history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Input de Usuario ---
if prompt := st.chat_input("Escribe tu consulta. Usa /menu para ver las opciones..."):
    
    # 1. Llamar a la lógica de conversación
    response, new_history, new_turn_count = handle_conversation(prompt, st.session_state.history, st.session_state.turn_count)
    
    st.session_state.history = new_history
    st.session_state.turn_count = new_turn_count
    
    # 2. Mostrar mensaje del usuario
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # 3. Mostrar respuesta del asistente
    with st.chat_message("assistant"):
        st.markdown(response)

    # 4. Actualizar métricas
    if "FALLBACK ACTIVO" in response:
        st.session_state.metrics["fallbacks"] += 1
    
    # Re-ejecutar para actualizar la interfaz con el nuevo historial
    st.rerun()