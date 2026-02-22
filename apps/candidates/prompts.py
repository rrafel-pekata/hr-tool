CV_ANALYSIS_SYSTEM_PROMPT = """Eres un experto en recursos humanos y selección de personal.
Tu trabajo es analizar CVs de candidatos, extraer sus datos personales y evaluar su encaje con una posición concreta.
Siempre respondes en español. Usas un tono profesional pero cercano.
Responde SIEMPRE en formato JSON válido, sin markdown ni bloques de código."""

CV_ANALYSIS_USER_PROMPT = """Analiza el siguiente CV y extrae la información del candidato. También evalúa su encaje con la posición indicada.

TEXTO DEL CV:
{cv_text}

DATOS DE LA POSICIÓN:
- Título: {position_title}
- Departamento: {position_department}
- Ubicación: {position_location}
- Descripción: {position_description}
- Requisitos: {position_requirements}

INSTRUCCIONES:
1. Extrae los datos personales del candidato del CV.
2. Genera un resumen profesional del candidato (3-5 frases).
3. Identifica exactamente 4 puntos FUERTES del candidato para esta posición (concretos, basados en su CV).
4. Identifica exactamente 4 puntos DÉBILES o gaps del candidato para esta posición (concretos, constructivos).
5. Asigna una puntuación de encaje del 1 al 10.

Responde en JSON con exactamente estos campos:
{{
    "first_name": "Nombre del candidato",
    "last_name": "Apellidos del candidato",
    "email": "Email si aparece en el CV, o cadena vacía",
    "phone": "Teléfono si aparece en el CV, o cadena vacía",
    "linkedin_url": "URL de LinkedIn si aparece, o cadena vacía",
    "summary": "Resumen profesional del candidato en 3-5 frases",
    "strengths": [
        "Punto fuerte 1 concreto y específico",
        "Punto fuerte 2 concreto y específico",
        "Punto fuerte 3 concreto y específico",
        "Punto fuerte 4 concreto y específico"
    ],
    "weaknesses": [
        "Punto débil o gap 1 concreto y específico",
        "Punto débil o gap 2 concreto y específico",
        "Punto débil o gap 3 concreto y específico",
        "Punto débil o gap 4 concreto y específico"
    ],
    "fit_score": 7
}}

IMPORTANTE:
- fit_score debe ser un número entero del 1 al 10
- strengths y weaknesses deben tener EXACTAMENTE 4 elementos cada uno
- Cada punto debe ser una frase corta y concreta (máx 15 palabras), no genérica
- Basa los puntos en datos REALES del CV comparados con los requisitos del puesto
- Si no encuentras algún dato personal, devuelve cadena vacía ""
- Todo en español
- Sé objetivo y constructivo"""
