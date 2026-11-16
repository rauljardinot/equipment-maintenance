{
    "name": "Mantenimiento de equipos",
    "version": "18.0.1.1.0",
    "category": "Maintenance",
    "summary": "Equipos y tareas de mantenimiento",
    "license": "LGPL-3",
    "depends": ["base", "web"],
    "data": [
        "security/maintenance_security.xml",
        "security/ir.model.access.csv",
        "views/equipment_views.xml",
        "views/task_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "installable": True,
}
