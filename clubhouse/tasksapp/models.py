# File: tasksapp/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, timedelta

POINTS_APPROVED = 10
POINTS_LATE_PENALTY = -10
POINTS_PER_STAR = 2

def monday_of_week(d: date):
    return d - timedelta(days=(d.weekday()))  # Monday is 0

class Task(models.Model):
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    week_start = models.DateField()  # Monday
    due_at = models.DateTimeField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks_created')

    def __str__(self):
        return f"{self.title} ({self.week_start})"

class Assignment(models.Model):
    STATUS_ASSIGNED = 'ASSIGNED'
    STATUS_SUBMITTED = 'SUBMITTED'
    STATUS_APPROVED = 'APPROVED'
    STATUS_CHOICES = [
        (STATUS_ASSIGNED, 'Assigned'),
        (STATUS_SUBMITTED, 'Submitted'),
        (STATUS_APPROVED, 'Approved'),
    ]
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='assignments')
    assignee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assignments')
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default=STATUS_ASSIGNED)
    submitted_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    due_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='approved_assignments')
    stars_awarded = models.IntegerField(default=0)
    points_awarded = models.IntegerField(default=0)
    late_penalized = models.BooleanField(default=False)
    rolled_from = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='rolls')

    class Meta:
        unique_together = ('task', 'assignee')

    def __str__(self):
        return f"{self.task.title} -> {self.assignee.username}"

    def save(self, *args, **kwargs):
        # Ensure per-assignment due_at is set (defaults from task on first save)
        if self.due_at is None and self.task_id:
            self.due_at = self.task.due_at
        super().save(*args, **kwargs)

    def mark_submitted(self):
        self.status = self.STATUS_SUBMITTED
        self.submitted_at = timezone.now()
        self.save()

    def approve(self, approver: User):
        self.status = self.STATUS_APPROVED
        self.approved_at = timezone.now()
        self.approved_by = approver
        base = POINTS_APPROVED
        bonus = self.stars_awarded * POINTS_PER_STAR
        self.points_awarded = base + bonus
        self.save()
        # update profile totals
        p = self.assignee.profile
        p.points_total += self.points_awarded
        p.stars_total += self.stars_awarded
        p.save()

    def award_star(self):
        self.stars_awarded += 1
        self.save()

    def is_overdue(self):
        """Return True if not approved and past its due time."""
        if self.approved_at is not None:
            return False
        if not self.due_at:
            return False
        return timezone.now() > self.due_at

    def apply_late_penalty_once(self):
        """Apply -10 once to the assignee's profile when overdue; no-op if already applied."""
        if self.late_penalized:
            return False
        p = self.assignee.profile
        p.points_total = (p.points_total or 0) + POINTS_LATE_PENALTY
        p.save(update_fields=['points_total'])
        self.late_penalized = True
        self.save(update_fields=['late_penalized'])
        return True
