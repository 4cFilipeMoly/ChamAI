from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('signup/', views.cadastro, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='tickets/registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('abrir/', views.abrir_chamado, name='abrir_chamado'),
    path('meus/', views.meus_tickets, name='meus_tickets'),
    path('historico/', views.historico_tickets, name='historico_tickets'),
    path('ver/<int:ticket_id>/', views.ver_ticket, name='ver_ticket'),
    path('editar/<int:ticket_id>/', views.editar_chamado, name='editar_chamado'),
    path('cancelar/<int:ticket_id>/', views.cancelar_chamado, name='cancelar_chamado'),
    path('resolutor/', views.area_resolutor, name='area_resolutor'),
    path('resolutor/triagem/<int:ticket_id>/', views.realizar_triagem, name='realizar_triagem'),
    path('gerenciar-workflow/<int:ticket_id>/', views.gerenciar_workflow, name='gerenciar_workflow'),
    path('dashboard/', views.dashboard_geral, name='dashboard_geral'),
    path('gestao/', views.painel_gestor, name='painel_gestor'),
    path('perfil/', views.meu_perfil, name='meu_perfil'),
    path('ajax/load-subsetores/', views.load_subsetores, name='ajax_load_subsetores'),
    path('ajax/load-categorias/', views.load_categorias, name='ajax_load_categorias'),
]