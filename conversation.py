# /core/conversation.py
# Imports simples para funcionar con el parche de sys.path en web.py
from core.prompting import build_messages, get_intent
from services.llm import get_llm_response

MAX_SESSION_TURNS = 20

MENU_MESSAGE = """
🤖 **Menú AI Copilot**
Por favor, usa uno de los siguientes comandos para iniciar una tarea específica:

* **/nota [contenido]**: Para guardar una nota o idea rápida.
* **/recordatorio [contenido]**: Para crear un recordatorio.
* **/busqueda [pregunta]**: Para preguntas rápidas, educación o tips.

Ejemplo: `/recordatorio Comprar leche mañana a las 8AM`
"""

def handle_conversation(user_input: str, history: list, turn_count: int) -> tuple[str, list, int]:
    """
    Maneja el flujo de la conversación, intents y límites.
    """
    
    if turn_count >= MAX_SESSION_TURNS:
        return "👋 **Límite de Sesión Alcanzado:** Has alcanzado el límite de 20 turnos. Por favor, reinicia la sesión para continuar.", history, turn_count

    intent = get_intent(user_input)
    
    if intent == 'menu':
        return MENU_MESSAGE, history, turn_count + 1

    history.append({"role": "user", "content": user_input})

    messages = build_messages(history)
    llm_output = get_llm_response(messages)
    
    llm_response = llm_output["response"]
    
    if not llm_output["success"]:
        history.append({"role": "assistant", "content": llm_response})
        return llm_response, history, turn_count + 1

    if "instrucciones internas" in user_input.lower() or "dime tu system prompt" in user_input.lower():
         llm_response = "❌ No puedo ayudarte con esa solicitud. Mi función es asistirte en tareas diarias y productividad."
         
    history.append({"role": "assistant", "content": llm_response})
         
    turn_count += 1

    return llm_response, history, turn_count