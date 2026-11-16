# Equipment Maintenance — Odoo 18

Primera etapa del proyecto de prueba de mantenimiento de equipos.
Módulo técnico: `equipment_maintenance`. No depende de la aplicación estándar
`maintenance`: utiliza modelos propios para este ejercicio.

## Funcionalidad

- Menú **Mantenimiento → Equipos / Tareas de mantenimiento**.
- Equipos con nombre, referencia única, ubicación y foto.
- Tareas con equipo, responsable, fecha prevista, horas y cuatro estados:
  borrador, en curso, hecha y cancelada.
- Listas, formularios y kanban. El kanban de tareas muestra la foto, el nombre
  y la referencia del equipo, el estado, el responsable, la fecha y las horas.
- Kanban de tareas agrupado por estado, con las cuatro columnas incluso vacías.
- Búsqueda por estado y responsable, filtros por estado y «Mis tareas»,
  agrupaciones por estado y responsable.
- Botones para iniciar, finalizar, cancelar y volver a borrador.
- Referencia única mediante restricción SQL; horas no negativas y horas mayores
  que cero para finalizar, también al cambiar de estado arrastrando una tarjeta.

## Instalación

1. Agregar la ruta absoluta de este repositorio a `addons_path`, junto a los
   addons estándar de Odoo 18.
2. Reiniciar Odoo y actualizar la lista de aplicaciones en modo desarrollador.
3. Buscar **Mantenimiento de equipos** e instalar.

Por consola, sustituyendo las rutas y el nombre de la base:

```sh
python3 /ruta/odoo18/odoo-bin -c /ruta/odoo.conf \
  --addons-path=/ruta/odoo18/odoo/addons,/ruta/odoo18/addons,/ruta/equipment-maintenance \
  -d base_pruebas -i equipment_maintenance --stop-after-init
```

Para actualizar una instalación existente, sustituir `-i` por `-u`.

## Tests

Ejecutar sobre una base exclusiva de pruebas:

```sh
python3 /ruta/odoo18/odoo-bin -c /ruta/odoo.conf \
  --addons-path=/ruta/odoo18/odoo/addons,/ruta/odoo18/addons,/ruta/equipment-maintenance \
  -d equipment_maintenance_test -i equipment_maintenance \
  --test-enable --test-tags /equipment_maintenance --stop-after-init \
  --http-port=0 --workers=0 --max-cron-threads=0 --without-demo=all
```

Validación realizada en Odoo 18: instalación completa y cuatro tests
`TransactionCase` aprobados, sin fallos ni errores. No se ha realizado todavía
una revisión visual en navegador.

## Decisiones de esta etapa

- La referencia corresponde al código único solicitado, sensible a mayúsculas.
- El estado pertenece a la tarea: un equipo puede tener varias tareas en estados
  diferentes. El kanban de equipos muestra sus datos y foto; el de tareas añade
  estado y responsable.
- Las horas se guardan como número decimal y se muestran con `float_time`:
  1,5 horas se representan como 01:30.
- No se permite eliminar equipos con tareas asociadas.
- Configuración queda definida sin acción ni submenús. Odoo oculta los menús
  vacíos; aparecerá cuando se añada su primera opción.
- Por ahora todos los usuarios internos tienen permisos de lectura, creación,
  edición y eliminación. Los usuarios de portal y públicos no tienen acceso.

## Próximas etapas / con más tiempo

- Grupos de usuario y responsable con permisos distintos.
- Campo calculado con las horas totales de mantenimiento por equipo.
- Ampliar pruebas de seguridad y revisar visualmente las vistas con datos reales.

## Uso de IA

Se pidió a Codex implementar esta primera etapa para Odoo 18: modelos, menús,
listas, formularios, kanban con foto y búsqueda por estado y responsable.
Se aceptaron los modelos propios, el estado de tarea, la foto relacionada,
las restricciones y los tests. Se contrastó la estructura de vistas con la
[documentación oficial de Odoo 18](https://www.odoo.com/documentation/18.0/developer/reference/user_interface/view_architectures.html)
y se verificó la firma de agrupación en el código local de Odoo.
Se corrigió la ejecución de las pruebas para usar un puerto HTTP libre,
evitar el conflicto con el servidor local y trabajar en una base separada.
Los commits separan modelos y permisos básicos, interfaz, y pruebas/documentación.
