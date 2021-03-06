import os
from django.conf import settings
from django.core.management import BaseCommand, call_command
from django.apps.registry import apps as project_apps


class Command(BaseCommand):
    help = 'Compile locale .po files for applications of project.'

    def _get_paths_of_apps(self):
        result = []
        for app in project_apps.app_configs.keys() + ['.']:
            if app == '.':
                path = settings.BASE_DIR
            else:
                path = os.path.abspath(project_apps.app_configs[app].path)
            assert os.path.isdir(path)
            if not path.startswith(settings.BASE_DIR):
                continue
            if not os.path.isdir(os.path.join(path, 'locale').replace('\\', '/')):
                continue
            result.append(path)
        if not result:
            self.stdout.write('Apps not found.')
            exit(1)
        return list(set(result))

    def handle(self, *args, **options):
        for path in self._get_paths_of_apps():
            os.chdir(path)
            self.stdout.write('chdir {}'.format(path))
            call_command('compilemessages')
