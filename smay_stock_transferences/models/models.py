# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class smayTransferencesResUser(models.Model):
    _inherit = 'res.users'

    stock_location_id = fields.Many2one('stock.location', string='Almacen origen para transferencias',
                                        domain="[('name','=','Stock')]")
    transfers_validator = fields.Boolean(string='Puede validar transferencias', default=False)
    picking_type_id = fields.Many2one('stock.picking.type', string='Tipo de movimiento por default',
                                      domain="[('name','=','Transferencias internas')]")
    sucursal_transferencias_id = fields.Many2one('res.partner', 'Sucursal Transferencias')


    x_validations_transfers = fields.Boolean('Validaciones Transferencias Smay', default=False)


class smayStocktMove(models.Model):
    _inherit = 'stock.move'

    @api.onchange('product_id', )
    def _calculate_qty(self):
        for move in self:
            ##ADD BY Gerardo Reyes Preciado
            if self.env.user.x_validations_transfers:
                if (move.product_id):
                    quant = self.env['stock.quant'].search(
                        [('product_id', '=', move.product_id.id), ('location_id', '=', move.location_id.id)])
                    move.product_uom_qty = quant.quantity - quant.reserved_quantity


class smayTransferencesStockPicking(models.Model):
    _inherit = 'stock.picking'

    # Se autocompleta con el valor asignado en res.users, se agrego el valor default
    partner_id = fields.Many2one(
        'res.partner', 'Partner',
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]},
        default=lambda self: self._default_partner())
    # Se autocompleta con el valor asignado en res.users, se agrego el valor default
    location_id = fields.Many2one(
        'stock.location', "Source Location",
        default=lambda self: self._default_location(),
        readonly=True, required=True,
        states={'draft': [('readonly', False)]})
    # Se autocompleta con el valor asignado en res.users, se agrego el valor default
    picking_type_id = fields.Many2one(
        'stock.picking.type', 'Operation Type',
        required=True,
        readonly=True,
        domain="[('name','=','Transferencias internas')]",
        states={'draft': [('readonly', False)]}, default=lambda self: self._default_picking_type())

    @api.model
    def _default_partner(self):
        if not self.env.user.has_group('stock.group_stock_manager') and self.env.user.x_validations_transfers:
            return self.env.user.sucursal_transferencias_id.id
        return

    @api.model
    def _default_location(self):
        if not self.env.user.has_group('stock.group_stock_manager') and self.env.user.x_validations_transfers:
            return self.env.user.stock_location_id.id
        return

    @api.model
    def _default_picking_type(self):
        if not self.env.user.has_group('stock.group_stock_manager') and self.env.user.x_validations_transfers:
            return self.env.user.picking_type_id.id
        return

    def validation_lines(self):
        if self.id:
            if self.location_id.id == self.location_dest_id.id:
                raise UserError('La ubicación origen y destino no pueden ser la misma.')

            for picking in self.move_ids_without_package:

                if picking.product_uom_qty <= 0:
                    raise UserError('La cantidad del producto ' + str(picking.product_id.name) + ' debe ser mayor a 0')

                for picking_aux in self.move_ids_without_package:
                    if picking_aux.id != picking.id and picking.product_id.id == picking_aux.product_id.id:
                        raise UserError('El producto ' + str(picking.product_id.name) + ' esta repetido.')

                stock = self.env['stock.quant'].search([('company_id', '=', self.env.user.company_id.id),
                                                        ('location_id', '=', self.location_id.id),
                                                        ('product_id', '=', picking.product_id.id)])
                if stock.quantity < picking.product_uom_qty:
                    raise UserError('No tienes stock para transferir el producto ' + str(picking.product_id.name))

    def action_confirm(self):
        if '/INT/' in str(self.name):
            if self.id and self.env.user.x_validations_transfers:
                self.validation_lines()
                if not self.env.user.has_group('stock.group_stock_manager'):
                    if self.location_dest_id.name in ('Mermas', 'Insumos'):
                        raise UserError('Solo los administradores pueden validar envios a Merma o Insumos')

                    if self.location_id.id == self.location_dest_id.id:
                        raise UserError('La ubicación origen y destino no pueden ser la misma.')

                    if self.location_id.id != self.env.user.stock_location_id.id:
                        raise UserError(
                            'Solo un usuario de la sucursal que envia puede marcar por realizar la transferencia.')
        return super(smayTransferencesStockPicking, self).action_confirm()

    def action_assign(self):
        if '/INT/' in str(self.name):
            if self.id and self.env.user.x_validations_transfers:
                self.validation_lines()
                if not self.env.user.has_group('stock.group_stock_manager'):
                    if self.location_id.id != self.env.user.stock_location_id.id:
                        raise UserError('Solo puedes comprobrar disponibilidad de la sucursal asignada.')
        return super(smayTransferencesStockPicking, self).action_assign()

    def button_validate(self):
        if '/INT/' in str(self.name):
            if self.id and self.env.user.x_validations_transfers:
                self.validation_lines()
                if not self.env.user.has_group('stock.group_stock_manager'):
                    if not self.env.user.transfers_validator:
                        raise UserError('No tienes lo privilegios para validar transferencias de inventario')
                    if self.location_dest_id.id != self.env.user.stock_location_id.id:
                        raise UserError('No puedes validar transferencias para el almacen de otra sucursal')
        return super(smayTransferencesStockPicking, self).button_validate()

    def button_scrap(self):
        if '/INT/' in str(self.name):
            if self.id and self.env.user.x_validations_transfers:
                if not self.env.user.has_group('stock.group_stock_manager'):
                    raise UserError(
                        'Funcionalidad deshabilitada, solo los administrativos pueden realizar esta operacion.')
        return super(smayTransferencesStockPicking, self).button_scrap()

    def do_unreserve(self):
        if '/INT/' in str(self.name):
            if self.id and self.env.user.x_validations_transfers:
                if not self.env.user.has_group('stock.group_stock_manager'):
                    if self.location_dest_id.id != self.env.user.stock_location_id.id:
                        raise UserError(
                            'Solo puedes cancelar la disponibilidad del las transferencias de la sucursal que tienes asignada.')
        super(smayTransferencesStockPicking, self).do_unreserve()

    def action_toggle_is_locked(self):
        if '/INT/' in str(self.name):
            if self.id and self.env.user.x_validations_transfers:
                if not self.env.user.has_group('stock.group_stock_manager'):
                    raise UserError(
                        'Funcionalidad deshabilitada, solo los administrativos pueden realizar esta operacion.')
        return super(smayTransferencesStockPicking, self).action_toggle_is_locked()
