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
from odoo import api, models, fields, _
from odoo.exceptions import UserError
from datetime import timedelta


class CRMLead(models.Model):
    _inherit = 'crm.lead'

    sequence_code = fields.Char(string="Sequence")
    job_type = fields.Selection([
        ('one_time','One Time Job'),
        ('amc_work','AMC'),
        ('project','Project'),
        ('other','Other')
    ],
    string="Job Type",
    tracking=True
    )
    location_url = fields.Char(string="Location Url", tracking=True)
    preferable_time = fields.Datetime(string='Preferable Date & Time')
    preferable_end_time = fields.Datetime(string='Preferable End Date')
    property_id = fields.Many2one('property.property', string="Property")
    property_status = fields.Char(string="Property Status")
    property_project = fields.Char(string="Project")
    property_unit = fields.Char(string="Unit")
    property_request = fields.Char(string="Request")
    stage_type = fields.Selection(
        [('under_inspection', 'Under Inspection'),
         ('quotation_created', 'Quotation Created'),
         ('quote_confirmed', 'Quotation Confirmed'),
         ('field_service', 'Field Service'),
         ('service_completed', 'Service Completed')], string="Stage type")

    assigned_to = fields.Boolean(
        string="Assigned To",
        default=False
    )

    @api.model_create_multi
    def create(self, vals_list):
        res = super(CRMLead, self).create(vals_list)
        for rec in res:
            rec.sequence_code = self.env['ir.sequence'].next_by_code('crm.lead')
        return res


    def action_assign_inspection(self):
        inspection_project = self.env['project.project'].search(
            [('is_inspection', '=', True)])
        if not self.description:
            raise UserError(_("Please add the description"))
        if not self.partner_id:
            raise UserError(_("Please choose the customer"))
        if not self.phone:
            raise UserError(_("Please Add Customer Phone Number"))
        if not self.preferable_time:
            raise UserError(_("Please Add Customer Preferable Time"))
        if not self.preferable_end_time:
            raise UserError(_("Please Add Customer Preferable End Time"))
        inspection_manager = self.env['inspection.team.member'].search([],
                                                                       limit=1)
        if not inspection_manager:
            raise UserError(_("Please Configure The Inspection Team"))
        sequence = self.env['ir.sequence'].next_by_code('project.task.inspection')

        if inspection_project:
            sequence_insp_task = self.env['ir.sequence'].next_by_code(
                'project.task.inspection')
            project_task = self.env['project.task'].sudo().create({
                'name': sequence_insp_task + ' - ' + self.name,
                'sequence_code': sequence_insp_task,
                'user_ids': [(6, 0, [inspection_manager.team_manager_id.id])],
                'partner_id': self.partner_id.id,
                'partner_phone': self.phone,
                'street1_f': self.street,
                'street2_f': self.street2,
                'city_f': self.city,
                'country_f_id': self.country_id.id,
                'state__f_id': self.state_id.id,
                'zip_f': self.zip,
                'location_url': self.location_url,
                'preferable_time': self.preferable_time,
                'preferable_end_time': self.preferable_end_time,
                'date_deadline': self.preferable_end_time + timedelta(hours=1),
                'description': self.description,
                'project_id': inspection_project.id,
                '_is_inspection_task': True,
                'crm_lead_id': self.id,
                'property_status': self.property_status,
                'property_project': self.property_project,
                'property_id': self.property_id.id,
                'property_unit': self.property_unit,
                'property_request': self.property_request,
            })
        else:
            inspection_project = self.env['project.project'].sudo().create({
                'name': 'Inspection Project',
                'user_id': inspection_manager.team_manager_id.id,
                'is_inspection': True,
                'allow_timesheets': True,
            })
            sequence_insp_task = self.env['ir.sequence'].next_by_code(
                'project.task.inspection')
            project_task = self.env['project.task'].sudo().create({
                'name': sequence_insp_task + ' - ' + self.name,
                'sequence_code': sequence_insp_task,
                'user_ids': [(6, 0, [inspection_manager.team_manager_id.id])],
                'partner_id': self.partner_id.id,
                'partner_phone': self.phone,
                'street1_f': self.street,
                'street2_f': self.street2,
                'city_f': self.city,
                'country_f_id': self.country_id.id,
                'state__f_id': self.state_id.id,
                'zip_f': self.zip,
                'location_url': self.location_url,
                'preferable_time': self.preferable_time,
                'preferable_end_time': self.preferable_end_time,
                'date_deadline': self.preferable_end_time + timedelta(hours=1),
                'description': self.description,
                'project_id': inspection_project.id,
                '_is_inspection_task': True,
                'crm_lead_id': self.id,
                'property_status': self.property_status,
                'property_project': self.property_project,
                'property_id': self.property_id.id,
                'property_unit': self.property_unit,
                'property_request': self.property_request,
            })
        self.assigned_to = True
        self.stage_type = 'under_inspection'



    def action_open_related_inspection_task(self):
        if self.assigned_to:
            task_id = self.env['project.task'].search([('crm_lead_id', '=', self.id)])
            return {
                'name': 'Inspection Task',
                'view_type': 'list',
                'view_mode': 'list,form',
                'res_model': 'project.task',
                'domain': [('id', 'in', task_id.ids)],
                'type': 'ir.actions.act_window',
            }

    def _prepare_opportunity_quotation_context(self):
        """ Prepares the context for a new quotation (sale.order) by sharing the values of common fields """
        self.ensure_one()
        quotation_context = {
            'default_opportunity_id': self.id,
            'default_ins_crm_id': self.id,
            'default_property_status': self.property_status,
            'default_property_project': self.property_project,
            'default_property_id': self.property_id.id,
            'default_property_unit': self.property_unit,
            'default_property_request': self.property_request,
            'default_job_type': self.job_type,
            'default_partner_id': self.partner_id.id,
            'default_campaign_id': self.campaign_id.id,
            'default_medium_id': self.medium_id.id,
            'default_origin': self.name,
            'default_source_id': self.source_id.id,
            'default_company_id': self.company_id.id or self.env.company.id,
            'default_tag_ids': [(6, 0, self.tag_ids.ids)]
        }
        if self.team_id:
            quotation_context['default_team_id'] = self.team_id.id
        if self.user_id:
            quotation_context['default_user_id'] = self.user_id.id
        return quotation_context