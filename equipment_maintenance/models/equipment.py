from odoo import api, fields, models


class Equipment(models.Model):
    _name = "equipment.maintenance.equipment"
    _description = "Equipo de mantenimiento"
    _order = "name, id"

    name = fields.Char(string="Nombre", required=True)
    code = fields.Char(string="Referencia", required=True, index=True, copy=False)
    location = fields.Char(string="Ubicación")
    image_1920 = fields.Image(string="Foto del equipo", max_width=1920, max_height=1920)
    task_ids = fields.One2many(
        "equipment.maintenance.task", "equipment_id", string="Tareas de mantenimiento",
        groups="equipment_maintenance.group_maintenance_manager",
    )
    total_maintenance_hours = fields.Float(
        string="Horas totales de mantenimiento",
        compute="_compute_total_maintenance_hours", store=True,
        groups="equipment_maintenance.group_maintenance_manager",
        help="Suma de las horas registradas en todas las tareas del equipo, en cualquier estado.",
    )

    @api.depends("task_ids.hours")
    def _compute_total_maintenance_hours(self):
        for equipment in self:
            equipment.total_maintenance_hours = sum(equipment.task_ids.mapped("hours"))

    _sql_constraints = [
        ("code_unique", "unique(code)", "La referencia del equipo debe ser única."),
    ]
