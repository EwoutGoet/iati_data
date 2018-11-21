from django.conf.urls import url

import api.chain.views

app_name = 'api'
urlpatterns = [
    url(r'^$',
        api.chain.views.ChainList.as_view(),
        name='chain-list'),
    url(r'^aggregations/',
        api.chain.views.ChainAggregations.as_view(),
        name='chain-aggregations'),
    url(r'^nodes/',
        api.chain.views.NodeList.as_view(),
        name='chain-nodes'),
    url(r'^errors/',
        api.chain.views.ErrorList.as_view(),
        name='chain-errors'),
    url(r'^(?P<pk>[^@$&+,/:;=?]+)/links/',
        api.chain.views.ChainLinkList.as_view(),
        name='chain-link-list'),
    url(r'^(?P<pk>[^@$&+,/:;=?]+)/nodes/',
        api.chain.views.ChainNodeList.as_view(),
        name='chain-node-list'),
    url(r'^(?P<pk>[^@$&+,/:;=?]+)/errors/',
        api.chain.views.ChainNodeErrorList.as_view(),
        name='chain-error-list'),
    url(r'^(?P<pk>[^@$&+,/:;=?]+)/activities/',
        api.chain.views.ChainActivities.as_view(),
        name='chain-activity-list'),
    url(r'^(?P<pk>[^@$&+,/:;=?]+)/transactions/',
        api.chain.views.ChainTransactionList.as_view(),
        name='chain-transaction-list'),
    url(r'^(?P<pk>[^@$&+,/:;=?]+)/',
        api.chain.views.ChainDetail.as_view(),
        name='chain-detail'),
]
