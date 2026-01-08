from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # --- AUTENTICAÇÃO (Mantendo o original) ---
    path('signup/', views.cadastro, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='tickets/registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # --- SOLICITANTE ---
    path('abrir/', views.abrir_chamado, name='abrir_chamado'),
    path('meus/', views.meus_tickets, name='meus_tickets'),
    path('historico/', views.historico_tickets, name='historico_tickets'),

    # --- AÇÕES DO TICKET ---
    path('ver/<int:ticket_id>/', views.ver_ticket, name='ver_ticket'),
    path('editar/<int:ticket_id>/', views.editar_chamado, name='editar_chamado'),
    path('cancelar/<int:ticket_id>/', views.cancelar_chamado, name='cancelar_chamado'),

    # --- RESOLUTOR ---
    path('resolutor/', views.area_resolutor, name='area_resolutor'),
    
    # CORREÇÃO 1: Mudamos o name para 'triagem_ticket' (para funcionar com o template novo)
    path('resolutor/triagem/<int:ticket_id>/', views.realizar_triagem, name='triagem_ticket'),

    # CORREÇÃO 2: Adicionada rota de Workflow (Pausar/Retomar SLA)
    path('workflow/<int:ticket_id>/<str:acao>/', views.acao_workflow, name='acao_workflow'),

    # --- GESTÃO & DASHBOARD ---
    path('dashboard/', views.dashboard_geral, name='dashboard_geral'),
    path('gestao/', views.painel_gestor, name='painel_gestor'),
    path('perfil/', views.meu_perfil, name='meu_perfil'),

    # --- AJAX (Dropdowns em Cascata) ---
    path('ajax/load-subsetores/', views.load_subsetores, name='ajax_load_subsetores'),
    path('ajax/load-categorias/', views.load_categorias, name='ajax_load_categorias'),
]