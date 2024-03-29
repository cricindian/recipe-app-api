import time

from django.db import connections
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Django command to pause execution until db is available."""

    def handle(self, *args, **options):
        self.stdout.write("waiting for databse")
        dbconn = None
        while not dbconn:
            try:
                dbconn = connections['default']
            except OperationalError:
                self.stdout.write("DB unavailable , waiting 1 sec")
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS("DB is available now "))
