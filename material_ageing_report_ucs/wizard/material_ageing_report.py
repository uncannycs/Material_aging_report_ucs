# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from .excel_styles import ExcelStyles
from odoo.exceptions import UserError
from datetime import datetime, timedelta
import xlwt
import io
import base64
from xlwt import Formula

product_filter_type = [
    ('rm', 'Raw Material'),
    ('tool_rm', 'Die Raw Material'),
    ('maintenance', 'Maintenance Spares'),
    ('asset', 'Assets'),
    ('consumable', 'Consumable Items'),
]


class MaterialAgeingReport(models.TransientModel):
    _name = "material.ageing.report"
    _description = "Material Ageing Report"

    name = fields.Char(string='Name', readonly=True)
    output = fields.Binary(string='Output', readonly=True)
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.user.company_id)
    product_ids = fields.Many2many('product.product', string='Product')

    def action_report(self):
        move_obj = self.env['stock.move']
        valuation_obj = self.env['stock.valuation.layer']
        quant_obj = self.env['stock.quant']
        report_name = "Material Ageing Report"

        curr_date = datetime.now() + timedelta(hours=5, minutes=30)
        curr_date_str = curr_date.strftime("%d-%m-%Y %I:%M:%S %p")
        # filters = "Filtered Based on As On date: " + str(curr_date_str)

        Style = ExcelStyles()
        wbk = xlwt.Workbook()

        sheet_one = "Material Ageing Report"
        sheet1 = wbk.add_sheet(sheet_one)
        sheet1.set_panes_frozen(True)

        domain = [('picking_id.picking_type_code', '=', 'incoming'), ('purchase_line_id', '!=', False)]

        inventory_location = self.env['stock.location'].search([('is_inventory_adjustment', '=', True)])

        inventory_domain = [('location_id', '=', inventory_location.id), ('is_inventory', '!=', False)]

        product_str, location_str, department_str = ", Product : ", ", Location : ", ", Department : "
        for product_id in self.product_ids:
            if self.product_ids[-1] == product_id:
                product_str += product_id.name
            else:
                product_str += product_id.name + ", "

        if self.product_ids:
            domain += [('product_id', 'in', self.product_ids.ids)]
            inventory_domain += [('product_id', 'in', self.product_ids.ids)]
            # filters += product_str

        purchase_moves = move_obj.search(domain, order="product_id")
        purchase_moves = purchase_moves.filtered(
            lambda l: l.purchase_line_id)
        inventory_moves = move_obj.search(inventory_domain, order="product_id")
        moves_ids = []
        moves_ids = purchase_moves.ids + inventory_moves.ids

        moves = move_obj.search([('id', 'in', moves_ids)], order="product_id")
        valuation_ids = valuation_obj.search([('stock_move_id', 'in', moves_ids)])
        sheet1.col(0).width = 1500
        sheet1.col(1).width = 3800
        sheet1.col(2).width = 10000
        sheet1.col(3).width = 3500
        sheet1.col(4).width = 4000
        sheet1.col(5).width = 4000
        sheet1.col(6).width = 4000
        sheet1.col(7).width = 5000
        sheet1.col(8).width = 4000
        sheet1.col(9).width = 5000
        sheet1.col(10).width = 4000
        sheet1.col(11).width = 5000
        sheet1.col(12).width = 4000
        sheet1.col(13).width = 4000
        sheet1.col(14).width = 6000

        row = 0
        sheet1.row(row).height = 300
        sheet1.write_merge(row, row, 0, 14, self.company_id.display_name, Style.main_title())

        row += 1
        sheet1.row(row).height = 300
        sheet1.write_merge(row, row, 0, 14, report_name, Style.main_title())

        row += 1
        sheet1.row(row).height = 300
        # sheet1.write_merge(row, row, 0, 14, filters, Style.subTitle_color_left())

        row += 2
        sheet1.row(row).height = 500
        sheet1.write(row, 0, "S.No", Style.contentTextBoldCenter(2, 'black', 'white'))
        sheet1.write(row, 1, "Material Code", Style.contentTextBoldCenter(2, 'black', 'white'))
        sheet1.write(row, 2, "Material Description", Style.contentTextBoldCenter(2, 'black', 'white'))
        sheet1.write(row, 3, "UOM", Style.contentTextBoldCenter(2, 'black', 'white'))
        sheet1.write(row, 4, "GRN No", Style.contentTextBoldCenter(2, 'black', 'white'))
        sheet1.write(row, 5, "Date of Receipt", Style.contentTextBoldCenter(2, 'black', 'white'))
        sheet1.write(row, 6, "Quantity", Style.contentTextBoldCenter(2, 'black', 'white'))
        sheet1.write(row, 7, "Traceability No", Style.contentTextBoldCenter(2, 'black', 'white'))
        sheet1.write(row, 8, "Value", Style.contentTextBoldCenter(2, 'black', 'white'))
        sheet1.write(row, 9, "Ageing Days", Style.contentTextBoldCenter(2, 'black', 'white'))
        sheet1.write(row, 10, "Order Reference", Style.contentTextBoldCenter(2, 'black', 'white'))
        sheet1.write(row, 11, "Responsible Person", Style.contentTextBoldCenter(2, 'black', 'white'))
        sheet1.set_horz_split_pos(row + 1)

        start_row = 0
        s_no = 0
        for each in moves:

            row += 1
            if not start_row:
                start_row = row
            s_no += 1
            sheet1.write(row, 0, s_no and s_no or "", Style.normal_left())
            sheet1.write(row, 1, each.product_id and each.product_id.default_code or "", Style.normal_left())
            sheet1.write(row, 2, each.product_id and each.product_id.name or "", Style.normal_left())
            sheet1.write(row, 3, each.product_uom and each.product_uom.name or "", Style.normal_left())

            date_format, date = False, False
            if each.date:
                date = each.date + timedelta(minutes=330)
                date_format = date.strftime("%Y-%m-%d")
                date_format = datetime.strptime(date_format, "%Y-%m-%d")
                date_str = date.strftime("%d-%m-%Y")

            sheet1.write(row, 4, each.picking_id and each.picking_id.name or "", Style.normal_left())
            sheet1.write(row, 5, date_str and date_str or "", Style.normal_left())
            lot_ids = each.move_line_ids.mapped('lot_id')
            remaining_value = remaining_qty = 0.0
            if lot_ids:
                lot_ids_list = lot_ids and lot_ids.mapped('name') or []
                lot_ids_str = str(lot_ids_list).replace("[", "").replace("]", "").replace("'", "")
                quants = quant_obj.search([('product_id', '=', each.product_id.id), ('lot_id', 'in', lot_ids.ids),
                                           ('location_id.usage', '=', 'internal')])
                remaining_qty = sum(quant.quantity for quant in quants)
                sheet1.write(row, 6, remaining_qty and remaining_qty or 0, Style.normal_num_right())
                sheet1.write(row, 7, lot_ids_str and lot_ids_str or "", Style.normal_left())
                sheet1.write(row, 8, (remaining_qty * each.price_unit), Style.normal_num_right())
            else:
                valuation_line = valuation_obj.search([
                    ('stock_move_id', '=', each.id)
                ], limit=1, order="id desc")
                if valuation_line:
                    remaining_qty = valuation_line.remaining_qty
                    remaining_value = valuation_line.remaining_value
                sheet1.write(row, 6, remaining_qty, Style.normal_num_right())
                sheet1.write(row, 7, "", Style.normal_left())
                sheet1.write(row, 8, remaining_value, Style.normal_num_right())

            ageing_days = (curr_date - date_format).days
            sheet1.write(row, 9, ageing_days and ageing_days or 0, Style.normal_num_int_right())

            sheet1.write(row, 10, each.picking_id and each.picking_id.origin or "", Style.normal_left())
            responsible_person = ""
            if each.purchase_line_id and each.purchase_line_id.order_id:
                responsible_person = each.purchase_line_id.order_id.user_id.name or ""
            elif each.sale_line_id and each.sale_line_id.order_id:
                responsible_person = each.sale_line_id.order_id.user_id.name or ""
            sheet1.write(row, 11, responsible_person,
                         Style.normal_left())

        stream = io.BytesIO()
        wbk.save(stream)

        self.write({'name': report_name + '.xls', 'output': base64.b64encode(stream.getvalue())})
        return {
            'name': _('Material Ageing Report'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'material.ageing.report',
            'res_id': self.id,
            'type': 'ir.actions.act_window',
            'target': 'new'
        }
