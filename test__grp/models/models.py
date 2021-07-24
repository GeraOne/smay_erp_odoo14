# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class test__grp(models.Model):
#     _name = 'test__grp.test__grp'
#     _description = 'test__grp.test__grp'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
