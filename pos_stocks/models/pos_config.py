# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
# 
#################################################################################
from odoo import api, fields, models

import logging

_logger = logging.getLogger(__name__)

'''
FECHA:		20201120 
VERSIÓN:	v13.0.0.1:
DESCRIPCIÓN:
		En la configuración del punto de venta añade los siguientes campos para poner restriccciones de venta y visualización
		
CAMPOS:
    
    wk_display_stock : Bandera para mostrar o no el stock en el POS.
    wk_stock_type: Cantidad presentada en el POS
    wk_deny_val: Bandera para no dejar vender el producto sin stock
    wk_error_msg : Mensaje que sera presentado en el POS al negar la venta.
    wk_hide_out_of_stock: bandera para ocultar productos sin stock    
'''


class PosConfig(models.Model):
    _inherit = 'pos.config'

    wk_display_stock = fields.Boolean('Display stock in POS', default=True)
    '''wk_stock_type = fields.Selection(
        [('available_qty', 'Available Quantity(On hand)'), ('forecasted_qty', 'Forecasted Quantity'),
         ('virtual_qty', 'Quantity on Hand - Outgoing Qty')], string='Stock Type', default='available_qty')
    wk_hide_out_of_stock = fields.Boolean(string="Hide Out of Stock products", default=True)'''
    wk_continous_sale = fields.Boolean('Allow Order When Out-of-Stock', default=True)
    wk_deny_val = fields.Integer('Deny order when product stock is lower than ')
    wk_error_msg = fields.Char(string='Custom message', default="Product out of stock")

    @api.model
    def existe_conexion(self):
        return True


class PosStocksProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def get_real_qty(self, company_id, location_id):
        '''
        V1
        stocks = self.env['stock.quant'].search(
            [('company_id', '=', company_id), ('location_id', '=', location_id)])
        result = {}
        for stock in stocks:
            result[stock.product_id.id] = stock.quantity - stock.reserved_quantity
        return result'''

        # v2
        self._cr.execute('''
                select  pp.id product_id, 
                        coalesce(sq.quantity - sq.reserved_quantity,0) qty
                from product_product pp
                left join stock_quant sq
                    on pp.id = sq.product_id
                    and sq.company_id = ''' + str(company_id) + '''
                    and location_id = ''' + str(location_id) + '''
                order by 1
        ''')
        stocks = self._cr.dictfetchall()
        result = {}
        for stock in stocks:
            result[stock['product_id']] = stock['qty']
        return result
