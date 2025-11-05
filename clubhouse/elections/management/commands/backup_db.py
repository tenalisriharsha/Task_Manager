# File: core/management/commands/backup_db.py
from django.core.management.base import BaseCommand
from django.conf import settings
from pathlib import Path
from datetime import datetime
import shutil

class Command(BaseCommand):
    help = "Copy db.sqlite3 into backups/ with timestamp."

    def handle(self, *args, **options):
        db = Path(settings.BASE_DIR) / 'db.sqlite3'
        backups = Path(settings.BASE_DIR) / 'backups'
        backups.mkdir(exist_ok=True)
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        dest = backups / f'db_{ts}.sqlite3'
        shutil.copy2(db, dest)
        self.stdout.write(self.style.SUCCESS(f"Backed up DB to {dest}"))
