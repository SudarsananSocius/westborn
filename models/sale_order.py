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
                # line.credit_points = int(line.price_unit)
                line.credit_points = int(round(line.price_subtotal / 20, 2))
            else:
                line.credit_points = 0

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    total_credits = fields.Integer(string="Total Credits", compute='_get_total_credits', help="Total credit points of the sale order.")


    def _get_total_credits(self):
        """ Compute the total credits of the SO. """
        for record in self:
            record.ensure_one()
            total_credits_apply = 0
            total_credits = 0
            for line in record.order_line:
                total_credits_apply += line.credit_points
                total_credits += line.credit_points if line.product_id.name != 'eWallet' else 0
            # total_credits = sum(line.credit_points for line in record.order_line)
            record.total_credits = total_credits_apply
            return total_credits
    
    def _get_total_credit_points(self, coupon):
        """ Compute the total credit points of the user. """
        self.ensure_one()
        points = coupon.points
        if self.state not in ('sale', 'done'):
            if coupon.program_id.applies_on != 'future':
                # Points that will be given by the order upon confirming the order
                points += self.coupon_point_ids.filtered(lambda p: p.coupon_id == coupon).points
            # Points already used by rewards
            points -= sum(self.order_line.filtered(lambda l: l.coupon_id == coupon).mapped('points_cost'))
        points = coupon.currency_id.round(points)
        credits = int(round(points / 20, 2))
        return credits
