from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class InvoiceConfirmation(models.TransientModel):
    _name = "invoice.confirm"

    sample_submission_form_id = fields.Many2one('sample.submission.form', string="Sample Submission Form", default=lambda self: self.env.context.get('active_id'))


    def action_create_invoice(self):
        invoice = self.env['account.move']
        journal = self.env['account.journal']

        invoice_record_list = []
        journal_id = journal.sudo().sudo().search(
            [('company_id', '=', self.sample_submission_form_id.company_id.id), ('type', '=', 'sale')],
            limit=1)

        vals1 = {
            'name': "sample submission -" + self.sample_submission_form_id.sequence,
            'quantity': 1,
            'price_unit': self.sample_submission_form_id.price,
            'discount': self.sample_submission_form_id.discount if self.sample_submission_form_id.discount else False,
            'tax_ids': [self.sample_submission_form_id.tax_id.id] if self.sample_submission_form_id.tax_id else False

        }
        invoice_record_list.append((0, 0, vals1))
        invoice_record = invoice.sudo().create({
            'move_type': 'out_invoice',
            'ref': self.sample_submission_form_id.sequence + "-" + self.sample_submission_form_id.name,
            'partner_id': self.sample_submission_form_id.partner_id.id,
            'company_id': self.sample_submission_form_id.company_id.id,
            'invoice_date': self.sample_submission_form_id.date,
            'invoice_line_ids': invoice_record_list,
            'journal_id': journal_id.id,
        })
        if invoice_record:
            self.sample_submission_form_id.invoice_ids = [invoice_record.id]

