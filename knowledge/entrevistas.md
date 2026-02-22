# Entrevistas

## Qué es
Las entrevistas permiten programar y registrar reuniones con candidatos. Cada entrevista está vinculada a un candidato y permite registrar resultado y puntuación.

## Flujo de usuario
1. Ir al detalle de un candidato (`/candidates/<uuid>/`)
2. Hacer clic en **Programar entrevista**
3. Seleccionar fecha, hora, tipo de entrevista y notas
4. Guardar — la entrevista aparece en el perfil del candidato
5. Tras realizar la entrevista, editarla para registrar resultado y puntuación

## Campos de la entrevista
- **Fecha y hora**: Cuándo se realizará la entrevista
- **Tipo**: Tipo de entrevista (presencial, videoconferencia, telefónica, etc.)
- **Notas previas**: Información a tener en cuenta antes de la entrevista
- **Resultado**: Cómo fue la entrevista (se rellena después)
- **Puntuación**: Valoración numérica de la entrevista

## Registrar resultado
Después de realizar la entrevista:
1. Ir al detalle del candidato
2. Hacer clic en la entrevista para editarla
3. Rellenar el campo de resultado con las observaciones
4. Asignar una puntuación
5. Guardar

## FAQs
- **¿Puedo programar varias entrevistas para un candidato?** — Sí, puedes crear múltiples entrevistas (ej. primera entrevista técnica, segunda con el equipo).
- **¿Las entrevistas se sincronizan con el calendario?** — Actualmente la integración con Google Calendar está en desarrollo.
- **¿Puedo cancelar una entrevista?** — Puedes editar o eliminar la entrevista desde su página de edición.

## URLs disponibles
- Crear entrevista: `/interviews/new/<uuid_candidato>/`
- Editar entrevista: `/interviews/<uuid>/edit/`
- Las entrevistas se listan en el detalle del candidato

## Notas por rol
- **Admin**: Puede gestionar todas las entrevistas
- **Recruiter**: Puede gestionar entrevistas de candidatos de su empresa

## Notas sobre plan
Las entrevistas están disponibles en todos los planes sin límites.
