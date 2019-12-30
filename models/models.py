# -*- coding: utf-8 -*-

from openerp import models, fields, api
# Download the helper library from https://www.twilio.com/docs/python/install
from twilio.rest import Client

class FinancieraWhatsappConfig(models.Model):
	_name = 'financiera.wa.config'

	name = fields.Char('Nombre')
	account_sid = fields.Char('SID de cuenta')
	auth_token = fields.Char('Token')
	number_send = fields.Char("Numero Twilio", default="+")
	number_received_test = fields.Char("Numero Recepcion para Test", default="+")
	body_send_test = fields.Text("Texto a enviar")
	company_id = fields.Many2one('res.company', 'Empresa', default=lambda self: self.env['res.company']._company_default_get('financiera.whatsapp.config'))
	# Mensajes
	# Aviso preventivo
	preventivo_body = fields.Text('Mensaje')
	preventivo_when_send = fields.One2many('financiera.wa.send.when', 'preventivo_when_send_id', 'Cuando enviar?')
	preventivo_who_send = fields.One2many('financiera.wa.send.who', 'preventivo_who_send_id', 'A quien enviar?')

	@api.one
	def test_connection(self):
		client = Client(self.account_sid, self.auth_token)
		message = client.messages.create(
			body=self.body_send_test,
			from_='whatsapp:'+self.number_send,
			to='whatsapp:'+self.number_received_test
		)

class FinancieraWhatsappSendWhen(models.Model):
	_name = 'financiera.wa.send.when'

	preventivo_when_send_id = fields.Many2one('financiera.wa.config')
	send_type = fields.Selection([('dia_especifico', 'Dia especifico'), ('dia_antes_vencimiento', 'Dias antes del vencimiento'), ('dia_despues_vencimiento', 'Dias despues del vencimiento')], 'Tipo de envio')
	date = fields.Integer('Dia/Dias')
	company_id = fields.Many2one('res.company', 'Empresa', default=lambda self: self.env['res.company']._company_default_get('financiera.whatsapp.config'))

class FinancieraWhatsappSendWho(models.Model):
	_name = 'financiera.wa.send.who'

	preventivo_who_send_id = fields.Many2one('financiera.wa.config')
	send_who = fields.Selection([
		('cuota_activa', 'Cliente con cuota activa'),
		('cuota_preventiva', 'Cliente con cuota en preventiva')],
		'Tipo de envio')
	company_id = fields.Many2one('res.company', 'Empresa', default=lambda self: self.env['res.company']._company_default_get('financiera.whatsapp.config'))


class ExtendsResCompany(models.Model):
	_inherit = 'res.company'

	wa_configuracion_id = fields.Many2one('financiera.wa.config', 'Configuracion sobre Whatsapp')
