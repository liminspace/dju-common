import os

from django.core.management.commands import makemessages


class Command(makemessages.Command):
    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument('--add-source-dir', action='append', dest='additional_source_dirs',
                            default=[], metavar='DIR',
                            help='Additional source directory. For example: "/path/to/src:/path/to/locale"')

    def handle(self, *args, **options):
        self.additional_source_dirs = options['additional_source_dirs']
        super(Command, self).handle(*args, **options)

    def find_files(self, root):
        files = super(Command, self).find_files(root)
        for d in self.additional_source_dirs:
            if ':' in d:
                src_dir, locale_dir = d.split(':', 1)
            else:
                src_dir, locale_dir = d, None
            add_files = super(Command, self).find_files(os.path.abspath(src_dir))
            for add_file in add_files:
                add_file.dirpath = os.path.relpath(add_file.dirpath, os.getcwd())
                if locale_dir:
                    add_file.locale_dir = locale_dir
            files.extend(add_files)
        return sorted(files)
