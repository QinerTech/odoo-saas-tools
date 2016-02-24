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

domain = 'qiner.com.cn'


class AliIsv(SaasPortal):
    @http.route('/aliisv', type='http', auth="public")
    def get_url(self, **post):
        # get current request url
        url = request.httprequest.url.decode('UTF-8')

#        url = 'http://www.qiner.com.cn/?p1=1&p2=2&p3=3&token=xxxxxx'
        query = urlparse.urlparse(url).query
        aliparams = dict([(k, v[0]) for k, v in urlparse.parse_qs(query).items()])

        product = request.env['product.template'].sudo().search([('aliskuid', '=', aliparams.get('skuId'))])
        if not product:
            #TODO: product not exists
            return 0
        plan = product.sudo().plan_id

        ulogin = aliparams.get('email') or aliparams.get('aliUid') + '@' + domain
        upassword = '1'

        user = request.env['res.users'].sudo().search([('aliuid', '=', aliparams.get('aliUid'))])
        if not user:
           user = request.env['res.users'].sudo().create({'name':aliparams.get('aliUid'),
                                                           'login': ulogin,
                                                           'password': upassword,
                                                           'email': aliparams.get('email'),
                                                           'mobile': aliparams.get('mobile'),
                                                           'aliuid':aliparams.get('aliUid'),
                                                           'customer': True,
                                                              })

        partner_id = user.partner_id.id
        user_id = user.id
        support_team = request.env.ref('saas_portal.main_support_team')

        try:
#            res = plan.create_new_database(dbname=dbname, user_id=user_id, partner_id=partner_id)
            res = plan.create_new_database(user_id=user_id, partner_id=partner_id)
        except MaximumDBException:
            url = request.env['ir.config_parameter'].sudo().get_param('saas_portal.page_for_maximumdb', '/')
            return werkzeug.utils.redirect(url)
        except MaximumTrialDBException:
            url = request.env['ir.config_parameter'].sudo().get_param('saas_portal.page_for_maximumtrialdb', '/')
            return werkzeug.utils.redirect(url)

        #TODO: encode json and return to ali
        if not res:
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
                    "frontEndUrl": "http://www.qiner.com.cn/",
                    "adminUrl": 'http://' + hostname,
                    "username": user.login,
                    "password": upassword,
                },
                "info": {
                    "key1": "my custom info"
                }
            })

        return values

    def creatInstance(self, param=None):

        return 0

    def renewInstance(self, param=None):

        return 0

    def expiredInstance(self, param=None):

        return 0

    def releaseInstance(self, param=None):

        return 0

    def bindDomain(self, param=None):

        return 0

    def generate_login(self, param=None):
        #TODO: check existing user or not
        if param is not None:
            login = param + '@' + domain

        return login

    def generate_password(self, user=None):
        if user is not None:
            password = '1'

        return password