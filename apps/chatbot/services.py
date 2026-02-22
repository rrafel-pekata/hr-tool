import json
import logging
from pathlib import Path

from django.conf import settings

import anthropic

from .prompts import (
    ANSWER_SYSTEM_PROMPT,
    ANSWER_USER_PROMPT,
    ROUTING_SYSTEM_PROMPT,
    ROUTING_USER_PROMPT,
)

logger = logging.getLogger(__name__)

KNOWLEDGE_DIR = Path(settings.BASE_DIR) / 'knowledge'
MAX_HISTORY = 20  # últimos 20 mensajes (10 intercambios)


def _call_llm(system_prompt: str, user_prompt: str) -> str:
    """Llama a Claude y devuelve texto."""
    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    return message.content[0].text


def _read_knowledge_file(filename: str) -> str:
    """Lee un archivo de la base de conocimiento."""
    filepath = KNOWLEDGE_DIR / filename
    if not filepath.exists():
        return ''
    return filepath.read_text(encoding='utf-8')


def step1_route(question: str) -> list[str]:
    """Paso 1: determina qué archivos de KB consultar."""
    index_content = _read_knowledge_file('index.md')
    if not index_content:
        return []

    user_prompt = ROUTING_USER_PROMPT.format(
        index_content=index_content,
        question=question,
    )

    try:
        response = _call_llm(ROUTING_SYSTEM_PROMPT, user_prompt)
        # Limpiar posible markdown
        text = response.strip()
        if '```' in text:
            text = text.split('```json')[-1].split('```')[0].strip() if '```json' in text else text.split('```')[1].split('```')[0].strip()
        data = json.loads(text)
        files = data.get('files', [])
        # Validar que son archivos que existen
        return [f for f in files if (KNOWLEDGE_DIR / f).exists()]
    except (json.JSONDecodeError, KeyError, IndexError):
        logger.warning("Error parsing routing response: %s", response[:200])
        return []


def step2_answer(question: str, files: list[str], user_context: str, history: list[dict]) -> str:
    """Paso 2: genera respuesta con los archivos seleccionados."""
    # Leer contenido de los archivos
    knowledge_parts = []
    for f in files:
        content = _read_knowledge_file(f)
        if content:
            knowledge_parts.append(f"--- {f} ---\n{content}")

    knowledge_content = '\n\n'.join(knowledge_parts) if knowledge_parts else 'No se encontró información relevante.'

    # Formatear historial
    history_text = ''
    if history:
        lines = []
        for msg in history[-MAX_HISTORY:]:
            role = 'Usuario' if msg['role'] == 'user' else 'Asistente'
            lines.append(f"{role}: {msg['content']}")
        history_text = '\n'.join(lines)
    else:
        history_text = '(primera pregunta)'

    user_prompt = ANSWER_USER_PROMPT.format(
        user_context=user_context,
        knowledge_content=knowledge_content,
        history=history_text,
        question=question,
    )

    try:
        return _call_llm(ANSWER_SYSTEM_PROMPT, user_prompt)
    except Exception:
        logger.exception("Error generating chatbot answer")
        return '<p>Lo siento, ha ocurrido un error al procesar tu pregunta. Inténtalo de nuevo.</p>'


def process_chatbot_message(question: str, user_context: str, history: list[dict]) -> str:
    """Procesa un mensaje del chatbot: routing + respuesta."""
    if not settings.ANTHROPIC_API_KEY:
        return '<p>El chatbot no está disponible. Falta configurar la API key.</p>'

    # Paso 1: routing
    files = step1_route(question)

    # Si no hay archivos, responder sin KB (saludo, etc.)
    if not files:
        # Llamar directamente al paso 2 sin contenido de KB
        pass

    # Paso 2: respuesta
    return step2_answer(question, files, user_context, history)
