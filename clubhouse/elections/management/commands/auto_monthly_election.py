# File: elections/management/commands/auto_monthly_election.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from elections.models import Election

def first_monday(dt):
    # dt is naive or aware? We’ll use timezone.localtime to today
    dt = dt.replace(day=1)
    while dt.weekday() != 0:  # Monday
        dt += timedelta(days=1)
    return dt

class Command(BaseCommand):
    help = "Create an election for the first Monday of the current month (09:00–21:00 CT), if not present."

    def handle(self, *args, **options):
        now = timezone.localtime()
        fm = first_monday(now.replace(hour=0, minute=0, second=0, microsecond=0))
        start = timezone.make_aware(datetime(fm.year, fm.month, fm.day, 9, 0))
        end = timezone.make_aware(datetime(fm.year, fm.month, fm.day, 21, 0))
        exists = Election.objects.filter(start_at=start, end_at=end).exists()
        if not exists:
            Election.objects.create(start_at=start, end_at=end)
            self.stdout.write(self.style.SUCCESS(f"Election created: {start} -> {end}"))
        else:
            self.stdout.write("Election already exists for this month.")
