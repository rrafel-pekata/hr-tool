SYSTEM_PROMPT = """Eres un experto en recursos humanos y employer branding.
Tu trabajo es mejorar y completar la información de empresas para que sus perfiles sean atractivos y profesionales.
Siempre respondes en español. Usas un tono profesional pero cercano.
Responde SIEMPRE en formato JSON válido, sin markdown ni bloques de código."""

IMPROVE_COMPANY_PROMPT = """Mejora y completa la información de esta empresa para que sea atractiva para candidatos.

DATOS ACTUALES DE LA EMPRESA:
- Nombre: {name}
- Web: {website}
- Descripción actual: {description}
- Beneficios actuales: {benefits}
- Jornada laboral: {work_schedule}
- Política remoto: {remote_policy}
- Ubicación oficina: {office_location}
- Cultura y valores: {culture}

INSTRUCCIONES:
Mejora y completa la información de la empresa. Si algún campo está vacío, genera contenido razonable basándote en el nombre y descripción. Si ya hay contenido, mejóralo y amplíalo. Responde en JSON con exactamente estos campos:
{{
    "description": "Descripción profesional de la empresa (3-5 frases). Qué hace, sector, misión y visión. Si ya hay contenido, mejóralo.",
    "benefits": "Lista de beneficios y ventajas con viñetas (•). Incluye los existentes y sugiere más si tiene sentido.",
    "work_schedule": "Jornada laboral clara y atractiva. Si está vacío, sugiere algo estándar como 'L-V 9:00-18:00, jornada flexible'.",
    "remote_policy": "Política de trabajo remoto clara. Si está vacío, sugiere algo como 'Modelo híbrido flexible'.",
    "culture": "Cultura y valores de la empresa (3-4 frases). Ambiente de trabajo, valores, tipo de equipo. Si ya hay contenido, mejóralo."
}}"""
