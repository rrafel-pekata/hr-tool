EVALUATION_SYSTEM_PROMPT = """Eres un experto en evaluación de candidatos para procesos de selección.
Tu trabajo es analizar TODA la información disponible de un candidato y generar una evaluación objetiva y completa.
Siempre respondes en español. Usas un tono profesional, directo y constructivo.
Responde SIEMPRE en formato JSON válido, sin markdown ni bloques de código."""

EVALUATION_USER_PROMPT = """Evalúa a este candidato basándote en toda la información disponible.

POSICIÓN:
- Título: {position_title}
- Departamento: {position_department}
- Descripción: {position_description}
- Requisitos: {position_requirements}

EMPRESA:
- Nombre: {company_name}

CANDIDATO:
- Nombre: {candidate_name}
- Resumen IA del CV: {candidate_summary}
- Texto del CV: {candidate_cv_text}

ENTREVISTAS REALIZADAS:
{interviews_text}

CASOS PRÁCTICOS:
{casestudies_text}

NOTAS DEL RECLUTADOR:
{recruiter_notes}

INSTRUCCIONES:
Genera una evaluación completa del candidato. Puntúa cada área del 1 al 10 (solo si hay datos para evaluar, si no hay datos pon null).

Responde en JSON con exactamente estos campos:
{{
    "cv_score": 7,
    "interview_score": 8,
    "case_score": 7,
    "overall_score": 7,
    "recommendation": "hire",
    "summary": "Resumen ejecutivo de 3-5 párrafos con: perfil del candidato, puntos fuertes, puntos débiles, encaje con la posición y recomendación final. Sé concreto y directo."
}}

IMPORTANTE:
- cv_score: evalúa formación, experiencia y encaje técnico según el CV. null si no hay CV.
- interview_score: evalúa según las notas y puntuaciones de las entrevistas. null si no hay entrevistas.
- case_score: evalúa la respuesta al caso práctico. null si no hay caso práctico entregado.
- overall_score: puntuación global del 1 al 10 (obligatorio, basado en la info disponible).
- recommendation: "hire" (contratar), "hold" (seguir evaluando) o "reject" (descartar).
- summary: debe ser un análisis detallado y útil para la toma de decisiones. Incluye fortalezas concretas, áreas de mejora y tu razonamiento.
- Basa tu evaluación SOLO en los datos proporcionados, no inventes información.
- Si falta información en alguna área, menciónalo en el summary."""
