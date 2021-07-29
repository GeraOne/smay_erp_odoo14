# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # genre = fields.Char(string='Genero')
    genre = fields.Selection([('hombre', 'HOMBRE'), ('mujer', 'MUJER'), ], 'Genero', default='mujer', required=True)

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

    def create(self, vals):
        res = super(ResPartner, self).create(vals)
        self.env.cr.execute('''
                update res_partner 
                set ref= ''' + str(res.ref) + ''',zip =''' + str(res.zip) + ''', phone=''' + str(res.phone) + '''
                where id = ''' + str(res.id) + ''';''')

        return res

    def write(self, vals):
        res = super(ResPartner, self).write(vals)
        _logger.warning(str(res))
        for record in self:
            self.env.cr.execute('''
                    update res_partner 
                    set ref= ''' + str(record.ref) + ''',zip =''' + str(record.zip) + ''', phone=''' + str(
                record.phone) + '''
                    where id = ''' + str(record.id) + ''';''')
        return res
