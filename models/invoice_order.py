from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    total_credits = fields.Integer(
        string="Total Credits",
        compute='_compute_total_credits',
        help="Total credit points from the related sale order"
    )

    @api.depends('invoice_line_ids.sale_line_ids.credit_points')
    def _compute_total_credits(self):
        for invoice in self:
            sale_lines = invoice.invoice_line_ids.mapped('sale_line_ids')
            invoice.total_credits = sum(sale_lines.mapped('credit_points'))


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    credit_points = fields.Integer(
        string="Credits",
        compute='_compute_credit_points'
    )

    @api.depends('sale_line_ids.credit_points')
    def _compute_credit_points(self):
        for line in self:
            line.credit_points = sum(line.sale_line_ids.mapped('credit_points'))
