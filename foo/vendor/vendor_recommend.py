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
class VendorRecommendCategoryListHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        ops = self.get_ops_info()

        access_token = self.get_access_token()
        logging.info("GET access_token %r", access_token)

        url = API_DOMAIN + "/api/item-recommend/leagues/"+ LEAGUE_ID +"/categories"
        http_client = HTTPClient()
        headers = {"Authorization":"Bearer " + access_token}
        response = http_client.fetch(url, method="GET", headers=headers)
        logging.info("got response.body %r", response.body)
        data = json_decode(response.body)
        recommend_categorys = data['rs']

        counter = self.get_counter(vendor_id)
        self.render('vendor/recommend-category-list.html',
                vendor_id=vendor_id,
                access_token=access_token,
                API_DOMAIN=API_DOMAIN,
                LEAGUE_ID=LEAGUE_ID,
                ops=ops,
                counter=counter,
                recommend_categorys=recommend_categorys)


 # /vendors/<string:vendor_id>/categorys
class VendorRecommendProductsListHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)

        ops = self.get_ops_info()
        recommend_category_id = self.get_argument('recommend_category_id','')
        logging.info("got recommend_category_id %r", recommend_category_id)

        access_token = self.get_access_token()
        logging.info("GET access_token %r", access_token)

        url = API_DOMAIN + "/api/item-recommend/categories/"+recommend_category_id
        http_client = HTTPClient()
        headers = {"Authorization":"Bearer " + access_token}
        response = http_client.fetch(url, method="GET", headers=headers)
        logging.info("got response.body %r", response.body)
        data = json_decode(response.body)
        _category = data['rs']

        url = API_DOMAIN + "/api/item-recommend/categories/"+recommend_category_id+"/items"
        http_client = HTTPClient()
        headers = {"Authorization":"Bearer " + access_token}
        response = http_client.fetch(url, method="GET", headers=headers)
        logging.info("got response.body %r", response.body)
        data = json_decode(response.body)
        recommend_categorys = data['rs']['data']

        counter = self.get_counter(vendor_id)
        self.render('vendor/recommend-products-list.html',
                vendor_id=vendor_id,
                access_token=access_token,
                API_DOMAIN=API_DOMAIN,
                LEAGUE_ID=LEAGUE_ID,
                ops=ops,
                counter=counter,
                _category=_category,
                recommend_categorys=recommend_categorys,
                recommend_category_id=recommend_category_id)

# 创建预估商品
class VendorRecommendCategoryCreateHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self, vendor_id):
        logging.info("got vendor_id %r in uri", vendor_id)
        access_token = self.get_access_token()

        ops = self.get_ops_info()
        recommend_category_id = self.get_argument('recommend_category_id','')
        logging.info('got recommend_category_id %r',recommend_category_id)

        url = API_DOMAIN + "/api/def/leagues/"+ LEAGUE_ID +"/categories"
        http_client = HTTPClient()
        headers = {"Authorization":"Bearer " + access_token}
        response = http_client.fetch(url, method="GET", headers=headers)
        logging.info("got response.body %r", response.body)
        data = json_decode(response.body)
        categorys = data['rs']

        counter = self.get_counter(vendor_id)
        self.render('vendor/recommend-product-create.html',
                vendor_id=vendor_id,
                API_DOMAIN=API_DOMAIN,
                access_token=access_token,
                categorys=categorys,
                ops=ops,
                counter=counter,
                recommend_category_id=recommend_category_id)

    # @tornado.web.authenticated  # if no session, redirect to login page
    # def post(self,vendor_id):
    #     logging.info("GET vendor_id %r", vendor_id)
    #
    #     access_token = self.get_access_token()
    #     logging.info("GET access_token %r", access_token)
    #
    #     ops = self.get_ops_info()
    #
    #     title = self.get_argument("title", "")
    #     logging.debug("got param title %r", title)
    #
    #     categroy = {"league_id":LEAGUE_ID, "parent_id":"00000000000000000000000000000000", "level":1,
    #                 "title":title, "img":"http://tripc2c-club-title.b0.upaiyun.com/default/banner4.png",}
    #
    #     url = API_DOMAIN+"/api/def/categories"
    #     http_client = HTTPClient()
    #     headers={"Authorization":"Bearer "+access_token}
    #     _json = json_encode(categroy)
    #     logging.info("request %r body %r", url, _json)
    #     response = http_client.fetch(url, method="POST", headers=headers, body=_json)
    #     logging.info("got response %r", response.body)
    #
    #     self.redirect('/vendors/' + vendor_id + '/categorys')


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
