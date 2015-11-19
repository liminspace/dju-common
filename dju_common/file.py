import os
from cStringIO import StringIO
from django.core.files.uploadedfile import InMemoryUploadedFile


def truncate_file(f):
    """
    Clear uploaded file and allow write to it.
    Only for not too big files!!!
    Also can clear simple opened file.
    Examples:
        truncate_file(request.FILES['file'])

        with open('/tmp/file', 'rb+') as f:
            truncate_file(f)
    """
    if isinstance(f, InMemoryUploadedFile):
        f.file = StringIO()
    else:
        f.seek(0)
        f.truncate(0)


def make_dirs_for_file_path(file_path, mode=0o775):
    """
    Make dirs for file file_path, if these dirs are not exist.
    """
    dirname = os.path.dirname(file_path)
    if not os.path.exists(dirname):
        os.makedirs(dirname, mode=mode)
