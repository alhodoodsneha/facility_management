#############################################################################
#    Alhodood Technologies.
#    Copyright (C) 2024-TODAY Alhodood Technologies(<https://www.alhodood.com>)
#    Author: Alhodood Technologies(<https://www.alhodood.com>)
#    You can modify it under the terms of the GNU Affero General Public License
#    (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License (AGPL v3) for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
from odoo import api, fields, models
from odoo.exceptions import UserError
from collections import defaultdict

class EmployeeOvertime(models.Model):
    _name = "employee.overtime"
    _description = "Employee Overtime"

    name = fields.Char(
        string="Name",
    )

    start_date = fields.Date(
        string="Start Dete",
        required=True
    )
    end_date = fields.Date(
        string="End Date",
        required=True
    )

    line_ids = fields.One2many(
        "employee.overtime.line",
        "overtime_id",
        string="Overtime Lines",
    )
    state = fields.Selection([
        ('draft','Draft'),
        ('completed','Completed')
    ],
        string="State",
        default='draft'
    )

    def action_generate(self):
        self.line_ids.unlink()

        if self.start_date > self.end_date:
            raise UserError("Start Date must be before End Date.")
        timesheets = self.env["account.analytic.line"].search([
            ("date", ">=", self.start_date),
            ("date", "<=", self.end_date),
            ("employee_id", "!=", False),
        ])
        data = defaultdict(float)
        # Group by Employee + Date
        for ts in timesheets:
            key = (ts.employee_id.id, ts.date)
            data[key] += ts.unit_amount

        for (employee_id, work_date), worked in data.items():
            employee = self.env["hr.employee"].browse(employee_id)

            expected = employee.resource_calendar_id.hours_per_day or 8.0

            overtime = max(worked - expected, 0)

            self.env["employee.overtime.line"].create({
                "overtime_id": self.id,
                "employee_id": employee.id,
                "date_start": work_date,
                "worked_hours": worked,
                "overtime_hours": overtime,
            })


class EmployeeOvertimeLine(models.Model):
    _name = "employee.overtime.line"
    _description = "Employee Overtime Line"

    overtime_id = fields.Many2one(
        "employee.overtime",
        string="Over Time"
    )

    employee_id = fields.Many2one(
        "hr.employee",
        string="Employee"
    )

    date_start = fields.Date(
        string="Date"
    )

    worked_hours = fields.Float(
        string="Worked Hours"
    )

    overtime_hours = fields.Float(
        string="Overtime Hours"
    )