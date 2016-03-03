# -*- coding: utf-8 -*-
from openerp import models, fields, api
from datetime import datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class SaasPortalClient(models.Model):
    _inherit = 'saas_portal.client'

    ali_orderbizid =  fields.Char(
        string='Ali OrderBizId',
        required=False,
        index=False,
        size=50,
        default=None
    )

class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    ali_orderid =  fields.Char(
        string='Ali OrderId',
        required=False,
        index=False,
        size=50,
        default=None
    )
