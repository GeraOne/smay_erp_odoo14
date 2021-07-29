# -*- coding: utf-8 -*-
{
    'name': "smay_stock_transferences",

    'summary': """
        Modificacion para las transferencias.""",

    'description': """
        El modulo realiza validaciones para que las transferencias sean enviadas correctamente.
    """,

    'author': "Gerardo Reyes Preciado",
    'website': "http://www.supermay.mx",

    'category': 'stock',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock'],

    # always loaded
    'data': [
        'views/views.xml',
    ],
}
