from odoo import api, fields, models
from odoo.exceptions import ValidationError


class MaintenanceTask(models.Model):
    _name = "equipment.maintenance.task"
    _description = "Tarea de mantenimiento"
    _rec_name = "equipment_id"
    _order = "planned_date, id"

    equipment_id = fields.Many2one(
        "equipment.maintenance.equipment", string="Equipo", required=True,
        ondelete="restrict", index=True,
    )
    responsible_id = fields.Many2one(
        "res.users", string="Responsable", required=True,
        default=lambda self: self.env.user, domain=[("share", "=", False)],
        ondelete="restrict", index=True,
    )
    planned_date = fields.Date(string="Fecha prevista", required=True, default=fields.Date.context_today)
    hours = fields.Float(string="Horas", default=0.0)
    state = fields.Selection(
        [("draft", "Borrador"), ("in_progress", "En curso"),
         ("done", "Hecha"), ("cancelled", "Cancelada")],
        string="Estado", required=True, default="draft", index=True,
        group_expand="_expand_states",
    )
    equipment_code = fields.Char(related="equipment_id.code", string="Referencia")
    equipment_image = fields.Image(related="equipment_id.image_1920", string="Foto del equipo")

    @api.model
    def _expand_states(self, states, domain):
        return [key for key, label in self._fields["state"].selection]

    @api.constrains("hours", "state")
    def _check_hours(self):
        for task in self:
            if task.hours < 0:
                raise ValidationError("Las horas no pueden ser negativas.")
            if task.state == "done" and task.hours <= 0:
                raise ValidationError("Debes indicar horas mayores que cero para marcar la tarea como hecha.")

    def action_start(self):
        self.write({"state": "in_progress"})

    def action_done(self):
        self.write({"state": "done"})

    def action_cancel(self):
        self.write({"state": "cancelled"})

    def action_draft(self):
        self.write({"state": "draft"})
