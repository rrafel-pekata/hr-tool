"""Receive a base64-encoded tar.gz of media/ from stdin and extract it."""
import base64
import io
import sys
import tarfile

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Load media files from base64-encoded tar.gz on stdin'

    def handle(self, *args, **options):
        self.stdout.write('Reading base64 data from stdin...')
        b64_data = sys.stdin.read().strip()
        raw = base64.b64decode(b64_data)
        self.stdout.write(f'Received {len(raw)} bytes, extracting...')

        media_root = str(settings.MEDIA_ROOT)
        with tarfile.open(fileobj=io.BytesIO(raw), mode='r:gz') as tar:
            tar.extractall(path=media_root)
            names = tar.getnames()

        self.stdout.write(self.style.SUCCESS(f'Extracted {len(names)} files to {media_root}'))
