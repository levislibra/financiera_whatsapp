# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import UserError, ValidationError

class ExtendsResPartner(models.Model):
	_name = 'res.partner'
	_inherit = 'res.partner'

	@api.multi
	def button_open_whatsapp(self):
		if self.mobile:
			return {
				'name'     : 'Whatsapp',
				'res_model': 'ir.actions.act_url',
				'type'     : 'ir.actions.act_url',
				'target'   : 'new',
				'url'      : 'https://wa.me/+549' + self.mobile + '?text=Hola ' + self.name
			}
		else:
			raise UserError("El celular no esta cargado.")
