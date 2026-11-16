from odoo import fields, models


class Equipment(models.Model):
    _name = "equipment.maintenance.equipment"
    _description = "Equipo de mantenimiento"
    _order = "name, id"

    name = fields.Char(string="Nombre", required=True)
    code = fields.Char(string="Referencia", required=True, index=True, copy=False)
    location = fields.Char(string="Ubicación")
    image_1920 = fields.Image(string="Foto del equipo", max_width=1920, max_height=1920)
    task_ids = fields.One2many(
        "equipment.maintenance.task", "equipment_id", string="Tareas de mantenimiento"
    )

    _sql_constraints = [
        ("code_unique", "unique(code)", "La referencia del equipo debe ser única."),
    ]
