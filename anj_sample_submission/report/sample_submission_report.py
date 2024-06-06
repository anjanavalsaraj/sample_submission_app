from odoo import api,fields,models ,_
from odoo.exceptions import ValidationError


class SampleSubmissionReportAbstract(models.AbstractModel):
    _name = 'report.anj_sample_submission.sample_submission_report_template'

    @api.model
    def _get_report_values(self, docids, data):
        data_filter = ''
        data_filter += " WHERE sm.company_id = '%s'" % (self.env.company.id)
        if data.get('start_date'):
            data_filter += " AND sm.date >= '%s'" % (data.get('start_date'))
        if data.get('end_date'):
            data_filter += " AND sm.date <= '%s'" % (data.get('end_date'))

        sql = ('''SELECT sm.date AS date,
                 rp.name AS customer_name,
                 sm.name AS name,
                 sm.price AS price
                 from sample_submission_form sm
                 left join res_partner rp on sm.partner_id = rp.id
                '''
               + data_filter + ''' GROUP BY sm.date, rp.name, sm.name, sm.price''')

        self.env.cr.execute(sql)
        sample_datas = self.env.cr.dictfetchall()
        if sample_datas:
            data = {
                'ids': self.ids,
                'model': 'report.wizard',
                'start_date': data.get('start_date'),
                'end_date': data.get('end_date'),
                'sample_datas': sample_datas

            }
            return{
                'doc_ids' :docids,
                'doc_model': 'report.wizard',
                'data':data
            }
        else:
            raise ValidationError(_('No datas found for the selected period!'))
