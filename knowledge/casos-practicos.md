# Casos Prácticos

## Qué es
Los casos prácticos son pruebas o ejercicios que se envían a los candidatos para evaluar sus habilidades de forma práctica. Pueden crearse manualmente o generarse con IA. El candidato recibe un email con un enlace al portal donde puede entregar su respuesta.

## Flujo de usuario
### Crear caso práctico
1. Ir al detalle de una posición que tenga **"Tiene caso práctico"** activado
2. Crear un caso práctico para la posición (manual o con IA)
3. El caso incluye: título, descripción, instrucciones y plazo

### Generar con IA
1. Ir al candidato y seleccionar **Generar caso práctico con IA**
2. La IA crea un caso práctico personalizado basado en la posición y el perfil del candidato
3. Revisar y ajustar el caso generado antes de enviarlo

### Enviar al candidato
1. Desde el caso práctico, hacer clic en **Enviar**
2. El candidato recibe un email con un enlace al portal de entrega
3. El candidato completa y sube su entrega a través del portal

### Evaluar entrega
1. Cuando el candidato entrega, aparece una notificación
2. Revisar la entrega en el detalle del caso práctico
3. Opcionalmente, usar la evaluación IA para analizar la entrega

## Portal del candidato
- El candidato accede mediante un enlace único (no necesita cuenta)
- Puede ver las instrucciones del caso práctico
- Sube su entrega (archivo o texto)
- Tiene un plazo para entregar

## Funcionalidades IA
- **Generar caso práctico**: Crea automáticamente un caso práctico relevante basado en la posición y el candidato
- La IA considera los requisitos de la posición para diseñar un caso realista y relevante

## FAQs
- **¿Puedo enviar el mismo caso a varios candidatos?** — Cada caso se personaliza por candidato, pero puedes usar el de la posición como base.
- **¿El candidato necesita cuenta para entregar?** — No, accede mediante un enlace único enviado por email.
- **¿Puedo re-enviar el caso?** — Sí, puedes reenviar el email con el enlace.
- **¿Qué formatos acepta la entrega?** — Depende de cómo configures el caso, puede ser texto o archivo.

## URLs disponibles
- Crear caso práctico: `/casestudies/create/<uuid_posicion>/`
- Generar con IA: `/casestudies/ai/generate/<uuid_candidato>/`
- Detalle de caso: `/casestudies/detail/<uuid>/`
- Editar caso: `/casestudies/edit/<uuid>/`
- Enviar a candidato: `/casestudies/send/<uuid_candidato>/`

## Notas por rol
- **Admin**: Puede crear, editar, enviar y evaluar todos los casos
- **Recruiter**: Puede gestionar casos de las posiciones de su empresa

## Notas sobre plan
Los casos prácticos y la generación con IA están disponibles en todos los planes.
