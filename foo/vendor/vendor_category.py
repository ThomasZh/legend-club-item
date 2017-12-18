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
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../dao"))
from comm import *
from dao import budge_num_dao
from dao import category_dao
from dao import group_qrcode_dao
from dao import vendor_wx_dao
from global_const import *
import uuid


# 这里vendorid是应该动态得到并赋值
class VendorIndexHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        ops = self.get_ops_info()
        logging.info("got ops %r in uri", ops)

        self.redirect('/vendors/' + ops['club_id'] + '/categorys')


# /vendors/<string:vendor_id>/categorys/<string:category_id>/delete
class VendorCategoryDeleteHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id, category_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got category_id %r in uri", category_id)

        ops = self.get_ops_info()

        category_dao.category_dao().delete(category_id)

        self.redirect('/vendors/' + vendor_id + '/categorys')


# /vendors/<string:vendor_id>/categorys
class VendorCategoryListHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        ops = self.get_ops_info()
        logging.info("got ops %r", ops)

        access_token = self.get_access_token()
        logging.info("GET access_token %r", access_token)

        club = self.get_club_basic_info(vendor_id)
        league_id = club['league_id']

        url = API_DOMAIN + "/api/def/leagues/"+ league_id +"/categories"
        http_client = HTTPClient()
        headers = {"Authorization":"Bearer " + access_token}
        response = http_client.fetch(url, method="GET", headers=headers)
        logging.info("got response.body %r", response.body)
        data = json_decode(response.body)
        categorys = data['rs']

        counter = self.get_counter(vendor_id)
        self.render('vendor/category-list.html',
                vendor_id=vendor_id,
                access_token=access_token,
                API_DOMAIN=API_DOMAIN,
                ops=ops,
                counter=counter,
                categorys=categorys)

# 二级分类
class VendorCategorySecondaryHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        ops = self.get_ops_info()
        access_token = self.get_access_token()
        logging.info("GET access_token %r", access_token)

        category_id = self.get_argument('category_id','')
        logging.info("get category_id",category_id)

        # TODO: get second_category info
        url = API_DOMAIN + "/api/def/categories/"+ category_id
        http_client = HTTPClient()
        headers = {"Authorization":"Bearer " + access_token}
        response = http_client.fetch(url, method="GET", headers=headers)
        logging.info("got response.body %r", response.body)
        data = json_decode(response.body)
        second_category_info = data['rs']

        url = API_DOMAIN + "/api/def/categories/"+ category_id +"/level2"
        http_client = HTTPClient()
        headers = {"Authorization":"Bearer " + access_token}
        response = http_client.fetch(url, method="GET", headers=headers)
        logging.info("got response.body %r", response.body)
        data = json_decode(response.body)
        second_categorys = data['rs']

        counter = self.get_counter(vendor_id)
        self.render('vendor/category-second.html',
                vendor_id=vendor_id,
                access_token=access_token,
                API_DOMAIN=API_DOMAIN,
                ops=ops,
                counter=counter,
                category_id=category_id,
                second_category_info=second_category_info,
                second_categorys=second_categorys)


# /vendors/<string:vendor_id>/categorys/create first_category
class VendorCategoryCreateHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        ops = self.get_ops_info()

        counter = self.get_counter(vendor_id)
        self.render('vendor/category-create.html',
                vendor_id=vendor_id,
                ops=ops,
                counter=counter)

    @tornado.web.authenticated  # if no session, redirect to login page
    def post(self,vendor_id):
        logging.info("GET vendor_id %r", vendor_id)

        access_token = self.get_access_token()
        logging.info("GET access_token %r", access_token)

        ops = self.get_ops_info()

        title = self.get_argument("title", "")
        logging.debug("got param title %r", title)

        club = self.get_club_basic_info(vendor_id)
        league_id = club['league_id']

        categroy = {"league_id":league_id, "parent_id":"00000000000000000000000000000000", "level":1,
                    "title":title, "img":"http://tripc2c-club-title.b0.upaiyun.com/default/banner4.png"}

        url = API_DOMAIN+"/api/def/categories"
        http_client = HTTPClient()
        headers={"Authorization":"Bearer "+access_token}
        _json = json_encode(categroy)
        logging.info("request %r body %r", url, _json)
        response = http_client.fetch(url, method="POST", headers=headers, body=_json)
        logging.info("got response %r", response.body)

        self.redirect('/vendors/' + vendor_id + '/categorys')


# /create second_category
class VendorCategoryCreateSecondHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        category_id = self.get_argument('category_id','')
        logging.info("get category_id",category_id)

        ops = self.get_ops_info()

        counter = self.get_counter(vendor_id)
        self.render('vendor/category-second-create.html',
                vendor_id=vendor_id,
                ops=ops,
                category_id=category_id,
                counter=counter)

    @tornado.web.authenticated  # if no session, redirect to login page
    def post(self,vendor_id):
        logging.info("GET vendor_id %r", vendor_id)

        access_token = self.get_access_token()
        logging.info("GET access_token %r", access_token)

        ops = self.get_ops_info()

        title = self.get_argument("title", "")
        logging.debug("got param title %r", title)

        parent_id = self.get_argument('category_id','')
        logging.info("get parent_id",parent_id)

        club = self.get_club_basic_info(vendor_id)
        league_id = club['league_id']

        categroy = {"league_id":league_id, "parent_id":parent_id, "level":2,
                    "title":title, "img":"http://tripc2c-club-title.b0.upaiyun.com/default/banner4.png"}

        url = API_DOMAIN+"/api/def/categories"
        http_client = HTTPClient()
        headers={"Authorization":"Bearer "+access_token}
        _json = json_encode(categroy)
        logging.info("request %r body %r", url, _json)
        response = http_client.fetch(url, method="POST", headers=headers, body=_json)
        logging.info("got response %r", response.body)

        self.redirect('/vendors/' + vendor_id + '/categorys/secondary?category_id='+parent_id)


# /品牌 brand
class VendorCategorySecondaryBrandHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        ops = self.get_ops_info()
        access_token = self.get_access_token()
        logging.info("GET access_token %r", access_token)

        second_categorys_id = self.get_argument('second_categorys_id','')
        logging.info("get second_categorys_id",second_categorys_id)

        # TODO: get second_category info
        url = API_DOMAIN + "/api/def/categories/"+ second_categorys_id
        http_client = HTTPClient()
        headers = {"Authorization":"Bearer " + access_token}
        response = http_client.fetch(url, method="GET", headers=headers)
        logging.info("got response.body %r", response.body)
        data = json_decode(response.body)
        second_category_info = data['rs']

        url = API_DOMAIN + "/api/def/categories/"+ second_categorys_id +"/brands"
        http_client = HTTPClient()
        headers = {"Authorization":"Bearer " + access_token}
        response = http_client.fetch(url, method="GET", headers=headers)
        logging.info("got response.body %r", response.body)
        data = json_decode(response.body)
        second_brands = data['rs']

        counter = self.get_counter(vendor_id)
        self.render('vendor/category-brand.html',
                vendor_id=vendor_id,
                access_token=access_token,
                API_DOMAIN=API_DOMAIN,
                ops=ops,
                counter=counter,
                second_category_info=second_category_info,
                second_categorys_id=second_categorys_id,
                second_brands=second_brands)


# /create 品牌
class VendorCategoryCreateBrandHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        second_categorys_id = self.get_argument('second_categorys_id','')
        logging.info("get second_categorys_id",second_categorys_id)

        ops = self.get_ops_info()

        counter = self.get_counter(vendor_id)
        self.render('vendor/category-brand-create.html',
                vendor_id=vendor_id,
                ops=ops,
                second_categorys_id=second_categorys_id,
                counter=counter)

    @tornado.web.authenticated  # if no session, redirect to login page
    def post(self,vendor_id):
        logging.info("GET vendor_id %r", vendor_id)

        access_token = self.get_access_token()
        logging.info("GET access_token %r", access_token)

        ops = self.get_ops_info()

        title = self.get_argument("title", "")
        logging.debug("got param title %r", title)

        second_categorys_id = self.get_argument('second_categorys_id','')
        logging.info("get second_categorys_id",second_categorys_id)

        categroy = {"category_id":second_categorys_id, "title":title, "img":"http://tripc2c-club-title.b0.upaiyun.com/default/banner4.png",}

        url = API_DOMAIN+"/api/def/brands"
        http_client = HTTPClient()
        headers={"Authorization":"Bearer "+access_token}
        _json = json_encode(categroy)
        logging.info("request %r body %r", url, _json)
        response = http_client.fetch(url, method="POST", headers=headers, body=_json)
        logging.info("got response %r", response.body)

        self.redirect('/vendors/' + vendor_id + '/categorys/secondary/brand?second_categorys_id='+second_categorys_id)


# /规格spec
class VendorCategorySecondarySpecHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        ops = self.get_ops_info()
        access_token = self.get_access_token()
        logging.info("GET access_token %r", access_token)

        second_categorys_id = self.get_argument('second_categorys_id','')
        logging.info("get second_categorys_id",second_categorys_id)

        # TODO: get second_category info
        url = API_DOMAIN + "/api/def/categories/"+ second_categorys_id
        http_client = HTTPClient()
        headers = {"Authorization":"Bearer " + access_token}
        response = http_client.fetch(url, method="GET", headers=headers)
        logging.info("got response.body %r", response.body)
        data = json_decode(response.body)
        second_category_info = data['rs']

        url = API_DOMAIN + "/api/def/categories/"+ second_categorys_id +"/specs"
        http_client = HTTPClient()
        headers = {"Authorization":"Bearer " + access_token}
        response = http_client.fetch(url, method="GET", headers=headers)
        logging.info("got response.body %r", response.body)
        data = json_decode(response.body)
        second_specs = data['rs']

        counter = self.get_counter(vendor_id)
        self.render('vendor/category-spec.html',
                vendor_id=vendor_id,
                access_token=access_token,
                API_DOMAIN=API_DOMAIN,
                ops=ops,
                counter=counter,
                second_categorys_id=second_categorys_id,
                second_category_info=second_category_info,
                second_specs=second_specs)


# /create 规格
class VendorCategoryCreateSpecHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        second_categorys_id = self.get_argument('second_categorys_id','')
        logging.info("get second_categorys_id",second_categorys_id)

        ops = self.get_ops_info()

        counter = self.get_counter(vendor_id)
        self.render('vendor/category-spec-create.html',
                vendor_id=vendor_id,
                ops=ops,
                second_categorys_id=second_categorys_id,
                counter=counter)

    @tornado.web.authenticated  # if no session, redirect to login page
    def post(self,vendor_id):
        logging.info("GET vendor_id %r", vendor_id)

        access_token = self.get_access_token()
        logging.info("GET access_token %r", access_token)

        ops = self.get_ops_info()

        title = self.get_argument("title", "")
        logging.debug("got param title %r", title)

        second_categorys_id = self.get_argument('second_categorys_id','')
        logging.info("get second_categorys_id",second_categorys_id)

        unit = self.get_argument('unit','')
        logging.info("get unit",unit)

        categroy = {"category_id":second_categorys_id, "title":title, 'amount':0, 'unit':unit, "img":"http://tripc2c-club-title.b0.upaiyun.com/default/banner4.png",}

        url = API_DOMAIN+"/api/def/specs"
        http_client = HTTPClient()
        headers={"Authorization":"Bearer "+access_token}
        _json = json_encode(categroy)
        logging.info("request %r body %r", url, _json)
        response = http_client.fetch(url, method="POST", headers=headers, body=_json)
        logging.info("got response %r", response.body)

        self.redirect('/vendors/' + vendor_id + '/categorys/secondary/spec?second_categorys_id='+second_categorys_id)



# 二级分类下添加商品
class VendorCategoryCreateProductHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        ops = self.get_ops_info()
        access_token = self.get_access_token()
        logging.info("GET access_token %r", access_token)
        second_categorys_id = self.get_argument('second_categorys_id','')
        logging.info("GET second_categorys_id %r", second_categorys_id)

        club = self.get_club_basic_info(vendor_id)
        league_id = club['league_id']

        url = API_DOMAIN + "/api/def/leagues/"+ league_id +"/categories"
        http_client = HTTPClient()
        headers = {"Authorization":"Bearer " + access_token}
        response = http_client.fetch(url, method="GET", headers=headers)
        logging.info("got response.body %r", response.body)
        data = json_decode(response.body)
        categorys = data['rs']

        url = API_DOMAIN + "/api/def/categories/"+second_categorys_id+"/brands"
        http_client = HTTPClient()
        headers = {"Authorization":"Bearer " + access_token}
        response = http_client.fetch(url, method="GET", headers=headers)
        logging.info("got response.body %r", response.body)
        data = json_decode(response.body)
        brands = data['rs']

        counter = self.get_counter(vendor_id)
        self.render('vendor/category-products-create.html',
                vendor_id=vendor_id,
                access_token=access_token,
                API_DOMAIN=API_DOMAIN,
                ops=ops,
                counter=counter,
                categorys=categorys,
                brands=brands,
                second_categorys_id=second_categorys_id)

    def post(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        access_token = self.get_secure_cookie("access_token")

        ops = self.get_ops_info()
        second_categorys_id = self.get_argument('second_categorys_id','')
        logging.info("GET second_categorys_id %r", second_categorys_id)
        _title = self.get_argument("title", "")
        _bk_img_url = self.get_argument("bk_img_url", "")
        brand = self.get_argument("brand", "")
        logging.info ("get brand %r", brand)

        # TODO: get second_category info
        url = API_DOMAIN + "/api/def/categories/"+ second_categorys_id
        http_client = HTTPClient()
        headers = {"Authorization":"Bearer " + access_token}
        response = http_client.fetch(url, method="GET", headers=headers)
        logging.info("got response.body %r", response.body)
        data = json_decode(response.body)
        second_category_info = data['rs']

        _category = second_category_info['parent_id']

        activity = {
            "club_id":vendor_id,
            "title":_title,
            "img":_bk_img_url,
            "category_id":_category,
            "level2_category_id":second_categorys_id,
            "brand_id":brand
        }
        logging.info("got activity %r",activity)
        headers = {"Authorization":"Bearer "+access_token}
        url = API_DOMAIN + "/api/items"
        _json = json_encode(activity)
        http_client = HTTPClient()
        response = http_client.fetch(url, method="POST", headers=headers, body=_json)
        logging.info("create activity response.body=[%r]", response.body)
        data = json_decode(response.body)
        rs = data['rs']
        _activity_id = rs["_id"]

        article = {'_id':_activity_id, 'title':_title, 'subtitle':_title, 'img':_bk_img_url, 'paragraphs':''}
        self.create_article(article)

        wx_app_info = vendor_wx_dao.vendor_wx_dao().query(vendor_id)
        wx_notify_domain = wx_app_info['wx_notify_domain']
        # create wechat qrcode
        activity_url = wx_notify_domain + "/bf/wx/vendors/" + vendor_id + "/items/" + _activity_id
        logging.info("got activity_url %r", activity_url)
        data = {"url": activity_url}
        _json = json_encode(data)
        logging.info("got ——json %r", _json)
        http_client = HTTPClient()
        response = http_client.fetch(QRCODE_CREATE_URL, method="POST", body=_json)
        logging.info("got response %r", response.body)
        qrcode_url = response.body
        logging.info("got qrcode_url %r", qrcode_url)

        _timestamp = time.time()
        wx_qrcode_url = "http://bike-forever.b0.upaiyun.com/vendor/wx/2016/7/21/66a75009-e60e-44b1-80f7-bf4a9d95525a.jpg"
        json = {"_id":_activity_id,
                "create_time":_timestamp, "last_update_time":_timestamp,
                "qrcode_url":qrcode_url, "wx_qrcode_url":wx_qrcode_url}
        group_qrcode_dao.group_qrcode_dao().create(json)

        counter = self.get_counter(vendor_id)
        self.redirect('/vendors/'+ vendor_id +'/categorys/secondary/products?second_categorys_id='+second_categorys_id)


# /二级分类下的商品
class VendorCategorySecondaryProductsHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        ops = self.get_ops_info()
        access_token = self.get_access_token()
        logging.info("GET access_token %r", access_token)

        second_categorys_id = self.get_argument('second_categorys_id','')
        logging.info("get second_categorys_id",second_categorys_id)

        # TODO: get second_category info
        url = API_DOMAIN + "/api/def/categories/"+ second_categorys_id
        http_client = HTTPClient()
        headers = {"Authorization":"Bearer " + access_token}
        response = http_client.fetch(url, method="GET", headers=headers)
        logging.info("got response.body %r", response.body)
        data = json_decode(response.body)
        second_category_info = data['rs']

        # 获取商品列表
        # params = {"_status":"all","page":1, "limit":200}
        # url = url_concat(API_DOMAIN + "/api/def/categories/"+ second_categorys_id +"/items", params)
        # http_client = HTTPClient()
        # headers = {"Authorization":"Bearer " + access_token}
        # response = http_client.fetch(url, method="GET", headers=headers,)
        # logging.info("got response.body %r", response.body)
        # data = json_decode(response.body)
        # second_products = data['rs']['data']

        counter = self.get_counter(vendor_id)
        self.render('vendor/category-products.html',
                vendor_id=vendor_id,
                access_token=access_token,
                API_DOMAIN=API_DOMAIN,
                ops=ops,
                counter=counter,
                second_categorys_id=second_categorys_id,
                second_category_info=second_category_info)


# /vendors/<string:vendor_id>/categorys/<string:category_id>/edit
class VendorCategoryEditHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id, category_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got category_id %r in uri", category_id)

        ops = self.get_ops_info()

        category = category_dao.category_dao().query(category_id)
        counter = self.get_counter(vendor_id)
        self.render('vendor/category-edit.html',
                vendor_id=vendor_id,
                ops=ops,
                counter=counter,
                category=category)

    @tornado.web.authenticated  # if no session, redirect to login page
    def post(self, vendor_id, category_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        logging.info("got category_id %r in uri", category_id)

        ops = self.get_ops_info()

        title = self.get_argument("title", "")
        desc = self.get_argument("desc", "")
        bk_img_url = self.get_argument("bk_img_url", "")
        logging.debug("got param title %r", title)
        logging.debug("got param desc %r", desc)
        logging.debug("got param bk_img_url %r", bk_img_url)

        categroy = {"_id":category_id, "title":title, "desc":desc ,"bk_img_url":bk_img_url}
        category_dao.category_dao().update(categroy);

        self.redirect('/vendors/' + vendor_id + '/categorys')
