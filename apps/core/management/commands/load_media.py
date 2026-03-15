"""Download and extract a tar.gz of media files from a URL."""
import io
import tarfile

import requests
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Load media files from a tar.gz URL'

    def add_arguments(self, parser):
        parser.add_argument('url', type=str, help='URL of tar.gz file')

    def handle(self, *args, **options):
        url = options['url']
        self.stdout.write(f'Downloading {url}...')
        resp = requests.get(url, timeout=120)
        resp.raise_for_status()
        self.stdout.write(f'Received {len(resp.content)} bytes, extracting...')

        media_root = str(settings.MEDIA_ROOT)
        with tarfile.open(fileobj=io.BytesIO(resp.content), mode='r:gz') as tar:
            tar.extractall(path=media_root)
            names = tar.getnames()

        self.stdout.write(self.style.SUCCESS(f'Extracted {len(names)} files to {media_root}'))
