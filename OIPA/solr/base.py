import json
from rest_framework import serializers
from rest_framework.renderers import JSONRenderer

from api.activity.serializers import NarrativeSerializer
from solr.utils import add_dict, add_value_list, value_string, get_child_attr


class BaseSerializer(serializers.Serializer):
    representation = {}

    def set_field(self, field, value):
        add_dict(self.representation, field, value)


class IndexingSerializer(BaseSerializer):
    indexing = {}
    record = None

    def add_field(self, field, value=None):
        self.indexing[field] = value

    def add_value_list(self, field, value):
        add_value_list(self.indexing[field], value)

    def build(self):
        for key in self.indexing:
            add_dict(self.representation, key, self.indexing[key])

    def narrative(self, field, field_name='narrative', is_json_string=False):
        if field:
            narratives_all = field.narratives.all()
            if narratives_all:
                narratives = list()
                for narrative in narratives_all:
                    value = JSONRenderer().render(NarrativeSerializer(narrative).data).decode() if is_json_string \
                        else NarrativeSerializer(narrative).data
                    add_value_list(narratives, value)

                self.set_field(field_name, narratives)
