import io
import json
import logging

from django.conf import settings
from django.utils.translation import get_language

import anthropic
import pdfplumber

logger = logging.getLogger(__name__)

LANGUAGE_NAMES = {
    'es': 'Spanish',
    'en': 'English',
    'ca': 'Catalan',
}
ALL_LANGUAGES = ('es', 'en', 'ca')


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


def call_claude(system_prompt: str, user_prompt: str, json_output: bool = False, model: str = "claude-sonnet-4-6", max_tokens: int = 4096) -> str:
    """Llama a Claude API y devuelve la respuesta como texto."""
    if not settings.ANTHROPIC_API_KEY:
        raise ValueError(
            "ANTHROPIC_API_KEY no configurada. Añádela en tu archivo .env"
        )

    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    message = client.messages.create(
        model=model,
        max_tokens=max_tokens,
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


def translate_fields(instance, source_lang, fields):
    """Translate model fields from source_lang to the other two languages using Claude.

    Args:
        instance: Model instance (must be registered with modeltranslation).
        source_lang: Language code of the source content ('es', 'en', or 'ca').
        fields: List of field names to translate.
    """
    target_langs = [lang for lang in ALL_LANGUAGES if lang != source_lang]

    # Collect source content (read from language-specific columns)
    source_data = {}
    for field in fields:
        value = getattr(instance, f'{field}_{source_lang}', '') or ''
        if value.strip():
            source_data[field] = value

    if not source_data:
        return

    system_prompt = (
        "You are a professional translator. Translate the provided content accurately "
        "while preserving formatting (markdown, line breaks, HTML tags). "
        "Do NOT translate proper nouns, brand names, or technical terms that should remain in the original language. "
        "Return ONLY a JSON object with the translations, no explanation."
    )

    fields_json = json.dumps(source_data, ensure_ascii=False)
    target_lang_names = [f"{lang} ({LANGUAGE_NAMES[lang]})" for lang in target_langs]

    user_prompt = (
        f"Translate the following fields from {LANGUAGE_NAMES[source_lang]} "
        f"to {' and '.join(target_lang_names)}.\n\n"
        f"Source content:\n{fields_json}\n\n"
        f"Return a JSON object with this exact structure:\n"
        + json.dumps({lang: {"<field_name>": "<translated_value>"} for lang in target_langs}, ensure_ascii=False)
    )

    try:
        result = call_claude(system_prompt, user_prompt, json_output=True, model="claude-haiku-4-5-20251001")
        if not isinstance(result, dict):
            logger.warning("translate_fields: Claude did not return valid JSON")
            return

        update_fields = []
        for lang in target_langs:
            lang_translations = result.get(lang, {})
            for field, translated_value in lang_translations.items():
                if field in fields and translated_value:
                    attr_name = f'{field}_{lang}'
                    setattr(instance, attr_name, translated_value)
                    update_fields.append(attr_name)

        if update_fields:
            instance.save(update_fields=update_fields)
            logger.info(
                "Translated %d fields for %s pk=%s from %s",
                len(update_fields), type(instance).__name__, instance.pk, source_lang,
            )
    except Exception:
        logger.exception(
            "Error translating fields for %s pk=%s",
            type(instance).__name__, instance.pk,
        )
