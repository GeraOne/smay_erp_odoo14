# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    genre = fields.Char(string='Genero')

    def change_genre(self):
        for contact in self:
            return True
