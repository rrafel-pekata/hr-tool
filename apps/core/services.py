import io
import json
import logging

from django.conf import settings

import anthropic
import pdfplumber

logger = logging.getLogger(__name__)


def extract_pdf_text(file_obj) -> str:
    """Extrae texto de un archivo PDF usando pdfplumber."""
    file_bytes = file_obj.read()
    file_obj.seek(0)

    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            pages_text = []
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    pages_text.append(text)
    except Exception as e:
        raise ValueError(f"No se pudo leer el PDF: {e}")

    full_text = "\n\n".join(pages_text)
    if not full_text.strip():
        raise ValueError(
            "No se pudo extraer texto del PDF. "
            "Es posible que sea un PDF escaneado (imagen). "
            "Sube un PDF con texto seleccionable."
        )

    return full_text


def call_claude(system_prompt: str, user_prompt: str, json_output: bool = False) -> str:
    """Llama a Claude API y devuelve la respuesta como texto."""
    if not settings.ANTHROPIC_API_KEY:
        raise ValueError(
            "ANTHROPIC_API_KEY no configurada. Añádela en tu archivo .env"
        )

    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=system_prompt,
        messages=[
            {"role": "user", "content": user_prompt}
        ],
    )

    text = message.content[0].text

    if json_output:
        # Intentar extraer JSON del response
        try:
            # Si viene envuelto en ```json ... ```
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            return json.loads(text)
        except (json.JSONDecodeError, IndexError):
            logger.warning("No se pudo parsear JSON de Claude: %s", text[:200])
            return text

    return text
