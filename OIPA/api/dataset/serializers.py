from rest_framework.serializers import HyperlinkedIdentityField
from rest_framework.serializers import HyperlinkedRelatedField
from rest_framework.serializers import SerializerMethodField
from iati_synchroniser.models import IatiXmlSource
from api.generics.serializers import DynamicFieldsModelSerializer

from django.core.urlresolvers import reverse
from iati.models import Activity


class DatasetSerializer(DynamicFieldsModelSerializer):

    url = HyperlinkedIdentityField(view_name='datasets:dataset-detail')
    publisher = HyperlinkedRelatedField(
        view_name='publishers:publisher-detail',
        read_only=True)
    type = SerializerMethodField()
    activities = SerializerMethodField()
    activity_count = SerializerMethodField()

    class Meta:
        model = IatiXmlSource
        fields = (
            'url',
            'ref',
            'title',
            'type',
            'publisher',
            'source_url',
            'activities',
            'activity_count',
            'date_created',
            'date_updated',
            'last_found_in_registry',
            'iati_standard_version')

    def get_type(self, obj):
        return obj.get_type_display()

    def get_activities(self, obj):
        request = self.context.get('request')
        url = request.build_absolute_uri(reverse('activities:activity-list'))
        return url + '?xml_source_ref=' + obj.ref

    def get_activity_count(self, obj):
        return Activity.objects.filter(xml_source_ref=obj.ref).count()