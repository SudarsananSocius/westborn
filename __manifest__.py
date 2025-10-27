# -*- encoding: utf-8 -*-
{
    "name": "Westborn",
    "version": "19.0.0.1",
    "category": "",
    "author": "",
    "license": 'AGPL-3',
    "description": """
    """,
    "depends": ['base','web', 'mail', 'sale', 'sale_management', 'sale_loyalty', 'loyalty', 'website_sale', 'website', 'website_sale_loyalty'],
    "data": [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rules.xml',
        'wizard/loyalty_generate_wizard_views.xml',
        'data/ewallet_mail_template.xml',
        'views/sale_order_views.xml',
        'views/product_template_views.xml',
        'views/website_product_template.xml',
        'views/website_sale_template_view.xml',
    ],
    'assets': {
        'web.assets_backend': [
        ],
        'web.assets_frontend': [
            'westborn/static/src/js/portal_price_dialogue.js',
            'westborn/static/src/xml/notification/credit_notification.xml'
        ],

    },
    'installable': True,
    'auto_install': False,
    'application': False,
}
