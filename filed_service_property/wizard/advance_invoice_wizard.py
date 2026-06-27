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
from odoo import fields, models, api,_
from odoo.exceptions import UserError

class CreateInvoiceAdvance(models.TransientModel):
    _name = 'advance.invoice.wizard'
    _description = "Advance Invoice"

    project_id = fields.Many2one('project.project', string="Project")
    balance_per = fields.Float(string="Balance Percentage")
    percentage = fields.Float(
        string="Percentage",
        default=0.0
    )

    def action_adv_create_adv(self):
        if self.percentage > self.project_id.balance_per:
            raise UserError(
                _("Please Choose Percentage Less than or Equal to Balance Percentage !!"))
        project_id = self.project_id
        invoice_lines = []
        analytic_id = project_id.account_id.id
        total_inv_pr = self.percentage
        invoice_price = (self.project_id.quoted_amount * total_inv_pr)/100
        invoice_lines.append((0, 0, {
            'name':"Progressive Invoice - "+self.project_id.name,
            'quantity': 1,
            'price_unit': invoice_price,
            'analytic_distribution': {
                analytic_id: 100.0,
            },
        }))
        account_move = self.env['account.move'].create({
            'partner_id': project_id.partner_id.id,
            'move_type': 'out_invoice',
            'is_prj_inv':True,
            'inv_per':total_inv_pr,
            'invoice_line_ids': invoice_lines,
            'project_id': project_id.id,
            'sale_inv_id': project_id.sale_order_id.id if project_id.sale_order_id else None,
            'user_id': project_id.sale_order_id.user_id.id if project_id.sale_order_id else None,
        })
