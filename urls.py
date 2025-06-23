from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('nominations/', views.nominations_view, name='nominations'),
    path('nominees/', views.nominees_view, name='nominees'),
    path('votes/', views.votes_view, name='votes'),
    path('jury_panel/', views.jury_panel_view, name='jury_panel'),

    path('nkexam/', views.nkexam, name='nkexam'),

    path('nominee/<int:pk>/delete/', views.nominee_delete, name='nominee_delete'), # delete nominee

]
