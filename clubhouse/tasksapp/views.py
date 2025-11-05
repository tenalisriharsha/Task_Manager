# File: tasksapp/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseBadRequest
from django.template.loader import render_to_string
from django.utils import timezone
from django.db import transaction
from django.core.paginator import Paginator
from datetime import date, timedelta
from core.models import SiteSetting
from .models import Task, Assignment, monday_of_week
from .forms import TaskForm

from functools import wraps

def is_leader(user):
    return SiteSetting.get_solo().current_leader_id == user.id or user.is_superuser or user.is_staff

# Require that the logged-in user's profile is approved; otherwise redirect to pending
def approved_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        # Safety: if Profile is missing, fail closed to pending
        prof = getattr(request.user, 'profile', None)
        if not prof or not prof.is_approved:
            return redirect('accounts:pending')
        return view_func(request, *args, **kwargs)
    return _wrapped

@login_required
@approved_required
def home(request):
    from django.db.models import Q

    now = timezone.now()

    # Use DB-level querysets (faster than slicing a Python list)
    base_qs = (Assignment.objects
               .select_related('task', 'assignee', 'assignee__profile')
               .order_by('-task__week_start', 'task__due_at'))

    assigned = list(base_qs.filter(status=Assignment.STATUS_ASSIGNED))
    submitted = list(base_qs.filter(status=Assignment.STATUS_SUBMITTED))
    approved = list(base_qs.filter(status=Assignment.STATUS_APPROVED))

    # Overdue = due time passed and not approved
    overdue = list(base_qs.filter(task__due_at__lt=now).exclude(status=Assignment.STATUS_APPROVED))

    # Apply -10 once for each freshly overdue assignment
    for a in overdue:
        if hasattr(a, 'late_penalized') and not a.late_penalized:
            prof = a.assignee.profile
            prof.points_total = (prof.points_total or 0) - 10
            prof.save(update_fields=['points_total'])
            a.late_penalized = True
            a.save(update_fields=['late_penalized'])

    # Weekly leaderboard (Mon–Sun)
    today = date.today()
    week_start = monday_of_week(today)

    weekly_points = {}
    weekly_stars = {}
    week_approved = [a for a in approved if a.task.week_start == week_start]
    for a in week_approved:
        weekly_points[a.assignee_id] = weekly_points.get(a.assignee_id, 0) + (a.points_awarded or 0)
        weekly_stars[a.assignee_id] = weekly_stars.get(a.assignee_id, 0) + (a.stars_awarded or 0)

    top_points = sorted(weekly_points.items(), key=lambda x: x[1], reverse=True)[:5]
    top_stars = sorted(weekly_stars.items(), key=lambda x: x[1], reverse=True)[:5]

    # Fetch involved users in one query
    user_ids = {uid for uid, _ in (top_points + top_stars)}
    users_map = {u.id: u for u in User.objects.filter(id__in=user_ids)}
    top_points = [(users_map.get(uid), pts) for uid, pts in top_points]
    top_stars = [(users_map.get(uid), st) for uid, st in top_stars]

    # ---- Full leaderboard (all members with last activity) ----
    users_all = (User.objects
                 .filter(is_active=True)
                 .select_related('profile')
                 .order_by('-profile__points_total', 'username'))

    leaderboard_all = []
    for u in users_all:
        last_task_title = None
        last_points = 0
        last_when = None
        last_status = None

        # Prefer most recent APPROVED (points_awarded is meaningful)
        last = (Assignment.objects
                .filter(assignee=u, status=Assignment.STATUS_APPROVED)
                .select_related('task')
                .order_by('-approved_at')
                .first())
        if last:
            last_status = 'approved'
            last_when = last.approved_at
            last_points = last.points_awarded or 0
            last_task_title = last.task.title if last.task_id else None
        else:
            # Fall back to most recent SUBMITTED
            last = (Assignment.objects
                    .filter(assignee=u, status=Assignment.STATUS_SUBMITTED)
                    .select_related('task')
                    .order_by('-submitted_at')
                    .first())
            if last:
                last_status = 'submitted'
                last_when = last.submitted_at
                last_task_title = last.task.title if last.task_id else None
            else:
                # Finally, most recent ASSIGNED (by due_at then id)
                last = (Assignment.objects
                        .filter(assignee=u, status=Assignment.STATUS_ASSIGNED)
                        .select_related('task')
                        .order_by('-task__due_at', '-id')
                        .first())
                if last:
                    last_status = 'assigned'
                    last_when = last.task.due_at
                    last_task_title = last.task.title if last.task_id else None

        leaderboard_all.append({
            'user': u,
            'points_total': getattr(getattr(u, 'profile', None), 'points_total', 0) or 0,
            'last_task_title': last_task_title,
            'last_points': last_points,
            'last_when': last_when,
            'last_status': last_status,
        })

    return render(request, 'tasksapp/home.html', {
        'assigned': assigned,
        'submitted': submitted,
        'approved': approved,
        'overdue': overdue,
        'is_leader': is_leader(request.user),
        'top_points': top_points,
        'top_stars': top_stars,
        'leaderboard_all': leaderboard_all,
        'week_start': week_start,
        'now': now,
    })

@login_required
@approved_required
def task_new(request):
    if not is_leader(request.user):
        messages.error(request, 'Only leader/admin can create tasks.')
        return redirect('tasksapp:home')
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            assignees = form.cleaned_data.pop('assignees', [])
            task = form.save(commit=False)
            task.created_by = request.user
            task.save()
            for u in assignees:
                Assignment.objects.get_or_create(task=task, assignee=u)
            messages.success(request, 'Task created and assigned.')
            return redirect('tasksapp:home')
    else:
        # Defaults: current week Monday
        from datetime import date
        from .models import monday_of_week
        initial = {'week_start': monday_of_week(date.today())}
        form = TaskForm(initial=initial)
    return render(request, 'tasksapp/task_form.html', {'form': form})

@login_required
@approved_required
@transaction.atomic
def assignment_submit(request, pk):
    a = get_object_or_404(Assignment, pk=pk, assignee=request.user)
    if a.status != Assignment.STATUS_ASSIGNED:
        return HttpResponseBadRequest("Invalid state.")

    now = timezone.now()
    # Block submissions after deadline; apply -10 once if available
    if a.task.due_at and now > a.task.due_at:
        if hasattr(a, 'late_penalized') and not a.late_penalized:
            p = a.assignee.profile
            p.points_total = (p.points_total or 0) - 10
            p.save(update_fields=['points_total'])
            a.late_penalized = True
            a.save(update_fields=['late_penalized'])
        # Return updated card for HTMX or flash + redirect otherwise
        if request.headers.get('HX-Request'):
            html = render_to_string('tasksapp/_card.html', {'a': a, 'is_leader': is_leader(request.user)}, request=request)
            return HttpResponse(html, headers={'HX-Trigger': 'deadline-passed'})
        messages.error(request, 'Deadline passed — cannot submit; -10 points applied.')
        return redirect('tasksapp:home')

    # Normal submit flow
    a.mark_submitted()
    if request.headers.get('HX-Request'):
        html = render_to_string('tasksapp/_card.html', {'a': a, 'is_leader': is_leader(request.user)}, request=request)
        return HttpResponse(html, headers={'HX-Trigger': 'assignment-submitted'})
    messages.success(request, 'Marked complete; awaiting approval.')
    return redirect('tasksapp:home')

@login_required
@approved_required
def assignment_approve(request, pk):
    a = get_object_or_404(Assignment, pk=pk)
    if not is_leader(request.user):
        return HttpResponseBadRequest("Only leader/admin can approve.")
    if a.status not in [Assignment.STATUS_SUBMITTED, Assignment.STATUS_ASSIGNED]:
        return HttpResponseBadRequest("Invalid state.")
    a.approve(request.user)
    # Record approver and ensure approved_at exists for history
    a.approved_by = request.user
    if not a.approved_at:
        a.approved_at = timezone.now()
    a.save(update_fields=["approved_by", "approved_at"])
    if request.headers.get('HX-Request'):
        html = render_to_string('tasksapp/_card.html', {'a': a, 'is_leader': is_leader(request.user)})
        # Fire confetti on the client
        return HttpResponse(html, headers={'HX-Trigger': 'approved-confetti'})
    messages.success(request, 'Approved! 🎉')
    return redirect('tasksapp:home')

@login_required
@approved_required
def assignment_star(request, pk):
    a = get_object_or_404(Assignment, pk=pk)
    if not is_leader(request.user):
        return HttpResponseBadRequest("Only leader/admin can star.")
    a.award_star()
    # If already approved, reflect +2 extra points
    if a.status == Assignment.STATUS_APPROVED:
        p = a.assignee.profile
        p.stars_total += 1
        p.points_total += 2
        a.points_awarded += 2
        a.save()
        p.save()
    if request.headers.get('HX-Request'):
        html = render_to_string('tasksapp/_card.html', {'a': a, 'is_leader': is_leader(request.user)})
        return HttpResponse(html, headers={'HX-Trigger': 'star-awarded'})
    messages.success(request, 'Star added.')
    return redirect('tasksapp:home')

@login_required
@approved_required
def history(request):
    now = timezone.now()
    qs = (Assignment.objects
          .select_related('task', 'assignee', 'approved_by')
          .order_by('-approved_at', '-submitted_at', '-created_at', '-id'))

    paginator = Paginator(qs, 25)
    page = paginator.get_page(request.GET.get('page'))

    # Compute display status for current page items
    for a in page.object_list:
        if a.status == Assignment.STATUS_APPROVED:
            a.display_status = 'Done'
        elif a.due_at and a.due_at < now and a.status != Assignment.STATUS_APPROVED:
            a.display_status = 'Incomplete'
        elif a.status == Assignment.STATUS_SUBMITTED:
            a.display_status = 'Submitted'

        else:
            a.display_status = 'Assigned'

    return render(request, 'tasksapp/history.html', {
        'page_obj': page,
    })
