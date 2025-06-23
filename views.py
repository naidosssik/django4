from django.shortcuts import render, get_object_or_404, redirect
from .models import Nomination, Nominee, Vote, User, Jury, Role
from django.db.models import Count, Avg, Max

from django.template.loader import render_to_string
from django.http import HttpResponse
# import weasyprint
from django.contrib.admin.views.decorators import staff_member_required


def index(request):
    """
    Функция отображения для домашней страницы сайта онлайн-голосования.
    """
    num_nominations = Nomination.objects.count()
    num_nominees = Nominee.objects.count()
    num_votes = Vote.objects.count()
    num_users = User.objects.count()
    num_jury_members = Jury.objects.count()
    nominees = Nominee.objects.all()[:5] 

    return render(
        request,
        'nomination/index.html',
        context={
            'num_nominations': num_nominations,
            'num_nominees': num_nominees,
            'num_votes': num_votes,
            'num_users': num_users,
            'num_jury_members': num_jury_members,
            'nominees': nominees,
        },
    )

def nominations_view(request):
    nominations = Nomination.objects.prefetch_related('nominees').all()
    return render(request, 'nomination/nominations.html', {'nominations': nominations})

def nominees_view(request):
    nominees = Nominee.objects.select_related('user', 'nomination').all()
    return render(request, 'nomination/nominees.html', {'nominees': nominees})

def votes_view(request):
    votes = Vote.objects.select_related('user', 'nominee').order_by('-voted_at') # votes = Vote.objects.select_related('user', 'nominee').prefetch_related('nominee__nomination').all()
    return render(request, 'nomination/votes.html', {'votes': votes})

def jury_panel_view(request):
    juries = Jury.objects.select_related('user').all()
    return render(request, 'nomination/jury_panel.html', {'juries': juries})


# def nominee_detail_view(request, pk):
#    nominee = get_object_or_404(Nominee, pk=pk)
#    return render(request, 'nomination/nominee_detail.html', {'nominee': nominee})


def some_view(request):
    votes = Vote.objects.filter(nominee__nomination_id=3)
    nominees = Nominee.objects.filter(project_name__startswith='Р').select_related('nomination')
    nominees_excluded = Nominee.objects.exclude(nomination_id=4)
    nominees_ordered = Nominee.objects.order_by('project_name')
    votes_ordered = Vote.objects.order_by('-voted_at')
    nominations = Nomination.objects.annotate(num_nominees=Count('nominees'))
    avg_votes = Nominee.objects.annotate(votes_count=Count('votes')).aggregate(avg_votes=Avg('votes_count'))
    max_votes = Nominee.objects.annotate(votes_count=Count('votes')).aggregate(max_votes=Max('votes_count'))

    context = {
        'votes': votes,
        'nominees': nominees,
        'nominees_excluded': nominees_excluded,
        'nominees_ordered': nominees_ordered,
        'votes_ordered': votes_ordered,
        'nominations': nominations,
        'avg_votes': avg_votes['avg_votes'],
        'max_votes': max_votes['max_votes'],
    }
    return render(request, 'nomination/filter_template.html', context)


def nominee_delete(request, pk):
    nominee = get_object_or_404(Nominee, pk=pk)
    if request.method == 'POST':
        nominee.delete()
        return redirect('nominees')
    return render(request, 'nomination/nominee_delete.html', {'nominee': nominee})



from django.shortcuts import render
from .models import nkexam

def nkexam_list(request):
    exams = nkexam.objects.filter(is_public=True)
    context = {
        'exams': exams,
        'fio': 'Касумова Наида Рашидовна',  
        'group': '231-323',              
    }
    return render(request, 'nkexam.html', context)
    
