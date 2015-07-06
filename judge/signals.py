from django.dispatch import Signal, receiver

from judge.models import UserStatts

problem_tried = Signal(providing_args = ['data'])

@receiver(problem_tried)
def receive_problem_tried(sender, **kwargs):
    data = kwargs['data']

    statts = UserStatts.objects.get(user = data.user)
    statts.triedProblems += 1
    statts.save()
