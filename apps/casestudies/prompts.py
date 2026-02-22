SYSTEM_PROMPT = """Eres un experto en diseño de pruebas prácticas para procesos de selección de personal.
Tu trabajo es crear casos prácticos realistas, directos y muy orientados al trabajo diario del puesto.
Siempre respondes en español. Usas un tono profesional y claro.
Responde SIEMPRE en formato JSON válido, sin markdown ni bloques de código."""

GENERATE_CASE_STUDY_PROMPT = """Genera un caso práctico personalizado para evaluar a este candidato para la posición indicada.

POSICIÓN:
- Título: {position_title}
- Departamento: {position_department}
- Descripción: {position_description}
- Requisitos: {position_requirements}

EMPRESA:
- Nombre: {company_name}
- Descripción: {company_description}

CANDIDATO:
- Nombre: {candidate_name}
- Resumen profesional: {candidate_summary}
- Texto del CV: {candidate_cv_text}

INSTRUCCIONES:
Genera un caso práctico con exactamente 2-3 preguntas/ejercicios. El caso debe:
- Simular una situación REAL del día a día del puesto
- Ser 100% práctico (nada teórico, nada genérico)
- Estar adaptado al nivel y experiencia del candidato según su CV
- Evaluar cómo resolvería problemas reales que se encontrará en el puesto

Responde en JSON con exactamente estos campos:
{{
    "title": "Título breve y descriptivo del caso práctico",
    "full_content": "Contenido del caso práctico. Estructura:\\n\\nCONTEXTO:\\nDescribe brevemente una situación realista del puesto (2-3 frases).\\n\\nEJERCICIOS:\\n\\n1. [Primera pregunta/ejercicio práctico]\\nDescripción clara de lo que debe hacer el candidato.\\n\\n2. [Segunda pregunta/ejercicio práctico]\\nDescripción clara de lo que debe hacer el candidato.\\n\\n3. [Tercera pregunta/ejercicio práctico (opcional)]\\nDescripción clara de lo que debe hacer el candidato.\\n\\nFORMATO DE ENTREGA:\\nIndicaciones breves sobre qué entregar y en qué formato.",
    "evaluation_criteria": "4-6 criterios concretos para evaluar las respuestas, separados por punto y coma"
}}

IMPORTANTE:
- Las preguntas deben ser MUY PRÁCTICAS: pedir que hagan algo concreto (diseñar, resolver, proponer, analizar un caso real).
- NO hagas preguntas teóricas tipo "¿qué harías si...?" o "explica la diferencia entre...".
- Adapta la dificultad al perfil del candidato (junior vs senior).
- Usa el contexto del puesto y la empresa para hacer el caso lo más realista posible.
- Máximo 2-3 ejercicios, directos y al grano."""
