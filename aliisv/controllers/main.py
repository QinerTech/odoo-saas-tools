# coding=utf-8

import openerp
from openerp import SUPERUSER_ID, exceptions
from openerp.addons.saas_base.exceptions import MaximumDBException, MaximumTrialDBException
from openerp.http import request
from openerp import http
import re
import urlparse
import werkzeug
from werkzeug.wrappers import Request, Response
from openerp.addons.saas_portal.controllers.main import SaasPortal

import json
import string
import random

import logging
_logger = logging.getLogger(__name__)

DEFAULT_LENGTH = 8

class AliIsv(SaasPortal):
    @http.route('/aliisv', type='http', auth="public")
    def get_url(self, **post):
        # get current request url
        url = request.httprequest.url.decode('UTF-8')

#        url = 'http://www.qiner.com.cn/?p1=1&p2=2&p3=3&token=xxxxxx'
        query = urlparse.urlparse(url).query
        aliparams = dict([(k, v[0]) for k, v in urlparse.parse_qs(query).items()])

        action = aliparams.get('action')
        if action is None:
            _logger.error('No action in URL: %s', url)
            return False
        elif action == 'createInstance':
            values = self.createInstance(aliparams)
        elif action == 'renewInstance':
            values = self.renewInstance(aliparams)
        elif action == 'expiredInstance':
            values = self.expiredInstance(aliparams)
        elif action == 'releaseInstance':
            values = self.releaseInstance(aliparams)
        elif action == 'bindDomain':
            values = self.bindDomain(aliparams)

        if not values:
            _logger.error('No return values for action: %s', action)
            return False

        return values

    def createInstance(self, param=None):
        # param should be a diction
        product = request.env['product.product'].sudo().search([('aliskuid', '=', param.get('skuId'))])
        if not product:
            _logger.error('No product with AliSkuId: %s', param.get('skuId'))
            return False

        plan = product.sudo().plan_id

        login = param.get('email') or param.get('aliUid') + '@qiner.com.cn'
        pwd = self.generate_password(symbols=False)

        user = request.env['res.users'].sudo().search([('aliuid', '=', param.get('aliUid'))])
        if not user:
           user = request.env['res.users'].sudo().create({'name':param.get('aliUid'),
                                                        'login': login,
                                                        'password': pwd,
                                                        'email': param.get('email'),
                                                        'mobile': param.get('mobile'),
                                                        'aliuid':param.get('aliUid'),
                                                        'customer': True,
                                                        })

        partner_id = user.partner_id.id
        user_id = user.id
        support_team = request.env.ref('saas_portal.main_support_team')

        try:
#            res = plan.create_new_database(dbname=dbname, user_id=user_id, partner_id=partner_id)
            res = plan.create_new_database(user_id=user_id, partner_id=partner_id, password=pwd)
        except MaximumDBException:
            url = request.env['ir.config_parameter'].sudo().get_param('saas_portal.page_for_maximumdb', '/')
            return werkzeug.utils.redirect(url)
        except MaximumTrialDBException:
            url = request.env['ir.config_parameter'].sudo().get_param('saas_portal.page_for_maximumtrialdb', '/')
            return werkzeug.utils.redirect(url)

        if not res:
            _logger.error('create_new_database failed')
            return None

        hostname = urlparse.urlparse(res.get('url')).hostname
        values = json.dumps({
                "instanceId": res.get('id'),
                "hostInfo": {
                    "name": res.get('client_id'),
                    "ip": "127.0.0.1",
                    "password": "root_password"
                },
                "appInfo": {
                    "frontEndUrl": 'http://' + hostname,
                    "adminUrl": "http://www.qiner.com.cn/",
                    "username": login,
                    "password": pwd,
                },
                "info": {
                    "key1": "my custom info"
                }
            })

        return values

    def renewInstance(self, param=None):

        return 0

    def expiredInstance(self, param=None):

        return 0

    def releaseInstance(self, param=None):

        return 0

    def bindDomain(self, param=None):

        return 0

    def generate_password(self, length=DEFAULT_LENGTH, capitals=True, numerals=True, symbols=True):
        """
        Generate a random password of specified length
        :param length: Length of generated password
        :param capitals: Include CAPITAL letters in the password
        :param numerals: Include NUMERALS in the password
        :param symbols: Include SYMBOLS in the password
        """

        chars = string.lowercase
        if capitals:
            chars += string.uppercase
        if numerals:
            chars += string.digits
        if symbols:
            chars += "@#$%^&?*():;-="

        password = []
        for i in xrange(length):
            index = random.SystemRandom().randrange(len(chars))
            password.append(chars[index])
        return "".join(password)
