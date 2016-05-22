import sys
import os
import subprocess
import errno
from copy import copy
from django.core.management import BaseCommand, CommandError
from django.conf import settings
from django.apps.registry import apps as project_apps


class Command(BaseCommand):
    help = 'Make locale .po files for applications of project.'

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument('--application', '-a', action='append', dest='apps', default=[], metavar='APPNAME',
                            help='The application name. If not set then using all project app. '
                                 '(Project locale named ".")')
        parser.add_argument('--locale', '-l', action='append', dest='locale', default=None,
                            help='Creates or updates the message files for the given locale(s) (e.g. pt_BR). '
                                 'Can be used multiple times, accepts a comma-separated list of locale names.')
        parser.add_argument('--domain', '-d', action='append', dest='domain', default=None,
                            help='The domain of the message files (default: ["django", "djangojs"]).')
        parser.add_argument('--extension', '-e', action='append', dest='extensions', default=None,
                            help='The file extension(s) to examine (default: "html,txt,rml", or "js" if the domain is '
                                 '"djangojs"). Separate multiple extensions with commas, or use -e multiple times.')

    def _get_paths_of_apps(self, apps):
        result = []
        for app in apps or (project_apps.app_configs.keys() + ['.']):
            if app == '.':
                path = settings.BASE_DIR
            else:
                path = os.path.abspath(project_apps.app_configs[app].path)
            assert os.path.isdir(path)
            if not path.startswith(settings.BASE_DIR):
                if apps:
                    raise CommandError('App "%s" is not in project path.' % app)
                continue
            if not os.path.isdir(os.path.join(path, 'locale').replace('\\', '/')):
                self.stdout.write('App "%s" ignore because locale path not found.' % app)
                continue
            result.append(path)
        if not result:
            exit('App list is empty.')
        return list(set(result))

    @staticmethod
    def _get_paths_of_apps_with_locale():
        result = []
        for app in project_apps.app_configs.values():
            app_path = os.path.abspath(app.path)
            assert os.path.isdir(app_path)
            if not app_path.startswith(settings.BASE_DIR):
                continue
            if not os.path.isdir(os.path.join(app_path, 'locale').replace('\\', '/')):
                continue
            result.append(app_path.rstrip('/'))
        return result

    @staticmethod
    def _make_locale_dirs(path):
        for lang_code, lang_name in settings.LANGUAGES:
            dn = os.path.join(path, 'locale', lang_code, 'LC_MESSAGES').replace('\\', '/')
            try:
                os.makedirs(dn, 0775)
            except OSError, e:
                if not (e.errno == errno.EEXIST and os.path.isdir(dn)):
                    raise e

    def handle(self, *args, **options):
        paths = self._get_paths_of_apps(options['apps'])
        command_base = [sys.executable, os.path.join(settings.BASE_DIR, 'manage.py').replace('\\', '/'), 'makemessages']
        if options['locale']:
            for lang in options['locale']:
                command_base.extend(['-l', lang])
        else:
            command_base.append('-a')
        if not options['domain']:
            options['domain'] = ['django', 'djangojs']
        for path in paths:
            os.chdir(path)
            for domain in options['domain']:
                command = copy(command_base)
                extensions = copy(options['extensions'])
                command.extend(['-d', domain])
                if not extensions:
                    if domain == 'django':
                        extensions = ['html', 'txt', 'rml', 'py']
                    elif domain == 'djangojs':
                        extensions = ['js']
                if extensions:
                    command.extend(['-e', ','.join(extensions)])
                if path == settings.BASE_DIR:
                    for app_path in self._get_paths_of_apps_with_locale():
                        command.extend(['-i', '{}/*'.format(app_path)])
                self.stdout.write('[%s] %s' % (path, ' '.join(command)))
                self._make_locale_dirs(path)
                subprocess.call(command)
