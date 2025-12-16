import os
import time
from dotenv import load_dotenv
from groq import Groq, GroqError
from tenacity import retry, stop_after_attempt, wait_exponential, RetryError, retry_if_exception_type

# =========================
# CARGAR VARIABLES .env
# =========================
load_dotenv(override=True)

GROQ_KEY = os.getenv("GROQ_API_KEY")
MODEL = os.getenv("MODEL_NAME")

# =========================
# PARÁMETROS DE INFERENCIA
# =========================
INFERENCE_PARAMS = {
    "temperature": 0.5,
    "max_tokens": 512,
    "top_p": 0.9,
    "seed": 42,
    "timeout": 12.0
}

# =========================
# LLAMADA A GROQ
# =========================
@retry(
    wait=wait_exponential(multiplier=1, min=2, max=6),
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type(Exception),
    reraise=True
)
def call_groq_api(messages: list, model: str) -> dict:

    if not GROQ_KEY:
        raise Exception("La clave API de Groq no fue encontrada o es inválida.")

    client = Groq(api_key=GROQ_KEY)

    start_time = time.time()

    completion = client.chat.completions.create(
        model=model,
        messages=messages,
        **INFERENCE_PARAMS
    )

    latency = time.time() - start_time

    return {
        "response": completion.choices[0].message.content,
        "latency": latency,
        "tokens_in": completion.usage.prompt_tokens,
        "tokens_out": completion.usage.completion_tokens,
        "success": True,
        "retries": call_groq_api.retry.statistics.get("attempt_number", 1) - 1
    }

# =========================
# FUNCIÓN PRINCIPAL
# =========================
def get_llm_response(messages: list) -> dict:
    try:
        return call_groq_api(messages, MODEL)

    except RetryError:
        return {
            "response": "🚨 **FALLBACK ACTIVO:** Error persistente al conectar con Groq.",
            "latency": 0,
            "tokens_in": 0,
            "tokens_out": 0,
            "success": False,
            "retries": 3
        }

    except Exception as e:
        return {
            "response": f"🚨 **FALLBACK ACTIVO:** {str(e)}",
            "latency": 0,
            "tokens_in": 0,
            "tokens_out": 0,
            "success": False,
            "retries": 0
        }
