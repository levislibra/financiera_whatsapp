# -*- coding: utf-8 -*-

from openerp import models, fields, api
from datetime import datetime, timedelta
from dateutil import relativedelta
# Download the helper library from https://www.twilio.com/docs/python/install
from twilio.rest import Client

WHATSAPP_NUMERO_NEUTRO = "0000000000"
WHATSAPP_PREFIX = '+549'

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
	preventivo_var_1 = fields.Selection([
		('nombre_cliente', 'Nombre de cliente'),
		('monto_cuota', 'Monto de la cuota'),
		('fecha_vencimiento', 'Fecha de vencimiento')],
		'Variable 1')
	preventivo_var_2 = fields.Selection([
		('nombre_cliente', 'Nombre de cliente'),
		('monto_cuota', 'Monto de la cuota'),
		('fecha_vencimiento', 'Fecha de vencimiento')],
		'Variable 2')
	preventivo_var_3 = fields.Selection([
		('nombre_cliente', 'Nombre de cliente'),
		('monto_cuota', 'Monto de la cuota'),
		('fecha_vencimiento', 'Fecha de vencimiento')],
		'Variable 3')
	# Aviso cuota vencida
	cuota_vencida_activar = fields.Boolean("Activar mensaje de cuota vencida")
	cuota_vencida_mensaje = fields.Text('Mensaje')
	cuota_vencida_dias_despues = fields.Integer("Dias despues del vencimiento")
	cuota_vencida_activar_segundo_envio = fields.Boolean("Activar segundo envio")
	cuota_vencida_segundo_envio_dias_despues = fields.Integer("Dias despues del vencimiento")
	cuota_vencida_var_1 = fields.Selection([
		('nombre_cliente', 'Nombre de cliente'),
		('monto_cuota', 'Monto de la cuota'),
		('fecha_vencimiento', 'Fecha de vencimiento')],
		'Variable 1')
	cuota_vencida_var_2 = fields.Selection([
		('nombre_cliente', 'Nombre de cliente'),
		('monto_cuota', 'Monto de la cuota'),
		('fecha_vencimiento', 'Fecha de vencimiento')],
		'Variable 2')
	cuota_vencida_var_3 = fields.Selection([
		('nombre_cliente', 'Nombre de cliente'),
		('monto_cuota', 'Monto de la cuota'),
		('fecha_vencimiento', 'Fecha de vencimiento')],
		'Variable 3')
	# Aviso notificacion deuda
	notificacion_deuda_activar = fields.Boolean("Activar mensaje de notificacion de deuda")
	notificacion_deuda_mensaje = fields.Text('Mensaje')
	notificacion_deuda_dia = fields.Integer("Dia del mes")
	notificacion_deuda_activar_segundo_envio = fields.Boolean("Activar segundo envio")
	notificacion_deuda_dia_segundo_envio = fields.Integer("Dia del mes")
	notificacion_deuda_var_1 = fields.Selection([
		('nombre_cliente', 'Nombre de cliente'),
		('monto_deuda', 'Monto de la deuda'),
		('cantidad_cuotas', 'Cantidad de cuotas')],
		'Variable 1')
	notificacion_deuda_var_2 = fields.Selection([
		('nombre_cliente', 'Nombre de cliente'),
		('monto_deuda', 'Monto de la deuda'),
		('cantidad_cuotas', 'Cantidad de cuotas')],
		'Variable 2')
	notificacion_deuda_var_3 = fields.Selection([
		('nombre_cliente', 'Nombre de cliente'),
		('monto_deuda', 'Monto de la deuda'),
		('cantidad_cuotas', 'Cantidad de cuotas')],
		'Variable 3')


	@api.one
	def test_connection(self):
		client = Client(self.account_sid, self.auth_token)
		message = client.messages.create(
			body=self.body_send_test,
			from_='whatsapp:'+self.number_send,
			to='whatsapp:'+self.number_received_test
		)

	def replace_values(self, mensaje, tipo_mensaje, cuota_id, partner_id, var1, var2, var3):
		if var1 != False:
			mensaje = mensaje.replace("{{1}}", var1)
		if var2 != False:
			mensaje = mensaje.replace("""{{2}}""", var2)
		if var3 != False:
			mensaje = mensaje.replace('{{3}}', var3)
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
		return mensaje

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
						mensaje = wa_configuracion_id.preventivo_mensaje
						mensaje = wa_configuracion_id.replace_values(mensaje, 'preventivo', cuota_id, cuota_id.partner_id,\
							wa_configuracion_id.preventivo_var_1, wa_configuracion_id.preventivo_var_2, wa_configuracion_id.preventivo_var_3)
						wa_message_values = {
							'partner_id': cuota_id.partner_id.id,
							'config_id': wa_configuracion_id.id,
							'from_': wa_configuracion_id.number_send,
							'to': cuota_id.partner_id.mobile or WHATSAPP_NUMERO_NEUTRO,
							'body': mensaje,
							'tipo': 'Preventivo',
						}
						message_id = self.env['financiera.wa.message'].create(wa_message_values)
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
						mensaje = wa_configuracion_id.cuota_vencida_mensaje
						mensaje = wa_configuracion_id.replace_values(mensaje, 'cuota_vencida', cuota_id, cuota_id.partner_id,\
							wa_configuracion_id.cuota_vencida_var_1, wa_configuracion_id.cuota_vencida_var_2, wa_configuracion_id.cuota_vencida_var_3)
						wa_message_values = {
							'partner_id': cuota_id.partner_id.id,
							'config_id': wa_configuracion_id.id,
							'from_': wa_configuracion_id.number_send,
							'to': cuota_id.partner_id.mobile or WHATSAPP_NUMERO_NEUTRO,
							'body': mensaje,
							'tipo': 'Cuota vencida',
						}
						message_id = self.env['financiera.wa.message'].create(wa_message_values)
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
							mensaje = wa_configuracion_id.notificacion_deuda_mensaje
							mensaje = wa_configuracion_id.replace_values(mensaje, 'notificacion_deuda', None, partner_id,\
								wa_configuracion_id.notificacion_deuda_var_1, wa_configuracion_id.notificacion_deuda_var_2, wa_configuracion_id.notificacion_deuda_var_3)
							wa_message_values = {
								'partner_id': cuota_id.partner_id.id,
								'config_id': wa_configuracion_id.id,
								'from_': wa_configuracion_id.number_send,
								'to': cuota_id.partner_id.mobile or WHATSAPP_NUMERO_NEUTRO,
								'body': mensaje,
								'tipo': 'Cuota vencida',
							}
							message_id = self.env['financiera.wa.message'].create(wa_message_values)
							message_id.send()

class FinancieraWhatsappMessage(models.Model):
	_name = 'financiera.wa.message'

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


class ExtendsResCompany(models.Model):
	_inherit = 'res.company'

	wa_configuracion_id = fields.Many2one('financiera.wa.config', 'Configuracion sobre Whatsapp')
