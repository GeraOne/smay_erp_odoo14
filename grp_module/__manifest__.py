# -*- coding: utf-8 -*-
{
    'name': "grp_module",

    'summary': """
        examen""",

    'description': """
        Examen de programador Junior odoo V14
    """,

    'author': "gerardo reyes preciado",
    'website': "http://www.geraone.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'contacts',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'contacts'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
    ],
}
