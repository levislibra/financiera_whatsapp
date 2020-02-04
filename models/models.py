# -*- coding: utf-8 -*-

from openerp import models, fields, api
from datetime import datetime, timedelta
from dateutil import relativedelta
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
	preventivo_activar = fields.Boolean("Activar mensaje preventivo")
	preventivo_mensaje = fields.Text('Mensaje')
	preventivo_dias_antes = fields.Integer("Dias antes del vencimiento")
	preventivo_activar_segundo_envio = fields.Boolean("Activar segundo envio")
	preventivo_segundo_envio_dias_antes = fields.Integer("Dias antes del vencimiento")

	@api.one
	def test_connection(self):
		client = Client(self.account_sid, self.auth_token)
		message = client.messages.create(
			body=self.body_send_test,
			from_='whatsapp:'+self.number_send,
			to='whatsapp:'+self.number_received_test
		)

	@api.model
	def _cron_enviar_mensajes_whatsapp(self):
		cr = self.env.cr
		uid = self.env.uid

		print("Ejecutando WA send ***********************")
		fecha_actual = datetime.now()
		company_obj = self.pool.get('res.company')
		comapny_ids = company_obj.search(cr, uid, [])
		for _id in comapny_ids:
			company_id = company_obj.browse(cr, uid, _id)
			print("Ejecutando para company:: ", company_id.name)
			if len(company_id.wa_configuracion_id) > 0:
				wa_configuracion_id = company_id.wa_configuracion_id
				# Mensajes preventivos
				if wa_configuracion_id.preventivo_activar:
					# fecha_relativa = relativedelta.relativedelta(days=i+dias_no_habiles)
					# check_fecha = fecha_inicial + fecha_relativa
					primer_fecha = fecha_actual + relativedelta.relativedelta(days=wa_configuracion_id.preventivo_dias_antes)
					print("primer_fecha: ", primer_fecha)
					segunda_fecha = None
					if wa_configuracion_id.preventivo_activar_segundo_envio:
						segunda_fecha = fecha_actual + relativedelta.relativedelta(days=wa_configuracion_id.preventivo_segundo_envio_dias_antes)
					print("segunda_fecha:: ", segunda_fecha)
					cuota_obj = self.pool.get('financiera.prestamo.cuota')
					cuota_ids = cuota_obj.search(cr, uid, [
						('company_id', '=', company_id.id),
						('state', '=', 'activa'),
						'|', ('fecha_vencimiento', '=', primer_fecha),
						('fecha_vencimiento', '=', segunda_fecha)
						])
					print("cuota_id: ", cuota_ids)
					for _id in cuota_ids:
						cuota_id = cuota_obj.browse(cr, uid, _id)
						mensaje = wa_configuracion_id.preventivo_mensaje
						mensaje.replace('{cliente_nombre}', cuota_id.partner_id.name)
						print("Cliente: ", cuota_id.partner_id.name)
						print("to: ", cuota_id.partner_id.mobile)
						wa_message_values = {
							'partner_id': cuota_id.partner_id.id,
							'config_id': wa_configuracion_id.id,
							'from_': wa_configuracion_id.number_send,
							'to': cuota_id.partner_id.mobile or "1234567891",
							'body': mensaje,
						}
						message_id = self.env['financiera.wa.message'].create(wa_message_values)
						# if message.from_ != None and message.to != None and message.config_id != None:
						message_id.send()


WHATSAPP_PREFIX = '+549'

class FinancieraWhatsappMessage(models.Model):
	_name = 'financiera.wa.message'

	partner_id = fields.Many2one('res.partner', 'Cliente')
	config_id = fields.Many2one('financiera.wa.config', 'Configuracion WA')
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
		client = Client(self.config_id.account_sid, self.config_id.auth_token)
		print("to send: ", self.to)
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

# class FinancieraWhatsappSendWhen(models.Model):
# 	_name = 'financiera.wa.send.when'

# 	when_send_id = fields.Many2one('financiera.wa.message')
# 	send_type = fields.Selection([('dia_especifico', 'Dia especifico'), ('dia_antes_vencimiento', 'Dias antes del vencimiento'), ('dia_despues_vencimiento', 'Dias despues del vencimiento')], 'Tipo de envio')
# 	date = fields.Integer('Dia/Dias')
# 	company_id = fields.Many2one('res.company', 'Empresa', default=lambda self: self.env['res.company']._company_default_get('financiera.whatsapp.config'))

# class FinancieraWhatsappSendWho(models.Model):
# 	_name = 'financiera.wa.send.who'

# 	who_send_id = fields.Many2one('financiera.wa.message')
# 	send_who = fields.Selection([
# 		('cuotas_activa', 'Cliente con al menos N cuotas activas'),
# 		('cuotas_vencidas', 'Cliente con al menos N cuotas vencidas'),
# 		('cuotas_preventiva', 'Cliente con al menos N cuotas en preventiva y no mas de M cuotas vencidas')],
# 		'Tipo de envio')
# 	n = fields.Integer("N")
# 	m = fields.Integer("M")
# 	company_id = fields.Many2one('res.company', 'Empresa', default=lambda self: self.env['res.company']._company_default_get('financiera.whatsapp.config'))

# class FinancieraWhatsappMessageSend(models.Model):
# 	_name = 'financiera.wa.message.send'

# 	_order = 'id desc'
# 	partner_id = fields.Many2one('res.partner','Cliente')
# 	wa_message_id = fields.Many2one('financiera.wa.message', 'Estructura de mensaje')
# 	# state = fields.Selection([('enviado', 'Enviado'), ('recibido', 'Recibido'), ('rechazado', 'Rechazado')], 'Estado', default='enviado')
# 	body = fields.Text('Mensaje')
# 	company_id = fields.Many2one('res.company', 'Empresa', default=lambda self: self.env['res.company']._company_default_get('financiera.whatsapp.message'))

class ExtendsResCompany(models.Model):
	_inherit = 'res.company'

	wa_configuracion_id = fields.Many2one('financiera.wa.config', 'Configuracion sobre Whatsapp')
