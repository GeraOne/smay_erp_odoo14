# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    genre = fields.Char(string='Genero')

    def change_genre(self):
        for contact in self:
            return True

# class grp_module(models.Model): contacts.res_partner_menu_contacts
#     _name = 'grp_module.grp_module'
#     _description = 'grp_module.grp_module'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
