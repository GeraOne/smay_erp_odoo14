# -*- coding: utf-8 -*-
###################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2020-TODAY Cybrosys Technologies (<https://www.cybrosys.com>).
#    Author: Risha C.T (<https://www.cybrosys.com>)
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
###################################################################################

from odoo import models, fields, api
from odoo.osv import expression
from odoo.exceptions import UserError, Warning, ValidationError
import logging
from datetime import date
import datetime

_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = 'product.product'

    product_multi_barcodes = fields.One2many('multi.barcode.products', 'product_multi', string='Barcodes')

    @api.model
    def create(self, vals):
        res = super(ProductProduct, self).create(vals)
        if res.product_multi_barcodes:
            res.product_multi_barcodes.update({
                'template_multi': res.product_tmpl_id.id
            })
        return res

    def write(self, vals):
        res = super(ProductProduct, self).write(vals)
        if self.product_multi_barcodes:
            self.product_multi_barcodes.update({
                'template_multi': self.product_tmpl_id.id
            })
        return res

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        res = super(ProductProduct, self)._name_search(name, args, operator, limit, name_get_uid)
        if len(res) > 0:
            _logger.warning('encontro producto')
            _logger.warning(str(res))
            return res
        '''product_ids = self.env['multi.barcode.products'].search([('multi_barcode', '=', name)]).mapped(
            'product_multi.id')
        if product_ids:
            _logger.warning('Segunda busqueda')
            _logger.warning(str(product_ids))
            return tuple([id for id in self.env['product.product'].search([('type','=','product')])])
            #return models.lazy_name_get(self.browse(product_ids).with_user(name_get_uid))'''
        product_id = self.env['multi.barcode.products'].search([('multi_barcode', 'ilike', name)],limit=1)
        if product_id:
            res = super(ProductProduct, self)._name_search(product_id.template_multi.name, args, operator, limit, name_get_uid)
            return res


        return res


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    _description = 'Guarda lo codigos alternos de los productos'

    template_multi_barcodes = fields.One2many('multi.barcode.products', 'template_multi', string='Codigos Alternos')

    @api.model
    def create(self, vals):
        res = super(ProductTemplate, self).create(vals)
        if res.template_multi_barcodes:
            res.template_multi_barcodes.update({
                'product_multi': res.product_variant_id.id
            })
        return res

    def write(self, vals):
        res = super(ProductTemplate, self).write(vals)
        if self.template_multi_barcodes:
            self.template_multi_barcodes.update({
                'product_multi': self.product_variant_id.id
            })
        return res


class ProductMultiBarcode(models.Model):
    _name = 'multi.barcode.products'
    _description = 'Guarda lo codigos alternos de los productos'

    multi_barcode = fields.Char(string="Barcode", help="Provide alternate barcodes for this product")
    product_multi = fields.Many2one('product.product')
    template_multi = fields.Many2one('product.template')

    @api.model
    def create(self, vals):
        if not vals['multi_barcode']:
            raise UserError("No pueden ingresarse codigos vacios.")
        barcode = self.env['product.product'].search([('barcode', '=', vals['multi_barcode'])])
        if barcode:
            raise UserError("El codigo de barras:" + str(
                vals['multi_barcode']) + " esta asignado al producto :" + barcode.product_tmpl_id.name)
        barcode = self.env['multi.barcode.products'].search([('multi_barcode', '=', vals['multi_barcode'])])
        if barcode:
            raise UserError("El codigo alterno: " + str(
                vals['multi_barcode']) + " ya esta asignado al producto: " + barcode.template_multi.name)
        res = super(ProductMultiBarcode, self).create(vals)

        return res

    def write(self, vals):
        res = super(ProductMultiBarcode, self).write(vals)
        for barcode in self.env['product.product'].browse(self.product_multi.id).product_multi_barcodes:
            barc = self.env['multi.barcode.products'].search([('multi_barcode', '=', barcode.multi_barcode)])
        if len(barc) > 1:
            raise UserError('No puedes asignar el codigo a más de un producto')
        return res
