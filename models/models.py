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
	# preventivo_body = fields.Text('Mensaje')
	# preventivo_when_send = fields.One2many('financiera.wa.send.when', 'preventivo_when_send_id', 'Cuando enviar?')
	# preventivo_who_send = fields.One2many('financiera.wa.send.who', 'preventivo_who_send_id', 'A quien enviar?')

	@api.one
	def test_connection(self):
		client = Client(self.account_sid, self.auth_token)
		message = client.messages.create(
			body=self.body_send_test,
			from_='whatsapp:'+self.number_send,
			to='whatsapp:'+self.number_received_test
		)

class FinancieraWhatsappMessage(models.Model):
	_name = 'financiera.wa.message'

	name = fields.Char('Nombre')
	active = fields.Boolean('Activo')
	state = fields.Selection([('borrador', 'Borrador'), ('aprobado', 'Aprobado'), ('rechazado', 'Rechazado')], 'Estado', default='borrador')
	body = fields.Text('Mensaje')
	body_word_replace = fields.Text('Palabras para reemplazar', default="""
	Cliente:
	* PRESTAMOS
		- prestamo_monto: monto solicitado
	* Cuotas
		- cuota_proximo_vencimiento: Proximo vencimiento y monto
		- cuota_vencimientos_montos: Vencimientos y montos del mes
		- cuota_vencidas_montos: Vencimeintos y montos vencidos
	* Generales:
		- monto_deuda_vencida: Monto deuda vencida
		- deuda_total: Deuda total
	""")
	when_send = fields.One2many('financiera.wa.send.when', 'when_send_id', 'Cuando enviar?')
	who_send = fields.One2many('financiera.wa.send.who', 'who_send_id', 'A quien enviar?')
	message_ids = fields.One2many('financiera.wa.message.send', 'wa_message_id', 'Mensajes enviados')
	company_id = fields.Many2one('res.company', 'Empresa', default=lambda self: self.env['res.company']._company_default_get('financiera.whatsapp.message'))

	@api.one
	def aprobar(self):
		self.state = 'aprobado'

	@api.one
	def borrador(self):
		self.state = 'borrador'

	@api.one
	def rechazar(self):
		self.state = 'rechazado'

class FinancieraWhatsappSendWhen(models.Model):
	_name = 'financiera.wa.send.when'

	when_send_id = fields.Many2one('financiera.wa.message')
	send_type = fields.Selection([('dia_especifico', 'Dia especifico'), ('dia_antes_vencimiento', 'Dias antes del vencimiento'), ('dia_despues_vencimiento', 'Dias despues del vencimiento')], 'Tipo de envio')
	date = fields.Integer('Dia/Dias')
	company_id = fields.Many2one('res.company', 'Empresa', default=lambda self: self.env['res.company']._company_default_get('financiera.whatsapp.config'))

class FinancieraWhatsappSendWho(models.Model):
	_name = 'financiera.wa.send.who'

	who_send_id = fields.Many2one('financiera.wa.message')
	send_who = fields.Selection([
		('cuotas_activa', 'Cliente con al menos N cuotas activas'),
		('cuotas_vencidas', 'Cliente con al menos N cuotas vencidas'),
		('cuotas_preventiva', 'Cliente con al menos N cuotas en preventiva y no mas de M cuotas vencidas')],
		'Tipo de envio')
	n = fields.Integer("N")
	m = fields.Integer("M")
	company_id = fields.Many2one('res.company', 'Empresa', default=lambda self: self.env['res.company']._company_default_get('financiera.whatsapp.config'))

class FinancieraWhatsappMessageSend(models.Model):
	_name = 'financiera.wa.message.send'

	_order = 'id desc'
	partner_id = fields.Many2one('res.partner','Cliente')
	wa_message_id = fields.Many2one('financiera.wa.message', 'Estructura de mensaje')
	# state = fields.Selection([('enviado', 'Enviado'), ('recibido', 'Recibido'), ('rechazado', 'Rechazado')], 'Estado', default='enviado')
	body = fields.Text('Mensaje')
	company_id = fields.Many2one('res.company', 'Empresa', default=lambda self: self.env['res.company']._company_default_get('financiera.whatsapp.message'))

class ExtendsResCompany(models.Model):
	_inherit = 'res.company'

	wa_configuracion_id = fields.Many2one('financiera.wa.config', 'Configuracion sobre Whatsapp')
