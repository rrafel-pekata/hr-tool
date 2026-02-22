# Evaluación con IA

## Qué es
La evaluación con IA es un análisis integral de un candidato que combina toda la información disponible: CV, entrevistas, caso práctico y notas. Genera una evaluación completa con puntuaciones y recomendación final.

## Flujo de usuario
1. Ir al detalle de un candidato (`/candidates/<uuid>/`)
2. Hacer clic en **Evaluar con IA**
3. El sistema recopila toda la información del candidato
4. La IA genera una evaluación completa
5. Se muestra la evaluación con puntuaciones y recomendación

## Qué analiza la IA
La evaluación tiene en cuenta:
- **CV y perfil**: Experiencia, formación, habilidades
- **Puntuación de encaje**: Del análisis inicial del CV
- **Entrevistas**: Resultados y puntuaciones de todas las entrevistas
- **Caso práctico**: Entrega y resultado del caso práctico (si existe)
- **Notas del reclutador**: Observaciones registradas

## Resultado de la evaluación
- **Puntuación general**: Valoración global del candidato
- **Análisis por áreas**: Evaluación detallada de diferentes competencias
- **Puntos fuertes**: Lo mejor del candidato
- **Áreas de mejora**: Donde necesita desarrollo
- **Recomendación**: Sugerencia de decisión (contratar, segunda entrevista, rechazar, etc.)

## Regenerar evaluación
- Si añades nueva información (otra entrevista, caso práctico), puedes regenerar la evaluación
- La nueva evaluación tendrá en cuenta toda la información actualizada

## FAQs
- **¿Cuándo debo evaluar?** — Idealmente cuando tengas suficiente información: al menos el CV analizado y una entrevista realizada.
- **¿La evaluación es definitiva?** — No, es una herramienta de apoyo. La decisión final siempre es del equipo de RRHH.
- **¿Puedo evaluar sin entrevista?** — Sí, pero la evaluación será más completa si incluye entrevistas y caso práctico.
- **¿Cuánto tarda?** — Unos segundos. La IA procesa toda la información rápidamente.

## URLs disponibles
- Evaluar candidato: `/evaluations/candidate/<uuid_candidato>/`
- La evaluación se muestra en el detalle del candidato

## Notas por rol
- **Admin**: Puede generar evaluaciones de cualquier candidato
- **Recruiter**: Puede generar evaluaciones de candidatos de su empresa

## Notas sobre plan
La evaluación con IA está disponible en todos los planes.
