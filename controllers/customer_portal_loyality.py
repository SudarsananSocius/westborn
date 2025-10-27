# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.http import request, route
from odoo.tools.misc import format_amount

from odoo.addons.loyalty.controllers import portal as loyalty_portal


class CustomerPortalLoyalty(loyalty_portal.CustomerPortalLoyalty):

    @route()
    def portal_get_card_history_values(self, card_id):
        """Add published trigger products for the loyalty program."""
        res = super().portal_get_card_history_values(card_id)
        card_sudo = request.env['loyalty.card'].sudo().search([
            ('id', '=', int(card_id)),
            ('partner_id', '=', request.env.user.partner_id.id)
        ])

        if not card_sudo:
            return res
        if self.env.user.has_group('westborn.group_beneficiary_admin'):
            res['card']['group_admin'] = True
        else:
            res['card']['group_admin'] = False
        res['card']['available_credits'] = card_sudo.credit_points

        
        return res
