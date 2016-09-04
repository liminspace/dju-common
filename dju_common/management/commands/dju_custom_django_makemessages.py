from django.core.management.commands import makemessages


class Command(makemessages.Command):
    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument('--add-source-dir', action='append', dest='additional_source_dirs',
                            default=[], metavar='DIR', help='Additional source directory.')

    def handle(self, *args, **options):
        self.additional_source_dirs = options['additional_source_dirs']
        super(Command, self).handle(*args, **options)

    def find_files(self, root):
        files = super(Command, self).find_files(root)
        print 'FILES 1', files
        for d in self.additional_source_dirs:
            files.extend(super(Command, self).find_files(d))
        print 'FILES 2', files
        return sorted(files)
