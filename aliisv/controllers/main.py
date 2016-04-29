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
_ISVKEY= '...'

class AliIsv(SaasPortal):
    @http.route('/aliisv', type='http', auth="public")
    def ali_action(self, **post):
        # get current request url
        url = request.httprequest.url.encode('utf-8')
        query = urlparse.urlparse(url).query

        aliparams = dict([(k, v[0]) for k, v in urlparse.parse_qs(query).items()])
        is_valid = self.validate_url(aliparams)
        if not is_valid:
            _logger.error('aliisv: Could not validate url: %s', url)
            return json.dumps({"instanceId": 0})

        action = aliparams.get('action')
        if action is None:
            _logger.error('aliisv: No action in URL: %s', url)
            return json.dumps({"instanceId": 0})
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
            _logger.error('aliisv: No return values for action: %s', action)
            return json.dumps({"instanceId": 0})

        return values

    def validate_url(self, params):
        keys = params.keys()
        new_url = ''
        token = ''

        keys.sort()
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
        aliuid = param.get('aliUid')
        ali_orderbizid = param.get('orderBizId')
        ali_orderid = param.get('orderId')
        ali_skuid = param.get('skuId')
        ali_accountquantity = param.get('accountQuantity')
        ali_expiredon = param.get('expiredOn')
        ali_email = param.get('email')
        ali_mobile = param.get('mobile')

        client = request.env['saas_portal.client'].sudo().search([('ali_orderbizid', '=', ali_orderbizid)])
        if client:
            if client.ali_action == 'createInstance':
                return client.ali_json
            else:
                return json.dumps({"instanceId": 0})

        login = ali_email or aliuid + '@qiner.com.cn'
        pwd = self.generate_password(symbols=False)
        product = request.env['product.product'].sudo().search([('ali_skuid', '=', ali_skuid)])
        if not product:
            _logger.error('aliisv: No product with AliSkuId: %s', ali_skuid)
            return False

        attribute_value_obj = product.attribute_value_ids.filtered(lambda r: r.attribute_id.saas_code == 'MAX_USERS')
        max_user = attribute_value_obj and int(attribute_value_obj[0].saas_code_value) or 0
        plan = product.sudo().plan_id
        plan.max_users = max_user
        user = request.env['res.users'].sudo().search([('aliuid', '=', aliuid)])
        if not user:
           user = request.env['res.users'].sudo().create({'name': aliuid,
                                                        'login': login,
                                                        'password': pwd,
                                                        'email': ali_email,
                                                        'mobile': ali_mobile,
                                                        'aliuid': aliuid,
                                                        'customer': True,
                                                        })
        else:
            login = user.login

        partner_id = user.partner_id.id
        user_id = user.id
        support_team_id = request.env.ref('saas_portal.main_support_team').id
        try:
#            res = plan.create_new_database(dbname=dbname, user_id=user_id, partner_id=partner_id)
            res = plan.create_new_database(user_id=user_id, partner_id=partner_id, support_team_id=support_team_id,
                                           password=pwd, ali_orderbizid=ali_orderbizid)
        except MaximumDBException:
            url = request.env['ir.config_parameter'].sudo().get_param('saas_portal.page_for_maximumdb', '/')
            return werkzeug.utils.redirect(url)
        except MaximumTrialDBException:
            url = request.env['ir.config_parameter'].sudo().get_param('saas_portal.page_for_maximumtrialdb', '/')
            return werkzeug.utils.redirect(url)

        if not res:
            _logger.error('aliisv: create_new_database failed')
            return None

        client_id = res.get('client_id')
        client = request.env['saas_portal.client'].sudo().search([('client_id', '=', client_id)])
        #TODO: To add ali oder info as invoice lines
        # vals = {
        #     'saas_portal_client_id':client_id,
        #     'product_id': product.id,
        #     'plan_id': plan.id,
        #     'ali_orderid': ali_orderid,
        # }
        # request.env['account.invoice.line'].create(vals)
        if ali_accountquantity or ali_expiredon:
            if int(ali_accountquantity) > 1:
                client.max_users = ali_accountquantity
            if ali_expiredon:
                client.expiration_datetime = datetime.datetime.strptime(ali_expiredon,'%Y-%m-%d %H:%M:%S')
            client.send_params_to_client_db()

        hostname = urlparse.urlparse(res.get('url')).hostname
        values = json.dumps({
                "instanceId": res.get('client_id'),
                "appInfo": {
                    "frontEndUrl": 'http://' + hostname,
                    "adminUrl": 'http://' + hostname,
                    "username": login,
                    "password": pwd,
                },
                "info": {
                    "key1": "欢迎使用我们的产品,感谢您的信任!"
                }
            })
        #Gavin: update the action complete info to client record for later checking
        client.write({'ali_action': 'createInstance',
                      'ali_date': datetime.datetime.now(),
                      'ali_json': values})
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

        #Gavin: update the action complete info to client record for later checking
        client.write({'ali_action': 'renewInstance',
                      'ali_date': datetime.datetime.now(),
                      'ali_json': values})
        return values

    def expiredInstance(self, param=None):
        client = request.env['saas_portal.client'].sudo().search([('client_id', '=', param.get('instanceId'))])
        expired_datetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        client.expiration_datetime = expired_datetime

        client.send_params_to_client_db()
        values = json.dumps({
            "success": "True"
        })

        #Gavin: update the action complete info to client record for later checking
        client.write({'ali_action': 'expiredInstance',
                      'ali_date': datetime.datetime.now(),
                      'ali_json': values})
        return values

    def releaseInstance(self, param=None):
        client = request.env['saas_portal.client'].sudo().search([('client_id', '=', param.get('instanceId'))])
        client.delete_expired_databases()

        values = json.dumps({
            "success": "True"
        })

        #Gavin: update the action complete info to client record for later checking
        client.write({'ali_action': 'releaseInstance',
                      'ali_date': datetime.datetime.now(),
                      'ali_json': values})
        return values

    def bindDomain(self, param=None):
        return json.dumps({
            "success": "True"
        })

    def verify_aliisv(self, param=None):
        return json.dumps({
            "success": "True"
        })

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
