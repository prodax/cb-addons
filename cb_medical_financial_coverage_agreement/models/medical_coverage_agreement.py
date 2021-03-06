# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class MedicalCoverageAgreement(models.Model):
    _name = 'medical.coverage.agreement'
    _description = "Coverage Agreement"
    _inherit = ['medical.abstract', 'mail.thread', 'mail.activity.mixin']

    def _get_default_currency_id(self):
        return self.env.user.company_id.currency_id.id

    name = fields.Char(
        string='Agreement Name',
        required=True,
        translate=True,
    )
    active = fields.Boolean(
        default=True,
    )
    center_ids = fields.Many2many(
        string='Centers',
        comodel_name='res.partner',
        domain=[('is_center', '=', True)],
        required=True,
        index=True,
        help='Medical centers',
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        required=True,
        index=True,
        help='Responsible Medical Company',
    )
    coverage_template_ids = fields.Many2many(
        string='Coverage Templates',
        comodel_name='medical.coverage.template',
        relation='medical_coverage_agreement_medical_coverage_template_rel',
        column1='agreement_id',
        column2='coverage_template_id',
        help='Coverage templates related to this agreement',
        auto_join=True,
    )
    item_ids = fields.One2many(
        comodel_name='medical.coverage.agreement.item',
        inverse_name='coverage_agreement_id',
        string='Agreement items',
        ondelete='cascade',
        copy=True,
    )
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Currency',
        default=_get_default_currency_id,
        required=True,
    )
    date_from = fields.Date(
        'From',
        required=True,
        default=fields.Date.today(),
    )
    date_to = fields.Date(
        'To',
    )
    actual_date = fields.Date(
        default=fields.Date.today(),
    )
    principal_concept = fields.Selection([
        ('private', 'Private'),
        ('coverage', 'Coverage')],
        'Concept',
    )

    @api.model
    def _get_internal_identifier(self, vals):
        return self.env['ir.sequence'].next_by_code(
            'medical.coverage.agreement') or '/'

    @api.onchange('date_from', 'date_to')
    def _onchange_date_range(self):
        if self.date_from and self.date_to:
            if (
                self.actual_date >= self.date_from and
                self.actual_date <= self.date_to
            ):
                self.active = True
            else:
                self.active = False
        if self.date_from and not self.date_to:
            if self.actual_date >= self.date_from:
                self.active = True
            else:
                self.active = False

    @api.multi
    def toggle_active(self):
        res = super(MedicalCoverageAgreement, self).toggle_active()
        for record in self:
            # Only deactivating items when inactive
            if not record.active:
                record.item_ids.filtered(
                    lambda r: r.active != record.active).toggle_active()
        return res

    @api.multi
    def action_search_item(self):
        action = self.env.ref('cb_medical_financial_coverage_agreement.'
                              'medical_coverage_agreement_item_action')
        result = action.read()[0]
        result['context'] = {'default_coverage_agreement_id': self.id}
        result['domain'] = [('coverage_agreement_id', '=', self.id)]
        return result
