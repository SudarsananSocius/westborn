from odoo import models, fields, api

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    credit_points = fields.Integer(string="Credits", compute='_compute_credit_amount', help="Credit points assigned for this sale order line.")
    is_group_user = fields.Boolean(compute='_compute_is_westborn_group', string="Is Group User")

    @api.depends('product_template_id', 'product_uom_qty', 'price_unit')
    def _compute_credit_amount(self):
        """ Compute the amounts of the SO line. """
        for line in self:
            if line.product_id and line.product_id.credit_value:
                if line.name == 'eWallet':
                    # line.credit_points = int(line.price_unit)
                    line.credit_points = int(round(line.price_unit / 20, 2))
                else:
                    line.credit_points = int(line.product_id.credit_value * line.product_uom_qty)
            else:
                line.credit_points = 0
    
    @api.depends('order_id.partner_id')
    def _compute_is_westborn_group(self):
        """ Compute if the partner belongs to the 'Westborn' group. """
        westborn_group_beneficiary = self.env.ref('westborn.group_beneficiary', raise_if_not_found=False)
        westborn_group_admin = self.env.ref('westborn.group_beneficiary_admin', raise_if_not_found=False)
        westborn_group_referrer = self.env.ref('westborn.group_referrer', raise_if_not_found=False)
        for line in self:
            line.is_group_user = westborn_group_admin in self.env.user.all_group_ids if westborn_group_admin else False

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    total_credits = fields.Integer(string="Total Credits", compute='_get_total_credits', help="Total credit points of the sale order.")

    def _get_total_credits(self):
        """ Compute the total credits of the SO. """
        self.ensure_one()
        total_credits = 0
        for line in self.order_line:
            total_credits += line.credit_points
        # total_credits = sum(line.credit_points for line in self.order_line)
        self.total_credits = total_credits
        return total_credits
        