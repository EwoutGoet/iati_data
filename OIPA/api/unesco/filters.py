from django.db.models import Q
from django_filters import CharFilter, DateFilter, NumberFilter

from api.generics.filters import (
    CommaSeparatedCharFilter, StartsWithInCommaSeparatedCharFilter,
    TogetherFilterSet
)
from unesco.models import TransactionBalance


class TransactionBalanceFilter(TogetherFilterSet):

    reporting_organisation_identifier = CommaSeparatedCharFilter(
        field_name='activity__publisher__publisher_iati_id',
        lookup_expr='in')

    recipient_country = CommaSeparatedCharFilter(
        lookup_expr='in',
        name='activity__recipient_country__code')

    recipient_region = CommaSeparatedCharFilter(
        lookup_expr='in',
        field_name='activity__recipient_region__code')

    sector = CommaSeparatedCharFilter(
        lookup_expr='in',
        field_name='activity__sector__code')

    sector_startswith_in = StartsWithInCommaSeparatedCharFilter(
        lookup_expr='startswith',
        field_name='activity__sector__code')

    transactionbalance_total_budget_lte = NumberFilter(
        lookup_expr='lte',
        field_name='total_budget')

    transactionbalance_total_budget_gte = NumberFilter(
        lookup_expr='gte',
        field_name='total_budget')

    transactionbalance_total_expenditure_lte = NumberFilter(
        lookup_expr='lte',
        field_name='total_expenditure')

    transactionbalance_total_expenditure_gte = NumberFilter(
        lookup_expr='gte',
        field_name='total_expenditure')

    activity_status = CommaSeparatedCharFilter(
        lookup_expr='in',
        field_name='activity__activity_status')

    planned_start_date_lte = DateFilter(
        lookup_expr='lte',
        field_name='activity__planned_start')

    planned_start_date_gte = DateFilter(
        lookup_expr='gte',
        field_name='activity__planned_start')

    planned_end_date_lte = DateFilter(
        lookup_expr='lte',
        field_name='activity__planned_end')

    planned_end_date_gte = DateFilter(
        lookup_expr='gte',
        field_name='activity__planned_end')

    activity_scope = CommaSeparatedCharFilter(
        lookup_expr='in',
        field_name='activity__scope__code')

    sector_vocabulary = CommaSeparatedCharFilter(
        lookup_expr='in',
        field_name='activity__sector__vocabulary__code'
    )

    participating_organisations = CommaSeparatedCharFilter(
        lookup_expr='in',
        field_name='activity__participating_organisations__primary_name')

    def filter_recipient_location(self, queryset, name, value):
        if value == 'countries':
            return queryset.filter(
                Q(activity__activityrecipientcountry__isnull=False)
            )
        elif value == 'regions':
            return queryset.filter(
                Q(activity__activityrecipientregion__isnull=False) &
                ~Q(activity__activityrecipientregion__region__code='99')
            )
        elif value == 'global':
            return queryset.filter(
                Q(activity__activityrecipientregion__region__code='99')
            )

    recipient_location = CharFilter(method='filter_recipient_location')

    class Meta:
        model = TransactionBalance
        fields = '__all__'
