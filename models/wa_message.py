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

	@api.one
	def set_message(self, mensaje, tipo_mensaje, cuota_id, partner_id, var1, var2, var3):
		if var1 != False:
			mensaje = mensaje.replace("{{1}}", var1)
		if var2 != False:
			mensaje = mensaje.replace("{{2}}", var2)
		if var3 != False:
			mensaje = mensaje.replace("{{3}}", var3)
		if tipo_mensaje == 'preventivo':
			mensaje = mensaje.replace("nombre_cliente", partner_id.name)
			mensaje = mensaje.replace("monto_cuota", str(cuota_id.saldo))
			date = datetime.strptime(cuota_id.fecha_vencimiento, '%Y-%m-%d')
			date = date.strftime('%d-%m-%Y')
			mensaje = mensaje.replace("fecha_vencimiento", date)
		elif tipo_mensaje == 'cuota_vencida':
			mensaje = mensaje.replace("nombre_cliente", partner_id.name)
			mensaje = mensaje.replace("monto_cuota", str(cuota_id.saldo))
			date = datetime.strptime(cuota_id.fecha_vencimiento, '%Y-%m-%d')
			date = date.strftime('%d-%m-%Y')
			mensaje = mensaje.replace("fecha_vencimiento", date)
		elif tipo_mensaje == 'notificacion_deuda':
			mensaje = mensaje.replace("nombre_cliente", partner_id.name)
			mensaje = mensaje.replace("monto_deuda", str(partner_id.saldo_cuotas_vencidas))
			mensaje = mensaje.replace("cantidad_cuotas", str(partner_id.cantidad_cuotas_vencidas))
		self.body = mensaje

	@api.one
	def set_message_code(self, mensaje, code):
		mensaje = mensaje.replace("{{1}}", code)
		self.body = mensaje

	@api.model
	def _cron_enviar_mensajes_whatsapp(self):
		cr = self.env.cr
		uid = self.env.uid
		fecha_actual = datetime.now()
		company_obj = self.pool.get('res.company')
		comapny_ids = company_obj.search(cr, uid, [])
		for _id in comapny_ids:
			company_id = company_obj.browse(cr, uid, _id)
			if len(company_id.wa_configuracion_id) > 0:
				wa_configuracion_id = company_id.wa_configuracion_id
				# Mensajes preventivos
				if wa_configuracion_id.preventivo_activar:
					primer_fecha = fecha_actual + relativedelta.relativedelta(days=wa_configuracion_id.preventivo_dias_antes)
					segunda_fecha = None
					if wa_configuracion_id.preventivo_activar_segundo_envio:
						segunda_fecha = fecha_actual + relativedelta.relativedelta(days=wa_configuracion_id.preventivo_segundo_envio_dias_antes)
					cuota_obj = self.pool.get('financiera.prestamo.cuota')
					cuota_ids = cuota_obj.search(cr, uid, [
						('company_id', '=', company_id.id),
						('state', '=', 'activa'),
						'|', ('fecha_vencimiento', '=', primer_fecha),
						('fecha_vencimiento', '=', segunda_fecha)
						])
					for _id in cuota_ids:
						cuota_id = cuota_obj.browse(cr, uid, _id)
						# mensaje = wa_configuracion_id.replace_values(mensaje, 'preventivo', cuota_id, cuota_id.partner_id,\
						# 	wa_configuracion_id.preventivo_var_1, wa_configuracion_id.preventivo_var_2, wa_configuracion_id.preventivo_var_3)
						wa_message_values = {
							'partner_id': cuota_id.partner_id.id,
							'config_id': wa_configuracion_id.id,
							'from_': wa_configuracion_id.number_send,
							'to': cuota_id.partner_id.mobile or WHATSAPP_NUMERO_NEUTRO,
							# 'body': mensaje,
							'tipo': 'Preventivo',
						}
						message_id = self.env['financiera.wa.message'].create(wa_message_values)
						message_id.set_message(
							wa_configuracion_id.preventivo_mensaje,
							'preventivo', 
							cuota_id, 
							cuota_id.partner_id,
							wa_configuracion_id.preventivo_var_1,
							wa_configuracion_id.preventivo_var_2,
							wa_configuracion_id.preventivo_var_3)
						message_id.send()
				# Mensaje cuota vencida
				if wa_configuracion_id.cuota_vencida_activar:
					primer_fecha = fecha_actual - relativedelta.relativedelta(days=wa_configuracion_id.cuota_vencida_dias_despues)
					segunda_fecha = None
					if wa_configuracion_id.cuota_vencida_activar_segundo_envio:
						segunda_fecha = fecha_actual - relativedelta.relativedelta(days=wa_configuracion_id.cuota_vencida_segundo_envio_dias_despues)
					cuota_obj = self.pool.get('financiera.prestamo.cuota')
					cuota_ids = cuota_obj.search(cr, uid, [
						('company_id', '=', company_id.id),
						('state', '=', 'activa'),
						'|', ('fecha_vencimiento', '=', primer_fecha),
						('fecha_vencimiento', '=', segunda_fecha)
						])
					for _id in cuota_ids:
						cuota_id = cuota_obj.browse(cr, uid, _id)
						wa_message_values = {
							'partner_id': cuota_id.partner_id.id,
							'config_id': wa_configuracion_id.id,
							'from_': wa_configuracion_id.number_send,
							'to': cuota_id.partner_id.mobile or WHATSAPP_NUMERO_NEUTRO,
							# 'body': mensaje,
							'tipo': 'Cuota vencida',
						}
						message_id = self.env['financiera.wa.message'].create(wa_message_values)
						message_id.set_message(
							wa_configuracion_id.cuota_vencida_mensaje,
							'cuota_vencida',
							cuota_id,
							cuota_id.partner_id,
							wa_configuracion_id.cuota_vencida_var_1,
							wa_configuracion_id.cuota_vencida_var_2,
							wa_configuracion_id.cuota_vencida_var_3)
						message_id.send()
				# Mensaje notificacion deuda
				if wa_configuracion_id.notificacion_deuda_activar:
					if fecha_actual.day == wa_configuracion_id.notificacion_deuda_dia\
					or fecha_actual.day == wa_configuracion_id.notificacion_deuda_dia_segundo_envio:
						partner_obj = self.pool.get('res.partner')
						partner_ids = partner_obj.search(cr, uid, [
							('company_id', '=', company_id.id),
							('cuota_ids.fecha_vencimiento', '<', fecha_actual),
							('cuota_ids.state', '=', 'activa')])
						for _id in partner_ids:
							partner_id = partner_obj.browse(cr, uid, _id)
							wa_message_values = {
								'partner_id': partner_id.id,
								'config_id': wa_configuracion_id.id,
								'from_': wa_configuracion_id.number_send,
								'to': partner_id.mobile,
								'tipo': 'Deuda',
							}
							message_id = self.env['financiera.wa.message'].create(wa_message_values)
							message_id.set_message(
								wa_configuracion_id.notificacion_deuda_mensaje,
								'notificacion_deuda',
								None,
								partner_id,
								wa_configuracion_id.notificacion_deuda_var_1,
								wa_configuracion_id.notificacion_deuda_var_2,
								wa_configuracion_id.notificacion_deuda_var_3)
							message_id.send()


class ExtendsMailMail(models.Model):
	_name = 'mail.mail'
	_inherit = 'mail.mail'

	@api.one
	def send(self, auto_commit=False, raise_exception=False):
		context = dict(self._context or {})
		active_model = context.get('active_model')
		sub_action = context.get('sub_action')
		active_id = context.get('active_id')
		super(ExtendsMailMail, self).send(auto_commit=False, raise_exception=False)
		if active_model == 'financiera.prestamo' and sub_action == 'tc_sent':
			cr = self.env.cr
			uid = self.env.uid
			prestamo_obj = self.pool.get('financiera.prestamo')
			prestamo_id = prestamo_obj.browse(cr, uid, active_id)
			wa_configuracion_id = prestamo_id.company_id.wa_configuracion_id
			if wa_configuracion_id.tc_codigo and prestamo_id.partner_id in self.recipient_ids:
				wa_message_values = {
					'partner_id': prestamo_id.partner_id.id,
					'config_id': wa_configuracion_id.id,
					'from_': wa_configuracion_id.number_send,
					'to': prestamo_id.partner_id.mobile,
					'tipo': 'Codigo TC',
				}
				message_id = self.env['financiera.wa.message'].create(wa_message_values)
				message_id.set_message_code(wa_configuracion_id.tc_mensaje, prestamo_id.email_tc_code)
				message_id.send()
				prestamo_id.email_tc_code_sent = True

