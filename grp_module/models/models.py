# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # genre = fields.Char(string='Genero')
    genre = fields.Selection([('hombre', 'HOMBRE'), ('mujer', 'MUJER'), ], 'Genero', default='mujer')

    def change_genre(self):
        for contact in self:
            new_genre = ''
            if contact.genre == 'mujer':
                new_genre = 'hombre'
            else:
                new_genre = 'mujer'

            contact.update({
                'genre': new_genre
            })
            return True
