"""
Tests for the views using the aggregation methods
"""

from collections import OrderedDict
from unittest import skip

from django.db.models import Count, Q
from django.test import TestCase as DjangoTestCase
from django.test.client import RequestFactory
from rest_framework import serializers

from api.aggregation.views import Aggregation, GroupBy
from api.generics.serializers import DynamicFieldsSerializer
from iati.factory.utils import _create_test_activity
from iati.models import Activity


class AggregationInstanceTestCase(DjangoTestCase):
    """
    Check the Aggregation class construction and methods behave correctly
    """

    def setUp(self):
        # TODO: mock a queryset instead - 2016-04-11
        self.activity = _create_test_activity(
            id="test", iati_identifier="test")
        self.activity.save()
        self.queryset = Activity.objects.all()

    def test_required_params_throws(self):
        """
        Test errors are thrown when not all required params are set.
        """

        with self.assertRaises(ValueError):
            Aggregation(
                field='count',
                annotate=Count('id'),
            )

        with self.assertRaises(ValueError):
            Aggregation(
                query_param='count',
                annotate=Count('id'),
            )

        with self.assertRaises(ValueError):
            Aggregation(
                query_param='count',
                field='count',
            )

    def test_required_params_passes(self):
        """
        Test giving required params constructs succesfully
        """
        Aggregation(
            query_param='count',
            field='count',
            annotate=Count('id'),
        )

    def test_apply_annotation_applies_annotation(self):
        """
        Test apply_annotation applies the annotation given in the constructor
        """
        aggregation = Aggregation(
            query_param='count',
            field='count',
            annotate=Count('id'),
        )

        aggregation.apply_annotation(self.queryset)

        # TODO: test for count - 2016-04-11
        # print(self.queryset)

    def test_extra_filter_non_Q_object_raises(self):
        """
        The "extra_filter" constructor param must be a django Q object
        """

        # TODO: Should we allow key-value dicts as well? - 2016-04-11
        with self.assertRaises(ValueError):
            Aggregation(
                query_param='count',
                field='count',
                annotate=Count('id'),
                extra_filter={'key': "value"},
            )

    def test_extra_filter_is_applied(self):
        """
        Test the extra filter is applied when given in the constructor
        """

        aggregation = Aggregation(
            query_param='count',
            field='count',
            annotate=Count('id'),
            extra_filter=Q(iati_identifier="test")
        )

        queryset = aggregation.apply_extra_filter(self.queryset)

        self.assertEqual(len(queryset), 1)
        self.assertEqual(queryset[0], self.activity)


class GroupByInstanceTestCase(DjangoTestCase):
    """
    Check the GroupBy class construction and methods behave correctly
    """

    def setUp(self):
        # TODO: mock a queryset instead - 2016-04-11
        self.activity = _create_test_activity(
            id="test", iati_identifier="test")
        self.activity2 = _create_test_activity(
            id="test2", iati_identifier="test2")
        self.activity.save()
        self.activity2.save()

        self.queryset = Activity.objects.all()

    def test_required_params_throws(self):
        """
        Test errors are thrown when not all required params are set.
        """
        with self.assertRaises(ValueError):
            GroupBy(
                fields="id",
            )

        with self.assertRaises(ValueError):
            GroupBy(
                query_param="test",
            )

    def test_required_params_passes(self):
        """
        Test giving required params constructs succesfully
        """

        GroupBy(
            query_param="test",
            fields="id",
            queryset=self.queryset,
        )

    def test_renamed_fields_exceeds_fields_len_raises(self):
        """
        Test when len(renamed_fields) > len(fields), throws error
        """
        with self.assertRaises(ValueError):
            GroupBy(
                query_param="test",
                fields=("id", "name"),
                renamed_fields=("id_renamed", "name_renamed", "ew_renamed"),
                queryset=self.queryset,
            )

    def test_get_renamed_fields_no_renaming(self):
        """
        Test when not renaming fields, returns an empty dictionary
        """

        group_by = GroupBy(
            query_param="test",
            fields="id",
            queryset=self.queryset,
        )

        self.assertEqual(bool(group_by.get_renamed_fields()), False)

    def test_get_renamed_fields_with_renaming(self):
        """
        Test when renaming fields, returns a key-value with renamed-actual
        """

        group_by = GroupBy(
            query_param="test",
            fields="id",
            renamed_fields="id_renamed",
            queryset=self.queryset,
        )

        renamed_fields = group_by.get_renamed_fields()

        self.assertEqual(len(renamed_fields), 1)
        self.assertCountEqual(renamed_fields.keys(), ["id_renamed"])

    def test_get_renamed_fields_with_multiple_renaming(self):
        """
        Test when renaming multiple fields, returns a key-value with
        renamed-actual
        """

        group_by = GroupBy(
            query_param="test",
            fields=("id", "name"),
            renamed_fields=("id_renamed", "name_renamed"),
            queryset=self.queryset,
        )

        renamed_fields = group_by.get_renamed_fields()

        self.assertEqual(len(renamed_fields), 2)
        self.assertCountEqual(renamed_fields.keys(), [
                              "id_renamed", "name_renamed"])

    def test_get_renamed_fields_partly(self):
        """
        Test renaming only a few of the fields also works
        """

        group_by = GroupBy(
            query_param="test",
            fields=("id", "name"),
            renamed_fields="id_renamed",
            queryset=self.queryset,
        )

        renamed_fields = group_by.get_renamed_fields()

        self.assertEqual(len(renamed_fields), 1)
        self.assertCountEqual(renamed_fields.keys(), ["id_renamed"])

    def test_get_fields_no_renaming(self):
        """
        Test get_fields() returns original fields if no renaming is done.
        """

        group_by = GroupBy(
            query_param="test",
            fields=("id", "name"),
            queryset=self.queryset,
        )

        self.assertEqual(group_by.get_fields(), group_by.fields)

    def test_get_fields_with_renaming(self):
        """
        Test get_fields() returns renamed fields when renaming.
        """

        group_by = GroupBy(
            query_param="test",
            fields=("id", "name"),
            renamed_fields=("id_renamed", "name_renamed"),
            queryset=self.queryset,
        )

        self.assertEqual(group_by.get_fields(), group_by.renamed_fields)

    def test_get_fields_with_partly_renaming(self):
        """
        Test get_fields() returns renamed fields when renaming only part of
        the fields.
        """

        group_by = GroupBy(
            query_param="test",
            fields=("id", "name"),
            renamed_fields="id_renamed",
            queryset=self.queryset,
        )

        self.assertCountEqual(group_by.get_fields(), ["id_renamed", "name"])

    def test_serialize_result_expands_key_given_results_array(self):
        """
        When calling serialize_results with an array of results, should
        serialize the result[key] with the given serializer and queryset from
        the constructor and return the resulting array.
        Here {key} is the first field given in the fields tuple in the
        constructor
        """

        class DummySerializer(DynamicFieldsSerializer):
            id = serializers.CharField()
            iati_identifier = serializers.CharField()

        group_by = GroupBy(
            query_param="test",
            fields="key",
            queryset=self.queryset,
            serializer=DummySerializer,
            serializer_main_field='iati_identifier',
            serializer_fk='iati_identifier',
            serializer_fields=['iati_identifier']
        )

        results = [
            {
                "key": "test",
                "count": 12345,
            },
            {
                "key": "test2",
                "count": 67890,
            }
        ]

        rf = RequestFactory()
        request = rf.get('/api/activities/')

        new_results = group_by.serialize_results(results, request)

        self.assertEqual(list(new_results), [
            {
                "key": OrderedDict([
                        ('iati_identifier', 'test'),
                ]),
                "count": 12345,
            },
            {
                "key": OrderedDict([
                    ('iati_identifier', 'test2'),
                ]),
                "count": 67890,
            }
        ])

    def test_serializer_fields_limits_serializer_fields(self):
        """
        When given a dynamic serializer, serializer_fields should determine
        the fields that the serialized field should expose
        """
        class DummySerializer(DynamicFieldsSerializer):
            id = serializers.CharField()
            iati_identifier = serializers.CharField()

        group_by = GroupBy(
            query_param="test",
            fields="key",
            queryset=self.queryset,
            serializer=DummySerializer,
            serializer_main_field='iati_identifier',
            serializer_fk='iati_identifier',
            serializer_fields=['iati_identifier']
        )

        results = [
            {
                "key": "test",
                "count": 12345,
            },
            {
                "key": "test2",
                "count": 67890,
            }
        ]

        rf = RequestFactory()
        request = rf.get('/api/activities/')

        new_results = group_by.serialize_results(results, request)

        self.assertCountEqual(new_results, [
            {
                "key": {
                    "iati_identifier": "test",
                },
                "count": 12345,
            },
            {
                "key": {
                    "iati_identifier": "test2",
                },
                "count": 67890,
            }
        ])


class AggregationViewTestCase(DjangoTestCase):
    """
    Unit tests for the aggregation views
    These tests try different combinations of allowed aggregations and
    group_by's to test their correctness
    """

    @skip('NotImplemented')
    def test_view_setup(self):
        """
        test for view construction
        """
        raise NotImplementedError()
