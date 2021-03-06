# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class SafeBox(models.Model):
    _name = 'safe.box'
    _description = 'Safe box'

    name = fields.Char(required=True)
    safe_box_group_id = fields.Many2one(
        comodel_name='safe.box.group',
        string='Safe box group',
    )
    currency_id = fields.Many2one(
        'res.currency',
        related='safe_box_group_id.currency_id',
        readonly=True,
    )
    amount = fields.Monetary(
        default='0.0',
        currency_field='currency_id'
    )
    coin_ids = fields.Many2many(
        comodel_name='safe.box.coin',
        relation='safe_box_coin_rel',
        column1='safe_box_id',
        column2='coin_id',
        string='Coins/Notes'
    )
    user_ids = fields.Many2many('res.users')

    @api.multi
    def recompute_amount(self):
        for record in self:
            moves = self.env['safe.box.move.line'].search([
                ('safe_box_id', '=', record.id),
                ('state', '=', 'closed')
            ])
            record.sudo().amount = sum(moves.mapped('amount')) or 0.0
