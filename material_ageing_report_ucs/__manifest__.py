# -*- coding: utf-8 -*-
{
    'name': "Material Ageing Report Ucs",
    'version': '18.0.0.1.0',
    'summary': """Material Ageing Report""",
    'description': """Material Ageing Report""",
    "website": "https://www.uncannycs.com",
    "author": "Uncanny Consulting Services LLP",
    "maintainers": "Uncanny Consulting Services LLP",
    "license": "Other proprietary",
    'category': 'Inventory',
    'depends': ['base','sale','purchase','product','stock','stock_account'],

    'data': [
        'security/ir.model.access.csv',
        'views/stock_location_views.xml',
        'wizard/material_ageing_report.xml'
    ],
}