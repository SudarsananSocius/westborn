from odoo import models, fields, api
#
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    credit_points = fields.Float(
        string="Credits", compute='_compute_credit_amount',
        help="Credit points assigned for this sale order line.")
    credit_value = fields.Float(related='product_id.credit_value', string="Credit Value", store=True, readonly=True)

    @api.depends('product_id', 'product_uom_qty', 'price_unit')
    def _compute_credit_amount(self):
        """ Compute the amounts of the SO line. """
        for line in self:
            if line.product_id and line.product_id.credit_value:
                # line.credit_points = int(line.price_unit)
                line.credit_points = float(line.price_subtotal / 20)
            else:
                line.credit_points = 0
    
    def get_line_total_credit(self):
        self.ensure_one()
        return self.credit_value

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    total_credits = fields.Float(string="Total Credits", compute='_get_total_credits', help="Total credit points of the sale order.")
    total_credits_apply = fields.Float(string="Total Credits Applied",compute='get_total_credit_apply', help="Total credit points applied for the sale order.")

    def _get_total_credits(self):
        """ Compute the total credits of the SO. """
        for record in self:
            record.ensure_one()
            total_credits = 0
            for line in record.order_line:
                total_credits += line.credit_points if line.product_id.name != 'eWallet' else 0
            record.total_credits = total_credits
            return total_credits
        return 0
    
    def get_total_credit_apply(self):
        total_credits_apply = 0
        for record in self:
            for line in record.order_line:
                total_credits_apply += line.credit_points
            record.total_credits_apply = total_credits_apply
        return 0
    
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
        credits = points / 20
        self.total_credits_apply = credits
        return credits
    
