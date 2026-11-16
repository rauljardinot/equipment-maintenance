from psycopg2 import IntegrityError

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged
from odoo.tools import mute_logger


@tagged("post_install", "-at_install")
class TestMaintenance(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.equipment = cls.env["equipment.maintenance.equipment"].create({
            "name": "Compresor", "code": "TEST-COMP-01", "location": "Taller",
        })

    def _task(self, **values):
        return self.env["equipment.maintenance.task"].create({
            "equipment_id": self.equipment.id, **values,
        })

    def test_equipment_code_unique(self):
        with mute_logger("odoo.sql_db"), self.assertRaises(IntegrityError), self.cr.savepoint():
            self.equipment.copy({"code": self.equipment.code})

    def test_negative_hours_rejected(self):
        with self.assertRaises(ValidationError), self.cr.savepoint():
            self._task(hours=-1)

    def test_done_requires_hours(self):
        task = self._task()
        with self.assertRaises(ValidationError), self.cr.savepoint():
            task.action_done()
        task.hours = 1.5
        task.action_start()
        self.assertEqual(task.state, "in_progress")
        task.action_done()
        self.assertEqual(task.state, "done")
        with self.assertRaises(ValidationError), self.cr.savepoint():
            task.hours = 0

    def test_kanban_states_and_related_equipment(self):
        task = self._task()
        self.assertEqual(task.equipment_code, "TEST-COMP-01")
        self.assertEqual(task._expand_states([], []), ["draft", "in_progress", "done", "cancelled"])
        task.action_cancel()
        self.assertEqual(task.state, "cancelled")
        task.action_draft()
        self.assertEqual(task.state, "draft")
