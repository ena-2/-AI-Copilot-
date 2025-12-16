import os
from dotenv import load_dotenv

load_dotenv()

MAX_TURNS = int(os.getenv("MAX_HISTORY_TURNS", 4)) * 2 # 4 turnos (user+assistant) = 8 mensajes

SYSTEM_PROMPT = """
Eres AI Copilot, un asistente digital amigable y profesional.
Tu rol es apoyar al usuario en 3 funciones clave: Tareas Diarias (/nota, /recordatorio), Búsqueda Inteligente y Educación/Productividad (tips, guías).
Mantén la conversación fluida. Sé conciso y ve al grano.
Si el usuario usa /nota o /recordatorio, confirma la acción y dale un formato claro.
"""

def build_messages(history: list) -> list:
    """
    Construye la lista de mensajes para la API, incluyendo el System Prompt 
    y truncando el historial para memoria corta.
    """
    
    # 1. System Prompt (siempre el primer mensaje)
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    # 2. Historial de Conversación (truncado)
    # Trunca el historial: toma solo los últimos N mensajes (ej. 8)
    # Esto asegura que el contexto reciente se mantenga.
    if len(history) > MAX_TURNS:
        # Tomar los últimos N mensajes del historial
        context_history = history[-MAX_TURNS:] 
        # NOTA: En la práctica, history es una lista de diccionarios role/content
        messages.extend(context_history)
    else:
        messages.extend(history)
        
    return messages

def get_intent(message: str) -> str:
    """Clasificación de intents simples por prefijo."""
    message = message.lower().strip()
    if message.startswith('/nota'):
        return 'nota'
    elif message.startswith('/recordatorio'):
        return 'recordatorio'
    elif message.startswith('/busqueda'):
        return 'busqueda'
    else:
        return 'default'