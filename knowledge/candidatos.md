# Candidatos

## Qué es
Un candidato es una persona que aplica a una posición específica. Cada candidato está vinculado a una posición y tiene su propio pipeline de estados.

## Flujo de usuario
1. Ir al detalle de una posición (`/positions/<uuid>/`)
2. Hacer clic en **Agregar candidato**
3. Subir el CV en PDF — el sistema analiza automáticamente con IA
4. El análisis extrae: nombre, email, teléfono, LinkedIn, resumen, puntos fuertes/débiles y puntuación de encaje
5. Revisar y ajustar los datos del candidato
6. Gestionar el candidato a lo largo del pipeline

## Subir CV
- Formato aceptado: PDF (máximo 10MB)
- El PDF debe contener texto seleccionable (no imágenes escaneadas)
- Al subir, la IA analiza el CV automáticamente y extrae información
- Si el candidato ya existe, puedes subir un nuevo CV desde su perfil

## Análisis IA del CV
Cuando subes un CV, la IA genera automáticamente:
- **Datos personales**: nombre, apellidos, email, teléfono, LinkedIn
- **Resumen profesional**: 3-5 frases sobre el candidato
- **Puntos fuertes** (4): fortalezas del candidato respecto a la posición
- **Puntos débiles** (4): gaps o áreas de mejora respecto a la posición
- **Puntuación de encaje** (1-10): cuánto encaja el candidato con la posición

## Pipeline de candidatos (estados)
- **Nuevo** (`new`): Candidato recién añadido
- **En revisión** (`reviewing`): CV siendo evaluado
- **Entrevista** (`interview`): Candidato en fase de entrevistas
- **Oferta** (`offer`): Se ha hecho o se va a hacer una oferta
- **Rechazado** (`rejected`): Candidato descartado

Para cambiar el estado, usa el selector de estado en el perfil del candidato.

## Rating (estrellas)
- Puedes asignar estrellas (1-5) a cada candidato
- Útil para ordenar y priorizar candidatos dentro de una posición

## Notas
- Cada candidato tiene un campo de notas donde puedes registrar observaciones
- Las notas son visibles para todos los miembros de la empresa

## FAQs
- **¿Puedo agregar un candidato sin CV?** — Sí, puedes crear un candidato manualmente sin subir CV. No se realizará el análisis IA automático.
- **¿Puedo cambiar la puntuación de encaje?** — La puntuación es generada por IA, pero puedes usar las estrellas para tu propia valoración.
- **¿Un candidato puede estar en varias posiciones?** — Cada candidatura es independiente. Puedes agregar al mismo candidato en distintas posiciones.
- **¿Puedo re-analizar el CV?** — Sube el CV nuevamente para generar un nuevo análisis.

## URLs disponibles
- Agregar candidato: `/candidates/new/<uuid_posicion>/`
- Detalle de candidato: `/candidates/<uuid>/`
- Editar candidato: `/candidates/<uuid>/edit/`
- Lista de candidatos: se ven dentro del detalle de la posición

## Notas por rol
- **Admin**: Acceso completo a todos los candidatos
- **Recruiter**: Puede gestionar candidatos de posiciones de su empresa

## Notas sobre plan
Sin límites en el número de candidatos. El análisis de CV con IA está disponible en todos los planes.
