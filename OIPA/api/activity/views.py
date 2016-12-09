from rest_framework.generics import ListAPIView, RetrieveAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView, GenericAPIView
from rest_framework.filters import DjangoFilterBackend
from rest_framework import mixins

from api.generics.views import SaveAllSerializer
from api.activity import serializers as activity_serializers
from api.activity import filters
from api.generics.filters import DistanceFilter
from api.generics.filters import SearchFilter
from api.generics.views import DynamicListView, DynamicDetailView, DynamicListCRUDView, DynamicDetailCRUDView
from api.transaction.serializers import TransactionSerializer
from api.activity.tree_serializers import ActivityTree
from api.transaction.filters import TransactionFilter

from api.aggregation.views import AggregationView, Aggregation, GroupBy

from django.db.models import Count, Sum, F

from geodata.models import Country
from geodata.models import Region

import iati.models as iati_models
from iati.transaction.models import Transaction
from iati.models import Activity, ActivityReportingOrganisation
from iati.models import Sector
from iati.models import ActivityStatus
from iati.models import PolicyMarker
from iati.models import CollaborationType
from iati.models import DocumentCategory
from iati.models import FlowType
from iati.models import AidType
from iati.models import FinanceType
from iati.models import TiedStatus
from iati.models import ActivityParticipatingOrganisation
from iati.models import OrganisationType
from iati.models import Organisation
from iati.models import PolicySignificance

from api.activity.serializers import CodelistSerializer
from api.country.serializers import CountrySerializer
from api.region.serializers import RegionSerializer
from api.sector.serializers import SectorSerializer
from api.organisation.serializers import OrganisationSerializer



class ActivityAggregations(AggregationView):
    """
    Returns aggregations based on the item grouped by, and the selected aggregation.

    ## Group by options

    API request has to include `group_by` parameter.
    
    This parameter controls result aggregations and
    can be one or more (comma separated values) of:

    - `recipient_country`
    - `recipient_region`
    - `sector`
    - `related_activity`
    - `reporting_organisation`
    - `participating_organisation`
    - `participating_organisation_type`
    - `document_link_category`
    - `activity_status`
    - `collaboration_type`

    ## Aggregation options

    API request has to include `aggregations` parameter.
    
    This parameter controls result aggregations and
    can be one or more (comma separated values) of:

    - `count`
    - `count_distinct`

    ## Request parameters

    All filters available on the Activity List, can be used on aggregations.

    """

    queryset = Activity.objects.all()

    filter_backends = (SearchFilter, DjangoFilterBackend,)
    filter_class = filters.ActivityFilter

    allowed_aggregations = (
        Aggregation(
            query_param='count',
            field='count',
            annotate=Count('id'),
        ),
        Aggregation(
            query_param='count_distinct',
            field='count',
            annotate=Count('id', distinct=True),
        ),
    )

    allowed_groupings = (
        GroupBy(
            query_param="recipient_country",
            fields="recipient_country",
            queryset=Country.objects.all(),
            serializer=CountrySerializer,
            serializer_fields=('url', 'code', 'name', 'location'),
            name_search_field='recipient_country__name',
            renamed_name_search_field='recipient_country_name',
        ),  
        GroupBy(
            query_param="recipient_region",
            fields="recipient_region",
            queryset=Region.objects.all(),
            serializer=RegionSerializer,
            serializer_fields=('url', 'code', 'name', 'location'),
            name_search_field="recipient_region__name",
            renamed_name_search_field="recipient_region_name",
        ),
        GroupBy(
            query_param="sector",
            fields="sector",
            queryset=Sector.objects.all(),
            serializer=SectorSerializer,
            serializer_fields=('url', 'code', 'name', 'location'),
            name_search_field="sector__name",
            renamed_name_search_field="sector_name",
        ),
        GroupBy(
            query_param="related_activity",
            fields=("relatedactivity__ref_activity__id"),
            renamed_fields="related_activity",
        ),
        GroupBy(
            query_param="reporting_organisation",
            fields="reporting_organisations__normalized_ref",
            renamed_fields="reporting_organisation",
            queryset=Organisation.objects.all(),
            serializer=OrganisationSerializer,
            serializer_main_field='organisation_identifier',
            name_search_field="reporting_organisations__organisation__primary_name",
            renamed_name_search_field="reporting_organisation_name"
        ),
        GroupBy(
            query_param="participating_organisation",
            fields=("participating_organisations__primary_name", "participating_organisations__normalized_ref"),
            renamed_fields=("participating_organisation", "participating_organisation_ref"),
            queryset=ActivityParticipatingOrganisation.objects.all(),
            name_search_field="participating_organisations__primary_name",
            renamed_name_search_field="participating_organisation_name"
        ),
        GroupBy(
            query_param="participating_organisation_type",
            fields="participating_organisations__type",
            renamed_fields="participating_organisation_type",
            queryset=OrganisationType.objects.all(),
            serializer=CodelistSerializer,
            name_search_field="participating_organisations__type__name",
            renamed_name_search_field="participating_organisations_type_name"
        ),
        GroupBy(
            query_param="document_link_category",
            fields="documentlink__categories__code",
            renamed_fields="document_link_category",
            queryset=DocumentCategory.objects.all(),
            serializer=CodelistSerializer,
            name_search_field="documentlink__categories__name",
            renamed_name_search_field="document_link_category_name"
        ),
        GroupBy(
            query_param="activity_status",
            fields="activity_status",
            queryset=ActivityStatus.objects.all(),
            serializer=CodelistSerializer,
            name_search_field="activity_status__name",
            renamed_name_search_field="activity_status_name"
        ),
        GroupBy(
            query_param="collaboration_type",
            fields="collaboration_type",
            renamed_fields="collaboration_type",
            queryset=CollaborationType.objects.all(),
            serializer=CodelistSerializer,
            name_search_field="collaboration_type__name",
            renamed_name_search_field="collaboration_type_name"
        ),
        GroupBy(
            query_param="policy_marker_significance",
            fields="activitypolicymarker__significance",
            renamed_fields="significance",
            queryset=PolicySignificance.objects.all(),
            serializer=CodelistSerializer,
        ),
    )


class ActivityList(DynamicListCRUDView):
    """
    Returns a list of IATI Activities stored in OIPA.

    ## Request parameters
    - `activity_id` (*optional*): Comma separated list of activity id's.
    - `activity_scope` (*optional*): Comma separated list of iso2 country codes.
    - `recipient_country` (*optional*): Comma separated list of iso2 country codes.
    - `recipient_region` (*optional*): Comma separated list of region codes.
    - `recipient_region_not_in` (*optional*): Comma separated list of region codes the activity should not be in.
    - `sector` (*optional*): Comma separated list of 5-digit sector codes.
    - `sector_category` (*optional*): Comma separated list of 3-digit sector codes.
    - `reporting_organisation` (*optional*): Comma separated list of organisation id's.
    - `participating_organisation` (*optional*): Comma separated list of organisation id's.
    - `total_budget_value_lte` (*optional*): Less then or equal total budget value
    - `total_budget_value_gte` (*optional*): Greater then or equal total budget value
    - `total_child_budget_value_lte` (*optional*): Less then or equal total child budget value
    - `total_child_budget_value_gte` (*optional*): Greater then or equal total child budget value
    - `planned_start_date_lte` (*optional*): Date in YYYY-MM-DD format, returns activities earlier or equal to the given activity date.
    - `planned_start_date_gte` (*optional*): Date in YYYY-MM-DD format, returns activities later or equal to the given activity date.
    - `actual_start_date_lte` (*optional*): Date in YYYY-MM-DD format, returns activities earlier or equal to the given activity date.
    - `actual_start_date_gte` (*optional*): Date in YYYY-MM-DD format, returns activities later or equal to the given activity date.
    - `planned_end_date_lte` (*optional*): Date in YYYY-MM-DD format, returns activities earlier or equal to the given activity date.
    - `planned_end_date_gte` (*optional*): Date in YYYY-MM-DD format, returns activities later or equal to the given activity date.
    - `actual_end_date_lte` (*optional*): Date in YYYY-MM-DD format, returns activities earlier or equal to the given activity date.
    - `actual_end_date_gte` (*optional*): Date in YYYY-MM-DD format, returns activities later or equal to the given activity date.
    - `activity_status` (*optional*): Comma separated list of activity statuses.
    - `hierarchy` (*optional*): Comma separated list of activity hierarchies.
    - `related_activity_id` (*optional*): Comma separated list of activity ids. Returns a list of all activities mentioning these activity id's.
    - `related_activity_type` (*optional*): Comma separated list of RelatedActivityType codes.
    - `related_activity_recipient_country` (*optional*): Comma separated list of iso2 country codes.
    - `related_activity_recipient_region` (*optional*): Comma separated list of region codes.
    - `related_activity_sector` (*optional*): Comma separated list of 5-digit sector codes.
    - `related_activity_sector_category` (*optional*): Comma separated list of 3-digit sector codes.
    - `transaction_provider_activity` (*optional*): Comma separated list of activity id's.
    - `transaction_date_year` (*optional*): Comma separated list of years in which the activity should have transactions.

    ## Text search

    API request may include `q` parameter. This parameter controls text search
    and contains expected value.

    By default, searching is performed on:

    - `iati_identifier` the IATI identifier
    - `title` narratives
    - `description` narratives
    - `recipient_country` recipient country code and name
    - `recipient_region` recipient region code and name
    - `reporting_org` ref and narratives
    - `sector` sector code and name
    - `document_link` url, category and title narratives
    - `participating_org` ref and narratives

    To search on subset of these fields the `q_fields` parameter can be used, like so;
    `q_fields=iati_identifier,title,description`

    By default, search only return results if the hit resembles a full word. 
    This can be altered through the `q_lookup` parameter. Options for this parameter are:

    - `exact` (default): Only return results when the query hit is a full word.
    - `startswith`: Also returns results when the word stars with the query. 

    ## Ordering

    API request may include `ordering` parameter. This parameter controls the order in which
    results are returned.

    Results can be ordered by:

    - `title`
    - `planned_start_date`
    - `actual_start_date`
    - `planned_end_date`
    - `actual_end_date`
    - `start_date`
    - `end_date`
    - `activity_budget_value`
    - `activity_incoming_funds_value`
    - `activity_disbursement_value`
    - `activity_expenditure_value`
    - `activity_plus_child_budget_value`

    The user may also specify reverse orderings by prefixing the field name with '-', like so: `-title`

    ## Aggregations

    At the moment there's no direct aggregations on this endpoint.

    The /activities/aggregations endpoint can be used for activity based aggregations.

    ## Result details

    Each item contains summarized information on the activity being shown,
    including the URI to activity details, which contain all information. 
    To show more information in list view the `fields` parameter can be used. Example;
    `fields=activity_id,title,country,any_field`.

    """

    queryset = Activity.objects.all()
    filter_backends = (SearchFilter, DjangoFilterBackend, DistanceFilter, filters.RelatedOrderingFilter,)
    filter_class = filters.ActivityFilter
    serializer_class = activity_serializers.ActivitySerializer

#     fields = (
#         'url', 
#         'iati_identifier', 
#         'title', 
#         'descriptions', 
#         'transactions', 
#         'reporting_organisations')

    always_ordering = 'id'

    ordering_fields = (
        'title',
        'recipient_country',
        'planned_start_date',
        'actual_start_date',
        'planned_end_date',
        'actual_end_date',
        'start_date',
        'end_date',
        'activity_budget_value',
        'activity_incoming_funds_value',
        'activity_disbursement_value',
        'activity_expenditure_value',
        'activity_plus_child_budget_value')


class ActivityDetail(DynamicDetailCRUDView):
    """
    Returns detailed information about Activity.

    ## URI Format

    ```
    /api/activities/{activity_id}
    ```

    ### URI Parameters

    - `activity_id`: Desired activity ID

    ## Extra endpoints

    All information on activity transactions can be found on a separate page:

    - `/api/activities/{activity_id}/transactions/`:
        List of transactions.
    - `/api/activities/{activity_id}/provider-activity-tree/`:
        The upward and downward provider-activity-id traceability tree of this activity.

    ## Request parameters

    - `fields` (*optional*): List of fields to display

    """
    queryset = Activity.objects.all()
    filter_class = filters.ActivityFilter
    serializer_class = activity_serializers.ActivitySerializer

# TODO separate endpoints for expensive fields like ActivityLocations & ActivityResults 08-07-2016


class ActivityTransactions(ListCreateAPIView):
    """
    Returns a list of IATI Activity Transactions stored in OIPA.

    ## URI Format

    ```
    /api/activities/{activity_id}/transactions
    ```

    ### URI Parameters

    - `activity_id`: Desired activity ID

    ## Request parameters:

    - `recipient_country` (*optional*): Recipient countries list.
        Comma separated list of strings.
    - `recipient_region` (*optional*): Recipient regions list.
        Comma separated list of integers.
    - `sector` (*optional*): Sectors list. Comma separated list of integers.
    - `sector_category` (*optional*): Sectors list. Comma separated list of integers.
    - `reporting_organisations` (*optional*): Organisation ID's list.
    - `participating_organisations` (*optional*): Organisation IDs list.
        Comma separated list of strings.
    - `min_total_budget` (*optional*): Minimal total budget value.
    - `max_total_budget` (*optional*): Maximal total budget value.
    - `activity_status` (*optional*):


    - `related_activity_id` (*optional*):
    - `related_activity_type` (*optional*):
    - `related_activity_recipient_country` (*optional*):
    - `related_activity_recipient_region` (*optional*):
    - `related_activity_sector` (*optional*):

    ## Searching is performed on fields:

    - `description`
    - `provider_organisation_name`
    - `receiver_organisation_name`

    """
    serializer_class = TransactionSerializer
    filter_class = TransactionFilter

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return Activity(pk=pk).transaction_set.all()

class ActivityTransactionDetail(RetrieveUpdateDestroyAPIView):
    serializer_class = TransactionSerializer

    def get_object(self):
        pk = self.kwargs.get('id')
        return Transaction.objects.get(pk=pk)


class ActivityReportingOrganisationList(ListCreateAPIView):
    serializer_class = activity_serializers.ReportingOrganisationSerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return Activity(pk=pk).reporting_organisations.all()

class ActivityReportingOrganisationDetail(RetrieveUpdateDestroyAPIView):
    serializer_class = activity_serializers.ReportingOrganisationSerializer

    def get_object(self):
        pk = self.kwargs.get('id')
        return ActivityReportingOrganisation.objects.get(pk=pk)

class ActivityDescriptionList(ListCreateAPIView):
    serializer_class = activity_serializers.DescriptionSerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return Activity(pk=pk).description_set.all()

class ActivityDescriptionDetail(RetrieveUpdateDestroyAPIView):
    serializer_class = activity_serializers.DescriptionSerializer

    def get_object(self):
        pk = self.kwargs.get('id')
        return iati_models.Description.objects.get(pk=pk)

class ActivityParticipatingOrganisationList(ListCreateAPIView):
    serializer_class = activity_serializers.ParticipatingOrganisationSerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return iati_models.Activity(pk=pk).participating_organisations.all()

class ActivityParticipatingOrganisationDetail(RetrieveUpdateDestroyAPIView):
    serializer_class = activity_serializers.ParticipatingOrganisationSerializer

    def get_object(self):
        pk = self.kwargs.get('id')
        return iati_models.ActivityParticipatingOrganisation.objects.get(pk=pk)

class ActivityOtherIdentifierList(ListCreateAPIView):
    serializer_class = activity_serializers.OtherIdentifierSerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return Activity(pk=pk).other_identifier_set.all()

class ActivityOtherIdentifierDetail(RetrieveUpdateDestroyAPIView):
    serializer_class = activity_serializers.OtherIdentifierSerializer

    def get_object(self):
        pk = self.kwargs.get('id')
        return iati_models.OtherIdentifier.objects.get(pk=pk)

class ActivityActivityDateList(ListCreateAPIView):
    serializer_class = activity_serializers.ActivityDateSerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return Activity(pk=pk).activity_date_set.all()

class ActivityActivityDateDetail(RetrieveUpdateDestroyAPIView):
    serializer_class = activity_serializers.ActivityDateSerializer

    def get_object(self):
        pk = self.kwargs.get('id')
        return iati_models.ActivityDate.objects.get(pk=pk)

class ActivityContactInfoList(ListCreateAPIView):
    serializer_class = activity_serializers.ContactInfoSerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return Activity(pk=pk).contact_info_set.all()

class ActivityContactInfoDetail(RetrieveUpdateDestroyAPIView):
    serializer_class = activity_serializers.ContactInfoSerializer

    def get_object(self):
        pk = self.kwargs.get('id')
        return iati_models.ContactInfo.objects.get(pk=pk)

class ActivityRecipientCountryList(ListCreateAPIView):
    serializer_class = activity_serializers.RecipientCountrySerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return iati_models.Activity(pk=pk).recipient_countries.all()

class ActivityRecipientCountryDetail(RetrieveUpdateDestroyAPIView):
    serializer_class = activity_serializers.RecipientCountrySerializer

    def get_object(self):
        pk = self.kwargs.get('id')
        return iati_models.ActivityRecipientCountry.objects.get(pk=pk)

class ActivityRecipientRegionList(ListCreateAPIView):
    serializer_class = activity_serializers.ActivityRecipientRegionSerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return iati_models.Activity(pk=pk).recipient_regions.all()

class ActivityRecipientRegionDetail(RetrieveUpdateDestroyAPIView):
    serializer_class = activity_serializers.ActivityRecipientRegionSerializer

    def get_object(self):
        pk = self.kwargs.get('id')
        return iati_models.ActivityRecipientRegion.objects.get(pk=pk)


class ActivitySectorList(ListCreateAPIView):
    serializer_class = activity_serializers.ActivitySectorSerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return iati_models.Activity(pk=pk).sectors.all()

class ActivitySectorDetail(RetrieveUpdateDestroyAPIView):
    serializer_class = activity_serializers.ActivitySectorSerializer

    def get_object(self):
        pk = self.kwargs.get('id')
        return iati_models.ActivitySector.objects.get(pk=pk)

class ActivityCountryBudgetItemDetail(mixins.RetrieveModelMixin,
                                      mixins.UpdateModelMixin,
                                      mixins.DestroyModelMixin,
                                      mixins.CreateModelMixin,
                                      GenericAPIView):
    serializer_class = activity_serializers.CountryBudgetItemsSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def get_object(self):
        pk = self.kwargs.get('pk')
        return iati_models.CountryBudgetItem.objects.get(activity=pk)

class ActivityBudgetItemList(ListCreateAPIView):
    serializer_class = activity_serializers.BudgetItemSerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return iati_models.Activity(pk=pk).country_budget_items.budgetitem_set.all()

class ActivityBudgetItemDetail(RetrieveUpdateDestroyAPIView):
    serializer_class = activity_serializers.BudgetItemSerializer

    def get_object(self):
        pk = self.kwargs.get('budget_item_id')
        return iati_models.BudgetItem.objects.get(pk=pk)

class ActivityLocationList(ListCreateAPIView):
    serializer_class = activity_serializers.LocationSerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return iati_models.Activity(pk=pk).locations.all()

class ActivityLocationDetail(RetrieveUpdateDestroyAPIView):
    serializer_class = activity_serializers.LocationSerializer

    def get_object(self):
        pk = self.kwargs.get('id')
        return iati_models.Location.objects.get(pk=pk)

class ActivityHumanitarianScopeList(ListCreateAPIView):
    serializer_class = activity_serializers.HumanitarianScopeSerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return iati_models.Activity(pk=pk).humanitarian_scopes.all()

class ActivityHumanitarianScopeDetail(RetrieveUpdateDestroyAPIView):
    serializer_class = activity_serializers.HumanitarianScopeSerializer

    def get_object(self):
        pk = self.kwargs.get('id')
        return iati_models.HumanitarianScope.objects.get(pk=pk)


class ActivityPolicyMarkerList(ListCreateAPIView):
    serializer_class = activity_serializers.ActivityPolicyMarkerSerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return iati_models.Activity(pk=pk).policy_markers.all()

class ActivityPolicyMarkerDetail(RetrieveUpdateDestroyAPIView):
    serializer_class = activity_serializers.ActivityPolicyMarkerSerializer

    def get_object(self):
        pk = self.kwargs.get('id')
        return iati_models.ActivityPolicyMarker.objects.get(pk=pk)

class ActivityBudgetList(ListCreateAPIView):
    serializer_class = activity_serializers.BudgetSerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return iati_models.Activity(pk=pk).budgets.all()

class ActivityBudgetDetail(RetrieveUpdateDestroyAPIView):
    serializer_class = activity_serializers.BudgetSerializer

    def get_object(self):
        pk = self.kwargs.get('id')
        return iati_models.Budget.objects.get(pk=pk)


class ActivityPlannedDisbursementList(ListCreateAPIView):
    serializer_class = activity_serializers.PlannedDisbursementSerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return iati_models.Activity(pk=pk).planned_disbursements.all()

class ActivityPlannedDisbursementDetail(RetrieveUpdateDestroyAPIView):
    serializer_class = activity_serializers.PlannedDisbursementSerializer

    def get_object(self):
        pk = self.kwargs.get('id')
        return iati_models.ActivityPlannedDisbursement.objects.get(pk=pk)

class ActivityDocumentLinkList(ListCreateAPIView):
    serializer_class = activity_serializers.DocumentLinkSerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return iati_models.Activity(pk=pk).document_links.all()

class ActivityDocumentLinkDetail(RetrieveUpdateDestroyAPIView):
    serializer_class = activity_serializers.DocumentLinkSerializer

    def get_object(self):
        pk = self.kwargs.get('id')
        return iati_models.ActivityDocumentLink.objects.get(pk=pk)

class ActivityRelatedActivityList(ListCreateAPIView):
    serializer_class = activity_serializers.RelatedActivitySerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return iati_models.Activity(pk=pk).related_activities.all()

class ActivityRelatedActivityDetail(RetrieveUpdateDestroyAPIView):
    serializer_class = activity_serializers.RelatedActivitySerializer

    def get_object(self):
        pk = self.kwargs.get('id')
        return iati_models.ActivityRelatedActivity.objects.get(pk=pk)

class ActivityLegacyDataList(ListCreateAPIView):
    serializer_class = activity_serializers.LegacyDataSerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return iati_models.Activity(pk=pk).legacydata_set.all()

class ActivityLegacyDataDetail(RetrieveUpdateDestroyAPIView):
    serializer_class = activity_serializers.LegacyDataSerializer

    def get_object(self):
        pk = self.kwargs.get('id')
        return iati_models.LegacyData.objects.get(pk=pk)

class ActivityResultList(ListCreateAPIView):
    serializer_class = activity_serializers.ResultSerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return iati_models.Activity(pk=pk).results.all()

class ActivityResultDetail(RetrieveUpdateDestroyAPIView):
    serializer_class = activity_serializers.ResultSerializer

    def get_object(self):
        pk = self.kwargs.get('id')
        return iati_models.Result.objects.get(pk=pk)

class ResultIndicatorList(ListCreateAPIView):
    serializer_class = activity_serializers.ResultIndicatorSerializer

    def get_queryset(self):
        pk = self.kwargs.get('activity_id')
        return iati_models.Activity(pk=pk).result_indicators.all()

class ResultIndicatorDetail(RetrieveUpdateDestroyAPIView):
    serializer_class = activity_serializers.ResultIndicatorSerializer

    def get_object(self):
        pk = self.kwargs.get('resultindicator_id')
        return iati_models.ResultIndicator.objects.get(pk=pk)

class ResultIndicatorReferenceList(ListCreateAPIView):
    serializer_class = activity_serializers.ResultIndicatorReferenceSerializer

    def get_queryset(self):
        pk = self.kwargs.get('resultindicator_id')
        return iati_models.Activity(pk=pk).result_indicator_references.all()

class ResultIndicatorReferenceDetail(RetrieveUpdateDestroyAPIView):
    serializer_class = activity_serializers.ResultIndicatorReferenceSerializer

    def get_object(self):
        pk = self.kwargs.get('reference_id')
        return iati_models.ResultIndicatorReference.objects.get(pk=pk)

class ResultIndicatorPeriodList(ListCreateAPIView):
    serializer_class = activity_serializers.ResultIndicatorPeriodSerializer

    def get_queryset(self):
        pk = self.kwargs.get('resultindicator_id')
        return iati_models.Activity(pk=pk).result_indicator_periods.all()

class ResultIndicatorPeriodDetail(RetrieveUpdateDestroyAPIView):
    serializer_class = activity_serializers.ResultIndicatorPeriodSerializer

    def get_object(self):
        pk = self.kwargs.get('period_id')
        return iati_models.ResultIndicatorPeriod.objects.get(pk=pk)

class ResultIndicatorPeriodActualLocationList(ListCreateAPIView):
    serializer_class = activity_serializers.ResultIndicatorPeriodActualLocationSerializer

    def get_queryset(self):
        pk = self.kwargs.get('resultindicator_id')
        return iati_models.Activity(pk=pk).result_indicator_period_actual_locations.all()

class ResultIndicatorPeriodActualLocationDetail(RetrieveUpdateDestroyAPIView):
    serializer_class = activity_serializers.ResultIndicatorPeriodActualLocationSerializer

    def get_object(self):
        pk = self.kwargs.get('actual_location_id')
        return iati_models.ResultIndicatorPeriodActualLocation.objects.get(pk=pk)

class ResultIndicatorPeriodTargetLocationList(ListCreateAPIView):
    serializer_class = activity_serializers.ResultIndicatorPeriodTargetLocationSerializer

    def get_queryset(self):
        pk = self.kwargs.get('resultindicator_id')
        return iati_models.Activity(pk=pk).result_indicator_period_target_locations.all()

class ResultIndicatorPeriodTargetLocationDetail(RetrieveUpdateDestroyAPIView):
    serializer_class = activity_serializers.ResultIndicatorPeriodTargetLocationSerializer

    def get_object(self):
        pk = self.kwargs.get('target_location_id')
        return iati_models.ResultIndicatorPeriodTargetLocation.objects.get(pk=pk)

class ResultIndicatorPeriodActualDimensionList(ListCreateAPIView):
    serializer_class = activity_serializers.ResultIndicatorPeriodActualDimensionSerializer

    def get_queryset(self):
        pk = self.kwargs.get('resultindicator_id')
        return iati_models.Activity(pk=pk).result_indicator_period_actual_dimensions.all()

class ResultIndicatorPeriodActualDimensionDetail(RetrieveUpdateDestroyAPIView):
    serializer_class = activity_serializers.ResultIndicatorPeriodActualDimensionSerializer

    def get_object(self):
        pk = self.kwargs.get('actual_dimension_id')
        return iati_models.ResultIndicatorPeriodActualDimension.objects.get(pk=pk)

class ResultIndicatorPeriodTargetDimensionList(ListCreateAPIView):
    serializer_class = activity_serializers.ResultIndicatorPeriodTargetDimensionSerializer

    def get_queryset(self):
        pk = self.kwargs.get('resultindicator_id')
        return iati_models.Activity(pk=pk).result_indicator_period_target_dimensions.all()

class ResultIndicatorPeriodTargetDimensionDetail(RetrieveUpdateDestroyAPIView):
    serializer_class = activity_serializers.ResultIndicatorPeriodTargetDimensionSerializer

    def get_object(self):
        pk = self.kwargs.get('target_dimension_id')
        return iati_models.ResultIndicatorPeriodTargetDimension.objects.get(pk=pk)

class ActivityConditionsDetail(SaveAllSerializer):
    serializer_class = activity_serializers.ConditionsSerializer

    def get_object(self):
        pk = self.kwargs.get('pk')
        return iati_models.Conditions.objects.get(activity=pk)

class ActivityConditionList(ListCreateAPIView):
    serializer_class = activity_serializers.ConditionSerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return iati_models.Activity(pk=pk).country_conditions.budgetitem_set.all()

class ActivityConditionDetail(RetrieveUpdateDestroyAPIView):
    serializer_class = activity_serializers.ConditionSerializer

    def get_object(self):
        pk = self.kwargs.get('condition_id')
        return iati_models.Condition.objects.get(pk=pk)

class ActivityCrsAddList(ListCreateAPIView):
    serializer_class = activity_serializers.CrsAddSerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return iati_models.Activity(pk=pk).crsadd_set.all()

class ActivityCrsAddDetail(RetrieveUpdateDestroyAPIView):
    serializer_class = activity_serializers.CrsAddSerializer

    def get_object(self):
        pk = self.kwargs.get('id')
        return iati_models.CrsAdd.objects.get(pk=pk)

class ActivityCrsAddOtherFlagsList(ListCreateAPIView):
    serializer_class = activity_serializers.CrsAddOtherFlagsSerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return iati_models.Activity(pk=pk).crsadd_set.all()

class ActivityCrsAddOtherFlagsDetail(RetrieveUpdateDestroyAPIView):
    serializer_class = activity_serializers.CrsAddOtherFlagsSerializer

    def get_object(self):
        pk = self.kwargs.get('id')
        return iati_models.CrsAddOtherFlags.objects.get(pk=pk)

class ActivityFssList(ListCreateAPIView):
    serializer_class = activity_serializers.FssSerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return iati_models.Activity(pk=pk).crsadd_set.all()

class ActivityFssDetail(RetrieveUpdateDestroyAPIView):
    serializer_class = activity_serializers.FssSerializer

    def get_object(self):
        pk = self.kwargs.get('id')
        return iati_models.Fss.objects.get(pk=pk)

class ActivityFssForecastList(ListCreateAPIView):
    serializer_class = activity_serializers.FssForecastSerializer

    def get_queryset(self):
        pk = self.kwargs.get('id')
        return iati_models.Fss(pk=pk).fssforecast_set.all()

class ActivityFssForecastDetail(RetrieveUpdateDestroyAPIView):
    serializer_class = activity_serializers.FssForecastSerializer

    def get_object(self):
        pk = self.kwargs.get('forecast_id')
        return iati_models.FssForecast.objects.get(pk=pk)

class ActivityProviderActivityTree(DynamicDetailView):
    """
    Returns the upward and downward traceability tree of this activity. Field specification:
    
    - `providing activities`: The upward three of all activities that are listed as provider-activity-id in this activity.
    - `receiving activities`: The downward tree of all activities that list this activity as provider-activity-id.

    ## URI Format

    ```
    /api/activities/{activity_id}/provider-activity-tree
    ```
    """
    serializer_class = ActivityTree
    queryset = Activity.objects.all()



