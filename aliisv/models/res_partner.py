# coding=utf-8

from openerp import models, fields


class ResParnterAliIsv(models.Model):
    _inherit = 'res.partner'

    aliuid = fields.Char(
        string = 'Aliyun Uid',
        required = False,
        index = False,
        size = 50,
        default = None,
    )
