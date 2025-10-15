from odoo import models, fields, api

class ResUsers(models.Model):
    _inherit = 'res.users'

    is_portal_user = fields.Boolean(
        compute='_compute_is_portal_user',
        store=True,
        index=True,
    )

    @api.depends('group_ids')
    def _compute_is_portal_user(self):
        portal_group = self.env.ref('base.group_portal')
        for user in self:
            user.is_portal_user = portal_group in user.group_ids
