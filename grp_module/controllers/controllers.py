# -*- coding: utf-8 -*-
# from odoo import http


# class GrpModule(http.Controller):
#     @http.route('/grp_module/grp_module/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/grp_module/grp_module/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('grp_module.listing', {
#             'root': '/grp_module/grp_module',
#             'objects': http.request.env['grp_module.grp_module'].search([]),
#         })

#     @http.route('/grp_module/grp_module/objects/<model("grp_module.grp_module"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('grp_module.object', {
#             'object': obj
#         })
