# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'AliIsv',
    'version': '1.0',
    'category': ' ',
    'summary': '',
    'author': 'Qiner Tech',
    'website': 'http://www.qineronline.com/',
    'description': """
""",
    'depends': [
        'sale', 'saas_portal_sale'
    ],
    'data': [
        'views/product_template.xml',
        'views/saas_portal.xml',
        'views/res_users.xml'
    ],

    'test': [

    ],
    'installable': True,
}
