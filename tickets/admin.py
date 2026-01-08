from django.contrib import admin
from .models import Setor, Subsetor, CategoriaConfig, Colaborador, Chamado

# --- INLINES (Tabelas dentro de outras tabelas) ---

class CategoriaInline(admin.TabularInline):
    model = CategoriaConfig
    extra = 1

class SubsetorInline(admin.TabularInline):
    model = Subsetor
    extra = 1

# --- ADMINS PRINCIPAIS ---

@admin.register(Setor)
class SetorAdmin(admin.ModelAdmin):
    list_display = ('id_setor', 'nome', 'is_gestor')
    ordering = ('nome',)
    inlines = [SubsetorInline] # Mostra os subsetores dentro do Setor

@admin.register(Subsetor)
class SubsetorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'setor_pai')
    list_filter = ('setor_pai',)
    inlines = [CategoriaInline] # Mostra as categorias dentro do Subsetor

@admin.register(CategoriaConfig)
class CategoriaConfigAdmin(admin.ModelAdmin):
    list_display = ('nome', 'subsetor_pertencente', 'sla_padrao_horas')
    list_filter = ('subsetor_pertencente__setor_pai', 'subsetor_pertencente')
    search_fields = ('nome',)

@admin.register(Colaborador)
class ColaboradorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'user', 'setor', 'subsetor', 'is_manager')
    list_filter = ('setor', 'is_manager')
    search_fields = ('nome', 'user__email')
    filter_horizontal = ('categorias_atribuidas',) # Facilita seleção de muitas categorias

@admin.register(Chamado)
class ChamadoAdmin(admin.ModelAdmin):
    list_display = ('id_chamado', 'titulo', 'solicitante', 'status', 'sla_status_label', 'data_abertura')
    list_filter = ('status', 'flash', 'setor_destino_cache')
    search_fields = ('titulo', 'descricao', 'id_chamado')
    readonly_fields = ('id_chamado', 'data_abertura', 'data_fechamento', 'ice_score_final')
    
    fieldsets = (
        ('Identificação', {
            'fields': ('id_chamado', 'titulo', 'solicitante', 'flash')
        }),
        ('Classificação', {
            'fields': ('setor_destino_cache', 'categoria', 'status')
        }),
        ('Inteligência', {
            'fields': ('impacto_solicitante', 'confianca_responsavel', 'facilidade_responsavel', 'ice_score_final')
        }),
        ('Prazos', {
            'fields': ('data_abertura', 'prazo_resposta_inicial', 'sla_prazo', 'data_fechamento')
        }),
        ('Detalhes', {
            'fields': ('descricao', 'descricao_resposta', 'caminhos_anexos')
        }),
    )