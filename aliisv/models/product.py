# coding=utf-8

from openerp import models, fields


class ProductTemplateAliIsv(models.Model):
    _inherit = 'product.product'

    ali_skuid = fields.Char(
        string = 'Ali skuId',
        required = False,
        index = False,
        size = 50,
        default = None
    )

#
# class ProductAttributeAliIsv(models.Model):
#     _inherit = "product.attribute"
#
#     saas_code = fields.Selection('_get_saas_codes')
#
#     def _get_saas_codes(self):
#         return [('SUBSCRIPTION_PERIOD', 'SUBSCRIPTION_PERIOD'),
#                 ('MAX_USERS', 'MAX_USERS'),
#                 ('INSTALL_MODULES', 'INSTALL_MODULES'),
#                 ('STORAGE_LIMIT', 'STORAGE_LIMIT')]
#     # saas_code = fields.Char('SaaS code', help='''Possible codes:
#     # * SUBSCRIPTION_PERIOD
#     # * MAX_USERS
#     # * INSTALL_MODULES
#     # * STORAGE_LIMIT
#     # ''')
#
#
# class ProductAttributeValueAliIsv(models.Model):
#     _inherit = "product.attribute.value"
#
#     saas_code_value = fields.Char('SaaS code value')
