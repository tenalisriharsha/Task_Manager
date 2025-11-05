# File: tasksapp/management/commands/rollover_assignments.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from tasksapp.models import Assignment, Task, monday_of_week, POINTS_LATE_PENALTY

class Command(BaseCommand):
    help = "Rollover incomplete assignments to next week and apply -10 penalty."

    def handle(self, *args, **options):
        now = timezone.now()
        incomplete = Assignment.objects.select_related('task', 'assignee', 'assignee__profile') \
            .filter(task__due_at__lt=now) \
            .exclude(status=Assignment.STATUS_APPROVED)

        for a in incomplete:
            # Penalty
            p = a.assignee.profile
            p.points_total += POINTS_LATE_PENALTY
            p.save()

            # Create next week task (per-member rollover of the same task title)
            next_week = a.task.week_start + timedelta(days=7)
            due_shift = a.task.due_at + timedelta(days=7)
            new_task, _ = Task.objects.get_or_create(
                title=a.task.title,
                description=a.task.description,
                week_start=next_week,
                defaults={'due_at': due_shift, 'created_by': a.task.created_by}
            )
            # Create assignment for same member
            new_a = Assignment.objects.create(
                task=new_task, assignee=a.assignee, rolled_from=a
            )
            self.stdout.write(f"Rolled {a} to {new_a}")
