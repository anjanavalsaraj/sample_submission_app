from odoo import models, fields, api,_



class SampleForm(models.Model):
    _name = "sample.submission.form"
    _description = "Sample submission form"
    _rec_name = 'name'
    _inherit = ['mail.thread']

    name = fields.Char(string="Name")
    sequence = fields.Char(string="Sequence", copy=False, readonly=True, default=lambda x: _('New'))
    description = fields.Text(string="Description")
    partner_id = fields.Many2one('res.partner', string="Customer")
    date = fields.Date(string="Date of Submission")
    price = fields.Float(string="Price")
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
        default=lambda self: self.env.company)
    stage = fields.Selection(string="Stages", selection=[
        ('pending', 'Pending'),
        ('doing', 'Doing'),
        ('completed_easily', 'Completed Easily')
    ], default='pending')
    discount = fields.Float(string="Discount")
    tax_id = fields.Many2one('account.tax', string="Tax")
    sample_submission_material_ids = fields.One2many('sample.submission.materials', 'sample_submission_form_id', string="Material Required")
    invoice_ids = fields.Many2many("account.move", string='Invoices', copy=False)
    invoice_count = fields.Integer(string="Invoice Count", compute="get_invoice_count")
    user_id = fields.Many2one(
        'res.users', string='Salesperson', default=lambda self: self.env.user, index=True, tracking=True)

    def action_mark_done(self):
        self.stage = 'completed_easily'

    def action_start(self):
        self.stage = 'doing'

    def get_invoice_count(self):
        for rec in self:
            rec.invoice_count = len(rec.invoice_ids)


    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('sequence') or vals['sequence'] == _('New'):
                vals['sequence'] = self.env['ir.sequence'].next_by_code('sample.submission.code') or _('New')
        return super().create(vals_list)

    def open_materials_wizard(self):
        """Wizard for adding materials required in sample submission form"""
        return {
            'name': 'Wizard',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            "view_type": "form",
            'res_model': 'materials.required',
            'target': 'new',
            'view_id': self.env.ref('anj_sample_submission.materials_required_view').id,
            'context': {'active_id': self.id},
        }

    def open_confirmation_wizard(self):
        """Wizard for confirming whether or not to create invoice"""
        action = {
            'name': _("Confirm"),
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'invoice.confirm',
            'type': 'ir.actions.act_window',
            'view_id': self.env.ref('anj_sample_submission.invoice_confirm_wizard_view').id,

            'target': 'new',
      }
        return action

    def action_get_invoices(self):
        return {
            'name': _('Invoices'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [('id', 'in', self.invoice_ids.ids)],
        }


class SampleSubmissionMaterials(models.Model):
    _name = "sample.submission.materials"

    sl_no = fields.Integer(string="Sl.no", compute="_compute_sl_number")
    product_id = fields.Many2one('product.product', string="Material")
    quantity = fields.Float(string="Quantity")
    remarks = fields.Char(string="Remarks")
    sample_submission_form_id = fields.Many2one('sample.submission.form', string="Sample Submission Form")
    invoice_line_id = fields.Many2one('account.move.line', string="Invoice Lines")

    def _compute_sl_number(self):
        for sample in self.mapped('sample_submission_form_id'):
            number = 1
            for line in sample.sample_submission_material_ids:
                line.sl_no = number
                number += 1