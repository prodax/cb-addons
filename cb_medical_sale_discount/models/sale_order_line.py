from odoo import models, fields


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    medical_sale_discount_id = fields.Many2one(
        'medical.sale.discount',
        readonly=True,
    )
