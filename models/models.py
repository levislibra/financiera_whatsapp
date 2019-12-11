# -*- coding: utf-8 -*-

from openerp import models, fields, api
# Download the helper library from https://www.twilio.com/docs/python/install
from twilio.rest import Client

class FinancieraWhatsappConfig(models.Model):
	_name = 'financiera.wa.config'

	name = fields.Char('Nombre')
	account_sid = fields.Char('SID de cuenta')
	auth_token = fields.Char('Token')
	company_id = fields.Many2one('res.company', 'Empresa', default=lambda self: self.env['res.company']._company_default_get('financiera.whatsapp.config'))



class ExtendsResCompany(models.Model):
	_inherit = 'res.company'

	wa_configuracion_id = fields.Many2one('financiera.wa.config', 'Configuracion sobre Whatsapp')
