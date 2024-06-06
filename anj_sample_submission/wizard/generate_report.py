from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ReportWizard(models.TransientModel):
    _name = "report.wizard"

    start_date = fields.Date('Start Date', default=lambda self: fields.Datetime.today())
    end_date = fields.Date('End Date', default=lambda self: fields.Datetime.today())

    def get_report_pdf(self):
        data = {
            'ids': self.ids,
            'model': 'report.wizard',
            'start_date': self.start_date,
            'end_date': self.end_date,

        }
        return self.env.ref('anj_sample_submission.sample_submission_report_pdf').report_action([], data=data)

    def get_report_xlsx(self):
        data = {
            'start_date': self.start_date,
            'end_date': self.end_date,
            'wiz_id': self.id
        }
        return self.env.ref('anj_sample_submission.sample_submission_report_xlsx').report_action(self, data=data)

    @api.onchange('start_date', 'end_date')
    def onchange_date(self):
        if self.start_date > self.end_date:
            raise ValidationError(_('Start date should not exceed end date.'))

