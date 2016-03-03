# coding=utf-8

from openerp import models, fields


class ResUsersAliIsv(models.Model):
    _inherit = 'res.users'

    aliuid = fields.Char(
        string= 'Aliyun Uid',
        required = False,
        index= False,
        size= 50,
        default= None,
    )
