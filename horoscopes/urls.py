# -*- coding:utf-8 -*-
from django.conf.urls import url
from . import views

urlpatterns = [
    # url(r'^get_latest_activity/(?P<server_code>[0-9]+)/', views.get_latest_activity_view),
    url(r'^get_horoscopes_data$', views.index),
    url(r'^info_regist$', views.info_regist),
    url(r'^login$', views.info_login),
    url(r'^auto_order$', views.auto_order),
    url(r'^get_compatibility_data', views.get_compatibility_data),
    # url(r'^activity_review_by_rid/', views.activity_review_by_rid),
]
