# -*- coding: utf-8 -*-
#############################################################################
#    Alhodood Technologies.
#
#    Copyright (C) 2024-TODAY Alhodood Technologies(<https://www.alhodood.com>)
#    Author: Alhodood Technologies(<https://www.alhodood.com>)
#
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
from odoo.exceptions import UserError
from odoo import api, models, fields, _


class Project(models.Model):
    _inherit = 'project.project'

    is_inspection = fields.Boolean(
        string="Inspection Task",
        default=False
    )

    is_amc_created = fields.Boolean(
        string="Is Amc Created",
        default=False
    )

    fsm_sale_order_id = fields.Many2one(
        'sale.order',
        string="Sale Order"
    )

    crm_lead_id = fields.Many2one(
        'crm.lead',
        string="Crm",
        tracking=True
    )

    quoted_amount = fields.Float(
        string="Quoted Amount"
    )

    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse')
    location_id = fields.Many2one('stock.location', string='Project Location')

    sequence_code = fields.Char(
        string="Sequence"
    )

    property_status = fields.Char(
        string="Property Status",
        tracking=True

    )
    property_project = fields.Char(
        string="Project",
        tracking=True
    )
    property_id = fields.Many2one(
        'property.property',
        string="Property",
        tracking=True
    )
    property_unit = fields.Char(
        string="Unit",
        tracking=True
    )
    property_request = fields.Char(
        string="Request",
        tracking=True
    )

    invoice_per = fields.Float(
        string="Invoice Percentage",
        compute='_compute_total_inv_per'

    )

    balance_per = fields.Float(
        string="Balance Percentage",
        compute='_compute_total_inv_per'
    )

    invoiced_amount = fields.Float(
        string="Invoiced Amount",
        default=0.0
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

    @api.depends('name', 'property_unit', 'property_project')
    def _compute_total_inv_per(self):
        for rec in self:
            invoice = self.env['account.move'].search(
                [('project_id', '=', rec.id),
                 ('move_type', '=', 'out_invoice'),
                 ('is_prj_inv', '=', True),
                 ('state', '=', 'posted')])
            if invoice:
                rec.invoice_per = sum(invoice.mapped('inv_per'))
                rec.invoiced_amount = (rec.quoted_amount * rec.invoice_per)/100
            else:
                rec.invoice_per = 0.0
                rec.invoiced_amount = 0.0
            rec.balance_per = 100 - rec.invoice_per

    def action_view_tasks(self):
        # Using the timesheet filter hide context
        action = super().action_view_tasks()
        if self.job_type:
            action['context']['default_job_type'] = self.job_type
            action['context']['default_property_project'] = self.property_project
            action['context']['default_property_status'] = self.property_status
            action['context']['default_property_id'] = self.property_id.id
            action['context']['default_property_unit'] = self.property_unit
            action['context']['default_property_request'] = self.property_request
        return action

    @api.model
    def create(self, vals):
        res = super(Project, self).create(vals)
        res.sequence_code = self.env['ir.sequence'].next_by_code('project.sequence')
        res.name = res.sequence_code +' -'+res.name
        warehouse = self.env['stock.warehouse'].sudo().create({
            'name': res.name,
            'code': res.sequence_code[:5].upper(),
        })
        location_vals = {
            'name': res.name,
            'location_id': warehouse.lot_stock_id.id,
            'usage': 'internal',
        }
        location = self.env['stock.location'].sudo().create(location_vals)
        res.warehouse_id = warehouse.id
        res.location_id = location.id
        return res


    def action_create_invoices(self):
        invoice = self.env['account.move'].search(
            [('project_id', '=', self.id), ('is_prj_inv', '=', True),
             ('move_type', '=', 'out_invoice'), ('state', '=', 'draft')])
        if invoice:
            raise UserError(
                _("Already Pending Invoices Are There Please Post Or Cancel It !!"))
        return {
            'name': 'Create Invoice',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            "view_type": "form",
            'res_model': 'advance.invoice.wizard',
            'target': 'new',
            'context': {
                'active_id': self.id,
                'default_project_id': self.id,
                'default_balance_per': self.balance_per,
            }
        }

    def action_view_invoices(self):
        return {
            'name': 'Customer Invoices',
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'list,form',
            'domain': [('project_id', '=', self.id),
                       ('move_type', 'in', ('out_invoice', 'out_refund'))],
            'target': 'current',
        }

    def action_view_purchase(self):
        if self.warehouse_id and self.warehouse_id.in_type_id:
            return {
                'name': 'Purchase',
                'type': 'ir.actions.act_window',
                'res_model': 'purchase.order',
                'view_mode': 'list,form',
                'domain': [('project_id', '=', self.id)],
                'target': 'current',
                'context': {
                    'default_project_id': self.id,
                    'default_picking_type_id': self.warehouse_id.in_type_id.id,
                }
            }
        else:
            return {
                'name': 'Purchase',
                'type': 'ir.actions.act_window',
                'res_model': 'purchase.order',
                'view_mode': 'list,form',
                'domain': [('project_id', '=', self.id)],
                'target': 'current',
                'context': {
                    'default_project_id': self.id,
                }
            }

    def action_view_internal_transfers(self):
        if self.warehouse_id and self.warehouse_id.int_type_id:
            return {
                'name': 'Internal Transfer',
                'type': 'ir.actions.act_window',
                'res_model': 'stock.picking',
                'view_mode': 'list,form',
                'domain': [('project_id', '=', self.id)],
                'target': 'current',
                'context': {
                    'default_project_id': self.id,
                    'default_restricted_picking_type_code': 'internal',
                    'default_picking_type_id':self.warehouse_id.int_type_id.id,
                }
            }
        else:
            return {
                'name': 'Internal Transfer',
                'type': 'ir.actions.act_window',
                'res_model': 'stock.picking',
                'view_mode': 'list,form',
                'domain': [('project_id', '=', self.id)],
                'target': 'current',
                'context': {
                    'default_project_id': self.id,
                    'default_restricted_picking_type_code':'internal',
                }
            }


    def action_view_timesheet_fsm(self):
        return {
            'name': 'Timesheets',
            'type': 'ir.actions.act_window',
            'res_model': 'account.analytic.line',
            'view_mode': 'list,form',
            'domain': [('project_id', '=', self.id)],
            'target': 'current',
            'context': {
                'default_project_id': self.id,
            }
        }
