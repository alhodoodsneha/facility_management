# -*- coding: utf-8 -*-
#############################################################################
from email.policy import default

#    Alhodood Technologies.
#    Copyright (C) 2024-TODAY Alhodood Technologies(<https://www.alhodood.com>)
#    Author: Alhodood Technologies(<https://www.alhodood.com>)
#    You can modify it under the terms of the GNU Affero General Public License
#    (AGPL v3), Version 3.
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License (AGPL v3) for more details.
#    You should have received a copy of the GNU Affero General Public License
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#############################################################################
from odoo import api, models, fields
from odoo.exceptions import UserError


class EstimationLineSales(models.Model):
    _name = 'estimation.line.sale.order'

    description = fields.Text(
        string='Description'
    )
    qty = fields.Float(
        string='Quantity'
    )
    unit_price = fields.Float(
        string='Unit Price'
    )
    line_margin = fields.Float(
        string='Margin'
    )
    total = fields.Float(
        'SubTotal',
        compute='_compute_total'
    )
    task_id = fields.Many2one(
        'project.task',
        string='Task'
    )
    sale_order_id = fields.Many2one(
        'sale.order',
        string='Sale Order'
    )

    @api.depends('qty', 'unit_price','line_margin')
    def _compute_total(self):
        for rec in self:
            if rec.qty and rec.unit_price:
                rec.total = rec.qty * (rec.unit_price + rec.line_margin)
            else:
                rec.total = 0.0


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    ins_task_id = fields.Many2one(
        'project.task',
        string='Estimation Task'
    )

    create_pr = fields.Boolean(
        string="Create Inspection job",
        default= False
    )

    estimation_line_ids = fields.One2many(
        'estimation.line.sale.order',
        'sale_order_id',
        string='Estimation Line'
    )
    estimation_total = fields.Float(
        string='Estimation Total'
    )

    ins_crm_id = fields.Many2one(
        'crm.lead',
        string="CRM"
    )

    property_status = fields.Char(
        string="Property Status"
    )
    property_project = fields.Char(
        string="Project"
    )
    property_id = fields.Many2one(
        'property.property',
        string="Property"
    )
    property_unit = fields.Char(
        string="Unit"
    )
    property_request = fields.Char(
        string="Request"
    )

    job_type = fields.Selection([
        ('one_time', 'One Time Job'),
        ('amc_work', 'AMC'),
        ('project', 'Project'),
        ('other', 'Other')
    ],
        string="Job Type",
        tracking=True
    )

    service_type = fields.Selection(
        [('service_created', 'Service Created'),
         ('service_done', 'Service Done'),
         ('amc_job', 'AMC Job Created')
         ],
        string="Service Type"
    )

    service_task = fields.Many2one(
        'project.task',
        string="Service task"
    )

    is_other_ot_task = fields.Boolean(
        string="Is Other Ot Task",
        default=False
    )

    other_one_time_task = fields.Many2one(
        'project.task',
        string="Related task"
    )

    other_one_time_prj = fields.Many2one(
        'project.project',
        string="Related Job"
    )


    def action_confirm(self):
        for order in self:
            if order.ins_crm_id:
                order.ins_crm_id.stage_type = 'quote_confirmed'
                order.ins_crm_id.action_set_won_rainbowman()
        return super(SaleOrder, self).action_confirm()


    def action_create_fsm_task(self):
        if not self.property_unit:
            raise UserError("Please Choose Property unit")
        if not self.property_project:
            raise UserError("Please Choose Project")
        return {
            'name': 'Field Service Creation',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'filed.service.create.wizard',
            'target': 'new',
            'context': {
                'active_id': self.id,
                'field_service': True,
            },
        }

    def action_create_fsm_job(self):
        if not self.property_unit:
            raise UserError("Please Choose Property unit")
        if not self.property_project:
            raise UserError("Please Choose Project")
        return {
            'name': 'Field Service Creation',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'filed.service.job.create.wizard',
            'target': 'new',
            'context': {
                'active_id': self.id,
                'field_service': True,
            },
        }