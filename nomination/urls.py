from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('nominations/', views.nominations_view, name='nominations'),
    path('jury_panel/', views.jury_panel_view, name='jury_panel'),

    path('nominees/', views.nominees_view, name='nominees'),
    path('nominee/add/', views.nominee_create, name='nominee_add'),
    path('nominee/<int:pk>/', views.nominee_detail_view, name='nominee_detail'),
    path('nominees/<int:pk>/edit/', views.nominee_edit, name='nominee_edit'),
    path('nominees/<int:pk>/delete/', views.nominee_delete, name='nominee_delete'),
    path('success/', views.success_view, name='nominee_success'),
    
    
    path('votes/', views.votes_view, name='votes'),
    path('votes/yes/', views.yes_votes_list, name='yes_votes_list'),
    path('votes/no/', views.no_votes_list, name='no_votes_list'),
    
    path('vote/<int:nominee_id>/', views.vote_nominee, name='vote_nominee'),
]



