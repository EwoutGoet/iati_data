from django.conf.urls import url
import api.activity.views
import api.sector.views
from django.views.decorators.cache import cache_page
from OIPA.production_settings import API_CACHE_SECONDS


urlpatterns = [
    url(r'^$',
        api.activity.views.ActivityList.as_view(),
        name='activity-list'),
    url(r'^aggregations/',
        cache_page(API_CACHE_SECONDS)(api.activity.views.ActivityAggregations.as_view()),
        name='activity-aggregations'),
    url(r'^(?P<pk>[^@$&+,/:;=?]+)/$',
        api.activity.views.ActivityDetail.as_view(),
        name='activity-detail'),
    url(r'^(?P<pk>[^@$&+,/:;=?]+)/transactions/',
        api.activity.views.ActivityTransactions.as_view(),
        name='activity-transactions'),
    url(r'^(?P<pk>[^@$&+,/:;=?]+)/provided-activities/',
        api.activity.views.ActivityProvidedActivities.as_view(),
        name='activity-provided-activities'),
    url(r'^(?P<pk>[^@$&+,/:;=?]+)/providing-activities/',
        api.activity.views.ActivityProvidingActivities.as_view(),
        name='activity-providing-activities'),
]
