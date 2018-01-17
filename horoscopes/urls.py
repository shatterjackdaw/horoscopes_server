# -*- coding:utf-8 -*-
from django.conf.urls import url
from . import views

urlpatterns = [
    # url(r'^get_latest_activity/(?P<server_code>[0-9]+)/', views.get_latest_activity_view),
    url(r'^get_horoscopes_data$', views.index),
    # url(r'^activity_review_by_rid/', views.activity_review_by_rid),
]
