# Posiciones

## Qué es
Una posición es una oferta de empleo dentro de una empresa. Representa un puesto que necesitas cubrir. Los candidatos se asocian a posiciones específicas.

## Flujo de usuario
1. Ir a **Posiciones** en el sidebar o a `/positions/`
2. Hacer clic en **Crear posición** (o desde el dashboard de la empresa)
3. Rellenar título, departamento, ubicación y descripción
4. Opcionalmente, usar **Generar con IA** para crear la descripción automáticamente
5. Guardar como borrador o publicar
6. Desde el detalle de la posición, gestionar candidatos

## Campos del formulario
- **Título** (obligatorio): Nombre del puesto (ej. "Desarrollador Full Stack Senior")
- **Departamento**: Área de la empresa (ej. "Tecnología", "Marketing")
- **Ubicación**: Ciudad o "Remoto"
- **Tipo de contrato**: Tiempo completo, parcial, freelance, prácticas
- **Rango salarial**: Opcional, texto libre
- **Descripción**: Descripción completa del puesto
- **Requisitos**: Lo que se pide al candidato
- **Beneficios**: Qué ofrece la empresa para este puesto
- **Sobre la empresa**: Snippet sobre la empresa para esta oferta
- **Tiene caso práctico**: Si la posición incluirá un caso práctico

## Estados de posición
- **Borrador** (`draft`): Posición creada pero no visible. Estado inicial.
- **Publicada** (`published`): Posición activa, se pueden recibir candidatos.
- **Pausada** (`paused`): Posición temporalmente detenida.
- **Cerrada** (`closed`): Posición finalizada, proceso completado.

Para cambiar el estado, usa el botón de estado en el detalle de la posición.

## Funcionalidades IA
- **Generar con IA**: En el formulario de creación, un botón genera automáticamente la descripción, requisitos, beneficios y snippet de empresa basándose en el título del puesto y los datos de la empresa. Esto ahorra mucho tiempo al redactar ofertas.

## Filtros
La lista de posiciones permite filtrar por:
- Estado (borrador, publicada, pausada, cerrada)
- Búsqueda por texto

## FAQs
- **¿Puedo editar una posición publicada?** — Sí, desde el detalle haz clic en editar.
- **¿Qué pasa al cerrar una posición?** — Los candidatos existentes se mantienen, pero no se pueden añadir nuevos.
- **¿Puedo reabrir una posición cerrada?** — Sí, cambiando su estado de vuelta a publicada.
- **¿La IA genera todo automáticamente?** — Genera una primera versión que puedes revisar y editar antes de guardar.

## URLs disponibles
- Lista de posiciones: `/positions/`
- Crear posición: `/positions/create/`
- Detalle de posición: `/positions/<uuid>/`
- Editar posición: `/positions/<uuid>/edit/`

## Notas por rol
- **Admin**: Puede crear, editar y cambiar estado de cualquier posición
- **Recruiter**: Puede crear y gestionar posiciones de su empresa

## Notas sobre plan
Actualmente no hay límite en el número de posiciones. La generación con IA está disponible en todos los planes.
