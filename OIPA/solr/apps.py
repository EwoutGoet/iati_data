from __future__ import unicode_literals

from django.apps import AppConfig


class SolrConfig(AppConfig):
    name = 'solr'
    verbose_name = 'SOLR'

    def ready(self):
        import solr.signals  # NOQA: F401
