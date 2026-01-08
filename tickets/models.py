import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

# --- ESTRUTURA ORGANIZACIONAL ---
class Setor(models.Model):
    id_setor = models.IntegerField(unique=True, verbose_name="ID Numérico")
    nome = models.CharField(max_length=255)
    email_setor = models.EmailField(null=True, blank=True)
    is_gestor = models.BooleanField(default=False, verbose_name="É setor de Gestão?")
    def __str__(self): return self.nome

class Subsetor(models.Model):
    setor_pai = models.ForeignKey(Setor, on_delete=models.CASCADE, related_name='subsetores')
    nome = models.CharField(max_length=255)
    def __str__(self): return f"{self.nome} ({self.setor_pai.nome})"

class CategoriaConfig(models.Model):
    nome = models.CharField(max_length=255)
    subsetor_pertencente = models.ForeignKey(Subsetor, on_delete=models.CASCADE, related_name='categorias')
    sla_padrao_horas = models.IntegerField(default=24, help_text="SLA padrão em horas")
    def __str__(self): return f"{self.nome} ({self.subsetor_pertencente.nome})"

# --- USUÁRIOS ---
class Colaborador(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='colaborador')
    nome = models.CharField(max_length=255)
    setor = models.ForeignKey(Setor, on_delete=models.SET_NULL, null=True)
    subsetor = models.ForeignKey(Subsetor, on_delete=models.SET_NULL, null=True, blank=True)
    categorias_atribuidas = models.ManyToManyField(CategoriaConfig, blank=True, related_name='resolutores')
    is_manager = models.BooleanField(default=False, verbose_name="É Gestor?")
    def __str__(self): return self.nome
    @property
    def is_resolutor(self): return self.categorias_atribuidas.exists()

# --- CHAMADOS ---
class Chamado(models.Model):
    STATUS_CHOICES = [
        ('Em fila', 'Em fila'),
        ('Em Produção', 'Em Produção'),
        ('Stand By', 'Stand By'),
        ('Homologação', 'Homologação'),
        ('Fechado', 'Fechado'),
        ('Declinado', 'Declinado'),
        ('Evitado', 'Evitado'),
        ('Cancelado', 'Cancelado'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    id_chamado = models.IntegerField(editable=False, unique=True, null=True, verbose_name="ID #")
    
    solicitante = models.ForeignKey(Colaborador, on_delete=models.CASCADE, related_name='solicitacoes')
    categoria = models.ForeignKey(CategoriaConfig, on_delete=models.SET_NULL, null=True)
    setor_destino_cache = models.ForeignKey(Setor, on_delete=models.SET_NULL, null=True, blank=True)
    responsavel_tecnico = models.ForeignKey(Colaborador, on_delete=models.SET_NULL, null=True, blank=True, related_name='atendimentos')
    
    # Campo para saber se o usuário editou o chamado depois de abrir
    flag_editado = models.BooleanField(default=False, verbose_name="Foi editado?")

    titulo = models.CharField(max_length=150)
    descricao = models.TextField()
    
    # --- INTELEGÊNCIA DE PRAZOS (ICE & SLA) ---
    impacto_solicitante = models.IntegerField(default=5, help_text="1-10")
    confianca_responsavel = models.IntegerField(default=5)
    facilidade_responsavel = models.IntegerField(default=5)
    ice_score_final = models.FloatField(default=0.0)
    
    flash = models.BooleanField(default=False)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Em fila')
    
    data_abertura = models.DateTimeField(auto_now_add=True)
    data_em_producao = models.DateTimeField(null=True, blank=True)
    data_fechamento = models.DateTimeField(null=True, blank=True)
    
    # --- NOVOS CAMPOS DE CONTROLE DE TEMPO ---
    prazo_resposta_inicial = models.DateTimeField(null=True, blank=True, verbose_name="Prazo 1ª Resposta")
    sla_prazo = models.DateTimeField(null=True, blank=True, verbose_name="SLA Resolução")
    
    data_inicio_standby = models.DateTimeField(null=True, blank=True)
    tempo_total_standby = models.DurationField(default=timedelta(0))
    
    descricao_resposta = models.TextField(null=True, blank=True)
    justificativa_recusa = models.TextField(null=True, blank=True)
    caminhos_anexos = models.JSONField(default=dict, blank=True, null=True)

    def save(self, *args, **kwargs):
        # 1. Gera ID se não existir
        if not self.id_chamado:
            last = Chamado.objects.all().order_by('id_chamado').last()
            self.id_chamado = (last.id_chamado + 1) if last and last.id_chamado else 1
        
        # 2. Cache do Setor
        if self.categoria and self.categoria.subsetor_pertencente:
            self.setor_destino_cache = self.categoria.subsetor_pertencente.setor_pai

        # 3. Calcula ICE Score
        self.ice_score_final = round((self.impacto_solicitante + self.confianca_responsavel + self.facilidade_responsavel) / 3, 1)

        # 4. REGRA DE PRAZO DE 1ª RESPOSTA
        # Calcula apenas se ainda não tiver data definida ou se for um novo salvamento
        if not self.prazo_resposta_inicial:
            agora = timezone.now()
            
            if self.flash:
                # Regra Flash: 1 Hora
                self.prazo_resposta_inicial = agora + timedelta(hours=1)
            else:
                # Regra Normal: Baseada no Impacto
                if self.impacto_solicitante >= 8: # Alto/Crítico
                    horas = 4
                elif self.impacto_solicitante >= 5: # Médio
                    horas = 8
                else: # Baixo
                    horas = 24
                self.prazo_resposta_inicial = agora + timedelta(hours=horas)

        super().save(*args, **kwargs)

    def pausar_sla(self):
        if self.status != 'Stand By':
            self.status = 'Stand By'
            self.data_inicio_standby = timezone.now()
            self.save()

    def retomar_sla(self, novo_prazo=None):
        if self.status == 'Stand By' and self.data_inicio_standby:
            pausa = timezone.now() - self.data_inicio_standby
            self.tempo_total_standby += pausa
            if not novo_prazo and self.sla_prazo:
                self.sla_prazo += pausa
            elif novo_prazo:
                self.sla_prazo = novo_prazo
            self.status = 'Em Produção'
            self.data_inicio_standby = None
            self.save()

    @property
    def sla_status_label(self):
        if self.status in ['Fechado', 'Cancelado', 'Declinado', 'Evitado']: return "Finalizado"
        if self.status == 'Stand By': return "Pausado"
        if self.sla_prazo and timezone.now() > self.sla_prazo: return "Vencido"
        return "No Prazo"
    
    @property
    def is_editable(self):
        # Permite editar apenas se estiver na fila e sem técnico atribuído
        return self.status.lower() == 'em fila' and self.responsavel_tecnico is None

    # Propriedade para ajudar na flag de "Vencido" (SLA Geral)
    @property
    def esta_vencido(self):
        if self.sla_prazo and timezone.now() > self.sla_prazo:
            return True
        return False

    # Propriedade para checar 1ª resposta
    @property
    def estourou_primeira_resposta(self):
        if self.prazo_resposta_inicial and timezone.now() > self.prazo_resposta_inicial:
            return True
        return False