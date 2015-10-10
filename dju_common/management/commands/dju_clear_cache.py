from django.core.cache import cache
from dju_common.management import LoggingBaseCommand


class Command(LoggingBaseCommand):
    help = 'Clear cache.'

    def handle(self, *args, **options):
        self.log('Clear cache...')
        cache.clear()
        self.log('Done')
