# If on Python 2.X
from __future__ import print_function

import pysolr
from django.conf import settings

from solr.tasks import BaseTaskIndexing

from iati_synchroniser.models import Dataset
from solr.dataset.indexing import DatasetIndexing

solr = pysolr.Solr(
    '{url}/{core}'.format(
        url=settings.SOLR.get('url'),
        core=settings.SOLR.get('cores').get('dataset')
    ), always_commit=True
)


class DatasetTaskIndexing(BaseTaskIndexing):
    indexing = DatasetIndexing
    model = Dataset
    solr = solr
