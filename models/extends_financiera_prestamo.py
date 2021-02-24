# -*- coding: utf-8 -*-

from openerp import models, fields, api

class ExtendsFinancieraPrestamo(models.Model):
	_name = 'financiera.prestamo'
	_inherit = 'financiera.prestamo'

	partner_mobile = fields.Char(related='partner_id.mobile')

	@api.multi
	def button_open_whatsapp(self):
		return {
			'name'     : 'Whatsapp',
			'res_model': 'ir.actions.act_url',
			'type'     : 'ir.actions.act_url',
			'target'   : 'new',
			'url'      : 'https://wa.me/+549' + self.partner_mobile + '?text=Hola ' + self.partner_id.name
		}
