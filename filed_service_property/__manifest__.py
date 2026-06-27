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

{
    'name': 'Facility Management',
    'version': '19.0.0.0.1',
    'category': 'Sales/CRM',
    'summary': 'Facility Management',
    'description': 'Facility Management System',
    'author': 'Alhodood Technologies',
    'depends': [
        'crm', 'mail', 'project', 'hr_timesheet', 'stock',
        'sale_management', 'purchase', 'hr', 'account','sale_crm',
        'sale_project','account_analytic_parent','project_purchase','industry_fsm','industry_fsm_sale'
    ],
    'data': [
        'data/ir_sequence.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/inspection_team.xml',
        'views/product_product.xml',
        'views/crm_lead.xml',
        'views/property_property.xml',
        'views/project_project.xml',
        'views/ir_action_report.xml',
        'views/inspectionl_report_template.xml',
        'views/project_task.xml',
        'views/sale_order.xml',
        'views/account_move.xml',
        'views/portal_home_inherit.xml',
        'views/portal_my_change_request.xml',
        'wizard/field_service_creation_wizard.xml',
        'wizard/advance_invoice_wizard.xml',
    ],
    'assets': {},
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
