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
import xlwt
import json as JSON # 启用别名，不会跟方法里的局部变量混淆
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../dao"))

from tornado.escape import json_encode, json_decode
from tornado.httpclient import HTTPClient
from tornado.httputil import url_concat
from bson import json_util

from comm import *


from dao import budge_num_dao
from dao import category_dao
from dao import activity_dao
from dao import group_qrcode_dao
from dao import cret_template_dao
from dao import bonus_template_dao
from dao import apply_dao
from dao import order_dao
from dao import group_qrcode_dao
from dao import cret_dao
from dao import vendor_member_dao
from dao import voucher_order_dao
from dao import club_dao

from global_const import *


class ApiOrdersXHR(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        product_type = self.get_argument("product_type", "all")
        logging.debug("get product_type=[%r] from argument", product_type)
        distributor_id = self.get_argument("distributor_id", "none")
        logging.debug("get distributor_id=[%r] from argument", distributor_id)
        page = self.get_argument("page", 1)
        logging.debug("get page=[%r] from argument", page)
        limit = self.get_argument("limit", 20)
        logging.debug("get limit=[%r] from argument", limit)

        access_token = self.get_access_token()

        params = {"club_id":vendor_id, "distributor_id":distributor_id, "page":page,"order_type":"buy_item", "limit":limit, "product_type": product_type}
        url = url_concat(API_DOMAIN + "/api/orders", params)
        http_client = HTTPClient()
        headers = {"Authorization":"Bearer " + access_token}
        response = http_client.fetch(url, method="GET", headers=headers)
        logging.info("got response.body %r", response.body)
        data = json_decode(response.body)
        rs = data['rs']
        orders = rs['data']

        for order in orders:
            # 下单时间，timestamp -> %m月%d 星期%w
            order['create_time'] = timestamp_datetime(float(order['create_time']))
            order['booking_time'] = timestamp_datetime(float(order['booking_time']))
            # 合计金额
            order['amount'] = float(order['amount']) / 100
            order['actual_payment'] = float(order['actual_payment']) / 100

        self.write(JSON.dumps(rs, default=json_util.default))
        self.finish()


class ApiActivityOrdersXHR(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id, activity_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got activity_id %r in uri", activity_id)
        product_type = self.get_argument("product_type", "all")
        page = self.get_argument("page", 1)
        logging.debug("get page=[%r] from argument", page)
        limit = self.get_argument("limit", 20)
        logging.debug("get limit=[%r] from argument", limit)

        access_token = self.get_access_token()

        params = {"filter":"item", "item_id":activity_id, "page":page, "limit":limit, "product_type": product_type}
        url = url_concat(API_DOMAIN + "/api/orders", params)
        http_client = HTTPClient()
        headers = {"Authorization":"Bearer " + access_token}
        response = http_client.fetch(url, method="GET", headers=headers)
        logging.info("got response.body %r", response.body)
        data = json_decode(response.body)
        rs = data['rs']
        orders = rs['data']

        for order in orders:
            # 下单时间，timestamp -> %m月%d 星期%w
            order['create_time'] = timestamp_datetime(float(order['create_time']))
            order['booking_time'] = timestamp_datetime(float(order['booking_time']))
            # 合计金额
            order['amount'] = float(order['amount']) / 100
            order['actual_payment'] = float(order['actual_payment']) / 100

        self.write(JSON.dumps(rs, default=json_util.default))
        self.finish()


# 查询订单详情
class ApiOrderInfoXHR(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id, order_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got order_id %r in uri", order_id)

        _order = self.get_symbol_object(order_id)
        # 价格转换成元
        _order['amount'] = float(_order['amount']) / 100
        _order['actual_payment'] = float(_order['actual_payment']) / 100
        for ext_fee in _order['ext_fees']:
            # 价格转换成元
            ext_fee['fee'] = float(ext_fee['fee']) / 100
        for insurance in _order['insurances']:
            # 价格转换成元
            insurance['fee'] = float(insurance['fee']) / 100
        # 价格转换成元
        _order['points_used'] = float(_order['points_used']) / 100

        for _voucher in _order['vouchers']:
            # 价格转换成元
            _voucher['fee'] = float(_voucher['fee']) / 100

        _json = JSON.dumps(_order, default=json_util.default)
        logging.info("got order %r", _json)
        self.write(_json)
        self.finish()


class ApiApplyListXHR(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        product_type = self.get_argument("product_type", "all")
        page = self.get_argument("page", 1)
        logging.debug("get page=[%r] from argument", page)
        limit = self.get_argument("limit", 20)
        logging.debug("get limit=[%r] from argument", limit)

        access_token = self.get_access_token()

        params = {"filter":"club", "club_id":vendor_id, "page":page, "limit":limit, "product_type": product_type}
        url = url_concat(API_DOMAIN + "/api/applies", params)
        http_client = HTTPClient()
        headers = {"Authorization":"Bearer " + access_token}
        response = http_client.fetch(url, method="GET", headers=headers)
        logging.info("got response.body %r", response.body)
        data = json_decode(response.body)
        rs = data['rs']
        applies = rs['data']

        for _apply in applies:
            # 下单时间，timestamp -> %m月%d 星期%w
            _apply['create_time'] = timestamp_datetime(float(_apply['create_time']))
            if _apply['gender'] == 'male':
                _apply['gender'] = u'男'
            else:
                _apply['gender'] = u'女'

        _json = json_encode(applies)
        logging.info("got _json %r", _json)
        self.write(JSON.dumps(rs, default=json_util.default))
        self.finish()


class ApiOrderReviewXHR(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id, order_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got order_id %r in uri", order_id)

        _timestamp = time.time()
        json = {"_id":order_id, "last_update_time":_timestamp, "review":True}
        order_dao.order_dao().update(json);

        self.check_order(order_id)
        self.counter_decrease(vendor_id, "activity_order")

        self.finish("ok")


class ApiOrderDeleteXHR(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def post(self, vendor_id, order_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got order_id %r in uri", order_id)

        order_dao.order_dao().delete(order_id);

        num = order_dao.order_dao().count_not_review_by_vendor(vendor_id)
        budge_num_dao.budge_num_dao().update({"_id":vendor_id, "order":num})

        self.finish("ok")


class ApiApplyReviewXHR(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id, apply_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got apply_id %r in uri", apply_id)

        _timestamp = time.time()
        json = {"_id":apply_id, "last_update_time":_timestamp, "review":True}
        apply_dao.apply_dao().update(json);

        self.check_apply(apply_id)
        self.counter_decrease(vendor_id, "activity_apply")

        self.finish("ok")


# 报名报表导出excel格式文件,
# 使用时必须先生成文件，然后再下载
class ApiActivityExportXHR(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        access_token = self.get_access_token()

        distributor_id = self.get_argument("distributor_id","")
        logging.info("got distributor_id %r",distributor_id)

        check_status = self.get_argument("check_status","")
        logging.info("got check_status %r",check_status)

        pay_status = self.get_argument("pay_status","")
        logging.info("got pay_status %r",pay_status)

        pagenum = self.get_argument("pagenum","")
        logging.info("got pagenum %r",pagenum)

        limit = self.get_argument("limit","")
        logging.info("got limit %r",limit)

        begin_time = self.get_argument("begin_time","")
        logging.info("got begin_time %r",begin_time)

        end_time = self.get_argument("end_time","")
        logging.info("got end_time %r",end_time)

        # utf8,gbk,gb2312
        _unicode = 'utf8'
        _file = xlwt.Workbook(encoding=_unicode) # Workbook
        rownum = None

        # activity = activity_dao.activity_dao().query(activity_id)
        # activity = self.get_activity(activity_id)
        # logging.info("got activity %r in uri", activity)
        #
        # for base_fee in activity['base_fee_template']:
        #     _table = _file.add_sheet(base_fee['name'])        # new sheet
        _table = _file.add_sheet('sheet')
        # column names
        rownum = 0
        _table.write(rownum, 0, unicode(u'订单号').encode(_unicode))
        _table.write(rownum, 1, unicode(u'客户').encode(_unicode))
        _table.write(rownum, 2, unicode(u'总计金额').encode(_unicode))
        _table.write(rownum, 3, unicode(u'已付金额').encode(_unicode))
        _table.write(rownum, 4, unicode(u'退款金额').encode(_unicode))
        _table.write(rownum, 5, unicode(u'下单时间').encode(_unicode))
        _table.write(rownum, 6, unicode(u'是否开发票').encode(_unicode))
        _table.write(rownum, 7, unicode(u'状态').encode(_unicode))
        _table.write(rownum, 8, unicode(u'仓库').encode(_unicode))

        # table
        params = {"club_id":vendor_id, "distributor_id":distributor_id, "check_status":check_status,"pay_status":pay_status, "page":pagenum, "limit":limit, "order_type":"buy_item","begin_time":begin_time, "end_time":end_time}
        url = url_concat(API_DOMAIN + "/api/orders", params)
        http_client = HTTPClient()
        headers = {"Authorization":"Bearer " + access_token}
        response = http_client.fetch(url, method="GET", headers=headers)
        logging.info("got response.body %r", response.body)
        data = json_decode(response.body)
        rs = data['rs']
        orders = rs['data']

        rownum = 1
        for order in orders:
            order['create_time'] = timestamp_datetime(float(order['create_time']))
            order['amount'] = float(order['amount'])/100
            order['actual_payment'] = float(order['actual_payment'])/100
            order['refund_amount'] = float(order['refund_amount'])/100

            if order['billing_required'] == 0:
                order['billing_required'] = u'否'
            elif order['billing_required'] == 1:
                order['billing_required'] = u'是'

            # 各种状态
            _status = ''
            if order.has_key('_status'):
                _status = order['_status']
                if _status == 0:
                    _status = u'未分配'
                elif _status == 200:
                    _status = u'未分配'
                elif _status == 300:
                    _status = u'未发货'
                elif _status == 400:
                    _status = u'未签收'
                elif _status == 500:
                    _status = u'已签收'

            pay_status = ''
            if order.has_key('pay_status'):
                pay_status = order['pay_status']
                if pay_status == 30:
                    pay_status = u'是'
                else:
                    pay_status = u'否'
                    order['actual_payment'] = '--'

            refund = ''
            if order.has_key('refund_amount'):
                refund = order['refund_amount']
                if refund > 0:
                    refund = u'是'
                else:
                    refund = u'否'
            _status = u"是否付款："+pay_status+u"\n订单状态："+_status+u"\n是否退款："+ refund

            _table.write(rownum, 0, order['trade_no'])
            _table.write(rownum, 1, order['nickname'])
            _table.write(rownum, 2, order['amount'])
            _table.write(rownum, 3, order['actual_payment'])
            _table.write(rownum, 4, order['refund_amount'])
            _table.write(rownum, 5, order['create_time'])
            _table.write(rownum, 6, order['billing_required'])
            _table.write(rownum, 7, _status)
            _table.write(rownum, 8, order['distributor_name'])

            rownum = rownum + 1
        _id = generate_uuid_str()
        _file.save('static/report/'+ _id +'.xls')     # Save file
        self.finish(JSON.dumps(ITEM_DOMAIN+"/static/report/"+ _id +".xls"))


'''
设置单元格样式
'''
def set_style(name,height,bold=False,border=False,number=False,align_horz=xlwt.Alignment.HORZ_LEFT):
    style = xlwt.XFStyle() # 初始化样式
    #style = xlwt.easyxf('align: wrap on') # 自动换行

    font = xlwt.Font() # 为样式创建字体
    font.name = name # 'Times New Roman'
    font.bold = bold
    font.color_index = 4
    font.height = height
    style.font = font

    if number:
        style.num_format_str = '#,##0.00'
    else:
        style.num_format_str = '0'

    alignment = xlwt.Alignment() # Create Alignment
    # alignment.horz = xlwt.Alignment.HORZ_CENTER # May be: HORZ_GENERAL, HORZ_LEFT, HORZ_CENTER, HORZ_RIGHT, HORZ_FILLED, HORZ_JUSTIFIED, HORZ_CENTER_ACROSS_SEL, HORZ_DISTRIBUTED
    alignment.horz = align_horz
    alignment.vert = xlwt.Alignment.VERT_CENTER # May be: VERT_TOP, VERT_CENTER, VERT_BOTTOM, VERT_JUSTIFIED, VERT_DISTRIBUTED
    style.alignment = alignment # Add Alignment to Style

    if border:
        borders = xlwt.Borders() # Create Borders
        borders.left = xlwt.Borders.THIN # May be: NO_LINE, THIN, MEDIUM, DASHED, DOTTED, THICK, DOUBLE, HAIR, MEDIUM_DASHED, THIN_DASH_DOTTED, MEDIUM_DASH_DOTTED, THIN_DASH_DOT_DOTTED, MEDIUM_DASH_DOT_DOTTED, SLANTED_MEDIUM_DASH_DOTTED, or 0x00 through 0x0D.
        borders.right = xlwt.Borders.THIN
        borders.top = xlwt.Borders.THIN
        borders.bottom = xlwt.Borders.THIN
        borders.left_colour = 0x40
        borders.right_colour = 0x40
        borders.top_colour = 0x40
        borders.bottom_colour = 0x40
        style.borders = borders # Add Borders to Style

    return style


# 订单详情页报表导出
class ApiActivityDetailExportXHR(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id, order_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got order_id %r in uri", order_id)

        access_token = self.get_access_token()

        # 获取订单详情
        order = self.get_symbol_object(order_id)
        logging.info("got order %r in uri", order)

        # utf8,gbk,gb2312
        _unicode = 'utf8'
        _file = xlwt.Workbook(encoding=_unicode) # Workbook

        sheet_1 = _file.add_sheet('sheet_1')
        sheet_1.col(0).width = 256*8
        sheet_1.col(1).width = 256*45
        sheet_1.col(2).width = 256*8
        sheet_1.col(3).width = 256*9
        sheet_1.col(4).width = 256*10
        sheet_1.col(5).width = 256*10

        # column names
        rownum = 0
        sheet_1.write_merge(rownum,rownum,0,5,"")
        rownum = rownum + 1
        sheet_1.write_merge(rownum,rownum,0,5,"空空配送装修建材配送单",set_style('Times New Roman',450,False,False,False,xlwt.Alignment.HORZ_CENTER))
        rownum = rownum + 1
        sheet_1.write_merge(rownum,rownum,0,5,"")

        rownum = rownum + 1
        sheet_1.write(rownum, 0, unicode(u'下单时间').encode(_unicode))
        create_time = timestamp_datetime(order['create_time'])
        sheet_1.write(rownum, 1, create_time)
        sheet_1.write(rownum, 2, unicode(u'单据编号').encode(_unicode))
        sheet_1.write_merge(rownum,rownum,3,5,order['trade_no'])

        # 收货地址
        shipping_addr = ''
        if order.has_key('shipping_addr'):
            shipping_addr = order['shipping_addr']
            rownum = rownum + 1
            sheet_1.write(rownum, 0, unicode(u'收货人').encode(_unicode))
            sheet_1.write(rownum, 1, shipping_addr['name'])
            sheet_1.write(rownum, 2, unicode(u'收货电话').encode(_unicode))
            sheet_1.write_merge(rownum,rownum,3,5,shipping_addr['phone'])

            rownum = rownum + 1
            sheet_1.write(rownum, 0, unicode(u'收货地址').encode(_unicode))
            sheet_1.write_merge(rownum,rownum,1,5,shipping_addr['_addr'])

        rownum = rownum + 1
        sheet_1.write(rownum, 0, unicode(u'配送仓库').encode(_unicode))
        sheet_1.write_merge(rownum,rownum,1,5,order['distributor_name'])

        # 发票
        billing_addr = ''
        if order.has_key('billing_addr'):
            billing_addr = order['billing_addr']
            rownum = rownum + 1
            sheet_1.write(rownum, 0, unicode(u'发票抬头').encode(_unicode))
            sheet_1.write(rownum, 1, billing_addr['company_title'])
            sheet_1.write(rownum, 2, unicode(u'税号').encode(_unicode))
            sheet_1.write_merge(rownum,rownum,3,5,billing_addr['tfn'])

        rownum = rownum + 1
        sheet_1.write_merge(rownum,rownum,0,5,"",set_style('Times New Roman',220,False,False))

        rownum = rownum + 1
        # 商品详情
        sheet_1.write(rownum, 0, unicode(u'行号').encode(_unicode),set_style('Times New Roman',220,False,True,False,xlwt.Alignment.HORZ_CENTER))
        sheet_1.write(rownum, 1, unicode(u'商品全称').encode(_unicode),set_style('Times New Roman',220,False,True,False,xlwt.Alignment.HORZ_CENTER))
        sheet_1.write(rownum, 2, unicode(u'数量').encode(_unicode),set_style('Times New Roman',220,False,True,False,xlwt.Alignment.HORZ_CENTER))
        sheet_1.write(rownum, 3, unicode(u'单价').encode(_unicode),set_style('Times New Roman',220,False,True,False,xlwt.Alignment.HORZ_CENTER))
        sheet_1.write(rownum, 4, unicode(u'小计').encode(_unicode),set_style('Times New Roman',220,False,True,False,xlwt.Alignment.HORZ_CENTER))
        sheet_1.write(rownum, 5, unicode(u'备注').encode(_unicode),set_style('Times New Roman',220,False,True,False,xlwt.Alignment.HORZ_CENTER))

        # 商品详情
        rownum = rownum + 1
        line = 1
        if order.has_key('items'):
            items = order['items']
            for item in items:
                sheet_1.write(rownum, 0, line,set_style('Times New Roman',220,False,True,False,xlwt.Alignment.HORZ_CENTER))
                sheet_1.write(rownum, 1, item['title'] + "(" + item['brand_title'] + ")" + item['spec_title'],set_style('Times New Roman',220,False,True,xlwt.Alignment.HORZ_LEFT))
                sheet_1.write(rownum, 2, int(item['quantity']),set_style('Times New Roman',220,False,True,False,xlwt.Alignment.HORZ_RIGHT))
                sheet_1.write(rownum, 3, float(item['amount'])/100,set_style('Times New Roman',220,False,True,True,xlwt.Alignment.HORZ_RIGHT))
                sheet_1.write(rownum, 4, float(item['amount'])/100*int(item['quantity']),set_style('Times New Roman',220,False,True,True,xlwt.Alignment.HORZ_RIGHT))
                sheet_1.write(rownum, 5, "",set_style('Times New Roman',220,False,True))
                rownum = rownum + 1
                line = line + 1

        sheet_1.write_merge(rownum,rownum,0,5,"",set_style('Times New Roman',220,False,True))

        rownum = rownum + 1
        sheet_1.write(rownum, 0, line, set_style('Times New Roman',220,False,True,False,xlwt.Alignment.HORZ_CENTER))
        sheet_1.write_merge(rownum,rownum,1,3,unicode(u'搬运费').encode(_unicode),set_style('Times New Roman',220,False,True,xlwt.Alignment.HORZ_LEFT))
        shipping_cost = float(order['shipping_cost']) / 100
        sheet_1.write(rownum, 4, shipping_cost,set_style('Times New Roman',220,False,True,True,xlwt.Alignment.HORZ_RIGHT))
        sheet_1.write(rownum, 5, "",set_style('Times New Roman',220,False,True))

        line = line + 1
        rownum = rownum + 1
        sheet_1.write(rownum, 0, line,set_style('Times New Roman',220,False,True,False,xlwt.Alignment.HORZ_CENTER))
        sheet_1.write_merge(rownum,rownum,1,3,unicode(u'原价合计').encode(_unicode),set_style('Times New Roman',220,False,True,xlwt.Alignment.HORZ_LEFT))
        amount = float(order['amount']) / 100
        sheet_1.write(rownum, 4, amount,set_style('Times New Roman',220,False,True,True,xlwt.Alignment.HORZ_RIGHT))
        sheet_1.write(rownum, 5, "",set_style('Times New Roman',220,False,True))

        line = line + 1
        rownum = rownum + 1
        sheet_1.write(rownum, 0, line,set_style('Times New Roman',220,False,True,False,xlwt.Alignment.HORZ_CENTER))
        sheet_1.write_merge(rownum,rownum,1,3,unicode(u'优惠').encode(_unicode),set_style('Times New Roman',220,False,True,xlwt.Alignment.HORZ_LEFT))
        sheet_1.write(rownum, 5, "",set_style('Times New Roman',220,False,True))

        rownum = rownum + 1
        sheet_1.write(rownum, 0, unicode(u'合计').encode(_unicode),set_style('Times New Roman',220,False,True,False,xlwt.Alignment.HORZ_CENTER))
        actual_payment = float(order['actual_payment']) / 100
        rmb = num2chn(actual_payment)
        sheet_1.write_merge(rownum,rownum,1,3,unicode(u'金额大写: ').encode(_unicode)+rmb,set_style('Times New Roman',220,False,True))
        sheet_1.write(rownum, 4, actual_payment,set_style('Times New Roman',220,False,True,True,xlwt.Alignment.HORZ_RIGHT))
        sheet_1.write(rownum, 5, '', set_style('Times New Roman',220,False,True))

        timestamp = int(time.time())
        _id = order['trade_no']+"_"+timestamp_short_datetime(timestamp)
        _file.save('static/report/'+ _id +'.xls')     # Save file
        self.finish(JSON.dumps(ITEM_DOMAIN+"/static/report/"+ _id +".xls"))


class ApiActivityDetailExport2XHR(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id, order_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got order_id %r in uri", order_id)

        access_token = self.get_access_token()

        # utf8,gbk,gb2312
        _unicode = 'utf8'
        _file = xlwt.Workbook(encoding=_unicode) # Workbook
        rownum = None

        sheet_1 = _file.add_sheet('概要信息')
        sheet_2 = _file.add_sheet('详情')
        sheet_3 = _file.add_sheet('送货地址')
        sheet_4 = _file.add_sheet('发票')
        # column names
        rownum = 0
        # 订单详情
        sheet_1.write(rownum, 0, unicode(u'订单号').encode(_unicode))
        sheet_1.write(rownum, 1, unicode(u'客户').encode(_unicode))
        sheet_1.write(rownum, 2, unicode(u'总计金额').encode(_unicode))
        sheet_1.write(rownum, 3, unicode(u'已付金额').encode(_unicode))
        sheet_1.write(rownum, 4, unicode(u'退款金额').encode(_unicode))
        sheet_1.write(rownum, 5, unicode(u'下单时间').encode(_unicode))
        sheet_1.write(rownum, 6, unicode(u'是否开发票').encode(_unicode))
        sheet_1.write(rownum, 7, unicode(u'状态').encode(_unicode))
        sheet_1.write(rownum, 8, unicode(u'仓库').encode(_unicode))
        sheet_1.write(rownum, 9, unicode(u'备注').encode(_unicode))

        # 商品详情
        sheet_2.write(rownum, 0, unicode(u'商品名').encode(_unicode))
        sheet_2.write(rownum, 1, unicode(u'品牌').encode(_unicode))
        sheet_2.write(rownum, 2, unicode(u'规格').encode(_unicode))
        sheet_2.write(rownum, 3, unicode(u'数量').encode(_unicode))
        sheet_2.write(rownum, 4, unicode(u'单价').encode(_unicode))
        sheet_2.write(rownum, 5, unicode(u'小计').encode(_unicode))

        # 收货信息
        sheet_3.write(rownum, 0, unicode(u'姓名').encode(_unicode))
        sheet_3.write(rownum, 1, unicode(u'联系方式').encode(_unicode))
        sheet_3.write(rownum, 2, unicode(u'地址').encode(_unicode))

        # 发票信息
        sheet_4.write(rownum, 0, unicode(u'公司抬头').encode(_unicode))
        sheet_4.write(rownum, 1, unicode(u'公司税号').encode(_unicode))

        rownum = 1
        # 获取订单详情
        order = self.get_symbol_object(order_id)
        logging.info("got order %r in uri", order)

        order['create_time'] = timestamp_datetime(order['create_time'])
        order['amount'] = float(order['amount']) / 100
        order['actual_payment'] = float(order['actual_payment']) / 100
        order['shipping_cost'] = float(order['shipping_cost']) / 100

        if order['billing_required'] == '0':
            order['billing_required'] = u'否'
        elif order['billing_required'] == '1':
            order['billing_required'] = u'是'
        logging.info("got billing_required %r", order['billing_required'])

        if order.has_key('refund_amount'):
            order['refund_amount'] = float(order['refund_amount']) / 100
        else:
            order['refund_amount'] = '--'

        # 各种状态
        _status = ''
        check_status = ''
        if order.has_key('check_status'):
            check_status = order['check_status']
            if check_status == 1:
                check_status = u'是'
            elif check_status == 0:
                check_status = u'否'

        pay_status = ''
        if order.has_key('pay_status'):
            pay_status = order['pay_status']
            if pay_status == 30:
                pay_status = u'是'
            else:
                pay_status = u'否'
                order['actual_payment'] = '--'

        delivered = ''
        if order.has_key('delivered_status'):
            delivered = order['delivered_status']
            if delivered == 1:
                delivered = u'是'
            else:
                delivered = u'否'

        refund = ''
        if order.has_key('refund_amount'):
            refund = order['refund_amount']
            if refund > 0:
                refund = u'是'
            else:
                refund = u'否'
        _status = u"是否付款："+pay_status+u"\n是否分配："+check_status+u"\n是否发货："+delivered+u"\n是否退款："+ refund

        logging.info("got billing_required %r in order", order['billing_required'])

        sheet_1.write(rownum, 0, order['trade_no'])
        sheet_1.write(rownum, 1, order['nickname'])
        sheet_1.write(rownum, 2, order['amount'])
        sheet_1.write(rownum, 3, order['actual_payment'])
        sheet_1.write(rownum, 4, order['refund_amount'])
        sheet_1.write(rownum, 5, order['create_time'])
        sheet_1.write(rownum, 6, order['billing_required'])
        sheet_1.write(rownum, 7, _status)
        sheet_1.write(rownum, 8, order['distributor_name'])
        note = ""
        if order.has_key('note'):
            note = order['note']
        sheet_1.write(rownum, 9, note)

        # 商品详情
        _rownum = 1
        if order.has_key('items'):
            items = order['items']
            for item in items:
                sheet_2.write(_rownum, 0, item['title'])
                sheet_2.write(_rownum, 1, item['brand_title'])
                sheet_2.write(_rownum, 2, item['spec_title'])
                sheet_2.write(_rownum, 3, item['quantity'])
                sheet_2.write(_rownum, 4, float(item['amount'])/100)
                sheet_2.write(_rownum, 5, str(float(item['amount'])/100*int(item['quantity'])))

                _rownum = _rownum +1

        # 收货地址
        shipping_addr = ''
        if order.has_key('shipping_addr'):
            shipping_addr = order['shipping_addr']

            sheet_3.write(rownum, 0, shipping_addr['name'])
            sheet_3.write(rownum, 1, shipping_addr['phone'])
            sheet_3.write(rownum, 2, shipping_addr['_addr'])

        # 发票
        billing_addr = ''
        if order.has_key('billing_addr'):
            billing_addr = order['billing_addr']

            sheet_4.write(rownum, 0, billing_addr['company_title'])
            sheet_4.write(rownum, 1, billing_addr['tfn'])

        _id = generate_uuid_str()
        _file.save('static/report/'+ _id +'.xls')     # Save file
        self.finish(JSON.dumps(ITEM_DOMAIN+"/static/report/"+ _id +".xls"))


class ApiVoucherOrderReviewXHR(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id, voucher_order_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got voucher_order_id %r in uri", voucher_order_id)

        _timestamp = time.time()
        json = {"_id":voucher_order_id, "last_update_time":_timestamp, "review":True}
        voucher_order_dao.voucher_order_dao().update(json);

        num = voucher_order_dao.voucher_order_dao().count_not_review_by_vendor(vendor_id)
        budge_num_dao.budge_num_dao().update({"_id":vendor_id, "voucher_order":num})

        self.finish("ok")


class ApiVoucherOrderListXHR(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        # _session_ticket = self.get_secure_cookie("session_ticket")

        iBefore = 0
        sBefore = self.get_argument("before", "") #格式 2016-06-01 22:36
        if sBefore != "":
            iBefore = float(datetime_timestamp(sBefore))
        else:
            iBefore = time.time()

        _array = voucher_order_dao.voucher_order_dao().query_pagination_by_vendor(vendor_id, iBefore, PAGE_SIZE_LIMIT);

        for _voucher_order in _array:
            _voucher_order['voucher_price'] = float(_voucher_order['voucher_price'])/100
            _voucher_order['voucher_amount'] = float(_voucher_order['voucher_amount'])/100
            _voucher_order['create_time'] = timestamp_datetime(_voucher_order['create_time'])

        _json = json_encode(_array)
        logging.info("got _json %r", _json)
        self.write(JSON.dumps(_json, default=json_util.default))
        self.finish()


class ApiApplySearchXHR(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        # _session_ticket = self.get_secure_cookie("session_ticket")

        _keys = self.get_argument("keysValue", "")
        _type = self.get_argument("searchType","")

        if(_type == 'title'):
            _array = apply_dao.apply_dao().query_by_title_keys(vendor_id,_keys);
        elif(_type == 'nickname'):
            _array = apply_dao.apply_dao().query_by_nickname_keys(vendor_id,_keys);
        elif(_type == 'date'):
            keys_array = _keys.split('~')
            begin_keys = float(date_timestamp(keys_array[0]))
            end_keys = float(date_timestamp(keys_array[1]))
            _array = apply_dao.apply_dao().query_by_time_keys(vendor_id,begin_keys,end_keys);
            logging.info("got begin_keys--------- %r in uri", begin_keys)
            logging.info("got end_keys--------- %r in uri", end_keys)
        else:
            _array = []

        if(_array):
            for _apply in _array:
                _activity = activity_dao.activity_dao().query(_apply['activity_id'])
                _apply['activity_title'] = _activity['title']
                logging.info("got activity_title %r", _apply['activity_title'])
                _apply['create_time'] = timestamp_datetime(_apply['create_time'])

                customer_profile = vendor_member_dao.vendor_member_dao().query_not_safe(vendor_id, _apply['account_id'])

                if(customer_profile):
                    try:
                        customer_profile['account_nickname']
                    except:
                        customer_profile['account_nickname'] = ''
                    try:
                        customer_profile['account_avatar']
                    except:
                        customer_profile['account_avatar'] = ''

                    _apply['account_nickname'] = customer_profile['account_nickname']
                    _apply['account_avatar'] = customer_profile['account_avatar']
                else:
                    _apply['account_nickname'] = ''
                    _apply['account_avatar'] = ''

                if _apply['gender'] == 'male':
                    _apply['gender'] = u'男'
                else:
                    _apply['gender'] = u'女'

        _json = json_encode(_array)
        logging.info("got _json %r", _json)
        self.write(JSON.dumps(_json, default=json_util.default))
        self.finish()


class ApiOrderSearchXHR(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        # _session_ticket = self.get_secure_cookie("session_ticket")

        _keys = self.get_argument("keysValue", "")
        _type = self.get_argument("searchType","")

        if(_type == 'order'):
            _array = order_dao.order_dao().query_by_order_keys(vendor_id,_keys);
        elif(_type == 'title'):
            _array = apply_dao.apply_dao().query_by_title_keys(vendor_id,_keys);
        elif(_type == 'nickname'):
            _array = order_dao.order_dao().query_by_nickname_keys(vendor_id,_keys);
        elif(_type == 'date'):
            keys_array = _keys.split('~')
            begin_keys = float(date_timestamp(keys_array[0]))
            end_keys = float(date_timestamp(keys_array[1]))
            logging.info("got begin_keys>>>>>>>>>>> %r in uri", begin_keys)
            logging.info("got end_keys>>>>>>>>>>> %r in uri", end_keys)
            _array = order_dao.order_dao().query_by_time_keys(vendor_id,begin_keys,end_keys)
        else:
            _array = []

        if(_array):
            for order in _array:
                _activity = activity_dao.activity_dao().query(order['activity_id'])
                order['activity_title'] = _activity['title']
                # order['activity_amount'] = _activity['amount']
                if not order['base_fees']:
                    order['activity_amount'] = 0
                else:
                    for base_fee in order['base_fees']:
                        # 价格转换成元
                        order['activity_amount'] = float(base_fee['fee']) / 100

                logging.info("got activity_title %r", order['activity_title'])
                order['create_time'] = timestamp_datetime(order['create_time'])

                customer_profile = vendor_member_dao.vendor_member_dao().query_not_safe(vendor_id, order['account_id'])

                if(customer_profile):
                    try:
                        customer_profile['account_nickname']
                    except:
                        customer_profile['account_nickname'] = ''
                    try:
                        customer_profile['account_avatar']
                    except:
                        customer_profile['account_avatar'] = ''

                    order['account_nickname'] = customer_profile['account_nickname']
                    order['account_avatar'] = customer_profile['account_avatar']
                else:
                    order['account_nickname'] = ''
                    order['account_avatar'] = ''

                try:
                    order['bonus']
                except:
                    order['bonus'] = 0
                # 价格转换成元
                order['bonus'] = float(order['bonus']) / 100
                try:
                    order['prepay_id']
                except:
                    order['prepay_id'] = ''
                try:
                    order['transaction_id']
                except:
                    order['transaction_id'] = ''
                try:
                    order['payed_total_fee']
                except:
                    order['payed_total_fee'] = 0

                for ext_fee in order['ext_fees']:
                    # 价格转换成元
                    ext_fee['fee'] = float(ext_fee['fee']) / 100

                for insurance in order['insurances']:
                    # 价格转换成元
                    insurance['fee'] = float(insurance['fee']) / 100

                for _voucher in order['vouchers']:
                    # 价格转换成元
                    _voucher['fee'] = float(_voucher['fee']) / 100

                _cret = cret_dao.cret_dao().query_by_account(order['activity_id'], order['account_id'])
                if _cret:
                    logging.info("got _cret_id %r", _cret['_id'])
                    order['cret_id'] = _cret['_id']
                else:
                    order['cret_id'] = None

                # order['activity_amount'] = float(_activity['amount']) / 100
                if not order['base_fees']:
                    order['activity_amount'] = 0
                else:
                    for base_fee in order['base_fees']:
                        # 价格转换成元
                        order['activity_amount'] = float(base_fee['fee']) / 100

                order['total_amount'] = float(order['total_amount']) / 100
                order['payed_total_fee'] = float(order['payed_total_fee']) / 100

        _json = json_encode(_array)
        logging.info("got _json %r", _json)
        self.write(JSON.dumps(_json, default=json_util.default))
        self.finish()
