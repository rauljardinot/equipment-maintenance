# Equipment Maintenance — Odoo 18

Proyecto de prueba de mantenimiento de equipos.
Módulo técnico: `equipment_maintenance`. No depende de la aplicación estándar
`maintenance`: utiliza modelos propios para este ejercicio.

## Funcionalidad

- Menú **Mantenimiento → Equipos / Tareas de mantenimiento**.
- Equipos con nombre, referencia única, ubicación y foto.
- Horas totales de mantenimiento calculadas por equipo, visibles en lista,
  formulario y kanban.
- Tareas con equipo, responsable asignado, fecha prevista, horas, nota y cuatro estados:
  borrador, en curso, hecha y cancelada.
- Listas, formularios y kanban. El kanban de tareas muestra la foto, el nombre
  y la referencia del equipo, el estado, el responsable, la fecha y las horas.
- Kanban de tareas agrupado por estado, con las cuatro columnas incluso vacías.
- Búsqueda por estado y responsable, filtros por estado y «Mis tareas»,
  agrupaciones por estado y responsable.
- Botones para iniciar, finalizar, cancelar y volver a borrador.
- Referencia única mediante restricción SQL; horas no negativas y horas mayores
  que cero para finalizar, también al cambiar de estado arrastrando una tarjeta.

## Cómo ejecutarlo

### Requisitos

- Una instalación funcional de **Odoo 18** con sus dependencias Python y PostgreSQL.
- Acceso a PostgreSQL con un usuario autorizado para crear la base de pruebas,
  o una base vacía previamente creada para Odoo.
- Este repositorio en el equipo donde se ejecuta Odoo. No requiere Enterprise.
  Las dependencias del módulo son `base` y `web`.

Clonar el proyecto si todavía no está disponible:

```sh
git clone https://github.com/rauljardinot/equipment-maintenance.git
cd equipment-maintenance
```

Los siguientes comandos usan rutas de ejemplo: sustituir `/ruta/odoo18`,
`/ruta/equipment-maintenance`, `/ruta/odoo.conf` y los nombres de base por los
valores del entorno. Usar el Python o entorno virtual de la instalación de Odoo.
El archivo `odoo.conf` debe contener la conexión local a PostgreSQL; no se incluye
ni se publica con credenciales en este repositorio.

### Instalar o actualizar

Instalar en una base exclusiva para el ejercicio:

```sh
python3 /ruta/odoo18/odoo-bin -c /ruta/odoo.conf \
  --addons-path=/ruta/odoo18/odoo/addons,/ruta/odoo18/addons,/ruta/equipment-maintenance \
  -d equipment_maintenance_demo -i equipment_maintenance \
  --without-demo=all --stop-after-init
```

Para actualizar una instalación existente, usar el mismo comando sustituyendo
`-i equipment_maintenance` por `-u equipment_maintenance`.

También se puede instalar desde la interfaz: añadir el repositorio a
`addons_path`, reiniciar Odoo, actualizar la lista de aplicaciones en modo
desarrollador y buscar **Mantenimiento de equipos**.

### Iniciar el servidor

El comando anterior termina tras instalar. Para entrar en la aplicación, iniciar
Odoo sin `--stop-after-init`:

```sh
python3 /ruta/odoo18/odoo-bin -c /ruta/odoo.conf \
  --addons-path=/ruta/odoo18/odoo/addons,/ruta/odoo18/addons,/ruta/equipment-maintenance \
  -d equipment_maintenance_demo --http-port=8069
```

Abrir [Odoo local](http://localhost:8069/web), iniciar sesión y asignar los grupos
indicados en **Seguridad y asignación de permisos**. Si el puerto está ocupado,
elegir otro y ajustar la dirección del navegador. El menú no aparece para cuentas
sin un grupo de mantenimiento asignado.

### Recorrido de prueba manual

1. Como administrador de usuarios, asignar **Responsable** a una cuenta y
   **Usuario** a otra cuenta interna.
2. Como Responsable, entrar en **Mantenimiento → Equipos** y crear un equipo con
   nombre, referencia única, ubicación y, opcionalmente, foto.
3. Crear una tarea, asignarla a la cuenta Usuario e indicar fecha y horas.
4. Entrar con la cuenta Usuario: comprobar que solo ve sus tareas, editar la nota
   y cambiar el estado. Los demás valores deben permanecer de solo lectura.
5. Volver como Responsable y comprobar las horas totales del equipo.
6. Comprobar que se rechazan referencias duplicadas, horas negativas y tareas
   hechas con cero horas. Un equipo con tareas asociadas no puede eliminarse.

Este recorrido queda documentado para la revisión manual; la validación ejecutada
hasta ahora es la instalación/actualización y los tests automáticos.

## Tests

Ejecutar sobre una base exclusiva de pruebas:

```sh
python3 /ruta/odoo18/odoo-bin -c /ruta/odoo.conf \
  --addons-path=/ruta/odoo18/odoo/addons,/ruta/odoo18/addons,/ruta/equipment-maintenance \
  -d equipment_maintenance_test -i equipment_maintenance \
  --test-enable --test-tags /equipment_maintenance --stop-after-init \
  --http-port=0 --workers=0 --max-cron-threads=0 --without-demo=all
```

Validación realizada en Odoo 18: instalación, actualización y veinticuatro tests
`TransactionCase` aprobados, sin fallos ni errores. No se ha realizado todavía
una revisión visual en navegador.

Las pruebas cubren referencias duplicadas al crear y editar equipos, horas
negativas al crear y editar tareas, bloqueo de tareas hechas sin horas al crear,
usar el botón o escribir el estado directamente (como hace el kanban), finalización
con horas positivas y los botones de cambio de estado. Cero horas es válido
mientras la tarea no esté hecha.
También se comprueba el total de horas sin tareas, al crear, editar y eliminar
tareas, al trasladarlas a otro equipo y después de guardar y volver a leer el total.

## Decisiones de diseño

- Se usan modelos propios para mantener el ejercicio independiente de la
  aplicación estándar de mantenimiento y concentrar las reglas en este módulo.
- La referencia corresponde al código único solicitado, sensible a mayúsculas.
  La unicidad se garantiza en PostgreSQL, incluso ante creaciones simultáneas.
- El estado pertenece a la tarea: un equipo puede tener varias tareas en estados
  diferentes. El kanban de equipos muestra sus datos y foto; el de tareas añade
  estado y responsable.
- Las horas se guardan como número decimal y se muestran con `float_time`:
  1,5 horas se representan como 01:30.
- El total de horas es calculado, almacenado y de solo lectura. Suma todas las
  tareas, incluidas las canceladas: el estado no elimina las horas registradas.
  Se recalcula al cambiar horas, crear o eliminar tareas o cambiar su equipo.
- No se permite eliminar equipos con tareas asociadas.
- Configuración queda definida sin acción ni submenús. Odoo oculta los menús
  vacíos; aparecerá cuando se añada su primera opción.
- El grupo Responsable administra equipos y tareas; el grupo Usuario solo accede
  a sus tareas asignadas y modifica estado y nota. Los usuarios sin estos grupos,
  de portal y públicos no tienen acceso.

## Seguridad y asignación de permisos

Después de reiniciar Odoo y actualizar el módulo (`-u equipment_maintenance`),
abrir **Ajustes → Usuarios y compañías → Usuarios**, seleccionar un usuario y
asignar su nivel en **Mantenimiento de equipos**:

| Nivel | Lectura | Cambios permitidos | Crear / eliminar |
| --- | --- | --- | --- |
| Usuario | Solo sus tareas y los datos básicos de sus equipos | Estado y nota de sus tareas | No |
| Responsable | Todos los equipos y tareas | Todos los valores editables | Sí |
| Sin grupo | Sin acceso al módulo | Ninguno | No |

El grupo Responsable incluye los permisos del grupo Usuario. El campo
**Responsable** de una tarea es su usuario asignado; esto no le otorga el grupo
Responsable. No se crean cuentas ni contraseñas automáticamente.

El usuario ve el menú de tareas; los menús Equipos y Configuración se reservan
al Responsable. Los datos de equipo, asignación, fecha y horas son de solo lectura
para el Usuario. Puede cambiar el estado con los botones o arrastrando en kanban
y editar una nota de texto. Para finalizar, la tarea debe tener horas positivas
registradas por un Responsable. La nota se puede editar; no es un historial de
comentarios.

Las ACL impiden crear y eliminar; las reglas de registro limitan la lectura y
edición a las tareas asignadas, y una validación en `write` permite al Usuario
únicamente `state` y `note`, también por RPC o importación. Los Responsables
mantienen las reglas de código único y horas válidas y la protección frente a
eliminar equipos con tareas asociadas.

El historial de tareas del equipo y su total de horas se reservan al Responsable
para no revelar actividad de otros usuarios sobre un equipo compartido.
Las ACL existentes se actualizan con los mismos identificadores, retirando el
acceso general que tenían los usuarios internos en la versión anterior.
Es necesario asignar los nuevos grupos a las cuentas que deban usar el módulo.
El superusuario técnico de Odoo conserva su acceso administrativo habitual.

Las diez pruebas de seguridad usan usuarios reales de prueba con `with_user`:
comprueban aislamiento entre asignaciones (también equipos compartidos), edición
de estado y nota, bloqueo de los demás campos y de escrituras mixtas, creación,
copia y eliminación prohibidas, restricciones de equipos, horas al finalizar,
acceso completo del Responsable y denegación al usuario interno sin grupo.

## Qué haría con más tiempo

- Revisar las vistas en navegador con ambos perfiles, distintas resoluciones,
  equipos con y sin foto y suficientes tareas para comprobar la navegación.
- Añadir tests de interfaz para los botones, el arrastre en kanban y la edición
  de notas, además de los tests actuales del servidor.
- Incorporar un historial de notas y cambios de estado con autor y fecha;
  actualmente la nota es un texto editable, sin trazabilidad de sus versiones.
- Añadir planificación recurrente y avisos de vencimiento si el alcance lo requiere.
- Medir el cálculo de horas con grandes volúmenes y valorar una suma agregada
  para reducir la lectura de tareas por equipo.
- Automatizar los tests en CI sobre una base temporal de Odoo 18.

Estas mejoras no forman parte de la funcionalidad implementada.

## Cómo se usó la IA

El desarrollo se realizó con Codex a partir de instrucciones del usuario, por
etapas. Se indica qué se incorporó al código y qué se corrigió durante la
validación; la revisión visual y la aceptación funcional del usuario siguen
pendientes.

### Qué se le pidió

- Crear el repositorio público y desarrollar un módulo para **Odoo 18**.
- Implementar equipos, tareas, menús, vistas de lista y formulario y kanban con
  foto, referencia, agrupación y búsqueda por estado y responsable.
- Garantizar código único, horas no negativas, finalización con horas positivas
  y botones para cambiar de estado.
- Calcular las horas totales por equipo.
- Limitar al Usuario a sus tareas asignadas, estado y nota, y dar al Responsable
  permisos para crear, editar y eliminar.
- Añadir tests `TransactionCase`, documentación y commits progresivos.

### Qué se aceptó e incorporó

- Modelos propios, estado en la tarea y foto/referencia relacionadas desde el equipo.
- Restricción SQL para el código único y validación de horas en el modelo, para
  cubrir formulario, cambios directos, importaciones y arrastre en kanban.
- Total calculado y almacenado con dependencias sobre las horas de las tareas;
  suma todos los estados, incluidas las tareas canceladas.
- Seguridad mediante ACL, reglas de registro y una lista de campos permitidos
  en `write`; los campos de solo lectura en las vistas complementan esa seguridad.
- Nota de texto editable y dos grupos, con el Responsable heredando del Usuario.
- Tests con usuarios de prueba y bases separadas, sin modificar la base de trabajo.

### Qué se corrigió o ajustó

- La primera ejecución de pruebas encontró un puerto ocupado. Se configuró
  `--http-port=0` para que el sistema eligiera uno libre, con workers y cron
  desactivados en la ejecución de tests.
- Se amplió la cobertura inicial de cuatro tests: primero se comprobaron las
  reglas al editar y escribir estados directamente; después, el recálculo de
  horas y la seguridad, hasta llegar a **24 tests**.
- Al introducir los grupos se sustituyeron las ACL iniciales de todos los usuarios
  internos por ACL de los grupos específicos, reutilizando sus identificadores
  para que la actualización retire los permisos anteriores.
- Una prueba detectó identificadores de tareas ajenas en el historial relacional
  en caché de un equipo compartido. Se restringieron el historial y el total de
  horas al Responsable y se añadieron comprobaciones de acceso a esos campos.
- Se documentó que Configuración, definido sin acción ni submenús, queda oculto
  por Odoo hasta añadir su primera opción.

### Cómo se verificó el resultado

Se contrastó la estructura de vistas con la
[documentación oficial de Odoo 18](https://www.odoo.com/documentation/18.0/developer/reference/user_interface/view_architectures.html)
y la firma de agrupación con el código local de Odoo. Se instaló y actualizó
el módulo en una base de pruebas y se ejecutaron los **24 tests `TransactionCase`
sin fallos ni errores**. Esto valida las reglas y permisos en el servidor;
la revisión visual en navegador todavía está pendiente.

Los commits separan modelos, interfaz, reglas, total de horas, seguridad y
ampliaciones de tests/documentación. El historial puede consultarse con:

```sh
git log --oneline --reverse
```
