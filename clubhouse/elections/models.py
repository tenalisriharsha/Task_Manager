# File: elections/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from core.models import SiteSetting

class Election(models.Model):
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"Election {self.start_at:%Y-%m-%d}"

    @property
    def is_open(self):
        now = timezone.now()
        return self.start_at <= now <= self.end_at

    def finalize_and_set_leader(self):
        # Compute votes, tie-break by earliest last_vote_at
        votes = (Vote.objects
                 .filter(election=self)
                 .values('candidate')
                 .annotate(count=models.Count('id')))
        if not votes:
            return None
        max_count = max(v['count'] for v in votes)
        top_candidates = [v['candidate'] for v in votes if v['count'] == max_count]
        if len(top_candidates) == 1:
            winner_id = top_candidates[0]
        else:
            earliest = (Vote.objects
                        .filter(election=self, candidate_id__in=top_candidates)
                        .order_by('last_vote_at').first())
            winner_id = earliest.candidate_id if earliest else top_candidates[0]
        winner = User.objects.get(pk=winner_id)
        settings = SiteSetting.get_solo()
        settings.current_leader = winner
        settings.save()
        return winner

class Vote(models.Model):
    election = models.ForeignKey(Election, on_delete=models.CASCADE)
    voter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='votes_cast')
    candidate = models.ForeignKey(User, on_delete=models.CASCADE, related_name='votes_received')
    last_vote_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('election', 'voter')
