from django.core.management.commands import makemessages


class Command(makemessages.Command):
    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument('--source-dir', action='append', dest='additional_source_dirs',
                            default=[], metavar='DIR', help='Additional source directory.')

    def handle(self, *args, **options):
        if options['additional_source_dirs']:
            self.xgettext_options = (
                makemessages.Command.xgettext_options +
                ['--directory={}'.format(d) for d in options['additional_source_dirs']]
            )
        super(Command, self).handle(*args, **options)
