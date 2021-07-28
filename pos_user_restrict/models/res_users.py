# -*- coding: utf-8 -*-

from odoo import fields, models

'''
FECHA:		20201211 
VERSIÓN:	13.0.0.1:
DESCRIPCIÓN:
		Restringe la visualización de puntos de venta y pedidos a los usuarios del POS.
		
CAMPOS:
    
    pos_config_ids : Define que puntos de venta seran visibles para el usuario.
'''


class ResUsers(models.Model):
    _inherit = 'res.users'

    x_pos_config_ids = fields.Many2many('pos.config', string='Puntos de Venta disponibles',
                                        help="Puntos de Venta disponibles para el usuario. El encargado de POS puede ver todos los puntos de venta.")
    x_branch_id = fields.Many2one('res.partner', 'Sucursal')


'''class ResPartner(models.Model):
    _inherit = 'res.partner'

   x_user_smay = fields.One2many('res.users', 'x_branch_id', 'Usuarios')'''
