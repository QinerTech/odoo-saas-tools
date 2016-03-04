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
    ali_action = fields.Char(
        string='Ali Action',
        required=False,
        index=False,
        size=50,
        default=None,
        readonly=True
    )
    ali_date = fields.Datetime(
        string='Ali Action Time',
        required=False,
        index=False,
        size=50,
        default=None,
        readonly=True
    )
    ali_json = fields.Text(
        string='Json Response',
        required=False,
        index=False,
        default=None,
        readonly=True
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
