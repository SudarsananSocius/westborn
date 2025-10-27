# -*- encoding: utf-8 -*-
{
    "name": "BrightPath-UK",
    "version": "19.0.0.1",
    "category": "",
    "author": "",
    "license": 'AGPL-3',
    "description": """
    """,
    "depends": ['base','web', 'mail', 'sale', 'sale_management', 'sale_loyalty', 'loyalty', 'website_sale', 'website', 'website_sale_loyalty'],
    "data": [
        'security/security.xml',
        'data/cron.xml',
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
            'Brightpath_UK/static/src/js/portal_price_dialogue.js',
            'Brightpath_UK/static/src/xml/notification/credit_notification.xml'
        ],

    },
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'auto_install': False,
    'application': False,
}
