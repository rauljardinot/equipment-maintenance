from odoo import Command
from odoo.exceptions import AccessError, ValidationError
from odoo.tests import TransactionCase, tagged
from odoo.tests.common import new_test_user


@tagged("post_install", "-at_install")
class TestMaintenanceSecurity(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.worker = new_test_user(cls.env, login="maintenance_worker", groups="equipment_maintenance.group_maintenance_user")
        cls.other = new_test_user(cls.env, login="maintenance_other", groups="equipment_maintenance.group_maintenance_user")
        cls.manager = new_test_user(cls.env, login="maintenance_manager", groups="equipment_maintenance.group_maintenance_manager")
        cls.internal = new_test_user(cls.env, login="maintenance_internal", groups="base.group_user")
        cls.equipment = cls.env["equipment.maintenance.equipment"].create({"name": "Equipo", "code": "SEC-01"})
        cls.other_equipment = cls.env["equipment.maintenance.equipment"].create({"name": "Otro equipo", "code": "SEC-02"})
        cls.task = cls.env["equipment.maintenance.task"].create({"equipment_id": cls.equipment.id, "responsible_id": cls.worker.id, "hours": 1})
        cls.other_task = cls.env["equipment.maintenance.task"].create({"equipment_id": cls.other_equipment.id, "responsible_id": cls.other.id, "hours": 2})
        cls.shared_task = cls.env["equipment.maintenance.task"].create({"equipment_id": cls.equipment.id, "responsible_id": cls.other.id, "hours": 3})

    def test_user_sees_only_assigned_tasks(self):
        tasks = self.env["equipment.maintenance.task"].with_user(self.worker).search([])
        self.assertIn(self.task, tasks)
        self.assertNotIn(self.other_task, tasks)
        self.assertNotIn(self.shared_task, tasks)
        with self.assertRaises(AccessError):
            self.other_task.with_user(self.worker).read(["note", "hours"])

    def test_user_can_update_state_and_note(self):
        task = self.task.with_user(self.worker)
        task.write({"state": "in_progress", "note": "Revisión iniciada"})
        self.assertEqual(task.note, "Revisión iniciada")
        task.action_done()
        self.assertEqual(task.state, "done")
        task.action_draft()
        task.action_cancel()
        self.assertEqual(task.state, "cancelled")

    def test_user_cannot_change_business_fields(self):
        task = self.task.with_user(self.worker)
        for values in [
            {"hours": 2}, {"responsible_id": self.other.id},
            {"equipment_id": self.other_equipment.id}, {"planned_date": "2026-12-01"},
            {"equipment_code": "OTHER"}, {"equipment_image": False},
            {"can_manage": True}, {"state": "done", "hours": 4},
        ]:
            with self.subTest(values=values), self.assertRaises(AccessError), self.cr.savepoint():
                task.write(values)

    def test_user_cannot_modify_another_task(self):
        for task in self.other_task | self.shared_task:
            with self.assertRaises(AccessError), self.cr.savepoint():
                task.with_user(self.worker).write({"note": "No permitido"})
            with self.assertRaises(AccessError), self.cr.savepoint():
                task.with_user(self.worker).action_start()
        with self.assertRaises(AccessError), self.cr.savepoint():
            (self.task | self.other_task).with_user(self.worker).write({"state": "in_progress"})

    def test_user_cannot_create_or_delete(self):
        with self.assertRaises(AccessError), self.cr.savepoint():
            self.env["equipment.maintenance.task"].with_user(self.worker).create({"equipment_id": self.equipment.id})
        with self.assertRaises(AccessError), self.cr.savepoint():
            self.task.with_user(self.worker).unlink()
        with self.assertRaises(AccessError), self.cr.savepoint():
            self.task.with_user(self.worker).copy()

    def test_user_equipment_read_only_and_scoped(self):
        equipment = self.equipment.with_user(self.worker)
        self.assertEqual(equipment.name, "Equipo")
        self.assertNotIn("task_ids", equipment.fields_get())
        self.assertNotIn("total_maintenance_hours", equipment.fields_get())
        with self.assertRaises(AccessError):
            equipment.read(["task_ids"])
        with self.assertRaises(AccessError):
            equipment.read(["total_maintenance_hours"])
        with self.assertRaises(AccessError):
            self.other_equipment.with_user(self.worker).read(["name"])
        with self.assertRaises(AccessError), self.cr.savepoint():
            equipment.write({"name": "Cambio"})
        with self.assertRaises(AccessError), self.cr.savepoint():
            equipment.write({"task_ids": [Command.update(self.task.id, {"hours": 5})]})
        with self.assertRaises(AccessError), self.cr.savepoint():
            equipment.unlink()
        with self.assertRaises(AccessError), self.cr.savepoint():
            self.env["equipment.maintenance.equipment"].with_user(self.worker).create({"name": "X", "code": "X"})

    def test_user_done_still_requires_hours(self):
        self.task.hours = 0
        with self.assertRaises(ValidationError), self.cr.savepoint():
            self.task.with_user(self.worker).action_done()

    def test_manager_full_access(self):
        model = self.env["equipment.maintenance.task"].with_user(self.manager)
        self.assertTrue(set((self.task | self.other_task | self.shared_task).ids) <= set(model.search([]).ids))
        self.other_task.with_user(self.manager).write({"hours": 4, "note": "Revisada", "responsible_id": self.worker.id})
        equipment = self.env["equipment.maintenance.equipment"].with_user(self.manager).create({"name": "Nuevo", "code": "SEC-NEW"})
        equipment.write({"location": "Taller"})
        task = model.create({"equipment_id": equipment.id, "hours": 2})
        task.action_done()
        self.assertEqual(equipment.total_maintenance_hours, 2)
        task.unlink()
        equipment.unlink()

    def test_internal_user_without_group_denied(self):
        for record in (self.task, self.equipment):
            with self.assertRaises(AccessError):
                record.with_user(self.internal).read(["id"])

    def test_form_permissions_and_note(self):
        form = self.env["equipment.maintenance.task"].with_user(self.worker).get_view(view_type="form")
        self.assertIn('name="note"', form["arch"])
        self.assertIn('readonly="not can_manage"', form["arch"])
        self.assertFalse(self.task.with_user(self.worker).can_manage)
        self.assertTrue(self.task.with_user(self.manager).can_manage)
