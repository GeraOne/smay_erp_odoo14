# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools
import logging

_logger = logging.getLogger(__name__)


class GenreReport(models.Model):
    _name = 'data.genre.report'
    _description = 'Data de reporte'
    _auto = False

    id = fields.Integer()
    genre = fields.Char('Genero')
    total_genre = fields.Integer('Contatos')
    total = fields.Integer('Todo Contactos')
    percent = fields.Float('Procentaje')

    def init4(self):
        tools.drop_view_if_exists(self.env.cr, 'data_genre_report')
        self.env.cr.execute('''
            CREATE OR REPLACE VIEW data_genre_report AS(
                SELECT  1 as "id",
                        pt1.genre as "genre",
                        pt1.total as "total_genre", 
                        pt2.total as "total", 
                        round(cast(pt1.total as numeric)/cast(pt2.total as numeric)*100,2) as "percent"
                    FROM(
                        SELECT '1' id ,
                            genre,
                            count(*) total
                        FROM res_partner
                        GROUP BY  genre
                        ) as pt1
                    JOIN (
                        SELECT '1' as id,
                            count(*) total
                        FROM res_partner
                        ) as pt2
                    ON pt1.id = pt2.id
                    )
             '''
                            )
        '''return {
            'name': "Reporte de Generos Contatos",
            'view_mode': 'pivot',
            'view_id': False,
            'view_type': 'pivot',
            'res_model': 'data.genre.report',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'domain': '[]',
            'context': None
        }'''


class ResPartner(models.Model):
    _inherit = 'res.partner'
    genre = fields.Selection([('masculino', 'HOMBRE'), ('femenino', 'MUJER'), ], 'Genero', default='femenino',
                             required=True)

    def change_genre(self):
        for contact in self:
            new_genre = ''
            if contact.genre == 'femenino':
                new_genre = 'masculino'
            else:
                new_genre = 'femenino'

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
