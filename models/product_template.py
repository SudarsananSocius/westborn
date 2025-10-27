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
        for product in self:
            # Example conversion: 1 credit = $20
            product.credit_value = round(product.list_price / 20, 2)