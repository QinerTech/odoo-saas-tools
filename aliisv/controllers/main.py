# __author__ = 'gaofeng'
# coding=utf-8

import openerp
from openerp.http import request
from openerp import http
import re
import urlparse
import werkzeug
from werkzeug.wrappers import Request, Response
from openerp.addons.saas_portal.controllers.main import SaasPortal
import json

domain = '127.0.0.1:8069'


class AliIsv(SaasPortal):
    @http.route('/allisv', type='http', auth="public")
    def get_url(self, **kw):
        # get current request url
        url = request.httprequest.url.decode('UTF-8')

#        url = 'http://www.qiner.com.cn/?p1=1&p2=2&p3=3&token=xxxxxx'
        query = urlparse.urlparse(url).query
        d = dict([(k, v[0]) for k, v in urlparse.parse_qs(query).items()])

        prod_id = self.get_prod(d.get('skuId'))
        plan_id = self.get_plan(prod_id)
        partner_id = self.get_parnter(d.get('aliUid'))

        rel= self.add_new_client(partner_id,prod_id,plan_id)


        values = self.get_return()

        return values

    def get_prod(self, skuId=None):
        #TODO: get product ID by skuId
        d = {'001':'1', '002':'2'}

        prod_id = d.get(skuId)

        return prod_id

    def get_parnter(self, aliUid):
        #TODO: check if it's a existing partner or create a new one
        d = {'001':'1', '002':'2'}

        partner_id = d.get(aliUid)

        return partner_id

    def get_plan(self, prod_id):
        #TODO: get plan Id from product
        d = {'001':'1', '002':'2'}

        plan_id = d.get(prod_id)

        return plan_id

    def add_new_client(self, parnter_id, prod_id, plan_id):
        #TODO: create a new client with params
        return 1

    def get_return(self):
        #TODO: encode json and return to ali
        values = json.dumps({
                    "instanceId": "1",
                    "hostInfo": {
                        "name": "linux server", "ip": "127.0.0.1",
                        "password": "root_password"
                            },
                    "appInfo": {
                        "frontEndUrl": "http://yourdomain.com/", "adminUrl": "http://yourdomain.com/admin", "username": "admin",
                        "password": "admin_password"
                    },
                    "info": {
                        "key1": "my custom info"
                    }
                })
        return values


