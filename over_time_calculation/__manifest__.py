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
    'name': 'Over Time Management',
    'version': '19.0.0.0.0',
    'category': 'Sales/CRM',
    'summary': 'Over Time Management',
    'description': 'Over Time Management System',
    'author': 'Alhodood Technologies',
    'depends': [
        'mail', 'project', 'hr_timesheet','hr',
        'sale_project','account_analytic_parent'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/over_time.xml',
    ],
    'assets': {},
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
