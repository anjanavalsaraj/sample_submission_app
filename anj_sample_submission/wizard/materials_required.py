from odoo import models, fields, api,_


class MaterialsRequired(models.TransientModel):
    _name = "materials.required"

    product_id = fields.Many2one('product.product', string="Product")
    quantity = fields.Float(string="Quantity")
    remarks = fields.Text(string="Remarks")

    def create_required_material_lines(self):
        sample_form = self.env['sample.submission.form'].browse(self.env.context.get('active_ids', []))
        sample_form.sample_submission_material_ids = [(0, 0, {
                'product_id': self.product_id.id,
                'quantity': self.quantity,
                'remarks': self.remarks
            })]
