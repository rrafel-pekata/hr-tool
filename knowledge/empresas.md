# Empresas

## Qué es
Una empresa es el tenant principal en Pekata. Representa tu organización y agrupa todas las posiciones, candidatos y usuarios. Cada usuario pertenece a una empresa.

## Flujo de usuario
1. Ir a **Empresas** en el sidebar o a `/companies/`
2. Hacer clic en **Crear empresa**
3. Rellenar los campos del formulario
4. Opcionalmente, usar el botón **Mejorar con IA** para mejorar la descripción
5. Guardar — se redirige al dashboard de la empresa

## Campos del formulario
- **Nombre** (obligatorio): Nombre de la empresa
- **Descripción**: Qué hace la empresa, sector, misión
- **Logo**: Imagen del logo (opcional)
- **Web corporativa**: URL del sitio web
- **Beneficios y ventajas**: Seguro, formación, fruta, gym, etc.
- **Jornada laboral**: Ej. "L-V 9:00-18:00", "jornada flexible"
- **Política de trabajo remoto**: Ej. "100% remoto", "híbrido 3 días oficina"
- **Ubicación oficina**: Dirección o zona de la oficina principal
- **Cultura y valores**: Valores, ambiente de trabajo, equipo

## Funcionalidades IA
- **Mejorar con IA**: Botón en el formulario de creación/edición que mejora automáticamente la descripción de la empresa usando IA. Genera un texto más profesional y completo basado en lo que hayas escrito.

## Dashboard de empresa
El dashboard muestra:
- Datos de la empresa
- KPIs: número de posiciones activas, candidatos totales, entrevistas programadas
- Lista de posiciones de la empresa
- Botón para crear nueva posición
- Botón para editar la empresa

## Multi-tenant
- Cada usuario pertenece a una sola empresa
- Los datos de una empresa no son visibles para otra
- Los Admins pueden crear nuevas empresas

## FAQs
- **¿Puedo tener varias empresas?** — Sí, un Admin puede crear múltiples empresas, pero cada usuario está vinculado a una empresa principal.
- **¿Puedo cambiar el nombre después?** — Sí, edita la empresa desde su dashboard.
- **¿Qué pasa si desactivo una empresa?** — La empresa y sus datos siguen existiendo pero se marca como inactiva.

## URLs disponibles
- Lista de empresas: `/companies/`
- Crear empresa: `/companies/create/`
- Detalle de empresa: `/companies/<uuid>/`
- Editar empresa: `/companies/<uuid>/edit/`

## Notas por rol
- **Admin**: Puede crear, editar y desactivar empresas
- **Recruiter**: Puede ver el dashboard de su empresa pero no crear nuevas

## Notas sobre plan
Actualmente no hay límite en el número de empresas. Todas las funcionalidades están disponibles.
