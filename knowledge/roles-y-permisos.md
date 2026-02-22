# Roles y Permisos

## Qué es
Pekata tiene un sistema de roles que determina qué puede hacer cada usuario dentro de la aplicación. Actualmente existen dos roles: Admin y Recruiter.

## Roles disponibles

### Admin
El administrador tiene acceso completo a todas las funcionalidades:
- Crear, editar y desactivar empresas
- Gestionar usuarios y asignar roles
- Crear y gestionar posiciones
- Gestionar candidatos, entrevistas y casos prácticos
- Generar evaluaciones con IA
- Acceso al panel de administración de Django (`/admin/`)

### Recruiter
El reclutador puede gestionar el proceso de selección dentro de su empresa:
- Ver el dashboard de su empresa
- Crear y gestionar posiciones
- Gestionar candidatos (agregar, editar, cambiar estado)
- Programar y registrar entrevistas
- Crear y enviar casos prácticos
- Generar evaluaciones con IA

### Diferencias clave
| Funcionalidad | Admin | Recruiter |
|---|---|---|
| Crear empresa | Sí | No |
| Editar empresa | Sí | No |
| Desactivar empresa | Sí | No |
| Gestionar usuarios | Sí | No |
| Panel admin Django | Sí | No |
| Crear posiciones | Sí | Sí |
| Gestionar candidatos | Sí | Sí |
| Entrevistas | Sí | Sí |
| Casos prácticos | Sí | Sí |
| Evaluación IA | Sí | Sí |

## Gestión de usuarios
- Los Admins pueden crear usuarios desde el panel de administración (`/admin/`)
- Al crear un usuario, se le asigna un rol y una empresa
- Cada usuario pertenece a una sola empresa

## FAQs
- **¿Puedo cambiar el rol de un usuario?** — Sí, desde el panel de administración de Django.
- **¿Puedo tener varios Admins?** — Sí, no hay límite en el número de Admins.
- **¿Un Recruiter puede ver datos de otra empresa?** — No, cada usuario solo ve datos de su empresa.
- **¿Cómo creo un nuevo usuario?** — Desde el panel de administración (`/admin/`), sección Usuarios.

## URLs disponibles
- Panel de administración: `/admin/`

## Notas sobre plan
El sistema de roles está disponible en todos los planes.
