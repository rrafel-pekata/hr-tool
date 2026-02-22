import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .context import build_user_context
from .services import process_chatbot_message


@login_required
@require_POST
def chatbot_message(request):
    """Procesa un mensaje del usuario y devuelve la respuesta del chatbot."""
    try:
        data = json.loads(request.body)
        question = data.get('message', '').strip()
    except (json.JSONDecodeError, AttributeError):
        return JsonResponse({'error': 'Mensaje inválido'}, status=400)

    if not question:
        return JsonResponse({'error': 'El mensaje no puede estar vacío'}, status=400)

    # Obtener o inicializar historial de sesión
    history = request.session.get('chatbot_history', [])

    # Construir contexto del usuario
    user_context = build_user_context(request)

    # Procesar mensaje
    answer = process_chatbot_message(question, user_context, history)

    # Actualizar historial (máx 20 mensajes)
    history.append({'role': 'user', 'content': question})
    history.append({'role': 'assistant', 'content': answer})
    request.session['chatbot_history'] = history[-20:]

    return JsonResponse({'answer': answer})


@login_required
@require_POST
def chatbot_clear(request):
    """Limpia el historial del chatbot."""
    request.session['chatbot_history'] = []
    return JsonResponse({'status': 'ok'})
