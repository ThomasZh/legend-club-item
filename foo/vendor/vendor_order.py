#!/usr/bin/env python
# _*_ coding: utf-8_*_
#
# Copyright 2016 planc2c.com
# dev@tripc2c.com
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.


import tornado.web
import logging
import uuid
import time
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../dao"))

from tornado.escape import json_encode, json_decode
from tornado.httpclient import HTTPClient
from tornado.httputil import url_concat

from global_const import *
from comm import AuthorizationHandler
from comm import timestamp_datetime
from comm import datetime_timestamp
from comm import timestamp_date
from comm import date_timestamp

from dao import budge_num_dao
from dao import category_dao
from dao import activity_dao
from dao import group_qrcode_dao
from dao import cret_template_dao
from dao import bonus_template_dao
from dao import apply_dao
from dao import order_dao
from dao import group_qrcode_dao
from dao import insurance_template_dao
from dao import vendor_member_dao
from dao import voucher_order_dao


class VendorOrdersMeAllHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        access_token = self.get_access_token()
        ops = self.get_ops_info()
        logging.info("get ops %r",ops)

        params = {"filter":"league","franchise_type":"供应商","page":1,"limit":20}
        url = url_concat(API_DOMAIN +"/api/leagues/"+ LEAGUE_ID +"/clubs",params)
        http_client = HTTPClient()
        headers={"Authorization":"Bearer "+access_token}
        response = http_client.fetch(url, method="GET", headers=headers)
        logging.info("got response.body=[%r]", response.body)
        data = json_decode(response.body)
        distributors = data['rs']['data']

        counter = self.get_counter(vendor_id)
        self.render('vendor/orders-me-all.html',
                vendor_id=vendor_id,
                ops=ops,
                API_DOMAIN=API_DOMAIN,
                access_token=access_token,
                counter=counter,
                distributors=distributors)


class VendorOrdersMeNoneHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        access_token = self.get_access_token()
        ops = self.get_ops_info()

        counter = self.get_counter(vendor_id)
        self.render('vendor/orders-me-none.html',
                vendor_id=vendor_id,
                ops=ops,
                API_DOMAIN=API_DOMAIN,
                access_token=access_token,
                counter=counter)


class VendorOrdersMeOtherHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        club_id = self.get_argument("club_id", "")

        access_token = self.get_access_token()
        ops = self.get_ops_info()

        counter = self.get_counter(vendor_id)
        self.render('vendor/orders-me-other.html',
                vendor_id=vendor_id,
                club_id=club_id,
                ops=ops,
                API_DOMAIN=API_DOMAIN,
                access_token=access_token,
                counter=counter)


class VendorOrdersMeOthersHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        access_token = self.get_access_token()
        ops = self.get_ops_info()

        counter = self.get_counter(vendor_id)
        self.render('vendor/orders-me-others.html',
                vendor_id=vendor_id,
                ops=ops,
                API_DOMAIN=API_DOMAIN,
                access_token=access_token,
                counter=counter)


class VendorOrdersOtherMeHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        club_id = self.get_argument("club_id", "")

        access_token = self.get_access_token()
        ops = self.get_ops_info()

        counter = self.get_counter(vendor_id)
        self.render('vendor/orders-other-me.html',
                vendor_id=vendor_id,
                club_id=club_id,
                ops=ops,
                API_DOMAIN=API_DOMAIN,
                access_token=access_token,
                counter=counter)


class VendorOrdersOthersMeHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        access_token = self.get_access_token()
        ops = self.get_ops_info()

        counter = self.get_counter(vendor_id)
        self.render('vendor/orders-others-me.html',
                vendor_id=vendor_id,
                ops=ops,
                API_DOMAIN=API_DOMAIN,
                access_token=access_token,
                counter=counter)


class VendorApplyListHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        access_token = self.get_access_token()
        ops = self.get_ops_info()

        counter = self.get_counter(vendor_id)
        self.render('vendor/applys.html',
                vendor_id=vendor_id,
                ops=ops,
                API_DOMAIN=API_DOMAIN,
                access_token=access_token,
                counter=counter)


class VendorVoucherOrderListHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        access_token = self.get_access_token()

        ops = self.get_ops_info()

        before = time.time()
        _array = voucher_order_dao.voucher_order_dao().query_pagination_by_vendor(vendor_id, before, PAGE_SIZE_LIMIT);
        for _voucher_order in _array:
            _voucher_order['voucher_price'] = float(_voucher_order['voucher_price'])/100
            _voucher_order['voucher_amount'] = float(_voucher_order['voucher_amount'])/100
            _voucher_order['create_time'] = timestamp_datetime(_voucher_order['create_time'])

        counter = self.get_counter(vendor_id)
        self.render('vendor/voucher-orders.html',
                vendor_id=vendor_id,
                ops=ops,
                API_DOMAIN=API_DOMAIN,
                access_token=access_token,
                counter=counter,
                voucher_orders= _array)


class VendorOrderInfoHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id, order_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got order_id %r in uri", order_id)
        access_token = self.get_access_token()

        ops = self.get_ops_info()
        #
        # order_index = self.get_order_index(order_id)
        # logging.info("got order_index %r in uri", order_index)

        order = self.get_symbol_object(order_id)
        logging.info("got order %r in uri", order)

        for base_fee in order['base_fees']:
            # 价格转换成元
            order['activity_amount'] = float(base_fee['fee']) / 100

        for coupon in order['coupon']['datas']:
            # 价格转换成元
            coupon['expired_at'] = timestamp_date(coupon['expired_at'])
            coupon['amount'] = float(coupon['amount']) / 100
            if coupon['_status'] == 1:
                coupon['_status'] = u"下单"
            elif coupon['_status'] == 2:
                coupon['_status'] = u"已使用"

        if not order.has_key('activity_amount'):
            order['activity_amount'] = 0

        for _voucher in order['vouchers']:
            # 价格转换成元
            _voucher['fee'] = float(_voucher['fee']) / 100

        for ext_fee in order['ext_fees']:
            # 价格转换成元
            ext_fee['fee'] = float(ext_fee['fee']) / 100

        for insurance in order['insurances']:
            # 价格转换成元
            insurance['fee'] = float(insurance['fee']) / 100
        order['create_time'] = timestamp_datetime(order['create_time'])
        order['amount'] = float(order['amount']) / 100
        order['points_used'] = float(order['points_used']) / 100
        order['shipping_cost'] = float(order['shipping_cost']) / 100
        # order['actual_payment'] = float(order['actual_payment']) / 100
        # order['amount'] = float(order['amount']) / 100

        # params = {"filter":"order", "order_id":order_id, "page":1, "limit":20}
        # url = url_concat(API_DOMAIN + "/api/applies", params)
        # http_client = HTTPClient()
        # headers = {"Authorization":"Bearer " + access_token}
        # response = http_client.fetch(url, method="GET", headers=headers)
        # logging.info("got response.body %r", response.body)
        # data = json_decode(response.body)
        # rs = data['rs']
        applies = order['items']
        logging.info("get applies %r",applies)
        for applys in applies:
            applys['total_fee'] = float(applys['amount'])*float(applys['quantity']) / 100
            applys['amount'] = float(applys['amount']) / 100

        params = {"filter":"league","franchise_type":"供应商","page":1,"limit":20}
        url = url_concat(API_DOMAIN +"/api/leagues/"+ LEAGUE_ID +"/clubs",params)
        http_client = HTTPClient()
        headers={"Authorization":"Bearer "+access_token}
        response = http_client.fetch(url, method="GET", headers=headers)
        logging.info("got response.body=[%r]", response.body)
        data = json_decode(response.body)
        distributors = data['rs']['data']

        #
        # for _apply in applies:
        #     # 下单时间，timestamp -> %m月%d 星期%w
        #     _apply['create_time'] = timestamp_datetime(float(_apply['create_time']))
        #     if _apply['gender'] == 'male':
        #         _apply['gender'] = u'男'
        #     else:
        #         _apply['gender'] = u'女'

        counter = self.get_counter(vendor_id)
        self.render('vendor/order-detail.html',
                vendor_id=vendor_id,
                order_id = order_id,
                API_DOMAIN=API_DOMAIN,
                ops=ops,
                access_token=access_token,
                counter=counter,
                order=order,
                applies=applies,
                distributors=distributors)

# 优惠券
class VendorOrdersCouponsHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        ops = self.get_ops_info()

        access_token = self.get_access_token()
        logging.info("GET access_token %r", access_token)

        # params = {"page":1,"limit":200}
        # url = url_concat(API_DOMAIN + "/api/coupons",params)
        # http_client = HTTPClient()
        # headers = {"Authorization":"Bearer " + access_token}
        # response = http_client.fetch(url, method="GET", headers=headers)
        # logging.info("got response.body %r", response.body)
        # data = json_decode(response.body)
        # coupons = data['rs']

        counter = self.get_counter(vendor_id)
        self.render('vendor/order-coupon.html',
                vendor_id=vendor_id,
                access_token=access_token,
                API_DOMAIN=API_DOMAIN,
                LEAGUE_ID=LEAGUE_ID,
                ops=ops,
                counter=counter)


# 生成优惠券
class VendorCouponsCreateHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        ops = self.get_ops_info()

        counter = self.get_counter(vendor_id)
        self.render('vendor/create-coupons.html',
                vendor_id=vendor_id,
                ops=ops,
                counter=counter)

    @tornado.web.authenticated  # if no session, redirect to login page
    def post(self,vendor_id):
        logging.info("GET vendor_id %r", vendor_id)

        access_token = self.get_access_token()
        logging.info("GET access_token %r", access_token)

        ops = self.get_ops_info()

        coupon_seq = self.get_argument("coupon-seq", "")
        logging.info("got coupon_seq", coupon_seq)
        coupon_fee = self.get_argument("coupon-fee", "")
        logging.info("got coupon_fee", coupon_fee)
        coupon_fee = int(float(coupon_fee) * 100)
        logging.info("got coupon_fee", coupon_fee)
        coupon_time = self.get_argument("coupon-time", "")
        logging.info("got coupon_time", coupon_time)
        coupon_time = date_timestamp(coupon_time)
        coupon_num = self.get_argument("coupon-num", "")
        logging.info("got coupon_num", coupon_num)

        coupons = {'_seq':coupon_seq, 'num':coupon_num, 'amount':coupon_fee, 'expired_at':coupon_time, 'club_id':vendor_id}

        url = API_DOMAIN+"/api/coupons"
        http_client = HTTPClient()
        headers={"Authorization":"Bearer "+access_token}
        _json = json_encode(coupons)
        logging.info("request %r body %r", url, _json)
        response = http_client.fetch(url, method="POST", headers=headers, body=_json)
        logging.info("got response %r", response.body)

        self.redirect('/vendors/' + vendor_id + '/coupons')
