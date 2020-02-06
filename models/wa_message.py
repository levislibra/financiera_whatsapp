# -*- coding: utf-8 -*-

from openerp import models, fields, api
from datetime import datetime, timedelta
from dateutil import relativedelta
# Download the helper library from https://www.twilio.com/docs/python/install
from twilio.rest import Client

WHATSAPP_NUMERO_NEUTRO = "0000000000"
WHATSAPP_PREFIX = '+549'

class FinancieraWhatsappMessage(models.Model):
	_name = 'financiera.wa.message'

	_order = 'id desc'
	partner_id = fields.Many2one('res.partner', 'Cliente')
	config_id = fields.Many2one('financiera.wa.config', 'Configuracion WA')
	tipo = fields.Char('Tipo de mensaje')
	from_ = fields.Char('Desde')
	to = fields.Char('Para')
	body = fields.Text('Mensaje')
	error_code = fields.Char("Codigo de error")
	error_message = fields.Char("Mensaje de error")
	status = fields.Char("Estado")
	price = fields.Char("Precio")
	price_unit = fields.Char("Precio unitario")
	company_id = fields.Many2one('res.company', 'Empresa', default=lambda self: self.env['res.company']._company_default_get('financiera.wa.message'))

	@api.one
	def send(self):
		if self.to != False and len(self.to) == 10:
			client = Client(self.config_id.account_sid, self.config_id.auth_token)
			message = client.messages.create(
				body=self.body,
				from_='whatsapp:'+self.from_,
				to='whatsapp:'+WHATSAPP_PREFIX+self.to
			)
			self.error_code = message.error_code
			self.error_message = message.error_message
			self.status = message.status
			self.price = message.price
			self.price_unit = message.price_unit
		else:
			self.error_message = "Numero destino"
			self.status = "Not send"
