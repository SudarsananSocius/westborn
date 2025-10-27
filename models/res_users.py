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


class ResPartner(models.Model):
    _inherit = 'res.partner'

    type = fields.Selection(selection_add=[('beneficiary', 'Beneficiary')])

    @api.model
    def create(self, vals):
        res = super(ResPartner, self).create(vals)
        for val in vals:
            if 'type' in vals and vals['type'] == 'beneficiary':
                print(val['type'])
                portal_id = self.env['portal.wizard'].create({})
                wizard = self.env['portal.wizard.user'].with_context(default_partner_id=res.id, default_wizard_id=portal_id,default_email=res.email).create({})
                wizard.action_grant_access()
            
                
        return res