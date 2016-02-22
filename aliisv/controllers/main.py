# __author__ = 'gaofeng'
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

domain = '127.0.0.1:8069'


class AliIsv(SaasPortal):
    @http.route('/allisv', type='http', auth="public")
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
        partner = request.env['res.partner'].sudo().search([('aliuid', '=', aliparams.get('aliUid'))])
        if not partner:
            #TODO: partner not exists
            partner.create({'name':'AliUser','user_id':001, 'aliuid':aliparams.get('aliUid')})

#        partner_id = partner.id
        partner_id = 1
#        user_id = partner.user_id.id
        user_id = 1
        support_team = request.env.ref('saas_portal.main_support_team')

        dbname = plan.generate_dbname()

        #
        # if not plan.free_subdomains:
        #     dbname = self.get_full_dbname(dbname)

        try:
            res = plan.create_new_database(dbname=dbname, user_id=user_id, partner_id=partner_id)
        except MaximumDBException:
            url = request.env['ir.config_parameter'].sudo().get_param('saas_portal.page_for_maximumdb', '/')
            return werkzeug.utils.redirect(url)
        except MaximumTrialDBException:
            url = request.env['ir.config_parameter'].sudo().get_param('saas_portal.page_for_maximumtrialdb', '/')
            return werkzeug.utils.redirect(url)

        return werkzeug.utils.redirect(res.get('url'))


##        values = self.get_return()

##        return values