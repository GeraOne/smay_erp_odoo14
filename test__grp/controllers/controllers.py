# -*- coding: utf-8 -*-
# from odoo import http


# class TestGrp(http.Controller):
#     @http.route('/test__grp/test__grp/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/test__grp/test__grp/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('test__grp.listing', {
#             'root': '/test__grp/test__grp',
#             'objects': http.request.env['test__grp.test__grp'].search([]),
#         })

#     @http.route('/test__grp/test__grp/objects/<model("test__grp.test__grp"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('test__grp.object', {
#             'object': obj
#         })
