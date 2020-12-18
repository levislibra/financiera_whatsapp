# -*- coding: utf-8 -*-

from openerp import models, fields, api

class ExtendsResPartner(models.Model):
	_name = 'res.partner'
	_inherit = 'res.partner'

	@api.multi
	def button_open_whatsapp(self):
		return {
			'name'     : 'Whatsapp',
			'res_model': 'ir.actions.act_url',
			'type'     : 'ir.actions.act_url',
			'target'   : 'new',
			'url'      : 'https://wa.me/+549' + self.mobile + '?text=Hola ' + self.name
		}
