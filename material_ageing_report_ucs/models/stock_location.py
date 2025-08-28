# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class StockLocation(models.Model):
    _inherit = 'stock.location'

    is_inventory_adjustment = fields.Boolean(string="Inventory Adjustment")