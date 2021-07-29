# -*- coding: utf-8 -*-

from odoo import models, fields, api,tools
import logging

_logger = logging.getLogger(__name__)


class GenreReport(models.TransientModel):
    _name = 'data.genre.report'
    _description = 'Data de reporte'
    _auto = False

    genre = fields.Char('Genero')
    total_genre = fields.Integer('Contatos')
    percent = fields.Float('Procentaje')

    def init(self):
        tools.drop_view_if_exists(self.env.cr, 'data_genre_report')
        self.env.cr.execute()



    def generate_report(self):
        self.env['stock.report.smay'].init()
        return {
            'name': _("Reporte de Generos Contatos"),
            'view_mode': 'pivot',
            'view_id': False,
            'view_type': 'pivot',
            'res_model': 'stock.report.smay',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'domain': '[]',
            'context': None
        }


class ResPartner(models.Model):
    _inherit = 'res.partner'
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
