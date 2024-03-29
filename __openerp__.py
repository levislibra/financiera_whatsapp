# -*- coding: utf-8 -*-
{
    'name': "Whatsapp Notificaiones para Financiera",

    'summary': """
        Notificaiones por medio de Whatsapp con posibilidad de respuestas.""",

    'description': """
        Moudulo Whatsapp Notificaciones para Financiera.
        * Notificaciones para cobranza preventiva.
        * Notificaciones de mora.
        * Notificaciones de punitorios.
        * Validacion de numero de movil.
    """,

    'author': "Librasoft",
    'website': "https://libra-soft.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'finance',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'financiera_prestamos', 'financiera_cobranza_mora'],

    # always loaded
    'data': [
        'security/user_groups.xml',
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/wa_configuracion.xml',
        'views/wa_message.xml',
        'views/extends_res_company.xml',
				'views/extends_res_partner.xml',
				'views/extends_financiera_prestamo.xml',
        'data/ir_cron.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}