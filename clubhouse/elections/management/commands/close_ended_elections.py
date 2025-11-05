# File: elections/management/commands/close_ended_elections.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from elections.models import Election

class Command(BaseCommand):
    help = "Close any elections past end_at and set leader."

    def handle(self, *args, **options):
        now = timezone.now()
        ended = Election.objects.filter(end_at__lt=now)
        for e in ended:
            winner = e.finalize_and_set_leader()
            self.stdout.write(self.style.SUCCESS(f"Finalized election {e.id}, leader: {winner}"))
