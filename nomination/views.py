from django.shortcuts import render, redirect, get_object_or_404
from .models import Nomination, Nominee, Vote, User, Jury
from django.db.models import Count, Avg, Max
from .forms import NomineeForm
from django.contrib.auth.decorators import login_required

from django.db.models import F, Q, Value
from django.db.models.functions import Concat

from django.utils.timezone import now, timedelta


def index(request):
    """
    Функция отображения для домашней страницы сайта онлайн-голосования.
    """
    num_nominations = Nomination.objects.count()
    num_nominees = Nominee.objects.count()
    num_votes = Vote.objects.count()
    num_users = User.objects.count()
    num_jury_members = Jury.objects.count()
    
    
    nominee_projects = Nominee.objects.values_list('project_name', flat=True)[:5]
    nominee_order = Nominee.objects.exclude(contact__isnull=True).order_by('project_name')
    nomination_names = Nomination.objects.values('name')[:5]
    has_nominees_without_contact = Nominee.objects.filter(contact__isnull=True).exists()
    
    nominations = Nomination.objects.annotate(num_nominees=Count('nominees'))
    avg_votes = Nominee.objects.annotate(votes_count=Count('votes')).aggregate(avg=Avg('votes_count'))
    max_votes = Nominee.objects.annotate(votes_count=Count('votes')).aggregate(max=Max('votes_count'))

    return render(
        request,
        'nomination/index.html',
        context={
            'num_nominations': num_nominations,
            'num_nominees': num_nominees,
            'num_votes': num_votes,
            'num_users': num_users,
            'num_jury_members': num_jury_members,
            
            'nominee_projects': nominee_projects,
            'nominee_order': nominee_order,
            'nomination_names': nomination_names,
            'has_nominees_without_contact': has_nominees_without_contact,
            
            'nominations': nominations,
            'avg_votes': avg_votes['avg'],
            'max_votes': max_votes['max'],
        },
    )

def nominations_view(request):
    nominations = Nomination.objects.prefetch_related('nominees').all()
    active_exists = nominations.filter(end_date__isnull=True).exists()
    
    context = {
        'nominations': nominations,
        'active_exists': active_exists,
    }
    return render(request, 'nomination/nominations.html', context)

def nominees_view(request):
    search = request.GET.get('search', '')
    if search:
        nominees = Nominee.objects.filter(project_name__contains=search)
    else:
        nominees = Nominee.objects.all()
    return render(request, 'nomination/nominee/nominees.html', {'nominees': nominees, 'search': search})

def votes_view(request):
    votes = Vote.objects.select_related('user', 'nominee').order_by('-voted_at')


    updated = False
    deleted = False
    votes_count = votes.count()
    has_abstain = votes.filter(choice='A').exists()

    if request.GET.get('update') == '1':
        votes.filter(choice='A').update(choice='Y')
        updated = True

    if request.GET.get('delete') == '1':
        cutoff_date = now() - timedelta(days=365)
        votes.filter(voted_at__lt=cutoff_date).delete()
        deleted = True

    context = {
        'votes': votes,
        'votes_count': votes_count,
        'has_abstain': has_abstain,
        'updated': updated,
        'deleted': deleted,
    }
    return render(request, 'nomination/votes/votes.html', context)

def yes_votes_list(request):
    yes_votes = Vote.yes_votes.all()
    return render(request, 'nomination/votes/yes_votes_list.html', {'yes_votes': yes_votes})

def no_votes_list(request):
    no_votes = Vote.no_votes.all()
    return render(request, 'nomination/votes/no_votes_list.html', {'votes': no_votes, 'title': 'Голоса "Против"'})

def nominee_detail_view(request, pk):
    nominee = get_object_or_404(Nominee, pk=pk)
    return render(request, 'nomination/nominee_detail.html', {'nominee': nominee}) # get_absolute_url

from django.db.models import F, Q

def jury_panel_view(request):
    search = request.GET.get('search', '')
    juries = Jury.objects.select_related('user')
    if search:
        juries = juries.filter(
            Q(user__name__icontains=search) | Q(user__surname__icontains=search)
        )

    updated = False
    deleted = False
    exists_photo = juries.filter(photo__isnull=False).exists()

    if request.GET.get('update') == '1':
        
        juries.filter(~Q(bio__icontains='[Обновлено]')).update(
            bio=Concat(F('bio'), Value(' [Обновлено]'))
        )
        updated = True

    if request.GET.get('delete') == '1':
        juries.filter(Q(bio='') | Q(bio__isnull=True)).delete()
        deleted = True

    context = {
        'juries': juries,
        'search': search,
        'updated': updated,
        'deleted': deleted,
        'exists_photo': exists_photo,
    }
    return render(request, 'nomination/jury_panel.html', context)


@login_required
def vote_nominee(request, nominee_id):
    nominee = get_object_or_404(Nominee, pk=nominee_id)
    user = request.user

    if request.method == 'POST':
        choice = request.POST.get('choice')
        if choice in ['Y', 'N', 'A']:
            Vote.objects.update_or_create(user=user, nominee=nominee, defaults={'choice': choice})
            return redirect('votes')
    
    return render(request, 'nomination/vote_nominee.html', {'nominee': nominee})


def nominee_create(request):
    if request.method == 'POST':
        form = NomineeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('votes')
    else:
        form = NomineeForm()
    return render(request, 'nomination/nominee/nominee_form.html', {'form': form, 'action': 'Создание'})


def nominee_edit(request, pk):
    nominee = get_object_or_404(Nominee, pk=pk)
    if request.method == 'POST':
        form = NomineeForm(request.POST, request.FILES, instance=nominee)
        if form.is_valid():
            form.save()
            return redirect('nominees')
    else:
        form = NomineeForm(instance=nominee)
    return render(request, 'nomination/nominee/nominee_form.html', {'form': form})


def nominee_delete(request, pk):
    nominee = get_object_or_404(Nominee, pk=pk)
    if request.method == 'POST':
        nominee.delete()
        return redirect('nominees')
    return render(request, 'nomination/nominee/nominee_delete.html', {'nominee': nominee})
