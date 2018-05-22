# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError, ValidationError


class TestMedicalCareplanSale(TransactionCase):
    def setUp(self):
        super(TestMedicalCareplanSale, self).setUp()
        self.payor = self.env['res.partner'].create({
            'name': 'Payor',
            'is_payor': True,
            'is_medical': True,
        })
        self.sub_payor = self.env['res.partner'].create({
            'name': 'Sub Payor',
            'is_sub_payor': True,
            'is_medical': True,
            'payor_id': self.payor.id,
        })
        self.coverage_template = self.env['medical.coverage.template'].create({
            'payor_id': self.payor.id,
            'name': 'Coverage',
        })
        self.company = self.browse_ref('base.main_company')
        self.center = self.env['res.partner'].create({
            'name': 'Center',
            'is_medical': True,
            'is_center': True,
            'stock_location_id': self.browse_ref('stock.warehouse0').id,
            'stock_picking_type_id': self.env['stock.picking.type'].search(
                [], limit=1).id
        })
        self.location = self.env['res.partner'].create({
            'name': 'Location',
            'is_medical': True,
            'is_location': True,
            'center_id': self.center.id,
            'stock_location_id': self.browse_ref('stock.warehouse0').id,
            'stock_picking_type_id': self.env['stock.picking.type'].search(
                [], limit=1).id
        })
        self.document_type = self.env['medical.document.type'].create({
            'name': 'CI',
            'document_type': 'action',
            'report_action_id': self.browse_ref(
                'medical_document.action_report_document_report_base').id,
            'text': '<p>${object.patient_id.name}</p>'
        })
        self.label_zpl2 = self.env['printing.label.zpl2'].create({
            'name': 'Label',
            'model_id': self.browse_ref(
                'medical_document.model_medical_document_reference').id,
            'component_ids': [(0, 0, {
                'name': 'text',
                'component_type': 'text',
                'data': 'object.encounter_id.internal_identifier',
                'origin_x': 10,
                'origin_y': 10,
                'height': 10,
                'width': 10,
                'font': '0',
                'orientation': 'N',

            })]
        })
        self.document_type.draft2current()
        self.document_type_label = self.env['medical.document.type'].create({
            'name': 'Label for scan',
            'document_type': 'zpl2',
            'label_zpl2_id': self.label_zpl2.id,
        })
        self.document_type_label.draft2current()
        self.agreement = self.env['medical.coverage.agreement'].create({
            'name': 'Agreement',
            'center_ids': [(4, self.center.id)],
            'coverage_template_ids': [(4, self.coverage_template.id)],
            'company_id': self.company.id,
            'invoice_group_method_id': self.browse_ref(
                'cb_medical_sale_invoice_group_method.by_preinvoicing').id,
            'authorization_method_id': self.browse_ref(
                'cb_medical_financial_coverage_request.without').id,
            'authorization_format_id': self.browse_ref(
                'cb_medical_financial_coverage_request.format_anything').id,
        })
        self.patient_01 = self.create_patient('Patient 01')
        self.coverage_01 = self.env['medical.coverage'].create({
            'patient_id': self.patient_01.id,
            'coverage_template_id': self.coverage_template.id,
        })
        self.product_01 = self.create_product('Medical resonance')
        self.product_02 = self.create_product('Report')
        self.product_03 = self.env['product.product'].create({
            'type': 'consu',
            'name': 'Clinical material',
            'is_medication': True,
            'lst_price': 10.0,
        })
        self.product_03.qty_available = 50.0
        self.product_04 = self.create_product('Medical visit')
        self.type = self.browse_ref('medical_workflow.medical_workflow')
        self.type.model_ids = [(4, self.browse_ref(
            'medical_medication_request.model_medical_medication_request').id)]
        self.plan_definition = self.env['workflow.plan.definition'].create({
            'name': 'Plan',
            'type_id': self.type.id,
            'is_billable': True,
        })
        self.plan_definition2 = self.env['workflow.plan.definition'].create({
            'name': 'Plan2',
            'type_id': self.type.id,
            'is_billable': True,
            'is_breakdown': False,
            'third_party_bill': True,
        })
        self.activity = self.env['workflow.activity.definition'].create({
            'name': 'Activity',
            'service_id': self.product_02.id,
            'model_id': self.browse_ref('medical_clinical_procedure.'
                                        'model_medical_procedure_request').id,
            'type_id': self.type.id,
        })
        self.activity2 = self.env['workflow.activity.definition'].create({
            'name': 'Activity2',
            'service_id': self.product_03.id,
            'model_id': self.browse_ref('medical_medication_request.'
                                        'model_medical_medication_request').id,
            'type_id': self.type.id,
        })
        self.activity3 = self.env['workflow.activity.definition'].create({
            'name': 'Activity3',
            'model_id': self.browse_ref(
                'medical_document.model_medical_document_reference').id,
            'document_type_id': self.document_type.id,
            'type_id': self.type.id,
        })
        self.activity4 = self.env['workflow.activity.definition'].create({
            'name': 'Activity4',
            'model_id': self.browse_ref(
                'medical_document.model_medical_document_reference').id,
            'document_type_id': self.document_type_label.id,
            'type_id': self.type.id,
        })
        self.env['workflow.plan.definition.action'].create({
            'activity_definition_id': self.activity.id,
            'direct_plan_definition_id': self.plan_definition2.id,
            'is_billable': False,
            'name': 'Action',
        })
        self.action = self.env['workflow.plan.definition.action'].create({
            'activity_definition_id': self.activity.id,
            'direct_plan_definition_id': self.plan_definition.id,
            'is_billable': True,
            'name': 'Action',
        })
        self.action2 = self.env['workflow.plan.definition.action'].create({
            'activity_definition_id': self.activity2.id,
            'direct_plan_definition_id': self.plan_definition.id,
            'is_billable': True,
            'name': 'Action2',
        })
        self.action3 = self.env['workflow.plan.definition.action'].create({
            'activity_definition_id': self.activity3.id,
            'direct_plan_definition_id': self.plan_definition.id,
            'is_billable': False,
            'name': 'Action3',
        })
        self.action4 = self.env['workflow.plan.definition.action'].create({
            'activity_definition_id': self.activity4.id,
            'direct_plan_definition_id': self.plan_definition.id,
            'is_billable': False,
            'name': 'Action4',
        })
        self.agreement_line = self.env[
            'medical.coverage.agreement.item'
        ].create({
            'product_id': self.product_01.id,
            'coverage_agreement_id': self.agreement.id,
            'plan_definition_id': self.plan_definition.id,
            'total_price': 100,
            'coverage_percentage': 0.5,
            'authorization_method_id': self.browse_ref(
                'cb_medical_financial_coverage_request.without').id,
            'authorization_format_id': self.browse_ref(
                'cb_medical_financial_coverage_request.format_anything').id,
        })
        self.agreement_line2 = self.env[
            'medical.coverage.agreement.item'
        ].create({
            'product_id': self.product_03.id,
            'coverage_agreement_id': self.agreement.id,
            'total_price': 0.0,
            'coverage_percentage': 100.0,
            'authorization_method_id': self.browse_ref(
                'cb_medical_financial_coverage_request.without').id,
            'authorization_format_id': self.browse_ref(
                'cb_medical_financial_coverage_request.format_anything').id,
        })
        self.agreement_line3 = self.env[
            'medical.coverage.agreement.item'
        ].create({
            'product_id': self.product_04.id,
            'coverage_agreement_id': self.agreement.id,
            'plan_definition_id': self.plan_definition2.id,
            'total_price': 100.0,
            'coverage_percentage': 0.0,
            'authorization_method_id': self.browse_ref(
                'cb_medical_financial_coverage_request.without').id,
            'authorization_format_id': self.browse_ref(
                'cb_medical_financial_coverage_request.format_anything').id,
        })
        self.practitioner_01 = self.create_practitioner('Practitioner 01')
        self.practitioner_02 = self.create_practitioner('Practitioner 02')
        self.product_01.medical_commission = True
        self.action.fixed_fee = 1
        self.pos_config = self.env['pos.config'].create({'name': 'PoS config'})
        self.pos_config.open_session_cb()
        self.session = self.pos_config.current_session_id
        self.session.action_pos_session_open()
        param_obj = self.env['ir.config_parameter'].sudo()
        param = param_obj.get_param('sale.default_deposit_product_id', False)
        if not param:
            param_obj.set_param(
                'sale.default_deposit_product_id',
                self.create_product('Down payment').id
            )

    def create_patient(self, name):
        return self.env['medical.patient'].create({
            'name': name
        })

    def create_product(self, name):
        return self.env['product.product'].create({
            'type': 'service',
            'name': name,
        })

    def create_careplan_and_group(self, agreement_line):
        encounter = self.env['medical.encounter'].create({
            'patient_id': self.patient_01.id,
            'center_id': self.center.id,
        })
        careplan_wizard = self.env[
            'medical.encounter.add.careplan'
        ].with_context(default_encounter_id=encounter.id).new({
            'coverage_id': self.coverage_01.id
        })
        careplan_wizard.onchange_coverage()
        careplan_wizard.onchange_coverage_template()
        careplan_wizard.onchange_payor()
        careplan_wizard = careplan_wizard.create(
            careplan_wizard._convert_to_write(careplan_wizard._cache))
        self.assertEqual(encounter, careplan_wizard.encounter_id)
        self.assertEqual(encounter.center_id, careplan_wizard.center_id)
        careplan_wizard.run()
        careplan = encounter.careplan_ids
        self.assertEqual(careplan.center_id, encounter.center_id)
        wizard = self.env['medical.careplan.add.plan.definition'].create({
            'careplan_id': careplan.id,
            'agreement_line_id': agreement_line.id,
        })
        self.action.is_billable = False
        wizard.run()
        group = self.env['medical.request.group'].search([
            ('careplan_id', '=', careplan.id)])
        group.ensure_one()
        self.assertEqual(group.center_id, encounter.center_id)
        return encounter, careplan, group

    def create_practitioner(self, name):
        return self.env['res.partner'].create({
            'name': name,
            'is_practitioner': True,
            'agent': True,
            'commission': self.browse_ref(
                'cb_medical_commission.commission_01').id,
        })

    def test_careplan_sale(self):
        encounter = self.env['medical.encounter'].create({
            'patient_id': self.patient_01.id,
            'center_id': self.center.id,
        })
        encounter_02 = self.env['medical.encounter'].create({
            'patient_id': self.patient_01.id,
            'center_id': self.center.id,
        })
        careplan = self.env['medical.careplan'].new({
            'patient_id': self.patient_01.id,
            'encounter_id': encounter.id,
            'coverage_id': self.coverage_01.id,
            'sub_payor_id': self.sub_payor.id,
        })
        careplan._onchange_encounter()
        careplan = careplan.create(careplan._convert_to_write(careplan._cache))
        self.assertEqual(careplan.center_id, encounter.center_id)
        self.env['wizard.medical.encounter.add.amount'].create({
            'encounter_id': encounter.id,
            'amount': 10,
            'pos_session_id': self.session.id,
            'journal_id': self.session.journal_ids[0].id,
        }).run()
        wizard = self.env['medical.careplan.add.plan.definition'].create({
            'careplan_id': careplan.id,
            'agreement_line_id': self.agreement_line.id,
        })
        with self.assertRaises(ValidationError):
            wizard.run()
        self.action.is_billable = False
        wizard.run()

        self.assertTrue(self.session.action_view_sale_orders()['res_id'])
        groups = self.env['medical.request.group'].search([
            ('careplan_id', '=', careplan.id)])
        self.assertTrue(groups)
        medication_requests = self.env['medical.medication.request'].search([
            ('careplan_id', '=', careplan.id)
        ])
        self.assertTrue(medication_requests.filtered(lambda r: r.is_billable))
        self.assertTrue(medication_requests.filtered(
            lambda r: r.is_sellable_insurance or r.is_sellable_private))
        for request in medication_requests:
            self.assertEqual(request.center_id, encounter.center_id)
            request.qty = 2
            request.draft2active()
            values = request.action_view_medication_administration()['context']
            admin = self.env[
                'medical.medication.administration'].with_context(
                values).create({})
            admin.location_id = self.location.id
            admin.preparation2in_progress()
            admin.in_progress2completed()
            stock_move = self.env['stock.picking'].search([
                ('medication_administration_id', '=', admin.id)
            ]).move_lines.move_line_ids
            self.assertEqual(stock_move.qty_done, 2.0)
        self.env['wizard.medical.encounter.close'].create({
            'encounter_id': encounter.id,
            'pos_session_id': self.session.id,
        }).run()
        self.assertTrue(encounter.sale_order_ids)
        self.assertGreater(self.session.encounter_count, 0)
        self.assertGreater(self.session.sale_order_count, 0)
        self.assertEqual(self.session.action_view_encounters()['res_id'],
                         encounter.id)
        self.session.action_pos_session_closing_control()
        self.assertTrue(self.session.invoice_ids)
        self.assertTrue(self.session.down_payment_ids)
        self.assertEqual(self.session.validation_status, 'in_progress')
        procedure_requests = self.env['medical.procedure.request'].search([
            ('careplan_id', '=', careplan.id)
        ])
        self.assertGreater(len(procedure_requests), 0)
        medication_requests = self.env['medical.medication.request'].search([
            ('careplan_id', '=', careplan.id)
        ])
        self.assertGreater(len(medication_requests), 0)
        for sale_order in encounter.sale_order_ids:
            sale_order.recompute_lines_agents()
            self.assertEqual(sale_order.commission_total, 0)
            medicaments = self.env['sale.order.line'].search([
                ('order_id', '=', sale_order.id),
                ('product_id', '=', self.product_03.id),
            ])
            for medicament in medicaments:
                medicament_price = medicament.price_unit
                self.assertEqual(medicament_price, 20.0)
        procedure_requests = self.env['medical.procedure.request'].search([
            ('careplan_id', '=', careplan.id)
        ])
        self.assertGreater(len(procedure_requests), 0)
        for request in procedure_requests:
            self.assertEqual(request.center_id, encounter.center_id)
            procedure = request.generate_event()
            procedure.performer_id = self.practitioner_01
            procedure.commission_agent_id = self.practitioner_01
            procedure.performer_id = self.practitioner_02
            procedure._onchange_performer_id()
            self.assertEqual(
                procedure.commission_agent_id, self.practitioner_02)
        encounter.recompute_commissions()
        self.assertTrue(encounter.sale_order_ids)
        for sale_order in encounter.sale_order_ids.filtered(
            lambda r: not r.is_down_payment
        ):
            sale_order.recompute_lines_agents()
            self.assertGreater(sale_order.commission_total, 0)
        preinvoice_obj = self.env['sale.preinvoice.group']
        self.assertFalse(preinvoice_obj.search([
            ('agreement_id', '=', self.agreement.id)]))
        self.env['wizard.sale.preinvoice.group'].create({
            'company_ids': [(6, 0, self.company.ids)],
            'payor_ids': [(6, 0, self.payor.ids)]
        }).run()
        self.assertFalse(preinvoice_obj.search([
            ('agreement_id', '=', self.agreement.id)]))
        self.assertTrue(encounter.sale_order_ids)
        for sale_order in encounter.sale_order_ids:
            sale_order.action_confirm()
            self.assertIn(sale_order.state, ['done', 'sale'])
        self.assertTrue(encounter.sale_order_ids.filtered(
            lambda r:
            r.invoice_status == 'to preinvoice' and
            r.invoice_group_method_id == self.browse_ref(
                'cb_medical_sale_invoice_group_method.by_preinvoicing')
        ))
        self.env['wizard.sale.preinvoice.group'].create({
            'company_ids': [(6, 0, self.company.ids)],
            'payor_ids': [(6, 0, self.payor.ids)]
        }).run()
        preinvoices = preinvoice_obj.search([
            ('agreement_id', '=', self.agreement.id),
            ('state', '=', 'draft')
        ])
        self.assertTrue(preinvoices)
        # Test cancellation of preinvoices
        for preinvoice in preinvoices:
            self.assertFalse(preinvoice.validated_line_ids)
            preinvoice.cancel()
            self.assertFalse(preinvoice.line_ids)
        preinvoices = preinvoice_obj.search([
            ('agreement_id', '=', self.agreement.id),
            ('state', '=', 'draft')
        ])
        self.assertFalse(preinvoices)
        self.env['wizard.sale.preinvoice.group'].create({
            'company_ids': [(6, 0, self.company.ids)],
            'payor_ids': [(6, 0, self.payor.ids)]
        }).run()
        preinvoices = preinvoice_obj.search([
            ('agreement_id', '=', self.agreement.id),
            ('state', '=', 'draft')
        ])
        self.assertTrue(preinvoices)
        # Test unlink of not validated order_lines
        for preinvoice in preinvoices:
            self.assertTrue(preinvoice.non_validated_line_ids)
            self.assertFalse(preinvoice.validated_line_ids)
            preinvoice.start()
            preinvoice.close_sorting()
            self.assertTrue(preinvoice.non_validated_line_ids)
            preinvoice.close()
            self.assertFalse(preinvoice.non_validated_line_ids)
        preinvoices = preinvoice_obj.search([
            ('agreement_id', '=', self.agreement.id),
            ('state', '=', 'draft')
        ])
        self.assertFalse(preinvoices)
        self.env['wizard.sale.preinvoice.group'].create({
            'company_ids': [(6, 0, self.company.ids)],
            'payor_ids': [(6, 0, self.payor.ids)]
        }).run()
        preinvoices = preinvoice_obj.search([
            ('agreement_id', '=', self.agreement.id),
            ('state', '=', 'draft')
        ])
        self.assertTrue(preinvoices)
        invoice_obj = self.env['account.invoice']
        self.assertFalse(invoice_obj.search([
            ('partner_id', '=', self.payor.id)
        ]))
        # Test barcodes
        for preinvoice in preinvoices:
            self.assertFalse(preinvoice.validated_line_ids)
            preinvoice.start()
            barcode = self.env['wizard.sale.preinvoice.group.barcode'].create({
                'preinvoice_group_id': preinvoice.id,
            })
            barcode.on_barcode_scanned(encounter.internal_identifier)
            self.assertEqual(barcode.status_state, 0)
            barcode.on_barcode_scanned('No Barcode')
            self.assertEqual(barcode.status_state, 1)
            barcode.on_barcode_scanned(encounter_02.internal_identifier)
            self.assertEqual(barcode.status_state, 1)
            preinvoice.close_sorting()
            preinvoice.close()
            self.assertTrue(preinvoice.invoice_id)
        invoices = invoice_obj.search([
            ('partner_id', 'in', [self.payor.id, self.sub_payor.id])
        ])
        self.assertTrue(invoices)
        # Test invoice unlink
        for invoice in invoices:
            self.assertEqual(invoice.state, 'draft')
            invoice.invoice_line_ids.unlink()
        for sale_order in encounter.sale_order_ids:
            for line in sale_order.order_line:
                self.assertFalse(line.preinvoice_group_id)
        # Test manual validation of lines on preinvoices
        preinvoices = preinvoice_obj.search([
            ('agreement_id', '=', self.agreement.id),
            ('state', '=', 'draft')
        ])
        self.assertFalse(preinvoices)
        self.env['wizard.sale.preinvoice.group'].create({
            'company_ids': [(6, 0, self.company.ids)],
            'payor_ids': [(6, 0, self.payor.ids)]
        }).run()
        preinvoices = preinvoice_obj.search([
            ('agreement_id', '=', self.agreement.id),
            ('state', '=', 'draft')
        ])
        self.assertTrue(preinvoices)
        for preinvoice in preinvoices:
            self.assertFalse(preinvoice.validated_line_ids)
            preinvoice.start()
            for line in preinvoice.line_ids:
                line.validate_line()
            preinvoice.close_sorting()
            preinvoice.close()
            self.assertTrue(preinvoice.line_ids)
            self.assertTrue(preinvoice.invoice_id)
        invoices = invoice_obj.search([
            ('partner_id', 'in', [self.payor.id, self.sub_payor.id])
        ])
        self.assertTrue(invoices)
        for invoice in invoices:
            self.assertGreater(invoice.commission_total, 0)
            invoice.recompute_lines_agents()
            self.assertGreater(invoice.commission_total, 0)

    def test_no_agreement(self):
        self.plan_definition.is_breakdown = True
        self.plan_definition.is_billable = True
        encounter, careplan, group = self.create_careplan_and_group(
            self.agreement_line
        )
        self.assertTrue(group.is_billable)
        self.assertTrue(group.is_breakdown)
        with self.assertRaises(ValidationError):
            group.breakdown()

    def test_no_breakdown(self):
        self.plan_definition.is_billable = True
        self.plan_definition.is_breakdown = False
        encounter, careplan, group = self.create_careplan_and_group(
            self.agreement_line
        )
        self.assertTrue(group.is_billable)
        self.assertFalse(group.is_breakdown)
        with self.assertRaises(ValidationError):
            group.breakdown()

    def test_third_party(self):
        self.plan_definition.is_breakdown = True
        self.plan_definition.is_billable = True
        encounter, careplan, group = self.create_careplan_and_group(
            self.agreement_line3
        )
        self.assertTrue(group.procedure_request_ids)
        for request in group.procedure_request_ids:
            request.draft2active()
            self.assertEqual(request.center_id, encounter.center_id)
            procedure = request.generate_event()
            procedure.performer_id = self.practitioner_01
            procedure.commission_agent_id = self.practitioner_01
            procedure.performer_id = self.practitioner_02
            procedure._onchange_performer_id()
            self.assertEqual(
                procedure.commission_agent_id, self.practitioner_02)
        self.practitioner_02.third_party_sequence_id = self.env[
            'ir.sequence'].create({
                'name': 'sequence'
            })
        self.assertTrue(
            group.is_sellable_insurance or group.is_sellable_private)
        self.assertTrue(
            group.third_party_bill
        )
        self.env['wizard.medical.encounter.close'].create({
            'encounter_id': encounter.id,
            'pos_session_id': self.session.id,
        }).run()
        self.assertTrue(encounter.sale_order_ids)
        sale_order = encounter.sale_order_ids
        self.assertTrue(sale_order.third_party_order)
        self.assertEqual(
            sale_order.third_party_partner_id, self.practitioner_02)

    def test_cancellation(self):
        self.plan_definition.is_breakdown = True
        self.plan_definition.is_billable = True
        encounter, careplan, group = self.create_careplan_and_group(
            self.agreement_line)
        group.cancel()
        self.assertEqual(group.state, 'cancelled')
        encounter.cancel()
        self.assertEqual(careplan.state, 'cancelled')
        with self.assertRaises(ValidationError):
            encounter.cancel()
        with self.assertRaises(ValidationError):
            careplan.cancel()

    def test_correct(self):
        self.plan_definition.is_breakdown = True
        self.plan_definition.is_billable = True
        encounter, careplan, group = self.create_careplan_and_group(
            self.agreement_line)
        self.assertTrue(careplan.document_reference_ids)
        self.assertTrue(group.document_reference_ids)
        documents = group.document_reference_ids.filtered(
            lambda r: r.document_type == 'action'
        )
        self.assertTrue(documents)
        for document in documents:
            with self.assertRaises(ValidationError):
                document.current2superseded()
            self.assertEqual(document.state, 'draft')
            self.assertTrue(document.is_editable)
            self.assertFalse(document.text)
            document.print()
            with self.assertRaises(ValidationError):
                document.draft2current()
            self.assertEqual(document.state, 'current')
            self.assertFalse(document.is_editable)
            self.assertTrue(document.text)
            self.assertEqual(document.text, '<p>%s</p>' % self.patient_01.name)
            self.patient_01.name = self.patient_01.name + ' Other name'
            document.print()
            self.assertEqual(document.state, 'current')
            self.assertNotEqual(document.text,
                                '<p>%s</p>' % self.patient_01.name)
            document.current2superseded()
            self.assertEqual(document.state, 'superseded')
            self.assertIsInstance(document.render(), bytes)
            with self.assertRaises(ValidationError):
                document.current2superseded()
            # We must verify that the document print cannot be changed
        documents = group.document_reference_ids.filtered(
            lambda r: r.document_type == 'zpl2'
        )
        self.assertTrue(documents)
        for document in documents:
            self.assertEqual(
                document.render(),
                # Label start
                '^XA\n'
                # Print width
                '^PW480\n'
                # UTF-8 encoding
                '^CI28\n'
                # Label position
                '^LH10,10\n'
                # Pased encounter
                '^FO10,10^A0N,10,10^FD%s^FS\n'
                # Recall last saved parameters
                '^JUR\n'
                # Label end
                '^XZ' % encounter.internal_identifier)
            with self.assertRaises(UserError):
                document.print()
        self.assertTrue(group.is_billable)
        self.assertTrue(group.is_breakdown)
        self.env[
            'medical.coverage.agreement.item'
        ].create({
            'product_id': self.product_02.id,
            'coverage_agreement_id': self.agreement.id,
            'total_price': 110,
            'coverage_percentage': 0.5,
            'authorization_method_id': self.browse_ref(
                'cb_medical_financial_coverage_request.without').id,
            'authorization_format_id': self.browse_ref(
                'cb_medical_financial_coverage_request.format_anything').id,
        })
        group.breakdown()
        self.assertFalse(group.is_billable)
        self.assertFalse(group.is_breakdown)
        self.env['wizard.medical.encounter.close'].create({
            'encounter_id': encounter.id,
            'pos_session_id': self.session.id,
        }).run()
        self.assertGreater(len(encounter.sale_order_ids), 0)
