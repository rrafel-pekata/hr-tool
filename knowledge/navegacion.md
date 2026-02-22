# Navegación

## Estructura del sidebar
El menú lateral (sidebar) contiene las siguientes secciones:
1. **Logo y nombre de empresa** — En la parte superior
2. **Dashboard** (`/`) — Página de inicio con resumen
3. **Posiciones** (`/positions/`) — Lista de ofertas de empleo
4. **Empresas** (`/companies/`) — Lista de empresas (visible para Admins)
5. **Ayuda** (`/ayuda/`) — Página de ayuda
6. **Perfil de usuario** — En la parte inferior, muestra nombre y email
7. **Cerrar sesión** — Botón de logout

## URLs principales

### Generales
- Dashboard: `/`
- Login: `/login/`
- Logout: `/logout/`
- Ayuda: `/ayuda/`
- Panel admin: `/admin/`

### Empresas
- Lista: `/companies/`
- Crear: `/companies/create/`
- Detalle: `/companies/<uuid>/`
- Editar: `/companies/<uuid>/edit/`

### Posiciones
- Lista: `/positions/`
- Crear: `/positions/create/`
- Detalle: `/positions/<uuid>/`
- Editar: `/positions/<uuid>/edit/`

### Candidatos
- Agregar a posición: `/candidates/new/<uuid_posicion>/`
- Detalle: `/candidates/<uuid>/`
- Editar: `/candidates/<uuid>/edit/`

### Entrevistas
- Crear: `/interviews/new/<uuid_candidato>/`
- Editar: `/interviews/<uuid>/edit/`

### Casos prácticos
- Crear para posición: `/casestudies/create/<uuid_posicion>/`
- Generar con IA: `/casestudies/ai/generate/<uuid_candidato>/`
- Detalle: `/casestudies/detail/<uuid>/`
- Editar: `/casestudies/edit/<uuid>/`

### Evaluaciones
- Evaluar candidato: `/evaluations/candidate/<uuid_candidato>/`

## Tours de ayuda
- Al visitar una página por primera vez, se muestra un tour guiado automáticamente
- El botón **?** (esquina inferior derecha) permite:
  - **Ver tour de esta página**: Repite el tour de la página actual
  - **Reiniciar todos los tours**: Resetea todos los tours para verlos de nuevo
- Los tours se recuerdan en el navegador (localStorage)

## Navegación en móvil
- En pantallas pequeñas, el sidebar se oculta
- Se accede con el botón de hamburguesa (☰) en la parte superior izquierda
- El sidebar se abre como overlay y se cierra al hacer clic fuera

## FAQs
- **¿Cómo vuelvo al dashboard?** — Haz clic en "Dashboard" en el sidebar o ve a `/`
- **¿Dónde veo los candidatos?** — Dentro del detalle de cada posición
- **¿Cómo accedo al panel de administración?** — Ve a `/admin/` (solo Admins)
- **¿Puedo usar atajos de teclado?** — Actualmente no hay atajos de teclado configurados

## Notas por rol
- **Admin**: Ve todas las opciones del sidebar incluyendo Empresas
- **Recruiter**: Ve las opciones relevantes a su rol

## Notas sobre plan
La navegación es igual para todos los planes.
