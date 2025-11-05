# File: elections/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Election, Vote
from .forms import ElectionForm, VoteForm
from core.models import SiteSetting
from datetime import timedelta

def is_admin_or_leader(user):
    settings = SiteSetting.get_solo()
    return user.is_superuser or user.is_staff or (settings.current_leader_id == user.id)

@login_required
def current(request):
    now = timezone.now()
    election = Election.objects.filter(end_at__gte=now).order_by('start_at').first()
    candidates = User.objects.filter(is_active=True, profile__is_approved=True)
    voted = None
    if election and request.user.is_authenticated:
        voted = Vote.objects.filter(election=election, voter=request.user).first()
    form = VoteForm(candidates_qs=candidates, initial={'candidate': voted.candidate_id if voted else None})
    return render(request, 'elections/current.html', {
        'election': election,
        'form': form,
        'voted': voted,
        'candidates': candidates,
    })

@login_required
@user_passes_test(is_admin_or_leader)
def manage(request):
    elections = Election.objects.order_by('-start_at')[:12]
    return render(request, 'elections/manage.html', {'elections': elections})

@login_required
@user_passes_test(is_admin_or_leader)
def create_election(request):
    if request.method == 'POST':
        form = ElectionForm(request.POST)
        if form.is_valid():
            e = form.save(commit=False)
            e.created_by = request.user
            e.save()
            messages.success(request, 'Election created.')
            return redirect('elections:manage')
    else:
        now_local = timezone.localtime(timezone.now()).replace(second=0, microsecond=0)
        initial = {'start_at': now_local, 'end_at': now_local + timedelta(days=1)}
        form = ElectionForm(initial=initial)
    return render(request, 'elections/new.html', {'form': form})

@login_required
def vote(request, election_id):
    election = get_object_or_404(Election, pk=election_id)
    if not election.is_open:
        messages.error(request, 'Election is not open.')
        return redirect('elections:current')
    candidates = User.objects.filter(is_active=True, profile__is_approved=True)
    form = VoteForm(request.POST or None, candidates_qs=candidates)
    if request.method == 'POST' and form.is_valid():
        candidate = form.cleaned_data['candidate']
        v, _ = Vote.objects.update_or_create(
            election=election, voter=request.user,
            defaults={'candidate': candidate}
        )
        messages.success(request, f'Voted for {candidate.username}. You can change it until close.')
        return redirect('elections:current')
    messages.error(request, 'Invalid vote.')
    return redirect('elections:current')

@login_required
@user_passes_test(is_admin_or_leader)
def close_election(request, election_id):
    election = get_object_or_404(Election, pk=election_id)
    election.end_at = timezone.now()
    election.save()
    winner = election.finalize_and_set_leader()
    if winner:
        messages.success(request, f'Election closed. Leader is {winner.username}.')
    else:
        messages.info(request, 'Election closed. No votes.')
    return redirect('elections:manage')
