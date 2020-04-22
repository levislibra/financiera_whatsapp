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

	# Notificacion Codigo Terminos y condiciones
	tc_codigo = fields.Boolean("Activar mensaje con codigo de terminos y condiciones.")
	tc_mensaje = fields.Text('Mensaje', help='Usar {{1}} como codigo.')

	@api.one
	def test_connection(self):
		client = Client(self.account_sid, self.auth_token)
		message = client.messages.create(
			body=self.body_send_test,
			from_='whatsapp:'+self.number_send,
			to='whatsapp:'+self.number_received_test
		)

class ExtendsResCompany(models.Model):
	_inherit = 'res.company'

	wa_configuracion_id = fields.Many2one('financiera.wa.config', 'Configuracion sobre Whatsapp')
