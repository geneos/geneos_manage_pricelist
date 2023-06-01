# -*- coding: utf-8 -*-
# from odoo import http


# class GeneosManagePricelist(http.Controller):
#     @http.route('/geneos_manage_pricelist/geneos_manage_pricelist/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/geneos_manage_pricelist/geneos_manage_pricelist/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('geneos_manage_pricelist.listing', {
#             'root': '/geneos_manage_pricelist/geneos_manage_pricelist',
#             'objects': http.request.env['geneos_manage_pricelist.geneos_manage_pricelist'].search([]),
#         })

#     @http.route('/geneos_manage_pricelist/geneos_manage_pricelist/objects/<model("geneos_manage_pricelist.geneos_manage_pricelist"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('geneos_manage_pricelist.object', {
#             'object': obj
#         })
