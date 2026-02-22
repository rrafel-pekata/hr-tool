SYSTEM_PROMPT = """Eres un experto en recursos humanos y redacción de ofertas de empleo.
Tu trabajo es mejorar y completar ofertas de trabajo para que sean atractivas, claras y profesionales.
Siempre respondes en español. Usas un tono profesional pero cercano.
Responde SIEMPRE en formato JSON válido, sin markdown ni bloques de código."""

GENERATE_POSITION_PROMPT = """Mejora y completa esta oferta de trabajo con la información proporcionada.

DATOS DE LA POSICIÓN:
- Título: {title}
- Departamento: {department}
- Ubicación: {location}
- Tipo de empleo: {employment_type}
- Rango salarial: {salary_range}

DESCRIPCIÓN ACTUAL (puede estar vacía o incompleta):
{description}

REQUISITOS ACTUALES (puede estar vacío o incompleto):
{requirements}

INFORMACIÓN DE LA EMPRESA:
- Nombre: {company_name}
- Descripción: {company_description}
- Web: {company_website}
- Beneficios y ventajas: {company_benefits}
- Jornada laboral: {company_work_schedule}
- Política de trabajo remoto: {company_remote_policy}
- Ubicación oficina: {company_office_location}
- Cultura y valores: {company_culture}

INSTRUCCIONES:
Genera una oferta mejorada y profesional. Integra la información de la empresa (beneficios, jornada, remoto, cultura) de forma natural en la oferta. Responde en JSON con exactamente estos campos:
{{
    "description": "Descripción completa del rol. Incluye: resumen del puesto (2-3 frases), responsabilidades principales (lista con viñetas usando •). Integra información relevante de la empresa (cultura, modalidad de trabajo). Si ya hay contenido, mejóralo y amplíalo manteniendo la esencia.",
    "requirements": "Requisitos del puesto. Incluye: requisitos obligatorios (lista con •), requisitos valorables (lista con •), y habilidades blandas importantes. Si ya hay contenido, mejóralo y estructura mejor.",
    "benefits": "Qué ofrecemos: lista con viñetas (•) de beneficios, ventajas, jornada, modalidad de trabajo y todo lo que hace atractiva la oferta. Usa la información de la empresa y amplíala si tiene sentido.",
    "about_company_snippet": "Párrafo atractivo de 3-4 frases sobre la empresa para incluir en la oferta. Usa la información disponible de la empresa incluyendo cultura y valores."
}}"""
