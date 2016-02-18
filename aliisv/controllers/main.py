# __author__ = 'gaofeng'
# coding=utf-8

import openerp
from openerp.http import request
from openerp import http
import re
import urlparse

from werkzeug.wrappers import Request, Response

domain = '127.0.0.1:8069'


class AliIsv(http.Controller):
    @http.route('/abc', type='http', auth="public")
    def deal_url(self, **kw):
        # get current request url
        params = request.httprequest.url.decode('UTF-8')

        url = 'http://www.qiner.com.cn/?p1=1&p2=2&p3=3&token=xxxxxx'
        query = urlparse.urlparse(url).query
        d = dict([(k, v[0]) for k, v in urlparse.parse_qs(query).items()])

        if d['p1'] == '1':
            print("create_instance")

        elif d['p2'] == '2':
            print (d)

        return 'OK!!!'
