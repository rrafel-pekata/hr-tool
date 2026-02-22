# Guía de Mantenimiento — Base de Conocimiento del Chatbot

## Ubicación
Los archivos de la base de conocimiento están en `/knowledge/`.

## Cuándo actualizar
- Al agregar una nueva funcionalidad a la aplicación
- Al cambiar URLs o rutas existentes
- Al modificar el comportamiento de una funcionalidad
- Al agregar nuevos roles o cambiar permisos
- Al introducir planes de pago o cambiar límites

## Formato de cada archivo

Cada archivo `.md` debe seguir esta estructura:

```markdown
# Nombre de la Funcionalidad

## Qué es
Descripción breve de la funcionalidad.

## Flujo de usuario
Pasos numerados que el usuario sigue.

## Funcionalidades IA (si aplica)
Qué funciones de IA están disponibles.

## FAQs
Preguntas frecuentes con respuestas concretas.

## URLs disponibles
Lista de URLs relevantes con su descripción.

## Notas por rol
Qué puede hacer Admin vs Recruiter.

## Notas sobre plan
Disponibilidad según plan (actualmente todo gratis).
```

## Buenas prácticas
1. **Mantén `index.md` actualizado**: Siempre que crees o modifiques un archivo, actualiza la descripción en `index.md`
2. **URLs concretas**: Incluye las URLs exactas. Para URLs con UUID, usa `<uuid>` como placeholder
3. **Lenguaje claro**: Escribe como si explicaras a un usuario no técnico
4. **Español**: Todo el contenido debe estar en español
5. **Sin duplicación**: No repitas información que ya está en otro archivo. Referencia al archivo correspondiente
6. **FAQs reales**: Anticipa preguntas que haría un usuario real del sistema
7. **Notas por rol siempre**: Cada archivo debe indicar qué puede hacer cada rol

## Al agregar una nueva app
1. Crea un nuevo archivo `nombre-funcionalidad.md`
2. Sigue la estructura estándar
3. Actualiza `index.md` con la descripción del nuevo archivo
4. Actualiza `navegacion.md` con las nuevas URLs

## Al modificar URLs
1. Actualiza el archivo de la funcionalidad afectada
2. Actualiza `navegacion.md`
