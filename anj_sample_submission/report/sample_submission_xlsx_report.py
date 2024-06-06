
from odoo import models, fields, _
import datetime
from odoo.exceptions import ValidationError

LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'


def excel_style(row, col):
    """ Convert given row and column number to an Excel-style cell name. """
    result = []
    while col:
        col, rem = divmod(col - 1, 26)
        result[:0] = LETTERS[rem]
    return ''.join(result) + str(row)


class SampleSubmissionXlsxReport(models.AbstractModel):
    _name = 'report.sample.submission.report.xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, wiz):

        heading_format = workbook.add_format({'align': 'center',
                                              'valign': 'vcenter',
                                              'bold': True, 'size': 15,
                                              })

        sub_heading_format_company = workbook.add_format({'align': 'left',
                                                          'valign': 'left',
                                                          'bold': True, 'size': 12,
                                                          })
        sub_heading_format_company_new = workbook.add_format({'align': 'left',
                                                          'valign': 'left',

                                                          'bold': True, 'size': 12,
                                                          })

        col_format = workbook.add_format({'valign': 'left',
                                          'align': 'left',
                                          'bold': True,
                                          'size': 10,
                                          'font_color': '#000000'
                                          })
        data_format = workbook.add_format({'valign': 'center',
                                           'align': 'center',
                                           'size': 10,
                                           'font_color': '#000000'
                                           })
        col_format.set_text_wrap()
        worksheet = workbook.add_worksheet('Sales Report')
        worksheet.set_column('A:A', 16)
        worksheet.set_column('B:B', 20)
        worksheet.set_column('C:C', 20)
        worksheet.set_column('D:D', 16)


        row = 1
        worksheet.set_row(row, 20)
        starting_col = excel_style(row, 1)
        ending_col = excel_style(row, 5)
        from_date = datetime.datetime.strptime(str(wiz.start_date), '%Y-%m-%d').strftime('%d/%m/%Y')
        to_date = datetime.datetime.strptime(str(wiz.end_date), '%Y-%m-%d').strftime('%d/%m/%Y')

        worksheet.merge_range('%s:%s' % (starting_col, ending_col),
                              "Sample Submission Report",
                              heading_format)
        row += 1
        worksheet.write(row, 0, "Start Date", sub_heading_format_company)
        worksheet.write(row, 1, from_date, data_format)
        worksheet.write(row, 3, "End Date", sub_heading_format_company)
        worksheet.write(row, 4, to_date, data_format)
        row += 2
        worksheet.write(row, 0, "DATE", sub_heading_format_company_new)
        worksheet.write(row, 1, "CUSTOMER", sub_heading_format_company_new)
        worksheet.write(row, 2, "NAME", sub_heading_format_company_new)
        worksheet.write(row, 3, "PRICE", sub_heading_format_company_new)

        data_filter = ''
        data_filter += " WHERE sm.company_id = '%s'" % (self.env.company.id)
        if data.get('start_date'):
            data_filter += " AND sm.date >= '%s'" % (wiz.start_date)
        if data.get('end_date'):
            data_filter += " AND sm.date <= '%s'" % (wiz.end_date)

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
        row += 1
        if sample_datas:
            for rec in sample_datas:
                rec_date = ""
                if rec['date']:
                    rec_date = datetime.datetime.strptime(str(rec['date']), '%Y-%m-%d').strftime('%d/%m/%Y')
                worksheet.write(row, 0, rec_date, data_format)
                worksheet.write(row, 1, rec['customer_name'], data_format)
                worksheet.write(row, 2, rec['name'], data_format)
                worksheet.write(row, 3, rec['price'], data_format)

                row += 1
        else:
            raise ValidationError(_('No datas found for the selected period!'))
