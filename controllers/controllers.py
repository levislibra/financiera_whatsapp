# -*- coding: utf-8 -*-
from openerp import http

# class FinancieraWhatsapp(http.Controller):
#     @http.route('/financiera_whatsapp/financiera_whatsapp/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/financiera_whatsapp/financiera_whatsapp/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('financiera_whatsapp.listing', {
#             'root': '/financiera_whatsapp/financiera_whatsapp',
#             'objects': http.request.env['financiera_whatsapp.financiera_whatsapp'].search([]),
#         })

#     @http.route('/financiera_whatsapp/financiera_whatsapp/objects/<model("financiera_whatsapp.financiera_whatsapp"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('financiera_whatsapp.object', {
#             'object': obj
#         })