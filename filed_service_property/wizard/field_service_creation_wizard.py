# -*- coding: utf-8 -*-
#############################################################################

#    Alhodood Technologies.
#
#    Copyright (C) 2024-TODAY Alhodood Technologies(<https://www.alhodood.com>)
#    Author: Alhodood Technologies(<https://www.alhodood.com>)
#
#    You can modify it under the terms of the GNU Affero General Public License (AGPL v3), Version 3.
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

from odoo import models, fields,_
from odoo.exceptions import UserError
from datetime import  timedelta


class FieldServiceCreation(models.TransientModel):
    _name = 'filed.service.create.wizard'
    _description = "Field Service Creation"

    description = fields.Text('Description')
    preferable_time = fields.Datetime(string='Preferable Date Time', tracking=True)
    preferable_end_time = fields.Datetime(string='Preferable End Date', tracking=True)
    user_ids = fields.Many2many(
        'res.users',
        string="Assignees",
        domain=lambda self: [
            '|',
            ('group_ids', 'in', self.env.ref('industry_fsm.group_fsm_user').id),
            ('group_ids', 'in', self.env.ref('industry_fsm.group_fsm_manager').id),
        ]
    )

    def action_add_feedback(self):
        project_id = self.env['project.project'].search([('is_fsm', '=', True),('is_amc_created','=',False)],limit=1)
        sale_oder = self.env['sale.order'].search([('id','=', self.env.context['active_id'])])
        if not project_id:
            raise UserError("Please Configure Field Service Project")
        service_task = self.env['project.task'].sudo().create({
            'project_id': project_id.id,
            'partner_id': sale_oder.partner_id.id,
            'fsm_sale_order_id': sale_oder.id,
            'crm_lead_id': sale_oder.ins_crm_id.id,
            'quoted_amount': sale_oder.amount_total,
            'job_type': sale_oder.job_type,
            'is_fsm': True,
            'planned_date_begin': self.preferable_time,
            'date_deadline': self.preferable_end_time,
            'name': 'Field Service - ' + sale_oder.property_project + sale_oder.property_unit,
            'description': self.description,
            'user_ids': self.user_ids.ids,
            'property_status': sale_oder.property_status,
            'property_project': sale_oder.property_project,
            'property_id': sale_oder.property_id.id,
            'property_unit': sale_oder.property_unit,
            'property_request': sale_oder.property_request,
        })
        sale_oder.ins_crm_id.write({'stage_type': 'field_service'})
        sale_oder.write({'service_type': 'service_created',
                         'service_task': service_task.id,
                         'create_pr': True,
                         })


class FieldServiceJobCreation(models.TransientModel):
    _name = 'filed.service.job.create.wizard'
    _description = "Field Service Job Creation"

    description = fields.Text('Description')
    preferable_time = fields.Date(string='Start Date', tracking=True)
    preferable_end_time = fields.Date(string='End Date', tracking=True)
    user_id = fields.Many2one(
        'res.users',
        string="Manager",
        domain=lambda self: [('group_ids', 'in', self.env.ref('industry_fsm.group_fsm_manager').id)]
    )

    def action_add_feedback(self):
        sale_oder = self.env['sale.order'].search([('id','=', self.env.context['active_id'])])
        project_id = self.env['project.project'].sudo().create({
            "name": sale_oder.property_id.name +' - '+ sale_oder.property_unit,
            "partner_id": sale_oder.partner_id.id,
            "fsm_sale_order_id": sale_oder.id,
            "crm_lead_id": sale_oder.ins_crm_id.id,
            "quoted_amount": sale_oder.amount_total,
            "user_id": self.user_id.id,
            "description": self.description,
            'is_fsm':True,
            'is_amc_created':True,
            'company_id':self.env.company.id,
            'property_status': sale_oder.property_status,
            'property_project': sale_oder.property_project,
            'property_id': sale_oder.property_id.id,
            'property_unit': sale_oder.property_unit,
            'property_request': sale_oder.property_request,
            'date_start': self.preferable_time,
            'date': self.preferable_end_time,
        })
        sale_oder.project_id = project_id.id
        sale_oder.service_type = 'amc_job'
        sale_oder.create_pr = True
