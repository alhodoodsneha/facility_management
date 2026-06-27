# -*- coding: utf-8 -*-
#############################################################################

#    Alhodood Technologies.
#
#    Copyright (C) 2026-TODAY Alhodood Technologies(<https://www.alhodood.com>)
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
import base64
from datetime import date, datetime
from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager

class ClientChangeRequestPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id
        if 'change_request_count' in counters:
            if partner:
                values['change_request_count'] = request.env['crm.lead'].sudo().search_count([
                    ('partner_id', '=', partner.id),
                ]) or 1
        return values

    @http.route(['/my/change-requests', '/my/change-requests/page/<int:page>'],
                type='http', auth='user', website=True)
    def portal_my_change_requests(self, page=1, **kw):
        partner = request.env.user.partner_id
        ChnageRequest = request.env['crm.lead'].sudo()

        domain = [('partner_id', '=', partner.id)]

        total = ChnageRequest.search_count(domain)

        pager = portal_pager(
            url='/my/change-requests',
            total=total,
            page=page,
            step=20
        )

        requests = ChnageRequest.search(
            domain,
            order='create_date desc',
            limit=20,
            offset=pager['offset']
        )

        values = {
            'requests': requests,
            'pager': pager,
            'page_name': 'my_change_requests',
            'leads': request.env['crm.lead'].sudo().search([('partner_id','=',partner.id)]),
        }
        return request.render('filed_service_property.portal_my_change_requests', values)


    @http.route('/my/change-requests/create', type='http',
                auth='user', website=True, methods=['POST'])
    def portal_create_change_request(self, **post):
        partner = request.env.user.partner_id
        change_request = request.env['crm.lead'].sudo().create({
            'name': post.get('name'),
            'property_project': post.get('property'),
            'property_unit': post.get('property_unit'),
            'description': post.get('note'),
            'property_request': post.get('note'),
            'date_deadline': post.get('deadline'),
            'partner_id': request.env.user.partner_id.id,
        })

        request.session['portal_success_message'] = (
            "Your Change Request has been created successfully."
        )

        return request.redirect('/my/change-requests')


