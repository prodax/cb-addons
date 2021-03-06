# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models


class PlanDefinition(models.Model):
    _inherit = 'workflow.plan.definition'

    def get_request_group_vals(self, vals):
        res = super().get_request_group_vals(vals)
        if not res.get('is_billable', False):
            return res
        if vals.get('coverage_agreement_item_id', False):
            cai = self.env['medical.coverage.agreement.item'].browse(
                res['coverage_agreement_item_id']
            )
            res['authorization_method_id'] = cai.authorization_method_id.id
            if cai.authorization_method_id.always_authorized:
                res['authorization_status'] = 'authorized'
            else:
                res['authorization_status'] = 'pending'
        return res
