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
import datetime
import hashlib


import logging
_logger = logging.getLogger(__name__)

DEFAULT_LENGTH = 8
_ISVKEY= 'AsQbqR8QyreVJPAlbLzS8i6H07nNiACm0wxdSoJuFOfvBBPrjk5YYhtXAVHhfFbe'

class AliIsv(SaasPortal):
    @http.route('/aliisv', type='http', auth="public")
    def get_url(self, **post):
        # get current request url
        url = request.httprequest.url.encode('utf-8')
        query = urlparse.urlparse(url).query

        json_false = json.dumps({
                "instanceId": 0
                })

        aliparams = dict([(k, v[0]) for k, v in urlparse.parse_qs(query).items()])
        is_valid = self.validate_url(aliparams)
        if not is_valid:
            _logger.error('Could not validate url: %s', url)
            return json_false

        action = aliparams.get('action')
        if action is None:
            _logger.error('No action in URL: %s', url)
            return json_false
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
        elif action == 'verify':
            values = self.verify_aliisv(aliparams)
        else:
            values = None

        if not values:
            _logger.error('No return values for action: %s', action)
            return json_false

        return values

    def validate_url(self, params):
        keys = params.keys()
        keys.sort()

        new_url = ''
        token = ''
        for i in keys:
            if i == 'token':
                token = params.get(i)
            else:
                new_url += i + '=' + params.get(i) + '&'

        full_url = new_url + 'key=' + _ISVKEY

        m = hashlib.md5()
        m.update(full_url)
        md5 = m.hexdigest()

        if token == md5:
            return True
        else:
            return False


    def createInstance(self, param=None):
        # param referece to ali API manual

        aliUid = param.get('aliUid')
        orderBizId = param.get('orderBizId')
        orderId = param.get('orderId')
        skuId = param.get('skuId')
        accountQuantity = param.get('accountQuantity')
        expiredOn = param.get('expiredOn')
        email = param.get('email')
        mobile = param.get('mobile')

        login = email or aliUid + '@qiner.com.cn'
        pwd = self.generate_password(symbols=False)

        product = request.env['product.product'].sudo().search([('aliskuid', '=', skuId)])
        if not product:
            _logger.error('No product with AliSkuId: %s', skuId)
            return False

        plan = product.sudo().plan_id

        user = request.env['res.users'].sudo().search([('aliuid', '=', aliUid)])
        if not user:
           user = request.env['res.users'].sudo().create({'name': aliUid,
                                                        'login': login,
                                                        'password': pwd,
                                                        'email': email,
                                                        'mobile': mobile,
                                                        'aliuid': aliUid,
                                                        'customer': True,
                                                        })

        partner_id = user.partner_id.id
        user_id = user.id
        support_team_id = request.env.ref('saas_portal.main_support_team').id

        try:
#            res = plan.create_new_database(dbname=dbname, user_id=user_id, partner_id=partner_id)
            res = plan.create_new_database(user_id=user_id, partner_id=partner_id, password=pwd,
                                           support_team_id=support_team_id)
        except MaximumDBException:
            url = request.env['ir.config_parameter'].sudo().get_param('saas_portal.page_for_maximumdb', '/')
            return werkzeug.utils.redirect(url)
        except MaximumTrialDBException:
            url = request.env['ir.config_parameter'].sudo().get_param('saas_portal.page_for_maximumtrialdb', '/')
            return werkzeug.utils.redirect(url)

        if not res:
            _logger.error('create_new_database failed')
            return None

        client_id = res.get('client_id')

        if accountQuantity or expiredOn:
            client = request.env['saas_portal.client'].sudo().search([('client_id', '=', client_id)])
            if accountQuantity:
                client.max_users = accountQuantity
            if expiredOn:
                client.expiration_datetime = datetime.datetime.strptime(expiredOn,'%Y-%m-%d %H:%M:%S')
            client.send_params_to_client_db()

        hostname = urlparse.urlparse(res.get('url')).hostname
        values = json.dumps({
                "instanceId": res.get('client_id'),
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

        client = request.env['saas_portal.client'].sudo().search([('client_id', '=', param.get('instanceId'))])
        expiration_time_to_update = datetime.datetime.strptime(param.get('expiredOn'),'%Y-%m-%d %H:%M:%S')
        client.expiration_datetime = expiration_time_to_update

        # update database
        client.send_params_to_client_db()

        values = json.dumps({
            "success": "True"
        })

        return values

    def expiredInstance(self, param=None):
        client = request.env['saas_portal.client'].sudo().search([('client_id', '=', param.get('instanceId'))])
        expired_datetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        client.expiration_datetime = expired_datetime

        client.send_params_to_client_db()
        values = json.dumps({
            "success": "True"
        })

        return values

    def releaseInstance(self, param=None):
        client = request.env['saas_portal.client'].sudo().search([('client_id', '=', param.get('instanceId'))])
        client.delete_expired_databases()

        values = json.dumps({
            "success": "True"
        })

        return values



    def bindDomain(self, param=None):

        return 0

    def verify_aliisv(self, param=None):
        return False

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
