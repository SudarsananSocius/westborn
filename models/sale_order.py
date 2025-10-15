from odoo import models, fields, api
#
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    credit_points = fields.Integer(
        string="Credits", compute='_compute_credit_amount',
        help="Credit points assigned for this sale order line.")

    @api.depends('product_id', 'product_uom_qty', 'price_unit')
    def _compute_credit_amount(self):
        """ Compute the amounts of the SO line. """
        for line in self:
            if line.product_id and line.product_id.credit_value:
                line.credit_points = int(line.product_id.credit_value * line.product_uom_qty)
            else:
                line.credit_points = 0

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    total_credits = fields.Integer(
        string="Total Credits",
        compute='_compute_total_credits',
        store=True
    )
    @api.depends('order_line.credit_points')
    def _compute_total_credits(self):
        for order in self:
            order.total_credits = sum(order.order_line.mapped('credit_points'))
