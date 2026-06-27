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
from odoo import api, models, fields, _
from odoo.exceptions import UserError
from odoo.fields import Command, Domain


class ProjectTask(models.Model):
    _inherit = 'project.task'

    sequence_code = fields.Char(
        string="Sequence",
        tracking=True
    )
    _is_inspection_task = fields.Boolean(
        string="Inspection Task",
        default=False,
        tracking=True
    )
    partner_phone = fields.Char(
        string='Phone',
        tracking=True
    )
    street1_f = fields.Char(
        string='street',
        tracking=True
    )
    street2_f = fields.Char(
        string='street2',
        tracking=True
    )
    city_f = fields.Char(
        string="City",
        tracking=True
    )
    country_f_id = fields.Many2one(
        'res.country',
        string="Country",
        tracking=True
    )
    state__f_id = fields.Many2one(
        'res.country.state',
        string="State",
        domain="[('country_id', '=', country_f_id)]",
        tracking=True
    )
    zip_f = fields.Char(
        string="Zip",
        tracking=True
    )
    location_url = fields.Char(
        string="Location Url",
        tracking=True
    )
    preferable_time = fields.Datetime(
        string='Preferable Date Time',
        tracking=True
    )
    preferable_end_time = fields.Datetime(
        string='Preferable End Date',
        tracking=True
    )

    crm_lead_id = fields.Many2one(
        'crm.lead',
        string="Crm",
        tracking=True
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
    is_completed = fields.Boolean(
        string='Complete',
        default=False
    )

    inspection_attachment_ids = fields.One2many(
        'inspection.attachment',
        'task_id',
        string="Inspection Attachment"
    )

    estimation_line_ids = fields.One2many(
        'estimation.line',
        'task_id',
        string='Estimation Line'
    )

    estimation_total = fields.Float(
        'Estimation Total',
        compute='_compute_estimation_total'
    )

    margin = fields.Float(string='Margin')

    fsm_sale_order_id = fields.Many2one(
        'sale.order',
        string="Sale Order"
    )

    quoted_amount = fields.Float(
        string="Quoted Amount"
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

    consumable_line_ids = fields.One2many(
        "project.task.material",
        "task_id",
        string="Consumable Materials",
    )

    @api.model_create_multi
    def create(self, vals_list):
        res = super(ProjectTask, self).create(vals_list)
        for rec in res:
            if rec.is_fsm:
                rec.sequence_code = self.env['ir.sequence'].next_by_code(
                'project.task.fsm')
                rec.name = rec.sequence_code +' - '+ rec.name
        return res


    @api.depends('estimation_line_ids')
    def _compute_estimation_total(self):
        for rec in self:
            if rec.estimation_line_ids:
                rec.estimation_total = sum(
                    line.total for line in rec.estimation_line_ids)
            else:
                rec.estimation_total = 0.0

    def action_margin_update(self):
        for line in self.estimation_line_ids:
            if line.unit_price > 0:
                margin_amount = (self.margin / 100) * line.unit_price
                line.line_margin = margin_amount

    def action_completed_inspection(self):
        if not self.inspection_attachment_ids:
            raise UserError(_("Please Add Some Inspection Lines"))
        if not self.estimation_line_ids:
            raise UserError("Please Add The Estimation Line")
        product_template_id = self.env['product.template'].search(
            [('estimation_ok', '=', True)], limit=1)
        if not product_template_id:
            raise UserError("Please Configure A Estimation Product.")
        order_lines = []
        sale_order = self.env['sale.order'].sudo().create({
            'partner_id': self.partner_id.id,
            'ins_task_id': self.id,
            'ins_crm_id': self.crm_lead_id.id,
            'estimation_total': self.estimation_total,
            'user_id': self.crm_lead_id.user_id.id,
            'property_status': self.property_status,
            'property_project': self.property_project,
            'property_id': self.property_id.id,
            'property_unit': self.property_unit,
            'property_request': self.property_request,
            'opportunity_id': self.crm_lead_id.id,
            'campaign_id': self.crm_lead_id.campaign_id.id,
            'medium_id': self.crm_lead_id.medium_id.id,
            'job_type': self.crm_lead_id.job_type,
            'origin': self.crm_lead_id.name,
            'source_id': self.crm_lead_id.source_id.id,
            'company_id': self.crm_lead_id.company_id.id or self.env.company.id,
            'tag_ids': [(6, 0, self.crm_lead_id.tag_ids.ids)],
            'order_line': [(0, 0, {
                'product_id': product.id,
                'product_uom_qty': 1,
                'price_unit': self.estimation_total,
            }) for product in product_template_id.product_variant_id],
            'estimation_line_ids': [(0, 0, {
                'description': line.description,
                'qty': line.qty,
                'unit_price': line.unit_price,
                'line_margin': line.line_margin,
                'task_id': line.task_id.id,
            }) for line in self.estimation_line_ids]
        })
        self.is_completed = True
        self.state = '1_done'
        self.crm_lead_id.stage_type = 'quotation_created'


    def action_create_new_quotation(self):
        sale_order = self.env['sale.order'].sudo().create({
            'is_other_ot_task': True,
            'other_one_time_task': self.id,
            'other_one_time_prj': self.project_id.id,
            'partner_id': self.project_id.partner_id.id,
            'user_id': self.project_id.crm_lead_id.user_id.id if self.project_id.crm_lead_id else None,
            'property_status': self.property_status,
            'property_project': self.property_project,
            'property_id': self.property_id.id if self.property_id else None,
            'property_unit': self.property_unit,
            'property_request': self.property_request,
            'opportunity_id': self.project_id.crm_lead_id.id if self.project_id.crm_lead_id else None,
            'campaign_id': self.project_id.crm_lead_id.campaign_id.id if self.project_id.crm_lead_id else None,
            'medium_id': self.project_id.crm_lead_id.medium_id.id if self.project_id.crm_lead_id else None,
            'job_type':'one_time',
            'origin': self.project_id.crm_lead_id.name if self.project_id.crm_lead_id else None,
            'source_id': self.project_id.crm_lead_id.source_id.id if self.project_id.crm_lead_id else None,
            'company_id': self.project_id.crm_lead_id.company_id.id or self.env.company.id,
            'tag_ids': [(6, 0, self.project_id.crm_lead_id.tag_ids.ids)] if self.project_id.crm_lead_id else None,
        })


    def action_fsm_validate(self, stop_running_timers=False):
        """ Moves Task to done state.
            If allow billable on task, timesheet product set on project and user has privileges :
            Create SO confirmed with time and material.
        """
        Timer = self.env['timer.timer']
        running_timers = Timer.search([('parent_res_model', '=', 'project.task'), ('parent_res_id', 'in', self.ids)])
        if running_timers:
            if stop_running_timers:
                self._stop_all_timers_and_update_timesheets(running_timers)
            else:
                wizard = self.env['project.task.stop.timers.wizard'].create({
                    'line_ids': [Command.create({'task_id': task.id}) for task in self],
                })
                return {
                    'name': _('Do you want to stop the running timers?'),
                    'type': 'ir.actions.act_window',
                    'view_mode': 'form',
                    'view_id': self.env.ref('industry_fsm.view_task_stop_timer_wizard_form').id,
                    'target': 'new',
                    'res_model': 'project.task.stop.timers.wizard',
                    'res_id': wizard.id,
                }

        self.write({'fsm_done': True, 'state': '1_done'})
        if self.job_type == 'one_time':
            self.fsm_sale_order_id.service_type = 'service_done'
            self.crm_lead_id.stage_type = 'service_completed'
        if self.consumable_line_ids:
            if not self.project_id.partner_id:
                raise UserError(_("Project customer not found."))
            warehouse = self.project_id.warehouse_id
            if not warehouse:
                raise UserError(_("Warehouse not configured."))
            picking_type = warehouse.out_type_id
            move_ids = []
            for line in self.consumable_line_ids:
                move_ids.append((0, 0, {
                    'product_id':line.product_id.id,
                    'product_uom_qty': line.quantity,
                    'product_uom': line.uom_id.id,
                }))
            picking = self.env["stock.picking"].create({
                "partner_id": self.project_id.partner_id.id,
                "picking_type_id": picking_type.id,
                "origin": self.name,
                "project_id": self.project_id.id,
                "fsm_project_task_id": self.id,
                'move_ids':move_ids
            })
            picking.action_confirm()

    def action_view_other_quotation(self):
        return {
            'name': 'Sales Order',
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'list,form',
            'domain': [('other_one_time_task', '=', self.id),('is_other_ot_task','=',True)],
            'target': 'current',
            'context': {

            }
        }

    def action_view_picking(self):
        return {
            'name': 'Consumed Items',
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'view_mode': 'list,form',
            'domain': [('fsm_project_task_id', '=', self.id)],
            'target': 'current',
            'context': {

            }
        }


class InspectionAttachment(models.Model):
    _name = 'inspection.attachment'

    description = fields.Text(
        string="Title"
    )
    images = fields.Binary(
        string="Images"
    )
    task_id = fields.Many2one(
        'project.task',
        string='Task'
    )
    is_completed = fields.Boolean(
        string='Complete',
        default=False,
        related='task_id.is_completed'
    )

    def unlink(self):
        if self.is_completed:
            raise UserError(
                _("You do not have the access to delete records !!"))
        else:
            return super(InspectionAttachment, self).unlink()


class EstimationLine(models.Model):
    _name = 'estimation.line'

    description = fields.Text(string='Description')
    qty = fields.Float(string='Quantity')
    unit_price = fields.Float(string='Unit Price')
    total = fields.Float('SubTotal', compute='_compute_total')
    line_margin = fields.Float(string='Margin')
    task_id = fields.Many2one('project.task', string='Task')

    @api.depends('qty', 'unit_price', 'line_margin')
    def _compute_total(self):
        for rec in self:
            if rec.qty and rec.unit_price:
                rec.total = rec.qty * (rec.unit_price + rec.line_margin)
            else:
                rec.total = 0.0


class ProjectTaskMaterial(models.Model):
    _name = "project.task.material"
    _description = "Task Consumable Material"

    task_id = fields.Many2one(
        "project.task",
        required=True,
        string="Task"
    )

    product_id = fields.Many2one(
        "product.product",
        required=True,
        domain="[('type','=','consu'),('is_storable','=',True)]",
        string="Product"
    )

    quantity = fields.Float(
        default=1,
        string="Quantity"
    )

    uom_id = fields.Many2one(
        "uom.uom",
        related="product_id.uom_id",
        string="Uom"
    )

    project_id = fields.Many2one(
        'project.project',
        related='task_id.project_id',
        string="Project"
    )