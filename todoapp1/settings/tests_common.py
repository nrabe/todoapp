from django.conf import settings
from django.test.runner import DiscoverRunner


class NoDbTestRunner(DiscoverRunner):
    def setup_test_environment(self, **kwargs):
        '''Override STATICFILES_STORAGE and pipeline DEBUG.'''
        # from pipeline.conf import settings as pipeline_settings
        t = settings.DEBUG
        super(NoDbTestRunner, self).setup_test_environment(**kwargs)
        settings.DEBUG = t
        # settings.STATICFILES_STORAGE = 'pipeline.storage.PipelineCachedStorage'
        # pipeline_settings.DEBUG = False

    def setup_databases(self, **kwargs):
        """ Override the database creation defined in parent class, skips DB creation """
        pass

    def teardown_databases(self, old_config, **kwargs):
        """ Override the database teardown defined in parent class, skips DB destruction """
        pass
