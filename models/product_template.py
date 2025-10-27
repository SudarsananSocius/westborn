from odoo import models, fields, api
from odoo.http import route

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    credit_value = fields.Float(
        string="Credit Value",
        compute="_compute_credit_value",
        store=False
    )

    @api.depends('list_price')
    def _compute_credit_value(self):
        """ Compute the credit value based on the product's list price. """
        credit_val = self.search([('name', '=', 'Top-up eWallet')], limit=1)
        if credit_val:
            list_price = credit_val.list_price
        else:
            list_price = 20
        for product in self:
            product.credit_value = round(product.list_price / list_price, 2)